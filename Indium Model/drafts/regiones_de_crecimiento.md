# Tres regiones de incorporación de In

Pozos cúbicos InGaN/GaN, crecimiento [001], sin polarización. El mismo dosis de
Ga y de In entra a cada pozo. Lo que cambia de muestra a muestra es el reparto
de ese In entre tres canales: enterrarse, seguir flotando, o desorberse.

## Lo que se ve en los crecimientos

| Región | Muestra | T del pozo | Forma del SIMS | In/N de cráter, QW1→QW3 |
|---|---|---|---|---|
| 1 | MME914 | 470 °C | Meseta ~10 %, cola exponencial corta. El último pozo es más alto y más angosto. | 8.6, 8.6, 12.6 % |
| 2 | MME925 | 427 °C | Meseta parecida, con hombros junto a los pozos. | 12.3, 11.7, 10.9 % |
| 3 | MME930, MME931 | 417 °C y 400 °C | Hasta ~26 %, pozos más anchos, sin hombros. Los dos perfiles se parecen. | 15.6, 18.3, 25.4 % y 14.9, 17.4, 26.3 % |

QW1 es el primer pozo que se crece, el más profundo en el SIMS. El In/N de cráter
es el pico del perfil. TEM: pozos de 925 ≈ 10–12 nm; pozos de 931 ≈ 16–20 nm.

## Balance por monocapa

En la nota de partida la barrera quedó escrita como `x0(1−Sn) Sn−N`. La forma
que cierra el balance, y que se reduce a Muraki cuando no hay desorción, es
otra. En cada monocapa de Ga el In disponible es el que acaba de llegar más el
que venía flotando:

```
A = θ + s
incorporado = I · A
θ siguiente = R · A
desorbido = D · A
I + R + D = 1
```

`s` son átomos de In entregados por átomo de Ga. El Ga se queda. La composición
y el espesor de ese paso son

```
x = i / (1 + i)
espesor = (1 + i) · a/2
```

con `a = 0.450 nm`, así que el plano catiónico [001] mide 0.225 nm. Un pozo que
retiene el In crece más grueso que uno que lo pierde, con el mismo tiempo de
obturador.

Dentro del pozo, con `s` constante y `α = I / (I + D)`:

```
i_n = α s (1 − R^n)
```

En la barrera que se crece después, paso `k = 1, 2, …`:

```
i_{N+k} = α s (1 − R^N) R^k
```

Con `D = 0`, `α = 1` y esto es la dosis de Muraki (1992). La cola apunta hacia
la superficie, que es la dirección de crecimiento. La barrera de abajo del pozo
no recibe In.

`α = I/(I+D)` es la fracción de la dosis que se queda en la película. `R` decide
si esa fracción se entierra en el pozo o cabalga hasta la barrera. En MME925 `α`
está cerca de 1 y `R` cerca de 1: el indio no se pierde, y el pozo es más corto
que `λ`, así que la mayor parte se incorpora ya en la barrera. En MME914 `α`
cae: la misma población flotante se desorbe, el hombro desaparece y el área de
la curva baja.

## Parámetros

El suministro está fijado por el techo de la región fría: con el In enterrado
por completo, `x → 0.26`, luego `s = 0.26 / 0.74 = 0.351`. Cada pozo recibe 48
monocapas de Ga (~10.8 nm de GaN antes de sumar el In) y cada barrera 178
(~40 nm). El 48 es la escala que deja el pozo de 427 °C cerca de los 10–12 nm
de TEM; es el mismo número en las cuatro muestras.

| Muestra | T | α | R | λ | x máximo | ancho del pozo | en el pozo | en la cola | desorbido |
|---|---|---|---|---|---|---|---|---|---|
| MME914 | 470 °C | 0.30 | 0.86 | 1.5 nm | 9.5 % | 11.8 nm | 26 % | 4 % | 70 % |
| MME925 | 427 °C | 0.95 | 0.98 | 11.1 nm | 17.3 % | 12.2 nm | 36 % | 59 % | 5 % |
| MME930 | 417 °C | 0.90 | 0.22 | 0.15 nm | 24.0 % | 14.2 nm | 89 % | 0.5 % | 10 % |
| MME931 | 400 °C | 0.98 | 0.12 | 0.11 nm | 25.6 % | 14.5 nm | 98 % | 0.3 % | 2 % |

