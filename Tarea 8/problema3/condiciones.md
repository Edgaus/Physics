# Condiciones del problema 3

Tabla para repetir las corridas. El cálculo usa el script de la página, no una reimplementación:

`Growth Simulator/simulacion/tlplib/epitaxial-growth/HTML5/epitaxial_growth.html`

Desde `Tarea 8/problema3`:

```js
const { runOnce } = require("./run_epitaxy.js");
runOnce({ n, tSlider, aabs, asbs, mismatchSlider, seed });
```

Hay que llamar `runOnce` de ese archivo. La semilla entra en el `mulberry32` de ahí; otro generador no reproduce `resultados.json`. Cada llamada recarga el script. El botón Restart de la página no borra `transformed` ni `strain`.

| Argumento | Control de la página | Conversión |
| --- | --- | --- |
| `n` | Number of atoms | Valor del slider. Válidos usados: 21, 31, 61, 81, 91, 121, 141. No usar 151: el HTML solo crea `a1`…`a149` y el depósito 150 truena. |
| `tSlider` | Temperature | 20, 30, 50, 70, 80. `T/Tm = round(tSlider * 100) / 10000`, o sea 0.2, 0.3, 0.5, 0.7, 0.8. |
| `aabs` | Adatom-adatom bond strength | Entero 0–100, unidades arbitrarias de la página. |
| `asbs` | Adatom-substrate bond strength | Entero 0–100, mismas unidades. |
| `mismatchSlider` | Lattice parameter difference | 0, 30, 60, 90, 100. La caja muestra `mismatchSlider / 100` seguido de `%`. `strain` interno es ese cociente. |
| `seed` | No está en la página | Entero. 1 es la semilla de las figuras principales. |

`resultados.json` guarda cada corrida con `group`, `n`, `tSlider`, `tOverTm`, `aabs`, `asbs`, `mismatchSlider`, `mismatchPercent` y `seed`.

## Corridas que sostienen el informe

Estas filas reconstruyen las figuras y las etiquetas. `grupo` es el campo `group` del JSON.

