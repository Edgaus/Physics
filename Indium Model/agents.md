Documento de handoff para un **chat nuevo de Cursor**. Léelo entero antes de escribir código o texto. No dependas del chat anterior (se acabaron los tokens).

**Usuario:** Edgar, CINVESTAV. Software engineer + crecimiento/caracterización de nitruros.

**Idioma:** español con el usuario; código y nombres de archivo en inglés.

---

## Qué es este proyecto

Pozos cuánticos de **InGaN cúbico (zincblenda, [001])**, no wurtzita.

Objetivo científico: **modelo en Python de la incorporación de In** en los pozos, contrastado con datos experimentales (Origin) y un manuscrito (Word).

No reinventar mecanismos ya publicados. La novedad viable es:

1. Parametrizar Muraki + pulling + desorción **en cúbico** (R vs T, In efectivo vs nominal).
2. Añadir un término de **enriquecimiento de In junto a stacking faults {111}** (Cambridge lo midió; no lo modeló vs T/flujo/espesor).
3. Si los pozos van sobre **c-AlN**, pulling distinto vs c-GaN/3C-SiC (literatura casi toda sobre 3C-SiC).

**No vender como nuevo:** “el In se segrega”, “no hay polarización en [001]”, “las SFs concentran In”, ni el mecanismo metal-modulado ACS 2025.

---

Sistema: **zb-InGaN/GaN, crecimiento [001], **sin polarización/QCSE**.

Componentes:

1. **Muraki (1992):** capa flotante; \(x_n = x_0(1-R^n)\) en el pozo; cola exponencial en la barrera.
2. **Dehaese (1995):** R depende de T y tasa (cinética, no solo equilibrio).
3. **Composition pulling (Kawaguchi/Hiramatsu):** strain reduce la entrada de In; más mismatch (p. ej. sobre GaN) → más pulling.
4. **Desorción térmica de In.**
5. **Término de SFs (novedad):** enriquecimiento local ∝ densidad de fallas × x_In; explica Stokes ~300 meV (XRD/In medio vs PL).

Salidas del script: `x_In(z)`, In medio del pozo, cola en la barrera, comparación In nominal vs efectivo. CSV + figuras.

Constantes de partida (cúbico): a_GaN ≈ 4.50 Å, a_InN ≈ 4.98 Å; bowing PL c-InGaN b ≈ 2.4 eV (Zscherp 2023). Gap c-GaN ~3.2–3.3 eV, c-InN ~0.7 eV.


---

## Literatura (prioridad)

Leer en este orden. Lista completa en el chat previo; esto es el mínimo.

1. Binks, Dawson, Oliver, Wallis, *Appl. Phys. Rev.* **9**, 041309 (2022). DOI 10.1063/5.0097558 — review cúbico, OA.
2. Muraki *et al.*, *Appl. Phys. Lett.* **61**, 557 (1992). DOI 10.1063/1.107835
3. Dehaese, Wallart, Mollot, *Appl. Phys. Lett.* **66**, 52 (1995)
4. Kawaguchi, Shimizu, Hiramatsu, Sawaki, composition pulling, *MRS Internet J. Nitride Semicond. Res.* (1997)
5. Ding *et al.*, *J. Appl. Phys.* **128**, 145703 (2020) — In ×2.3 junto a SFs
6. *J. Phys. D* (2024) impact of SFs on zb InGaN SQW luminescence
7. Pacheco-Salazar *et al.*, *SST* **21**, 846 (2006) — Stokes ~300 meV, clusters
8. Zscherp *et al.*, *ACS AMI* **15**, 39513 (2023) — c-InGaN todo el rango, b = 2.4 eV
9. Zscherp *et al.*, *Cryst. Growth Des.* **25**, 3793 (2025). DOI 10.1021/acs.cgd.5c00202 — In se acumula y entra al crecer GaN. **Citar, no redescubrir.**
10. Karpov/Talalaev MOVPE rate equations (*pss a* 2002, *pss c* 2003) si es MOCVD
11. Chen/Feenstra/Northrup MBE In segregation (hex, mecanismo de superficie) si es MBE

