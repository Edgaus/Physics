#!/usr/bin/env python3
"""Tablas de la barrida y figuras de red hexagonal."""
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

ROOT = Path(__file__).resolve().parent
WIDTH = 29


def load(path):
    data = json.loads(Path(path).read_text())
    return data["results"]


def key_of(r):
    return (r["aabs"], r["asbs"], r["tOverTm"], r["mismatchPercent"], r["n"])


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def fmt_pct(x):
    return f"{100 * x:5.1f}%"


def summarize(results, out):
    groups = defaultdict(list)
    for r in results:
        groups[r["group"]].append(r)

    lines = []
    def emit(s=""):
        lines.append(s)

    emit("ERRORES")
    nerr = [r for r in results if r["error"]]
    emit(f"  {len(nerr)} / {len(results)}")
    for r in nerr[:8]:
        emit(f"  {r['group']} N={r['n']} T={r['tOverTm']} aa={r['aabs']} as={r['asbs']} m={r['mismatchPercent']} seed={r['seed']} {str(r['error'])[:180]}")

    emit("\nBONDS T=0.5 m=0  (media de semillas)")
    emit(f"{'aa':>4} {'as':>4} {'N':>4} {'cov1':>7} {'gap':>4} {'h':>4} {'above':>6} {'full':>5} {'isl':>5} {'openML':>6}")
    bond = [r for r in results if r["group"] == "bonds"]
    buckets = defaultdict(list)
    for r in bond:
        buckets[(r["aabs"], r["asbs"], r["n"])].append(r)
    for k in sorted(buckets):
        rs = buckets[k]
        m = [x["metrics"] for x in rs]
        emit(
            f"{k[0]:4d} {k[1]:4d} {k[2]:4d} {fmt_pct(mean(x['firstLayerCoverage'] for x in m))} "
            f"{mean(x['firstLayerMaxGap'] for x in m):4.1f} {mean(x['maxHeight'] for x in m):4.1f} "
            f"{mean(x['atomsAboveFirstLayer'] for x in m):6.1f} {mean(x['completeLayersFromAtoms'] for x in m):5.2f} "
            f"{mean(x['islands'] for x in m):5.2f} {mean(1 if x['multilayerWhileFirstOpen'] else 0 for x in m):6.2f}"
        )

    emit("\nSK  fraccion transformed y morfologia")
    emit(f"{'aa':>4} {'as':>4} {'T':>4} {'m%':>5} {'N':>4} {'SKfrac':>7} {'cov1':>7} {'h':>5} {'full':>5} {'above':>6}")
    sk = [r for r in results if r["group"] == "sk"]
    buckets = defaultdict(list)
    for r in sk:
        buckets[(r["aabs"], r["asbs"], r["tOverTm"], r["mismatchPercent"], r["n"])].append(r)
    for k in sorted(buckets):
        rs = buckets[k]
        m = [x["metrics"] for x in rs]
        skf = mean(1 if x["transformed"] else 0 for x in rs)
        if skf == 0 and k[3] == 0 and k[4] not in (31, 141):
            continue
        if skf == 0 and k[3] not in (0, 0.6, 1.0):
            continue
        emit(
            f"{k[0]:4d} {k[1]:4d} {k[2]:4.1f} {k[3]:5.1f} {k[4]:4d} {skf:7.2f} "
            f"{fmt_pct(mean(x['firstLayerCoverage'] for x in m))} {mean(x['maxHeight'] for x in m):5.2f} "
            f"{mean(x['completeLayersFromAtoms'] for x in m):5.2f} {mean(x['atomsAboveFirstLayer'] for x in m):6.1f}"
        )

    emit("\nTEMPERATURA m=0")
    emit(f"{'aa':>4} {'as':>4} {'T':>4} {'N':>4} {'cov1':>7} {'h':>5} {'full':>5} {'above':>6} {'gap':>5}")
    temp = [r for r in results if r["group"] == "temperature"]
    buckets = defaultdict(list)
    for r in temp:
        buckets[(r["aabs"], r["asbs"], r["tOverTm"], r["n"])].append(r)
    for k in sorted(buckets):
        rs = buckets[k]
        m = [x["metrics"] for x in rs]
        emit(
            f"{k[0]:4d} {k[1]:4d} {k[2]:4.1f} {k[3]:4d} {fmt_pct(mean(x['firstLayerCoverage'] for x in m))} "
            f"{mean(x['maxHeight'] for x in m):5.2f} {mean(x['completeLayersFromAtoms'] for x in m):5.2f} "
            f"{mean(x['atomsAboveFirstLayer'] for x in m):6.1f} {mean(x['firstLayerMaxGap'] for x in m):5.2f}"
        )

    emit("\nBASELINE")
    base = [r for r in results if r["group"] == "baseline"]
    buckets = defaultdict(list)
    for r in base:
        buckets[r["n"]].append(r)
    for n in sorted(buckets):
        rs = buckets[n]
        m = [x["metrics"] for x in rs]
        emit(
            f"  N={n:3d} cov1={fmt_pct(mean(x['firstLayerCoverage'] for x in m))} "
            f"h={mean(x['maxHeight'] for x in m):.2f} full={mean(x['completeLayersFromAtoms'] for x in m):.2f} "
            f"above={mean(x['atomsAboveFirstLayer'] for x in m):.1f} "
            f"openML={mean(1 if x['multilayerWhileFirstOpen'] else 0 for x in m):.2f} "
            f"isl={mean(x['islands'] for x in m):.2f} seeds={len(rs)}"
        )
        for r in sorted(rs, key=lambda z: z["seed"]):
            mm = r["metrics"]
            emit(
                f"    s{r['seed']} cov1={fmt_pct(mm['firstLayerCoverage'])} h={mm['maxHeight']} "
                f"gap={mm['firstLayerMaxGap']} layers={mm['layerCounts']} isl={mm['islands']}"
            )

    text = "\n".join(lines) + "\n"
    Path(out).write_text(text)
    print(text)


