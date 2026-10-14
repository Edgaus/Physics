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

`R` y `α` se eligen por separado, con la restricción `I + R + D = 1`. Una `R`
alta deja poca probabilidad por monocapa tanto para enterrarse como para
desorberse: el In recorre muchas monocapas y el hombro aparece en la barrera.
Si la desorción se lleva parte de esa probabilidad, `R` baja y la cola se
acorta aunque la superficie esté caliente. Por eso la longitud de segregación
no crece de forma monótona con la temperatura.

## Parámetros

El suministro está fijado por el techo de la región fría: con el In enterrado
por completo, `x → 0.26`, luego `s = 0.26 / 0.74 = 0.351`. Cada pozo recibe 48
monocapas de Ga (~10.8 nm de GaN antes de sumar el In) y cada barrera 178
(~40 nm). El 48 es la escala que deja el pozo de 427 °C cerca de los 10–12 nm
de TEM; es el mismo número en las cuatro muestras.

| Muestra | T | α | R | λ | x máximo | ancho del pozo | en el pozo | en la cola | desorbido |
|---|---|---|---|---|---|---|---|---|---|
| MME914 | 470 °C | 0.32 | 0.90 | 2.1 nm | 10.1 % | 11.8 nm | 26 % | 6 % | 68 % |
| MME925 | 427 °C | 0.42 | 0.96 | 5.5 nm | 11.3 % | 11.7 nm | 24 % | 18 % | 58 % |
| MME930 | 417 °C | 0.90 | 0.22 | 0.15 nm | 24.0 % | 14.2 nm | 89 % | 0.5 % | 10 % |
| MME931 | 400 °C | 0.98 | 0.12 | 0.11 nm | 25.6 % | 14.5 nm | 98 % | 0.3 % | 2 % |

α y R no salen de un solo Arrhenius. Entre 417 y 427 °C el perfil cambia de
pozo cuadrado a hombro, y entre 427 y 470 °C la composición casi no se mueve
mientras la cola se acorta. Una sola barrera de desorción no puede ser plana
en un tramo y abrupta en el otro.

## Cómo se lee cada región

**Región 1, 470 °C.** El pozo llega a una meseta del 10 %. La longitud de
segregación es 2 nm: hay cola, y se apaga dentro de la barrera. Dos tercios
del In enviado se desorben. El primer pozo y el último reciben la misma dosis
y quedan iguales. Un desenfoque que crece con la profundidad (σ = 1.6 nm +
0.028 × profundidad, puesto para ilustrar, no ajustado) baja el pico profundo
de 10 % a 6.8 % y lo ensancha de 12.8 nm a 16.9 nm, en el mismo sentido que
8.6 % contra 12.6 %. No alcanza para fabricar el 12.6 % del pozo superficial:
ese pozo queda por encima del modelo.

**Región 2, 427 °C.** La meseta no llega a formarse. Con λ = 5.5 nm y un pozo
de 12 nm, la composición sube durante todo el pozo y el máximo (11 %) queda en
la interfaz superior. A partir de ahí decae dentro de la barrera: ese decaimiento
es el hombro. El 18 % del In enviado termina en las barreras, frente al 6 % de
la región 1, con una composición de pozo casi igual. El flanco de subida y el
hombro son la misma R. Si en el SIMS de 925 el pozo es una meseta plana con un
bulto a cada lado, esta R única no alcanza y hay que separar el intercambio
durante el pozo del intercambio ya sobre GaN.

El cráter de 925 baja ligeramente hacia la superficie (12.3 → 10.9 %). El
desenfoque empuja al revés, porque el pozo profundo es el que más se aplana.
La tendencia de 925 no es un artefacto de resolución.

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

- Las barreras de 40 nm vacían la capa flotante. El pozo siguiente no hereda In
  del anterior. Tres pozos iguales son la predicción si el obturador y la
  temperatura no cambian.
- El plan de 914 sí cambiaba el tiempo de In frente al de Ga de un pozo al
  siguiente. La bitácora de 930 y 931 no separa una temperatura por pozo. El
  gradiente interno de la región 3 pide dosis distinta, o una eficiencia que
  sube durante el crecimiento, y no está en las fotos de la libreta.
- El ancho TEM de 931 (16–20 nm) frente al de 925 (10–12 nm) es un factor ~1.6.
  El modelo, a dosis de Ga igual, solo da 14.5 / 11.7 ≈ 1.24. El sentido
  coincide; la diferencia de más apunta a que el tiempo de pozo tampoco fue el
  mismo.
- MME914 no es únicamente la muestra caliente. En la bitácora la presión al
  crecer las barreras y el ciclo de Ga no son los de 925.

Quedan fuera del perfil, a propósito. El pulling de composición bajaría x
cuando la deformación crece, en contra de la región 3, y no fabrica hombros.
El enriquecimiento junto a fallas de apilamiento es local: mueve la
luminiscencia respecto del In promedio y no el cráter de SIMS, que promedia
el pozo.