---

## Estrategia de repo en Cursor

Workspace a usar (crear si no existe; **no** abrir todo OneDrive):

`C:\Users\edgau\OneDrive - CINVESTAV\Documentos\Indium InGaN incorporation`

Estructura objetivo:

```
c-InGaN-wells/
  README.md
  AGENTS.md              ← este archivo (copiar aquí)
  src/                   ← Python
  data/raw/              ← CSV de Origin / perfilometría
  data/processed/
  origin/                ← .opj (binario; no editar)
  drafts/
    manuscript.docx
    manuscript.md        ← esto sí lo edita el agente
  refs/reading-list.md
  .gitignore
  .cursor/rules/project.mdc
```

- Git: Cursor-hosted repo (no público). Pedir “guarda / crea el repo en Cursor” cuando haya esqueleto + CSV.
- `.gitignore`: `__pycache__/`, `.venv/`, `~$*.docx`, `*.opj.bak`, `Thumbs.db`
- **Origin (.opj):** archivo. El trabajo diario son CSV (File → Export → ASCII).
- **Word:** el agente edita `drafts/manuscript.md`; Edgar pega al `.docx`.
- No meter XML enormes ni AFM crudos. PDFs de papers: máximo 5–10, mejor DOI.



---

## Prompt mínimo para el chat nuevo

Pegar esto:

> Abre la carpeta del repo (o créala). Lee `AGENTS.md`. Pozos InGaN **cúbicos**. Arma el esqueleto del repo + Python del modelo Muraki/pulling/SF. 










# Condiciones de crecimiento de InGaN cúbico (Indium InGaN incorporation)— notas para otro agente

Cuatro muestras de pozos cuánticos cúbicos InGaN/GaN sobre 3C-SiC(001)/Si: **MME914**, **MME925**, **MME930** y **MME931**. Hay tres fuentes y no dicen lo mismo. No las mezcles.

| Fuente | Qué es | Qué no es |
|---|---|---|
| Borrador del artículo | Texto que el autor escribió después. Resume las condiciones de diseño. | No es la bitácora. |
| Planes PDF 913-914 (01/10/25) y 932 (19/11/25) | Receta prevista antes de crecer. | No es lo que quedó registrado en el crecimiento. El 932 no es ninguna de las cuatro muestras. |
| Fotos de la bitácora | Lo que se anotó durante el crecimiento. | No trae tiempos de obturador de In/Ga en los pozos, salvo el cambio de ciclo de Ga en 925. |

El Word `Condiciones_crecimiento_InGaN.docx` sale solo del borrador. La bitácora lo corrige en temperatura de barreras, presión de 914 y en el significado de las ternas 417/410/400 y 400/390/380.

## Muestras y técnica

- Técnica escrita en el artículo: *migration-enhanced epitaxy* bajo nitrógeno activo continuo. En las conclusiones el mismo proceso se llama *metal-modulated epitaxy*. En el laboratorio se abrevia MME.
- Estructura: tres pozos de InGaN y barreras de GaN. QW1 es el primero que se crece.
- Sustrato de los planes: 3C-SiC(001).
- El artículo dice que la presión de MBE se igualó a 4.2×10⁻⁶ Torr en los cuatro crecimientos y que la diferencia de diseño es la temperatura de los pozos.

## 1. Lo que dice el borrador del artículo

Título: *Growth-controlled carrier redistribution and negative thermal quenching in cubic InGaN/GaN quantum wells on 3C-SiC(001)/Si*.

Fragmento de crecimiento, citado en el Word:

> The structures were grown by migration-enhanced epitaxy under continuous active nitrogen. The three quantum wells were deposited with a common sequence but at different temperatures, whereas the GaN barriers were grown at 720 °C. MME914 represents the high-temperature limit, with well temperatures of 470–490 °C and short 2 s Ga-on/2 s Ga-off barrier cycles. MME925, MME930 and MME931 used 30 s Ga-on/30 s Ga-off barriers. Their well temperatures decreased progressively, reaching 427 °C in MME925, 417/410/400 °C in MME930 and 400/390/380 °C in MME931. The N2 flow (0.30 sccm in MME914, 0.26 sccm in MME925 and MME930, 0.28 sccm in MME931) was adjusted so that the MBE pressure was 4.2×10−6 Torr in every growth.

