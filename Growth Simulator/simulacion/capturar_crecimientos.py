#!/usr/bin/env python3
"""Corre la simulación de crecimiento epitaxial en Chrome y guarda una captura de cada resultado final.

Ejemplo:
    python3 capturar_crecimientos.py --atomos 81 --temperatura 0.5 --enlace-aa 50 --enlace-as 25 --desajuste 0 --corridas 3
"""

import argparse
import functools
import http.server
import json
import threading
import time
from collections import Counter
from pathlib import Path

from playwright.sync_api import sync_playwright

SIMULACION = Path(__file__).resolve().parent
PAGINA = "tlplib/epitaxial-growth/HTML5/epitaxial_growth.html"
# El HTML pide GSAP al CDN; se le sirve la copia local, que es el mismo archivo, para no depender de la red.
GSAP_CDN = "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.9.1/gsap.min.js"
GSAP_LOCAL = SIMULACION / "tlplib/epitaxial-growth/HTML5/gsap.min.js"

# La página sólo lee los parámetros cuando se mueve cada barra (oninput), no de las cajas de texto.
FIJAR_BARRA = """([id, valor]) => {
    const barra = document.getElementById(id);
    barra.value = String(valor);
    barra.dispatchEvent(new Event('input', {bubbles: true}));
    barra.dispatchEvent(new Event('change', {bubbles: true}));
    return {valor: Number(barra.value), min: barra.min, max: barra.max, step: barra.step};
}"""

LEER_PARAMETROS = """() => ({
    atomos: Number(scr),
    temperatura: Number(celcius),
    enlace_aa: Number(aabs),
    enlace_as: Number(asbs),
    desajuste: Number(strain),
})"""

LEER_ESTADO = """() => ({
    depositados: Number(aindex),
    total: Number(atombucket),
    pausado: blossomtimer.paused(),
})"""

# Fantasmas: celdas que `filled` marca como adátomo (2) sin que haya ninguno ahí. El script original
# los deja al mover un átomo "bloqueado" sin vaciar su celda, y sirven de apoyo invisible a otros.
# Fuera de vista: adátomos dibujados fuera del SVG de 550 px (columna 0, o más allá del guarda en 29).
LEER_FINAL = """() => {
    const ancho = document.getElementById('svg2').width.baseVal.value;
    const adatomos = [];
    const ocupadas = new Set();
    let fueraDeVista = 0;
    for (let i = 1; i <= atombucket; i++) {
        const a = document.getElementById(aatom[i]);
        adatomos.push([Number(a.p), Number(a.q)]);
        ocupadas.add(Number(a.p) + ',' + Number(a.q));
        const cx = Number(a.getAttribute('cx'));
        const r = Number(a.getAttribute('r'));
        if (cx + r <= 0 || cx - r >= ancho) fueraDeVista++;
    }
    let fantasmas = 0;
    for (let p = -4; p <= 35; p++) {
        for (let q = 0; q <= 13; q++) {
            if (filled[p][q] == 2 && !ocupadas.has(p + ',' + q)) fantasmas++;
        }
    }
    return {adatomos, fantasmas, fueraDeVista, transformed: Boolean(transformed)};
}"""


class Manejador(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def servir(carpeta):
    manejador = functools.partial(Manejador, directory=str(carpeta))
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), manejador)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    return servidor


def barras(args):
    return {
        "go_sb": args.atomos,
        "temp_sb": round(args.temperatura * 100),
        "aabs_sb": args.enlace_aa,
        "asbs_sb": args.enlace_as,
        "sizedifference_sb": round(args.desajuste * 100),
    }


def configurar(pagina, args):
    pagina.click("#start")
    for id_barra, valor in barras(args).items():
        barra = pagina.evaluate(FIJAR_BARRA, [id_barra, valor])
        if barra["valor"] != valor:
            raise SystemExit(
                f"{id_barra} no puede tomar {valor} (min={barra['min']}, max={barra['max']}, step={barra['step']})"
            )

    leidos = pagina.evaluate(LEER_PARAMETROS)
    pedidos = {
        "atomos": args.atomos,
        "temperatura": args.temperatura,
        "enlace_aa": args.enlace_aa,
        "enlace_as": args.enlace_as,
        "desajuste": args.desajuste,
    }
    for nombre, pedido in pedidos.items():
        if abs(leidos[nombre] - pedido) > 1e-9:
            raise SystemExit(f"La página leyó {nombre}={leidos[nombre]}, se pidió {pedido}")
    return leidos


