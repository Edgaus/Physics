"""Afirmaciones que agents.md deja en pie. Cada una se evalúa con los datos separados."""

from __future__ import annotations

from indium_model.article import HAMILTONIAN, SAMPLES, sims_by_sample
from indium_model.bitacora import NOTEBOOKS, WELL_SHUTTER_TIMES, by_sample
from indium_model.plans import (
    FOUR_SAMPLES,
    GA_BEP,
    GA_CELL_C,
    IN_BEP_DURING_RAMP,
    IN_BEP_STABLE,
    IN_CELL_STABLE_C,
    PLAN_913_914,
    PLAN_932,
    PLAN_932_PLASMA_W,
    WELLS_913,
    plan_932_is_outside_the_four,
    time_fraction_scale_percent,
)
from indium_model.units import Torr, flow_percent_to_sccm


def section_5() -> list[tuple[str, bool]]:
    m914 = by_sample("MME914")
    m925 = by_sample("MME925")
    m930 = by_sample("MME930")
    m931 = by_sample("MME931")
    growth_930 = m930.crecimiento()
    growth_931 = m931.crecimiento()
    article_pressure = Torr("4.2", -6)
    sims_914 = sims_by_sample("MME914").percent
    plan_in = tuple(well.expected_in_percent for well in WELLS_913)
    ham_914 = next(row for row in HAMILTONIAN if row.sample == "MME914")

    percent_rejected = False
    try:
        flow_percent_to_sccm(2.6)
    except ValueError:
        percent_rejected = True

    rounded_targets = tuple(
        round(time_fraction_scale_percent(well.ga_open_s, well.in_open_s))
        for well in WELLS_913
    )

    return [
        (
            "Ga 2.93×10⁻⁷ Torr a 898 °C e In estable 2.79×10⁻⁷ Torr a ≈ 569 °C, y no son iguales.",
            GA_BEP == Torr("2.93", -7)
            and GA_CELL_C == 898
            and IN_BEP_STABLE == Torr("2.79", -7)
            and IN_CELL_STABLE_C == 569
            and GA_BEP != IN_BEP_STABLE,
        ),
        (
            "El In de la rampa (2.7×10⁻⁷ Torr) es otro momento que el In ya estable.",
            IN_BEP_DURING_RAMP == Torr("2.7", -7) and IN_BEP_DURING_RAMP != IN_BEP_STABLE,
        ),
        (
            "Ninguna temperatura de crecimiento de barreras o pozos en la bitácora es 720 °C.",
            all(
                reading.tsus_C != 720 and reading.tpiro_C != 720
                for book in NOTEBOOKS
                for reading in book.crecimiento()
            ),
        ),
        (
            "Los ~720 °C de la libreta caen en la monocapa o en el buffer caliente.",
            any(
                reading.stage == "etapa_caliente" and reading.tpiro_C in {720, 721, 723, 724}
                for book in NOTEBOOKS
                for reading in book.readings
            ),
        ),
        (
            "En MME930, 417, 410 y 400 son una sola consigna, no tres pozos.",
            len(growth_930) == 1
            and growth_930[0].tpiro_C == 417
            and growth_930[0].tsus_C == 410
            and "400" in growth_930[0].detail
            and m930.ga_cycle is None,
        ),
        (
            "En MME931, 400 °C es Tpiro y 380 °C es Tsus. El 390 °C no está en las fotos.",
            len(growth_931) == 1
            and growth_931[0].tpiro_C == 400
            and growth_931[0].tsus_C == 380
            and 390 not in _temperatures(m931),
        ),
        (
            "En MME925, 427 °C es Tpir y el termopar de esa zona está en 450 °C.",
            any(
                reading.tpiro_C == 427 and reading.tsus_C == 450
                for reading in m925.crecimiento()
            ),
        ),
        (
            "En MME914, 470–490 °C cubre el Tpiro buscado (470) y el medido en la barrera (489). El termopar está en 500 °C.",
            {reading.tpiro_C for reading in m914.crecimiento()} == {470, 489}
            and {reading.tsus_C for reading in m914.crecimiento()} == {500},
        ),
        (
            "El ciclo 30 s/30 s de MME925 es un cambio a mitad de crecimiento, después de un tramo a 2 s/2 s.",
            m925.ga_cycle is not None and "2 s" in m925.ga_cycle and "30 s" in m925.ga_cycle,
        ),
        (
            "MME914 y MME930 no traen, en estas páginas, el ciclo de Ga que el artículo les asigna.",
            m914.ga_cycle is None and m930.ga_cycle is None,
        ),
        (
            "El plan 932 no es condición de 914, 925, 930 ni 931. Su potencia de pozo es 170/190/210 W.",
            plan_932_is_outside_the_four()
            and PLAN_932_PLASMA_W == {"QW1": 170, "QW2": 190, "QW3": 210}
            and PLAN_932.applies_to_samples == (),
        ),
        (
            "SIMS y el Hamiltoniano quedan como medidas del artículo.",
            ham_914.percent == (15.5,) and sims_914 == (8.6, 8.6, 12.6),
        ),
        (
            "El In esperado del plan 913-914 (11/17/22 %) no es el SIMS de MME914.",
            plan_in == (11, 17, 22) and sims_914 != plan_in,
        ),
        (
            "Esos 11/17/22 coinciden, al entero, con (100/3)·t_In/(t_In+t_Ga). El plan no escribe la fórmula.",
            rounded_targets == (11, 17, 22),
        ),
        (
            "4.2×10⁻⁶ Torr es la presión del artículo en las cuatro muestras, y la libreta la anota en 925 y en 931.",
            all(row.pmbe == article_pressure for row in SAMPLES)
            and _has_pressure(m925, article_pressure)
            and _has_pressure(m931, article_pressure)
            and not _has_pressure(m914, article_pressure)
            and not _has_pressure(m930, article_pressure),
        ),
        (
            "El flujo de la libreta no se convierte de por ciento a sccm.",
            percent_rejected and WELL_SHUTTER_TIMES is None,
        ),
        (
            "El artículo iguala las barreras a 720 °C y da el flujo en sccm. Eso vive solo en el borrador.",
            all(row.barrier_GaN_C == 720 for row in SAMPLES)
            and tuple(row.sample for row in SAMPLES) == FOUR_SAMPLES
            and PLAN_913_914.applies_to_samples == ("MME914",),
        ),
    ]


def _temperatures(book) -> set[float]:
    values: set[float] = set()
    for reading in book.readings:
        if reading.tsus_C is not None:
            values.add(float(reading.tsus_C))
        if reading.tpiro_C is not None:
            values.add(float(reading.tpiro_C))
    return values


def _has_pressure(book, pressure: Torr) -> bool:
    return any(note.value == pressure for note in book.pressures)
