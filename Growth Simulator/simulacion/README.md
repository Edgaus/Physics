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