| inciso | grupo | para qué | n | tSlider | T/Tm | aabs | asbs | mismatchSlider | desajuste | semillas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a | baseline | Figura `a_base_dosis.png` y morfología pedida. La del enunciado es n = 81. | 21, 81, 141 | 50 | 0.5 | 50 | 25 | 0 | 0 % | 1 |
| a | baseline | Figura `a_base_semillas.png`. Reproducibilidad a la dosis pedida. | 81 | 50 | 0.5 | 50 | 25 | 0 | 0 % | 1, 2, 3, 4, 5 |
| a | baseline | Dosis extra, calculada y no dibujada. | 31 | 50 | 0.5 | 50 | 25 | 0 | 0 % | 1, 2, 3, 4, 5 |
| b | bonds | Figura `b_fm.png`. Candidato Frank–van der Merwe, etiqueta tentativo. | 21, 81, 141 | 50 | 0.5 | 40 | 60 | 0 | 0 % | 2 |
| b | bonds | Figura `b_fm_semillas.png`. La semilla 1 no repite la película plana. | 141 | 50 | 0.5 | 40 | 60 | 0 | 0 % | 1, 2, 3 |
| b | bonds | Figura `b_vw.png`. Candidato Volmer–Weber, etiqueta apoyado. | 21, 81, 141 | 50 | 0.5 | 90 | 10 | 0 | 0 % | 1 |
| b | bonds | Figura `b_vw_semillas.png`. | 81 | 50 | 0.5 | 90 | 10 | 0 | 0 % | 1, 2, 3 |
| b | bonds | Contraste citado: sustrato muy fuerte, columnas altas. | 141 | 50 | 0.5 | 0 | 100 | 0 | 0 % | 1, 2, 3 |
| b | bonds | Contraste citado: sustrato muy fuerte, columnas altas. | 141 | 50 | 0.5 | 20 | 80 | 0 | 0 % | 1, 2, 3 |
| b | bonds | Contraste citado: sustrato solo un poco mayor que el adátomo. | 141 | 50 | 0.5 | 30 | 40 | 0 | 0 % | 1, 2, 3 |
| b | bonds | Mismo modo de islas en otros pares. | 141 | 50 | 0.5 | 80 | 10 | 0 | 0 % | 1, 2, 3 |
| b | bonds | Mismo modo de islas en otros pares. | 141 | 50 | 0.5 | 70 | 20 | 0 | 0 % | 1, 2, 3 |
| b | bonds | Mismo modo de islas en otros pares. | 141 | 50 | 0.5 | 100 | 0 | 0 | 0 % | 1, 2, 3 |
| c | sk | Figura `c_sk.png`, fila sin desajuste. También el mojado inicial. | 31, 61, 141 | 50 | 0.5 | 50 | 50 | 0 | 0 % | 1 |
| c | sk | Figura `c_sk.png`, fila con desajuste. A n = 61 la etiqueta es apoyado. | 31, 61, 141 | 50 | 0.5 | 50 | 50 | 100 | 1 % | 1 |
| c | sk | Reproducibilidad del caso anterior. Las tres semillas coinciden en n = 61. | 61, 141 | 50 | 0.5 | 50 | 50 | 0 | 0 % | 1, 2, 3 |
| c | sk | Reproducibilidad del caso anterior. Las tres semillas coinciden en n = 61. | 61, 141 | 50 | 0.5 | 50 | 50 | 100 | 1 % | 1, 2, 3 |
| c | sk | Desajuste 0.6 %: a n = 61 el interruptor no dispara. Etiqueta no reproducido en esa dosis. | 61 | 50 | 0.5 | 50 | 50 | 60 | 0.6 % | 1, 2, 3 |
| d | temperature | Figura `d_temperatura.png`. Enlaces fijos, cambia solo la temperatura. | 141 | 20 | 0.2 | 50 | 50 | 0 | 0 % | 1 |
| d | temperature | Figura `d_temperatura.png`. | 141 | 50 | 0.5 | 50 | 50 | 0 | 0 % | 1 |
| d | temperature | Figura `d_temperatura.png`. | 141 | 80 | 0.8 | 50 | 50 | 0 | 0 % | 1 |
| d | temperature | Figura `d_temperatura_s3.png`. A 0.8 Tm la cobertura cae a 72 %. | 141 | 20, 50, 80 | 0.2, 0.5, 0.8 | 50 | 50 | 0 | 0 % | 3 |
| e | baseline | Repetición de (a). | 81 | 50 | 0.5 | 50 | 25 | 0 | 0 % | 1, 2, 3, 4, 5 |
| e | bonds | Repetición de Volmer–Weber. | 21, 81, 141 | 50 | 0.5 | 90 | 10 | 0 | 0 % | 1, 2, 3 |
| e | bonds | Repetición de Frank–van der Merwe a dosis alta. | 141 | 50 | 0.5 | 40 | 60 | 0 | 0 % | 1, 2, 3 |
| e | sk | Repetición de Stranski–Krastanov a 1 %. | 61, 141 | 50 | 0.5 | 50 | 50 | 100 | 1 % | 1, 2, 3 |
| e | sk | Repetición del control sin desajuste. | 61, 141 | 50 | 0.5 | 50 | 50 | 0 | 0 % | 1, 2, 3 |
| e | sk | Repetición que no dispara a 0.6 %. | 61 | 50 | 0.5 | 50 | 50 | 60 | 0.6 % | 1, 2, 3 |
| e | temperature | El modo de islas se mantiene al cambiar T. | 21, 81, 141 | 20, 30, 50, 70, 80 | 0.2, 0.3, 0.5, 0.7, 0.8 | 90 | 10 | 0 | 0 % | 1, 2, 3 |

El inciso (e) no tiene controles nuevos: vuelve a correr filas de (a), (b), (c) y (d).

## Barrido con el que se eligieron esos pares

Producto cartesiano. `run_epitaxy.js` lo arma en `sweep()`.

| inciso | grupo | n | tSlider | T/Tm | pares aabs, asbs | mismatchSlider | desajuste | semillas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a | baseline | 21, 31, 81, 141 | 50 | 0.5 | 50, 25 | 0 | 0 % | 1, 2, 3, 4, 5 |
| b | bonds | 21, 81, 141 | 50 | 0.5 | 0,100; 10,90; 20,80; 30,70; 30,40; 40,60; 50,50; 50,25; 50,10; 60,30; 70,20; 80,10; 90,10; 100,20; 100,0; 40,40; 20,50; 60,90 | 0 | 0 % | 1, 2, 3 |
| c | sk | 31, 61, 91, 121, 141 | 50 y 80 | 0.5 y 0.8 | 20,80; 30,70; 40,60; 50,50; 30,40; 60,90 | 0, 30, 60, 90, 100 | 0, 0.3, 0.6, 0.9, 1 % | 1, 2, 3 |
| d | temperature | 21, 81, 141 | 20, 30, 50, 70, 80 | 0.2, 0.3, 0.5, 0.7, 0.8 | 20,80; 50,25; 90,10; 50,50 | 0 | 0 % | 1, 2, 3 |

En el barrido (c), el desajuste 0.3 % deja el crítico en 3 capas, 0.6 % en 2, y 0.9 % o 1 % en 1. Por debajo de 0.3 % el crítico queda en 20 y la transición no puede disparar con estos `n`.

## Lista para copiar