Tabla tal como quedó en el Word. El orden QW1/QW2/QW3 de 930 y 931 es una lectura del artículo (temperaturas en descenso y el pozo final es el más frío). El artículo no escribe “QW1 = 417 °C”. La bitácora no sostiene esa lectura: ver sección 4.

| Muestra | Temperatura de los pozos (°C) | Barreras de GaN (°C) | Ciclo Ga-on / Ga-off | Flujo de N₂ (sccm) | Presión MBE (Torr) |
|---|---|---|---|---|---|
| MME914 | 470–490 (intervalo; no hay un valor por pozo) | 720 | 2 s / 2 s | 0.30 | 4.2×10⁻⁶ |
| MME925 | 427 (un solo valor) | 720 | 30 s / 30 s | 0.26 | 4.2×10⁻⁶ |
| MME930 | 417 / 410 / 400 | 720 | 30 s / 30 s | 0.26 | 4.2×10⁻⁶ |
| MME931 | 400 / 390 / 380 | 720 | 30 s / 30 s | 0.28 | 4.2×10⁻⁶ |

El artículo añade, sin número: el pozo final combina la temperatura más baja de su receta con la mayor exposición de In respecto de Ga.

El artículo no da potencia de plasma, BEP de In o Ga, temperatura de celda, tiempos de obturador durante el pozo, ni razón In/Ga numérica. El intervalo 800–2000 nm y la función de trabajo de la plata (4.26–4.74 eV) son del modelo SCAPS de otro resumen y no pertenecen a estas muestras.

SIMS del artículo, In/N de cráter en orden de crecimiento (cota inferior de x, no consigna):

| Muestra | QW1 | QW2 | QW3 |
|---|---|---|---|
| MME914 | 8.6% | 8.6% | 12.6% |
| MME925 | 12.3% | 11.7% | 10.9% |
| MME930 | 15.6% | 18.3% | 25.4% |
| MME931 | 14.9% | 17.4% | 26.3% |

El Hamiltoniano usa otros In/N (promedio de capa, no el pico de cráter): 15.5% en el último pozo de 914; 13.7, 17.3 y 17.9% en 925; 16.3, 19.1 y 25.4% en 930; 16.4, 18.4 y 27.1% en 931. TEM: pozos de 925 ≈ 10–12 nm; pozos de 931 ≈ 16–20 nm; 930 sin ancho TEM.

## 2. Plan 913-914 del 01/10/25

Archivo: `Plan de Crecimiento 913-914 01-10-25 Copy.pdf`.

Objetivo escrito: pozos de InGaN por MME para ver la incorporación de indio según el tiempo de apertura de los obturadores.

Equipo: Mario Alberto Zambrano, Luis Vargas Hernández, Edgar Agustín Contreras, Marco Hinojosa.

Apila, de sustrato a superficie: 3C-SiC / buffer GaN 240 nm / barrera 1 40 nm / QW1 / barrera 2 40 nm / QW2 / barrera 3 40 nm / QW3 / barrera 4 40 nm.

Preparación y buffer, iguales en espíritu al plan 932:

- Sustrato 3C-SiC(001), desengrase 10 min en ultrasonido (xileno, acetona, isopropanol), BOE 30 s, portasustrato de tantalio de 3 pulgadas.
- Desorción 1 h hasta Tsus = 1050 °C ≈ Tpiro = 850 °C. Rampas de In y Ga en 40 min.
- Cinco toques de Ga de 1 s.
- Bajada a Tpiro ≈ 720 °C y 1 monocapa de Ga (4 s).
- Plasma: modo bajo al 6%, modo brillante al 4%, 150 W, flujo para PMBE = 4.6×10⁻⁶ Torr.
- Buffer a Tsus = 720 °C, 4 nm/min, 240 nm en 1 h. Se abre Ga y el nitrógeno 2 s después.

