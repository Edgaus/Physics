# Simulación de crecimiento epitaxial

Copia local de la página de DoITPoMS:

https://www.doitpoms.ac.uk/tlplib/epitaxial-growth/HTML5/epitaxial_growth.html

El recurso es de DoITPoMS, bajo Creative Commons Attribution-NonCommercial-ShareAlike 4.0. La licencia está en la propia página.

El script de la simulación va dentro de `tlplib/epitaxial-growth/HTML5/epitaxial_growth.html`. La única diferencia con la página publicada es que GSAP 3.9.1 está en `gsap.min.js`, al lado del HTML, para que abra sin la red.

## Correrla

Desde esta carpeta:

```bash
python3 -m http.server 8741
```

Abre http://127.0.0.1:8741/tlplib/epitaxial-growth/HTML5/epitaxial_growth.html

`epitaxial_growth_corregido.html` es la misma página con los dos fallos de la transición corregidos: la lista se llama `blacklistArray`, igual que donde se declara, y el enlace adátomo–adátomo sí se duplica (`aabs = initaabs * 2`). Al pulsar Restart esa transición vuelve a empezar en falso. El resto del script no cambia.

Pulsa el botón de inicio, ajusta los controles y pulsa Go. No muevas las barras mientras corre: el temporizador es de 1 ms y la página se traba. Si se queda pegada, recarga.

Abrir el HTML directo con el navegador (`file://`) no resuelve las imágenes, porque el HTML las pide en `../../../images/`. Hace falta servir esta carpeta.

## Capturas automáticas

`capturar_crecimientos.py` sirve esta carpeta, abre la página en Chrome sin ventana, mueve las barras, pulsa Go y guarda una captura cuando cae el último átomo. Cada corrida es una página recién cargada, así que Restart no arrastra estado entre corridas.

```bash
pip install playwright
python3 capturar_crecimientos.py --atomos 81 --temperatura 0.5 --enlace-aa 50 --enlace-as 25 --desajuste 0 --corridas 3
```

Los valores tienen que caer en el paso de cada barra (átomos 1, 11, …, 151; temperatura 0.2–0.8 de 0.1 en 0.1; adátomo–adátomo de 10 en 10; desajuste 0–1 % de 0.1 en 0.1). Si no, el script se detiene en vez de redondear.

Guarda en `resultados/<parámetros>/` las capturas `corrida_N.png`, `parametros.png` (el panel antes de Go) y `resumen.json`. Por corrida, `resumen.json` trae los adátomos por capa, cuántos quedaron dibujados fuera del recuadro (columna 0, o empujados más allá del guarda derecho) y cuántos sitios fantasma dejó el script: celdas marcadas como ocupadas sin átomo, que hacen que otros átomos se vean flotando.