Misma información que la primera tabla, una corrida por objeto. Donde la tabla agrupa varios `n` o varias semillas, aquí van sueltos solo los de las figuras. El resto sale del producto de esa tabla.

```json
[
  {"inciso": "a", "n": 21, "tSlider": 50, "aabs": 50, "asbs": 25, "mismatchSlider": 0, "seed": 1},
  {"inciso": "a", "n": 81, "tSlider": 50, "aabs": 50, "asbs": 25, "mismatchSlider": 0, "seed": 1},
  {"inciso": "a", "n": 141, "tSlider": 50, "aabs": 50, "asbs": 25, "mismatchSlider": 0, "seed": 1},
  {"inciso": "a", "n": 81, "tSlider": 50, "aabs": 50, "asbs": 25, "mismatchSlider": 0, "seed": 2},
  {"inciso": "a", "n": 81, "tSlider": 50, "aabs": 50, "asbs": 25, "mismatchSlider": 0, "seed": 3},
  {"inciso": "a", "n": 81, "tSlider": 50, "aabs": 50, "asbs": 25, "mismatchSlider": 0, "seed": 4},
  {"inciso": "a", "n": 81, "tSlider": 50, "aabs": 50, "asbs": 25, "mismatchSlider": 0, "seed": 5},
  {"inciso": "b", "n": 21, "tSlider": 50, "aabs": 40, "asbs": 60, "mismatchSlider": 0, "seed": 2},
  {"inciso": "b", "n": 81, "tSlider": 50, "aabs": 40, "asbs": 60, "mismatchSlider": 0, "seed": 2},
  {"inciso": "b", "n": 141, "tSlider": 50, "aabs": 40, "asbs": 60, "mismatchSlider": 0, "seed": 2},
  {"inciso": "b", "n": 141, "tSlider": 50, "aabs": 40, "asbs": 60, "mismatchSlider": 0, "seed": 1},
  {"inciso": "b", "n": 141, "tSlider": 50, "aabs": 40, "asbs": 60, "mismatchSlider": 0, "seed": 3},
  {"inciso": "b", "n": 21, "tSlider": 50, "aabs": 90, "asbs": 10, "mismatchSlider": 0, "seed": 1},
  {"inciso": "b", "n": 81, "tSlider": 50, "aabs": 90, "asbs": 10, "mismatchSlider": 0, "seed": 1},
  {"inciso": "b", "n": 141, "tSlider": 50, "aabs": 90, "asbs": 10, "mismatchSlider": 0, "seed": 1},
  {"inciso": "b", "n": 81, "tSlider": 50, "aabs": 90, "asbs": 10, "mismatchSlider": 0, "seed": 2},
  {"inciso": "b", "n": 81, "tSlider": 50, "aabs": 90, "asbs": 10, "mismatchSlider": 0, "seed": 3},
  {"inciso": "c", "n": 31, "tSlider": 50, "aabs": 50, "asbs": 50, "mismatchSlider": 0, "seed": 1},
  {"inciso": "c", "n": 61, "tSlider": 50, "aabs": 50, "asbs": 50, "mismatchSlider": 0, "seed": 1},
  {"inciso": "c", "n": 141, "tSlider": 50, "aabs": 50, "asbs": 50, "mismatchSlider": 0, "seed": 1},
  {"inciso": "c", "n": 31, "tSlider": 50, "aabs": 50, "asbs": 50, "mismatchSlider": 100, "seed": 1},
  {"inciso": "c", "n": 61, "tSlider": 50, "aabs": 50, "asbs": 50, "mismatchSlider": 100, "seed": 1},
  {"inciso": "c", "n": 141, "tSlider": 50, "aabs": 50, "asbs": 50, "mismatchSlider": 100, "seed": 1},
  {"inciso": "c", "n": 61, "tSlider": 50, "aabs": 50, "asbs": 50, "mismatchSlider": 60, "seed": 1},
  {"inciso": "d", "n": 141, "tSlider": 20, "aabs": 50, "asbs": 50, "mismatchSlider": 0, "seed": 1},
  {"inciso": "d", "n": 141, "tSlider": 50, "aabs": 50, "asbs": 50, "mismatchSlider": 0, "seed": 1},
  {"inciso": "d", "n": 141, "tSlider": 80, "aabs": 50, "asbs": 50, "mismatchSlider": 0, "seed": 1},
  {"inciso": "d", "n": 141, "tSlider": 20, "aabs": 50, "asbs": 50, "mismatchSlider": 0, "seed": 3},
  {"inciso": "d", "n": 141, "tSlider": 50, "aabs": 50, "asbs": 50, "mismatchSlider": 0, "seed": 3},
  {"inciso": "d", "n": 141, "tSlider": 80, "aabs": 50, "asbs": 50, "mismatchSlider": 0, "seed": 3}
]
```
