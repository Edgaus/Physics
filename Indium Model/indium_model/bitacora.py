"""Bitácora fotografiada. No es el borrador ni el plan.

El flujo queda en por ciento. No hay tiempos de obturador de In/Ga dentro
de los pozos; el único ciclo de Ga anotado con un cambio es el de MME925.
"""

from __future__ import annotations

from dataclasses import dataclass

from indium_model.units import Torr

# Las fotos no traen los segundos de In y de Ga durante el pozo.
WELL_SHUTTER_TIMES = None


@dataclass(frozen=True)
class Reading:
    """Una temperatura anotada, con la etapa a la que pertenece.

    ``crecimiento`` es barreras y pozos. ``etapa_caliente`` es la monocapa,
    el buffer caliente o la caja de ~720 °C. No se intercambian.
    """

    stage: str
    label: str
    tsus_C: float | None = None
    tpiro_C: float | None = None
    detail: str = ""


@dataclass(frozen=True)
class PressureNote:
    context: str
    value: Torr


@dataclass(frozen=True)
class Notebook:
    sample: str
    pages: str
    pages_note: str
    flow_percent: float
    plasma_calibration_W: int
    plasma_set_W: int
    readings: tuple[Reading, ...]
    pressures: tuple[PressureNote, ...]
    ga_cycle: str | None
    video: tuple[str, ...]
    notes: tuple[str, ...] = ()

    def crecimiento(self) -> tuple[Reading, ...]:
        return tuple(reading for reading in self.readings if reading.stage == "crecimiento")