def site_xy(p, q, scale=1.0):
    # Misma red que updateatom: las filas pares se corren medio espaciado.
    shift = -0.5 * scale if q % 2 == 0 else 0.0
    x = ((p - 1) * scale) + shift
    y = -q * 0.866 * scale
    return x, y


def draw_lattice(ax, atoms, subtitle):
    ax.set_aspect("equal")
    ax.axis("off")
    seen = {}
    for p, q in atoms:
        seen.setdefault((p, q), 0)
        seen[(p, q)] += 1
    for q in (16, 15, 14):
        for p in range(0, 29):
            x, y = site_xy(p, q)
            ax.add_patch(Circle((x, y), 0.42, facecolor="#1c1c1c", edgecolor="#111", lw=0.3, zorder=1))
    for (p, q), n in seen.items():
        if not (0 <= p <= 28):
            continue
        x, y = site_xy(p, q)
        color = "#c0392b" if n == 1 else "#6c3483"
        ax.add_patch(Circle((x, y), 0.42, facecolor=color, edgecolor="#7b241c", lw=0.3, zorder=2))
    xs, ys = [], []
    for q in (16, 15, 14):
        for p in range(0, 29):
            x, y = site_xy(p, q)
            xs.append(x)
            ys.append(y)
    for p, q in atoms:
        x, y = site_xy(p, q)
        xs.append(x)
        ys.append(y)
    pad = 1.2
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(min(ys) - pad, max(ys) + pad)
    ax.set_title(subtitle, fontsize=9, pad=2)


def find_run(results, **spec):
    hits = []
    for r in results:
        ok = True
        for k, v in spec.items():
            if r.get(k) != v:
                ok = False
                break
        if ok:
            hits.append(r)
    if not hits:
        raise KeyError(spec)
    return hits


