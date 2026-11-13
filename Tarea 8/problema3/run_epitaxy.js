/**
 * Corre el simulador de epitaxial_growth.html sin reescribir su física.
 * El script de la página se evalúa en una caja con un DOM mínimo y un
 * temporizador GSAP que se drena dentro de esa misma caja. Math.random
 * queda sembrado para poder repetir cada configuración.
 *
 *   node run_epitaxy.js
 *   node run_epitaxy.js --sweep resultados.json
 */
const fs = require("fs");
const os = require("os");
const path = require("path");
const { Worker, isMainThread, parentPort, workerData } = require("worker_threads");

const HTML_PATH = path.resolve(
  __dirname,
  "../../Growth Simulator/simulacion/tlplib/epitaxial-growth/HTML5/epitaxial_growth.html"
);

const WIDTH = 29;

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function extractInlineScripts(html) {
  const parts = [];
  const re = /<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi;
  let m;
  while ((m = re.exec(html))) {
    const open = m[0].slice(0, m[0].indexOf(">") + 1);
    if (/\ssrc\s*=/.test(open)) continue;
    parts.push(m[1]);
  }
  return parts.join("\n;\n");
}

function staticNodes(html) {
  const items = [];
  const re = /<([a-zA-Z0-9]+)([^>]*?)>/g;
  let m;
  while ((m = re.exec(html))) {
    const attrs = m[2];
    const id = (attrs.match(/\bid="([^"]*)"/) || [])[1] || "";
    const className = (attrs.match(/\bclass="([^"]*)"/) || [])[1] || "";
    if (id || className) items.push({ id, className });
  }
  return items;
}

const HTML = fs.readFileSync(HTML_PATH, "utf8");
const PAGE_JS = extractInlineScripts(HTML);
const PRE_NODES = staticNodes(HTML);

function createDocument() {
  const ids = Object.create(null);
  const classes = Object.create(null);
  function makeEl(id, className) {
    const e = { style: {}, attrs: Object.create(null), children: [], value: "" };
    e.setAttribute = function (name, value) {
      this.attrs[name] = String(value);
      if (name === "id" && value !== "") ids[value] = this;
    };
    e.setAttributeNS = function (_ns, name, value) {
      this.setAttribute(name, value);
    };
    e.getAttribute = function (name) {
      return Object.prototype.hasOwnProperty.call(this.attrs, name) ? this.attrs[name] : null;
    };
    e.appendChild = function (child) {
      this.children.push(child);
      return child;
    };
    if (id) e.setAttribute("id", id);
    if (className) {
      for (const bit of className.split(/\s+/)) {
        if (!bit) continue;
        if (!classes[bit]) classes[bit] = [];
        classes[bit].push(e);
      }
    }
    return e;
  }
  for (const item of PRE_NODES) makeEl(item.id, item.className);
  return {
    getElementById(id) {
      return ids[id] || null;
    },
    getElementsByClassName(c) {
      return classes[c] || [];
    },
    createElementNS() {
      return makeEl("", "");
    },
  };
}

function createGsap(timelines) {
  return {
    timeline() {
      const tl = {
        queue: [],
        paused: true,
        to(_sel, opts) {
          this.queue.push(opts.onComplete);
          return this;
        },
        pause() {
          this.paused = true;
        },
        play() {
          this.paused = false;
        },
      };
      timelines.push(tl);
      return tl;
    },
  };
}

// new Function mantiene el script en el mismo motor que este archivo.
// Una caja vm hace lentísimo el acceso a las variables globales de la página.
const factory = new Function(
  "document",
  "gsap",
  "Math",
  "window",
  `${PAGE_JS}
function __drain(tl) {
  var steps = 0;
  var MAX = 400000;
  while (!tl.paused && tl.queue.length && steps < MAX) {
    var cb = tl.queue.shift();
    steps++;
    cb();
  }
  return steps;
}
function __snapshot(n) {
  var atoms = [];
  for (var i = 1; i <= n; i++) {
    var el = document.getElementById(aatom[i]);
    if (!el) atoms.push(null);
    else atoms.push([Number(el.p), Number(el.q)]);
  }
  return {
    atoms: atoms,
    transformed: transformed,
    critical: critical,
    strain: strain,
    temperature: temperature,
    aabs: aabs,
    initaabs: initaabs,
    asbs: asbs,
    completed: completedlayers()
  };
}
return {
  go_sbListener: go_sbListener,
  temp_sbListener: temp_sbListener,
  aabs_sbListener: aabs_sbListener,
  asbs_sbListener: asbs_sbListener,
  sizedifference_sbListener: sizedifference_sbListener,
  gogo: gogo,
  __drain: __drain,
  __snapshot: __snapshot
};
`
);