NOTEBOOKS: tuple[Notebook, ...] = (
    Notebook(
        sample="MME914",
        pages="129–131",
        pages_note="",
        flow_percent=3.0,
        plasma_calibration_W=120,
        plasma_set_W=150,
        readings=(
            Reading(
                "crecimiento",
                "Bajada para la región activa",
                tsus_C=500,
                tpiro_C=470,
                detail="Tsus = 500 °C para tener Tpiro = 470 °C.",
            ),
            Reading(
                "crecimiento",
                "En la barrera",
                tsus_C=500,
                tpiro_C=489,
                detail="Tpiro = 489 °C y Tsus = 500 °C.",
            ),
            Reading(
                "etapa_caliente",
                "Monocapa de Ga",
                tsus_C=840,
                tpiro_C=721,
                detail="Duró del segundo 30 al 34 (4 s).",
            ),
            Reading(
                "etapa_caliente",
                "Antes de la monocapa",
                tsus_C=900,
                tpiro_C=755,
                detail="Se llegó a Tsus = 900 °C y Tpiro = 755 °C.",
            ),
        ),
        pressures=(
            PressureNote("En la barrera", Torr("9.7", -6)),
            PressureNote("Plasma dejado en 3 % a 120 W, luego 150 W", Torr("4.6", -6)),
        ),
        ga_cycle=None,
        notes=("Estas páginas no escriben el ciclo de 2 s.",),
        video=(
            "QW1 inicia a 0:26:50.",
            "Barrera 2 inicia a 0:32:00.",
            "QW2 inicia a 0:48:31.",
            "Barrera 3 inicia a 0:52:59.",
            "El arranque de QW3 está tachado y no se toma como inicio.",
            "Barrera final inicia a 1:19:19 y termina a 1:30:21.",
            "Fin del crecimiento a las 16:07.",
        ),
    ),
    Notebook(
        sample="MME925",
        pages="164, 166–167",
        pages_note=(
            "La página 164 solo dice «Crecimiento 925». "
            "El registro está en 166–167 y puede seguir en hojas que no se enviaron."
        ),
        flow_percent=2.6,
        plasma_calibration_W=120,
        plasma_set_W=150,
        readings=(
            Reading(
                "crecimiento",
                "Pozos y barreras",
                tsus_C=450,
                tpiro_C=427,
                detail="Tsus = 450 °C y Tpir = 427 °C.",
            ),
            Reading(
                "etapa_caliente",
                "Tras bajar de 1050 a 850 °C",
                tsus_C=850,
                tpiro_C=724,
                detail="Tsus = 850 °C y Tpir = 724 °C.",
            ),
            Reading(
                "desorcion",
                "Máximo de la desorción",
                tsus_C=1060,
                tpiro_C=850,
                detail="La desorción subió hasta Tsus = 1060 °C y Tpir = 850 °C.",
            ),
        ),
        pressures=(
            PressureNote("Flujo 2.6 % a 120 W y luego 150 W", Torr("4.2", -6)),
        ),
        ga_cycle=(
            "El Ga empezó en 2 s abierto / 2 s cerrado y, marcado «Cambio», "
            "pasó a 30 s / 30 s."
        ),
        video=(
            "Mezcla reloj y tiempo de video; la secuencia de obturador sí es clara.",
            "Video «Well and Barriers 925», Tsus = 450 °C, Tpir = 427 °C, Ga abre en 00:15.",
            "A 09:15 de video inicia la segunda barrera: nitrógeno modulado y el Ga abre después.",
            "Luego se cierra Ga y el nitrógeno queda puntual.",
            "Después: Ga modulado 2 s abierto / 2 s cerrado.",
            "«Cambio»: se cierra Ga, N abierto, y se abre Ga 30 s / 30 s.",
        ),
    ),
    Notebook(
        sample="MME930",
        pages="179–181",
        pages_note="",
        flow_percent=2.6,
        plasma_calibration_W=120,
        plasma_set_W=150,
        readings=(
            Reading(
                "crecimiento",
                "Una sola consigna al bajar del buffer",
                tsus_C=410,
                tpiro_C=417,
                detail=(
                    "Se esperaba 400 ≤ Tpiro ≤ 430 °C y se midió Tpiro = 417 °C. "
                    "417, 410 y 400 están en la misma nota. No hay una temperatura por pozo."
                ),
            ),
            Reading(
                "etapa_caliente",
                "Caja marcada hacia el buffer",
                tsus_C=830,
                tpiro_C=720,
                detail="Tsus = 830 °C y Tpiro = 720 °C.",
            ),
        ),
        pressures=(
            PressureNote("Recuadro", Torr("4.7", -6)),
            PressureNote("Recuadro", Torr("4.1", -6)),
        ),
        ga_cycle=None,
        video=(
            "B1 termina en el min 1:00. QW1 inicia a 2:50. B2 inicia a 11:20.",
            "B2 termina y QW2 inicia a 19:50. QW2 termina a 27:31. "
            "B3 inicia a 27:50 y termina a 36:00.",
            "QW3 de 36:30 a 43:26. B4 de 43:40 a 50:20. Fin a las 17:12.",
            "No traen segundos de obturador.",
        ),
        notes=("Celdas anotadas: TGa = 898 °C y TIn = 569 °C.",),
    ),
    Notebook(
        sample="MME931",
        pages="183–184",
        pages_note="",
        flow_percent=2.5,
        plasma_calibration_W=120,
        plasma_set_W=150,
        readings=(
            Reading(
                "desorcion",
                "Rampa",
                tsus_C=1050,
                detail="Desorción en rampa a Tsus = 1050 °C en 40 min.",
            ),
            Reading(
                "etapa_caliente",
                "Monocapa",
                tsus_C=815,
                tpiro_C=723,
                detail="Tsus = 815 °C y Tpiro = 723 °C.",
            ),
            Reading(
                "bajada",
                "Después del buffer",
                tsus_C=405,
                detail="Bajada hacia Tsus = 405 °C.",
            ),
            Reading(
                "crecimiento",
                "Barreras y pozos",
                tsus_C=380,
                tpiro_C=400,
                detail=(
                    "Tsus = 380 °C y Tpiro = 400 °C. "
                    "El 390 °C no está en estas hojas."
                ),
            ),
        ),
        pressures=(
            PressureNote("Flujo 2.5 % a 120 W, luego 150 W", Torr("4.2", -6)),
        ),
        ga_cycle=None,
        video=(
            "La primera barrera se describe de 5 nm y arranca al minuto 1 del video.",
            "Parte de los minutos de QW1 se leen peor que el resto. "
            "Tsus = 380 °C / Tpiro = 400 °C está escrito junto al inicio de B2 y es la cifra firme.",
            "B2 termina a 20:35. QW2 de 21:00 a 28:40. B3 de 29:00 a 37:30.",
            "QW3 de 38:00 a 45:00. B4 de 45:10 a 53:50. Fin a las 22:35.",
        ),
        notes=(
            "La primera barrera se anota de 5 nm.",
            "Buffer: Ga en el segundo 10 y N en el 12.",
        ),
    ),
)


def by_sample(sample: str) -> Notebook:
    for book in NOTEBOOKS:
        if book.sample == sample:
            return book
    raise KeyError(sample)


def quoted_temperatures(book: Notebook) -> set[float]:
    values: set[float] = set()
    for reading in book.readings:
        if reading.tsus_C is not None:
            values.add(reading.tsus_C)
        if reading.tpiro_C is not None:
            values.add(reading.tpiro_C)
    return values