def esperar_fin(pagina, errores, limite_s, sin_avance_s):
    inicio = time.monotonic()
    ultimo_avance = inicio
    depositados = 0
    while True:
        if errores:
            raise RuntimeError(f"Error de JavaScript en la simulación: {errores[0]}")
        estado = pagina.evaluate(LEER_ESTADO)
        ahora = time.monotonic()
        if estado["depositados"] != depositados:
            depositados = estado["depositados"]
            ultimo_avance = ahora
        if estado["depositados"] >= estado["total"] and estado["pausado"]:
            return ahora - inicio
        if ahora - inicio > limite_s:
            raise TimeoutError(f"No terminó en {limite_s} s ({depositados}/{estado['total']} átomos)")
        if ahora - ultimo_avance > sin_avance_s:
            raise TimeoutError(f"Se quedó pegada en {depositados}/{estado['total']} átomos")
        time.sleep(0.5)


def por_capa(adatomos):
    # El substrato ocupa q = 14..16, así que la capa 1 sobre él es q = 13.
    conteo = Counter(14 - q for _, q in adatomos)
    return {str(capa): conteo[capa] for capa in sorted(conteo)}


def nombre_carpeta(args):
    return (
        f"N{args.atomos}_T{args.temperatura:g}_aa{args.enlace_aa:g}"
        f"_as{args.enlace_as:g}_desajuste{args.desajuste:g}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--atomos", type=int, required=True, help="1 a 151, de 10 en 10 desde 1")
    parser.add_argument("--temperatura", type=float, required=True, help="0.2 a 0.8 Tm, de 0.1 en 0.1")
    parser.add_argument("--enlace-aa", type=int, required=True, help="adátomo–adátomo, 0 a 100 de 10 en 10")
    parser.add_argument("--enlace-as", type=int, required=True, help="adátomo–substrato, 0 a 100")
    parser.add_argument("--desajuste", type=float, default=0, help="diferencia de parámetro de red en %%, 0 a 1")
    parser.add_argument("--corridas", type=int, default=3)
    parser.add_argument("--salida", type=Path, default=SIMULACION / "resultados")
    parser.add_argument("--limite", type=float, default=900, help="segundos máximos por corrida")
    parser.add_argument("--chrome", help="ruta a un Chrome/Chromium; por defecto, el Chrome instalado")
    args = parser.parse_args()

    carpeta = args.salida / nombre_carpeta(args)
    carpeta.mkdir(parents=True, exist_ok=True)
    servidor = servir(SIMULACION)
    url = f"http://127.0.0.1:{servidor.server_address[1]}/{PAGINA}"
    resumen = {"pagina": PAGINA, "corridas": []}

    with sync_playwright() as pw:
        if args.chrome:
            navegador = pw.chromium.launch(executable_path=args.chrome, headless=True)
        else:
            navegador = pw.chromium.launch(channel="chrome", headless=True)
        for corrida in range(1, args.corridas + 1):
            contexto = navegador.new_context(viewport={"width": 800, "height": 600}, device_scale_factor=2)
            contexto.route(GSAP_CDN, lambda ruta: ruta.fulfill(path=GSAP_LOCAL, content_type="application/javascript"))
            pagina = contexto.new_page()
            errores = []
            pagina.on("pageerror", lambda e: errores.append(str(e)))
            pagina.goto(url)

            resumen["parametros"] = configurar(pagina, args)
            if corrida == 1:
                pagina.locator("#kanvas").screenshot(path=carpeta / "parametros.png")

            pagina.click("#go_btn")
            duracion = esperar_fin(pagina, errores, args.limite, sin_avance_s=60)

            captura = carpeta / f"corrida_{corrida}.png"
            pagina.locator("#kanvas").screenshot(path=captura)
            final = pagina.evaluate(LEER_FINAL)
            capas = por_capa(final["adatomos"])
            resumen["corridas"].append({
                "captura": captura.name,
                "segundos": round(duracion, 1),
                "adatomos_por_capa": capas,
                "adatomos_fuera_de_vista": final["fueraDeVista"],
                "sitios_fantasma": final["fantasmas"],
                "transicion_sk": final["transformed"],
            })
            print(
                f"corrida {corrida}: {captura} ({duracion:.1f} s), por capa {capas}, "
                f"{final['fueraDeVista']} fuera de vista, {final['fantasmas']} sitios fantasma"
            )
            contexto.close()
        navegador.close()

    servidor.shutdown()
    (carpeta / "resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