El área bajo el SIMS es la suma de las dos columnas de incorporación. En MME914
se queda el 30 % de la dosis; en MME925 se queda el 95 %. α y R no salen de un
solo Arrhenius: entre 417 y 427 °C el indio pasa de enterrarse en el pozo a
cabalgar hacia la barrera, y entre 427 y 470 °C ese reservorio se desorbe.

## Cómo se lee cada región

**Región 1, 470 °C.** El indio que alcanza a flotar se desorbe. En la película
queda el 30 % de la dosis, casi todo dentro de una meseta del 9.5 %, con una
cola de 1.5 nm. El hombro no llega a formarse porque el reservorio se vacía
hacia el vacío y no hacia la barrera. El primer pozo y el último reciben la
misma dosis. Un desenfoque que crece con la profundidad (σ = 1.6 nm + 0.028 ×
profundidad) baja el pico profundo de 9.5 % a 6.5 % y lo ensancha hasta 16.6 nm.
El cráter del pozo superficial, 12.6 %, sigue por encima de esa meseta.

**Región 2, 427 °C.** La desorción está casi cerrada: se queda el 95 % de la
dosis. Con λ = 11 nm y un pozo de 12 nm, el indio no alcanza a enterrarse
durante el pozo. El 59 % de la dosis se incorpora en la barrera de arriba y el
36 % dentro del pozo. El máximo, 17 %, está en la interfaz superior; la
composición media del pozo es ~11 %, cerca del cráter. El hombro es esa cola.
El área total es la de las muestras frías: lo que cambia es el sitio, no la
cantidad que sobrevivió.

Eso solo ocurre porque el pozo es más corto que λ. En estado estacionario,
aunque R sea alta, la meseta volvería a `x = s/(1+s) = 26 %` y el hombro se
quedaría solo con el reservorio `θ ≈ s λ / (a/2)`. Un pozo mucho más grueso que
11 nm, a la misma temperatura, subiría de composición.

El cráter de 925 baja hacia la superficie (12.3 → 10.9 %). La cola de 11 nm
dentro de una barrera de 40 nm deja pasar un poco de indio al pozo siguiente,
y el desenfoque aplana más el pozo profundo: las dos cosas empujan el pico
hacia arriba en la dirección de crecimiento. La pendiente medida va al revés.

**Región 3, 400–417 °C.** R cae por debajo de 0.25 y la desorción casi se
apaga. El In se entierra donde llega: pozo cuadrado, sin hombro, x = 24 % y
26 %. Entre 417 y 400 °C los dos puntos ya están del lado frío del umbral, así
que el perfil se mantiene. El 26 % es el In/(In+Ga) que llegó al sustrato. Los
pozos salen de 14.2 y 14.5 nm, unos 3 nm más anchos que a 470 °C, porque los
cationes de In se quedan.

El cráter del último pozo (25.4 % y 26.3 %) coincide con ese techo. Los pozos
profundos, 15–18 %, quedan por debajo. En un pozo de 14 nm el desenfoque usado
aquí solo los baja a ~18–20 % en el más profundo. La pendiente 15 → 26 % dentro
de 930 y de 931 es incorporación real que cambia de pozo a pozo, con la misma
temperatura nominal.

## Qué no cierra con una sola temperatura

- En MME914 y en la región 3 la barrera de 40 nm apaga la cola. En MME925 la
  cola mide 11 nm y deja pasar unos pocos por ciento al pozo siguiente. Con el
  obturador fijo, los tres pozos siguen saliendo casi iguales.
- El plan de 914 sí cambiaba el tiempo de In frente al de Ga de un pozo al
  siguiente. La bitácora de 930 y 931 no separa una temperatura por pozo. El
  gradiente interno de la región 3 pide dosis distinta, o una eficiencia que
  sube durante el crecimiento, y no está en las fotos de la libreta.
- El ancho TEM de 931 (16–20 nm) frente al de 925 (10–12 nm) es un factor ~1.6.
  El modelo, a dosis de Ga igual, solo da 14.5 / 12.2 ≈ 1.2. El sentido
  coincide; la diferencia de más apunta a que el tiempo de pozo tampoco fue el
  mismo.
- MME914 no es únicamente la muestra caliente. En la bitácora la presión al
  crecer las barreras y el ciclo de Ga no son los de 925.

Quedan fuera del perfil, a propósito. El pulling de composición bajaría x
cuando la deformación crece, en contra de la región 3, y no fabrica hombros.
El enriquecimiento junto a fallas de apilamiento es local: mueve la
luminiscencia respecto del In promedio y no el cráter de SIMS, que promedia
el pozo.