function analyze(atoms) {
  const layerPs = new Map();
  let off = 0;
  let missing = 0;
  for (const site of atoms) {
    if (!site) {
      missing++;
      continue;
    }
    const [p, q] = site;
    const h = 14 - q;
    if (!Number.isFinite(p) || !Number.isFinite(q) || p < 0 || p > 28 || h < 1 || h > 20) {
      off++;
      continue;
    }
    if (!layerPs.has(h)) layerPs.set(h, new Set());
    layerPs.get(h).add(p);
  }
  const heights = Array(WIDTH).fill(0);
  for (const [h, set] of layerPs) {
    for (const p of set) heights[p] = Math.max(heights[p], h);
  }
  const coverage = {};
  const counts = {};
  let maxH = 0;
  for (const [h, set] of layerPs) {
    counts[h] = set.size;
    coverage[h] = +(set.size / WIDTH).toFixed(4);
    if (h > maxH) maxH = h;
  }
  let islands = 0;
  let inIsland = false;
  let maxGap = 0;
  let gap = 0;
  let occupied = 0;
  for (const h of heights) {
    if (h > 0) {
      occupied++;
      if (gap > maxGap) maxGap = gap;
      gap = 0;
      if (!inIsland) {
        islands++;
        inIsland = true;
      }
    } else {
      gap++;
      inIsland = false;
    }
  }
  if (gap > maxGap) maxGap = gap;
  const h1 = coverage[1] || 0;
  let above = 0;
  for (const [h, set] of layerPs) if (h >= 2) above += set.size;
  let complete = 0;
  for (let h = 1; h <= maxH; h++) if ((counts[h] || 0) === WIDTH) complete++;
  const sumH = heights.reduce((s, h) => s + h, 0);
  return {
    nAtoms: atoms.length - missing,
    missing,
    offLattice: off,
    maxHeight: maxH,
    layerCounts: counts,
    coverage,
    firstLayerCoverage: h1,
    firstLayerMaxGap: occupied === 0 ? WIDTH : maxGap,
    columnCoverage: +(occupied / WIDTH).toFixed(4),
    islands,
    atomsAboveFirstLayer: above,
    completeLayersFromAtoms: complete,
    meanColumnHeight: +(sumH / WIDTH).toFixed(3),
    multilayerWhileFirstOpen: above > 0 && h1 < 0.999,
    continuousFirstLayer: h1 >= 0.9 && maxGap <= 2,
    heights,
  };
}

function runOnce({ n, tSlider, aabs, asbs, mismatchSlider, seed }) {
  const document = createDocument();
  const timelines = [];
  const gsap = createGsap(timelines);
  const math = Object.create(Math);
  math.random = mulberry32(seed);
  const api = factory(document, gsap, math, {});
  let steps = 0;
  let error = null;
  let snap = null;
  try {
    api.go_sbListener(n);
    api.temp_sbListener(tSlider);
    api.aabs_sbListener(aabs);
    api.asbs_sbListener(asbs);
    api.sizedifference_sbListener(mismatchSlider);
    api.gogo();
    steps = api.__drain(timelines[0]);
    if (steps >= 400000) error = "max-steps";
    snap = api.__snapshot(n);
  } catch (err) {
    error = String(err && err.stack ? err.stack : err);
    try {
      snap = api.__snapshot(n);
    } catch (err2) {
      snap = { atoms: [], transformed: false, critical: null, strain: null, temperature: null, aabs: null, initaabs: null, asbs: null, completed: null };
    }
  }
  const atoms = snap.atoms || [];
  const metrics = analyze(atoms);
  return {
    n,
    tSlider,
    tOverTm: Math.round(tSlider * 100) / 10000,
    aabs,
    asbs,
    mismatchSlider,
    mismatchPercent: mismatchSlider / 100,
    seed,
    steps,
    error,
    transformed: Boolean(snap.transformed),
    critical: snap.critical,
    strain: snap.strain,
    temperatureInternal: snap.temperature,
    aabsFinal: snap.aabs == null ? null : Number(snap.aabs),
    initaabs: snap.initaabs == null ? null : Number(snap.initaabs),
    completedLayersInternal: snap.completed,
    atoms,
    metrics,
  };
}

function tag(r) {
  return `N${r.n}_T${r.tOverTm}_aa${r.aabs}_as${r.asbs}_m${r.mismatchPercent}_s${r.seed}`;
}

function summarize(r) {
  const m = r.metrics;
  const cov = ((m.firstLayerCoverage || 0) * 100).toFixed(0);
  return `${tag(r)} h=${m.maxHeight} cov1=${cov}% gap=${m.firstLayerMaxGap} isl=${m.islands} above=${m.atomsAboveFirstLayer} full=${m.completeLayersFromAtoms} SK=${r.transformed} crit=${r.critical} err=${r.error ? "Y" : "N"} steps=${r.steps}`;
}