Celdas, también iguales en el plan 932:

| Momento | BEP Ga | T Ga | BEP In | T In |
|---|---|---|---|---|
| Durante la rampa / desorción | 2.93×10⁻⁷ Torr | 898 °C | 2.7×10⁻⁷ Torr | ≈ 565 °C |
| En los toques de Ga | 2.93×10⁻⁷ Torr | 898 °C | 2.79×10⁻⁷ Torr | ≈ 569 °C |
| En el buffer (solo Ga) | 2.93×10⁻⁷ Torr | 898 °C | no se reescribe | — |

Los flujos de In y Ga no son iguales entre sí. El Ga queda en 2.93×10⁻⁷ Torr. El In llega a 2.79×10⁻⁷ Torr. Ninguno cambia de pozo a pozo en la hoja. Durante los pozos el plan no vuelve a fijar el BEP.

Barreras del plan 913-914:

- Barreras 1 a 3: 40 nm, ≈ 16 min, a Tpiro = 450 °C. N abierto. Ga 2 s abierto, 2 s cerrado y 2 s solo con nitrógeno.
- Barrera 4: el mismo ciclo, y a los 5 min sube a Tsus = 720 °C en 10 min.

Pozos del plan. N abierto. 40 pulsos. El In esperado es meta del plan, no SIMS.

| Pozo | Ga abierto | Pausa solo N | In abierto | Pausa | In esperado | Tiempo escrito |
|---|---|---|---|---|---|---|
| QW1 | 2 s | 2 s | 1 s | 2 s | 11% | 4 min 38 s |
| QW2 | 2 s | 2 s | 2 s | 2 s | 17% | 3 min 54 s |
| QW3 | 1 s | 2 s | 2 s | 2 s | 22% | 4 min |

QW3 es el de mayor tiempo de In respecto de Ga. El tiempo de QW1 coincide con 40 ciclos de 7 s si no se cuenta la pausa final. El de QW2 (3 min 54 s) no coincide con 40 ciclos de 8 s.

Diferencias ya visibles entre este plan y el artículo para MME914: el plan pone las primeras barreras a Tpiro = 450 °C y PMBE = 4.6×10⁻⁶ Torr. El artículo pone pozos a 470–490 °C, barreras a 720 °C y 4.2×10⁻⁶ Torr. El In de 11/17/22% no es el SIMS 8.6/8.6/12.6%.

## 3. Plan 932 del 19/11/25

Archivo: `Plan de Crecimiento 932 19_11_25 Copy.pdf`.

No es MME914, 925, 930 ni 931. Es un crecimiento posterior.

Objetivo: subir la incorporación de In (15% hasta entonces) cambiando la potencia de plasma de un pozo al siguiente.

Equipo: Mario Alberto Zambrano, Luis Vargas Hernández, Marco Hinojosa.

Apila: 3C-SiC(001) / buffer 240 nm / barrera 1 de 5 nm / QW1 10 nm / barrera 2 de 30 nm / QW2 10 nm / barrera 3 de 30 nm / QW3 10 nm / barrera 4 de 30 nm.

Igual que 913-914 en sustrato, desorción, toques de Ga, 1 ML, buffer y BEP de In y Ga. Distinto en plasma y en la región activa:

- Ignición todavía a 150 W, pero PMBE prevista = 3×10⁻⁶ Torr.
- Primera barrera a Tpiro = 430 °C, bajada de 5 min con obturadores cerrados. Espesor 5 nm. Ga 7 s abierto y pausa de 10 s, 5 ciclos, ≈ 1 min 15 s.
- Barreras 2 a 4: 30 nm, 26 ciclos, 7 min 30 s. No hay rampa a 720 °C en la cuarta barrera.
- Pozos: la misma secuencia en los tres. Ga 2 s, pausa 2 s, In 2 s, pausa 2 s, 20 pulsos, 10 nm, 2 min 36 s.
- Potencia en el pozo: QW1 170 W, QW2 190 W, QW3 210 W.