def panel(results, specs, path, suptitle, ncols):
    n = len(specs)
    nrows = (n + ncols - 1) // ncols
    fig_w = 4.4 * ncols
    fig_h = 3.3 * nrows + 0.6
    fig, axes = plt.subplots(nrows, ncols, figsize=(fig_w, fig_h), squeeze=False)
    for i, spec in enumerate(specs):
        ax = axes[i // ncols][i % ncols]
        title = spec.pop("_title")
        runs = find_run(results, **spec)
        r = runs[0]
        m = r["metrics"]
        sk = "sí" if r["transformed"] else "no"
        head = (
            f"{title}\n"
            f"N={r['n']}  T/Tm={r['tOverTm']}  aa={r['aabs']}  as={r['asbs']}  Δa={r['mismatchPercent']}%\n"
            f"cob. capa 1={100*m['firstLayerCoverage']:.0f}%  h={m['maxHeight']}  "
            f"capas llenas={m['completeLayersFromAtoms']}  SK={sk}  semilla={r['seed']}"
        )
        atoms = [tuple(a) for a in r["atoms"] if a]
        draw_lattice(ax, atoms, head)
    for j in range(n, nrows * ncols):
        axes[j // ncols][j % ncols].axis("off")
    fig.suptitle(suptitle, fontsize=13, y=1.0)
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path)


def S(title, **kw):
    item = dict(kw)
    item["_title"] = title
    return item


def make_figures(results):
    out = ROOT / "figuras"
    out.mkdir(exist_ok=True)
    panel(
        results,
        [
            S("Cobertura baja", group="baseline", n=21, seed=1),
            S("Corrida pedida", group="baseline", n=81, seed=1),
            S("Cobertura alta", group="baseline", n=141, seed=1),
        ],
        out / "a_base_dosis.png",
        "Base: 81 es el caso pedido. 21 y 141 usan los mismos enlaces, T/Tm = 0.5 y desajuste 0.",
        3,
    )
    panel(
        results,
        [S(f"Semilla {s}", group="baseline", n=81, seed=s) for s in (1, 2, 3, 4, 5)],
        out / "a_base_semillas.png",
        "Base repetida, N = 81. Misma física, distinto azar de llegada y de difusión.",
        5,
    )
    panel(
        results,
        [
            S("21 átomos", group="bonds", aabs=40, asbs=60, n=21, seed=2),
            S("81 átomos", group="bonds", aabs=40, asbs=60, n=81, seed=2),
            S("141 átomos", group="bonds", aabs=40, asbs=60, n=141, seed=2),
        ],
        out / "b_fm.png",
        "Candidato a Frank–van der Merwe. T/Tm = 0.5, enlaces 40 y 60, desajuste 0, semilla 2.",
        3,
    )
    panel(
        results,
        [S(f"Semilla {s}", group="bonds", aabs=40, asbs=60, n=141, seed=s) for s in (1, 2, 3)],
        out / "b_fm_semillas.png",
        "El mismo candidato de capa, N = 141, tres semillas.",
        3,
    )
    panel(
        results,
        [
            S("21 átomos", group="bonds", aabs=90, asbs=10, n=21, seed=1),
            S("81 átomos", group="bonds", aabs=90, asbs=10, n=81, seed=1),
            S("141 átomos", group="bonds", aabs=90, asbs=10, n=141, seed=1),
        ],
        out / "b_vw.png",
        "Candidato a Volmer–Weber. T/Tm = 0.5, enlaces 90 y 10, desajuste 0, semilla 1.",
        3,
    )
    panel(
        results,
        [S(f"Semilla {s}", group="bonds", aabs=90, asbs=10, n=81, seed=s) for s in (1, 2, 3)],
        out / "b_vw_semillas.png",
        "Volmer–Weber repetido, N = 81, tres semillas.",
        3,
    )
    panel(
        results,
        [
            S("0 %, 31 átomos", group="sk", aabs=50, asbs=50, tOverTm=0.5, mismatchPercent=0, n=31, seed=1),
            S("0 %, 61 átomos", group="sk", aabs=50, asbs=50, tOverTm=0.5, mismatchPercent=0, n=61, seed=1),
            S("0 %, 141 átomos", group="sk", aabs=50, asbs=50, tOverTm=0.5, mismatchPercent=0, n=141, seed=1),
            S("1 %, 31 átomos", group="sk", aabs=50, asbs=50, tOverTm=0.5, mismatchPercent=1.0, n=31, seed=1),
            S("1 %, 61 átomos", group="sk", aabs=50, asbs=50, tOverTm=0.5, mismatchPercent=1.0, n=61, seed=1),
            S("1 %, 141 átomos", group="sk", aabs=50, asbs=50, tOverTm=0.5, mismatchPercent=1.0, n=141, seed=1),
        ],
        out / "c_sk.png",
        "Mismo enlace 50/50 y T/Tm = 0.5, semilla 1. Arriba sin desajuste; abajo con 1 %.",
        3,
    )
    panel(
        results,
        [
            S("T/Tm = 0.2", group="temperature", aabs=50, asbs=50, tOverTm=0.2, n=141, seed=1),
            S("T/Tm = 0.5", group="temperature", aabs=50, asbs=50, tOverTm=0.5, n=141, seed=1),
            S("T/Tm = 0.8", group="temperature", aabs=50, asbs=50, tOverTm=0.8, n=141, seed=1),
        ],
        out / "d_temperatura.png",
        "Temperatura, con enlaces 50/50, desajuste 0, N = 141 y semilla 1 fijos.",
        3,
    )
    panel(
        results,
        [
            S("T/Tm = 0.2", group="temperature", aabs=50, asbs=50, tOverTm=0.2, n=141, seed=3),
            S("T/Tm = 0.5", group="temperature", aabs=50, asbs=50, tOverTm=0.5, n=141, seed=3),
            S("T/Tm = 0.8", group="temperature", aabs=50, asbs=50, tOverTm=0.8, n=141, seed=3),
        ],
        out / "d_temperatura_s3.png",
        "Las mismas condiciones que la figura anterior, semilla 3.",
        3,
    )


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    src = Path(args[0] if args else ROOT / "resultados.json")
    results = load(src)
    if "--fig" in sys.argv:
        make_figures(results)
    else:
        summarize(results, ROOT / "resumen.txt")


if __name__ == "__main__":
    main()