function sweep() {
  const jobs = [];
  const add = (group, spec, Ns, seeds) => {
    for (const n of Ns) {
      for (const seed of seeds) {
        jobs.push({ group, ...spec, n, seed });
      }
    }
  };

  add("baseline", { tSlider: 50, aabs: 50, asbs: 25, mismatchSlider: 0 }, [21, 31, 81, 141], [1, 2, 3, 4, 5]);

  const pairs = [
    [0, 100], [10, 90], [20, 80], [30, 70], [30, 40], [40, 60],
    [50, 50], [50, 25], [50, 10], [60, 30], [70, 20], [80, 10],
    [90, 10], [100, 20], [100, 0], [40, 40], [20, 50], [60, 90],
  ];
  for (const [aabs, asbs] of pairs) {
    add("bonds", { tSlider: 50, aabs, asbs, mismatchSlider: 0 }, [21, 81, 141], [1, 2, 3]);
  }

  const skBonds = [[20, 80], [30, 70], [40, 60], [50, 50], [30, 40], [60, 90]];
  const skMismatch = [0, 30, 60, 90, 100];
  const skN = [31, 61, 91, 121, 141];
  for (const [aabs, asbs] of skBonds) {
    for (const mismatchSlider of skMismatch) {
      for (const tSlider of [50, 80]) {
        add("sk", { tSlider, aabs, asbs, mismatchSlider }, skN, [1, 2, 3]);
      }
    }
  }

  for (const [aabs, asbs] of [[20, 80], [50, 25], [90, 10], [50, 50]]) {
    for (const tSlider of [20, 30, 50, 70, 80]) {
      add("temperature", { tSlider, aabs, asbs, mismatchSlider: 0 }, [21, 81, 141], [1, 2, 3]);
    }
  }

  return jobs;
}

module.exports = { runOnce, analyze, tag, summarize, sweep };

function runJob(job) {
  const { group, ...spec } = job;
  const result = runOnce(spec);
  result.group = group;
  return result;
}

if (!isMainThread) {
  parentPort.on("message", (msg) => {
    if (!msg) {
      parentPort.close();
      return;
    }
    parentPort.postMessage({ i: msg.i, result: runJob(msg.job) });
  });
} else if (require.main === module) {
  const sweepIdx = process.argv.indexOf("--sweep");
  if (sweepIdx === -1) {
    const demo = runOnce({ n: 81, tSlider: 50, aabs: 50, asbs: 25, mismatchSlider: 0, seed: 1 });
    console.log(summarize(demo));
    console.log(JSON.stringify(demo.metrics, null, 2));
    process.exit(0);
  }
  const outPath = path.resolve(process.argv[sweepIdx + 1] || path.join(__dirname, "resultados.json"));
  const jobs = sweep();
  const nWorkers = Math.min(8, Math.max(1, os.cpus().length));
  const results = new Array(jobs.length);
  const t0 = Date.now();
  let next = 0;
  let done = 0;
  const pool = new Promise((resolve, reject) => {
    const launch = () => {
      const worker = new Worker(__filename, { workerData: { worker: true } });
      const send = () => {
        if (next >= jobs.length) {
          worker.postMessage(null);
          return;
        }
        const i = next++;
        worker.postMessage({ i, job: jobs[i] });
      };
      worker.on("message", (msg) => {
        results[msg.i] = msg.result;
        done++;
        if (done % 40 === 0 || done === jobs.length) {
          const dt = ((Date.now() - t0) / 1000).toFixed(1);
          console.log(`${done}/${jobs.length} ${dt}s  ${summarize(msg.result)}`);
        }
        if (done === jobs.length) resolve();
        else send();
      });
      worker.on("error", reject);
      send();
    };
    for (let w = 0; w < nWorkers; w++) launch();
  });
  pool
    .then(() => {
      const payload = {
        source: "Growth Simulator/simulacion/tlplib/epitaxial-growth/HTML5/epitaxial_growth.html",
        note: "Cada corrida ejecuta el script de la página con el generador aleatorio sembrado. El desajuste en % es el número que muestra la caja de texto (posición del slider / 100). 151 átomos no se usa: el HTML solo crea los sprites a1..a149 y el depósito 150 revienta.",
        generatedAt: new Date().toISOString(),
        results,
      };
      fs.writeFileSync(outPath, JSON.stringify(payload));
      console.log("wrote", outPath, "runs", results.length, "sec", ((Date.now() - t0) / 1000).toFixed(1));
    })
    .catch((err) => {
      console.error(err);
      process.exit(1);
    });
}