## 4. Bitácora (fotos de libreta) frente a la tabla del artículo

Las fotos cubren 914 (páginas 129–131), 925 (164 en blanco, con título; el registro está en 166–167 y puede seguir en hojas que no se enviaron), 930 (179–181) y 931 (183–184). La página 164 solo dice “Crecimiento 925”.

En los cuatro crecimientos el plasma se calibra a 120 W y después se fija en 150 W. El flujo está en por ciento, no en sccm. Los puntos de trabajo anotados son 3% (914), 2.6% (925 y 930) y 2.5% (931).

| Muestra | Tabla del artículo | Bitácora |
|---|---|---|
| MME914 | Pozos 470–490 °C. Barreras a 720 °C. Ciclo 2 s/2 s. N₂ 0.30 sccm. 4.2×10⁻⁶ Torr. | Bajada a Tsus = 500 °C para tener Tpiro = 470 °C. En la barrera: Tpiro = 489 °C, Tsus = 500 °C, PMBE = 9.7×10⁻⁶ Torr. Plasma dejado en 3% y 4.6×10⁻⁶ Torr a 120 W, luego 150 W. Estas páginas no escriben el ciclo de 2 s. |
| MME925 | Pozos a 427 °C. Barreras a 720 °C. Ciclo 30 s/30 s. N₂ 0.26 sccm. 4.2×10⁻⁶ Torr. | Pozos y barreras a Tsus = 450 °C y Tpir = 427 °C. El 4.2×10⁻⁶ Torr sí está, con flujo 2.6% a 120 W y luego 150 W. El Ga empezó en 2 s abierto / 2 s cerrado y, marcado “Cambio”, pasó a 30 s / 30 s. |
| MME930 | Pozos 417 / 410 / 400 °C. Barreras a 720 °C. Ciclo 30 s/30 s. N₂ 0.26 sccm. 4.2×10⁻⁶ Torr. | Una sola consigna al bajar del buffer: Tsus = 410 °C, esperando 400 ≤ Tpiro ≤ 430 °C, y se midió Tpiro = 417 °C. Flujo 2.6%, con 4.7×10⁻⁶ y 4.1×10⁻⁶ Torr en el recuadro, 120 W y luego 150 W. No hay ciclo de 30 s ni una temperatura por pozo. |
| MME931 | Pozos 400 / 390 / 380 °C. Barreras a 720 °C. Ciclo 30 s/30 s. N₂ 0.28 sccm. 4.2×10⁻⁶ Torr. | Temperatura de crecimiento anotada: Tsus = 380 °C y Tpiro = 400 °C. Flujo 2.5% y 4.2×10⁻⁶ Torr a 120 W, luego 150 W. El 390 °C no está en estas hojas. La primera barrera se anota de 5 nm. |

Lectura de las ternas del artículo, a la luz de la libreta:

- 930: 417, 410 y 400 están en la misma nota (Tpiro medido, Tsus y el límite inferior esperado). No son QW1, QW2 y QW3.
- 931: 400 °C es Tpiro y 380 °C es Tsus. El 390 °C no aparece en las fotos.
- 925: 427 °C es Tpir. El termopar de esa zona está en 450 °C. El artículo no menciona los 450 °C.
- 914: 470–490 °C cubre el Tpiro buscado (470) y el medido (489). El termopar está en 500 °C.

El 720 °C sí aparece, pero en la monocapa de Ga o al cerrar la etapa caliente, antes de bajar a las barreras:

- 914: Tsus = 840 °C y Tpiro = 721 °C en la monocapa. Antes se llegó a Tsus = 900 °C y Tpiro = 755 °C. La monocapa duró del segundo 30 al 34 (4 s), como el plan.
- 925: tras bajar de 1050 a 850 °C, Tsus = 850 °C y Tpir = 724 °C. La desorción había subido hasta Tsus = 1060 °C y Tpir = 850 °C.
- 930: hay una caja Tsus = 830 °C y Tpiro = 720 °C marcada hacia el buffer. Las celdas anotadas en esa libreta son TGa = 898 °C y TIn = 569 °C, las mismas del plan.
- 931: caja Tsus = 815 °C y Tpiro = 723 °C en la etapa de la monocapa. Desorción en rampa a Tsus = 1050 °C en 40 min. Buffer: Ga en el segundo 10 y N en el 12. Luego bajada hacia Tsus = 405 °C y, ya en barreras y pozos, Tsus = 380 °C y Tpiro = 400 °C.

Presión: 4.2×10⁻⁶ Torr cuadra con la bitácora de 925 y de 931. En 930 el recuadro trae 4.7×10⁻⁶ y 4.1×10⁻⁶ Torr. En 914, al crecer las barreras, la libreta dice 9.7×10⁻⁶ Torr, no 4.2×10⁻⁶.

El flujo de la libreta no está en sccm. No conviertas 2.6% en 0.26 sccm: la hoja no da esa equivalencia.

### Tiempos de video que sí se leen

914, video de barreras y pozos (página 131). El arranque de QW3 está tachado; no lo uses como inicio.

- QW1 inicia a 0:26:50.
- Barrera 2 inicia a 0:32:00.
- QW2 inicia a 0:48:31.
- Barrera 3 inicia a 0:52:59.
- Barrera final inicia a 1:19:19 y termina a 1:30:21.
- Fin del crecimiento a las 16:07.

925, página 167. Mezcla reloj y tiempo de video; la secuencia de obturador sí es clara.

- Video “Well and Barriers 925”, Tsus = 450 °C, Tpir = 427 °C, Ga abre en 00:15.
- A 09:15 de video inicia la segunda barrera: nitrógeno modulado y el Ga abre después.
- Luego se cierra Ga y el nitrógeno queda puntual.
- Después: Ga modulado 2 s abierto / 2 s cerrado.
- “Cambio”: se cierra Ga, N abierto, y se abre Ga 30 s / 30 s.

930, tiempos de video en las páginas 180–181. No traen segundos de obturador.

- B1 termina en el min 1:00. QW1 inicia a 2:50. B2 inicia a 11:20.
- B2 termina y QW2 inicia a 19:50. QW2 termina a 27:31. B3 inicia a 27:50 y termina a 36:00.
- QW3 de 36:30 a 43:26. B4 de 43:40 a 50:20. Fin a las 17:12.

931, páginas 183–184. La primera barrera se describe de 5 nm y arranca al minuto 1 del video. Parte de los minutos de QW1 se leen peor que el resto; la temperatura Tsus = 380 °C / Tpiro = 400 °C está escrita junto al inicio de B2 y es la cifra firme.

- B2 termina a 20:35. QW2 de 21:00 a 28:40. B3 de 29:00 a 37:30.
- QW3 de 38:00 a 45:00. B4 de 45:10 a 53:50. Fin a las 22:35.

## 5. Qué puede afirmar el siguiente agente

- Los BEP de In y Ga de los dos planes son los mismos entre sí y no cambian por pozo. Ga 2.93×10⁻⁷ Torr a 898 °C. In 2.79×10⁻⁷ Torr a ≈ 569 °C una vez estabilizada la celda. No son iguales el uno al otro.
- La temperatura de barreras a 720 °C de la tabla del artículo no es la temperatura a la que la bitácora crece las barreras. 720 °C es la zona de la monocapa o del buffer caliente.
- Las ternas 417/410/400 y 400/390/380 no deben tratarse como tres pozos mientras no aparezca otra hoja que las separe.
- El ciclo 30 s/30 s de 925 es un cambio a mitad de crecimiento, después de un tramo a 2 s/2 s.
- 932 es otra muestra. Sirve como receta posterior (potencia 170/190/210 W), no como condición de 914, 925, 930 o 931.
- SIMS, RHEED y TEM del artículo son medidas, no consignas.

## Archivos de este repositorio

- `Condiciones_crecimiento_InGaN.docx` — tabla extraída solo del borrador.
- `generate_tabla.py` — la regenera.
- `condiciones_crecimiento_InGaN.md` — este archivo.
