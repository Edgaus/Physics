"""Borrador del artículo. No es la bitácora ni el plan.

Sección 1 de agents.md. La tabla del Word sale solo de aquí.
"""

from __future__ import annotations

from dataclasses import dataclass

from indium_model.units import Torr

ARTICLE_TITLE = (
    "Growth-controlled carrier redistribution and negative thermal quenching "
    "in cubic InGaN/GaN quantum wells on 3C-SiC(001)/Si"
)

GROWTH_PARAGRAPH = (
    "The structures were grown by migration-enhanced epitaxy under continuous "
    "active nitrogen. The three quantum wells were deposited with a common "
    "sequence but at different temperatures, whereas the GaN barriers were "
    "grown at 720 °C. MME914 represents the high-temperature limit, with well "
    "temperatures of 470–490 °C and short 2 s Ga-on/2 s Ga-off barrier cycles. "
    "MME925, MME930 and MME931 used 30 s Ga-on/30 s Ga-off barriers. Their well "
    "temperatures decreased progressively, reaching 427 °C in MME925, "
    "417/410/400 °C in MME930 and 400/390/380 °C in MME931. The N2 flow "
    "(0.30 sccm in MME914, 0.26 sccm in MME925 and MME930, 0.28 sccm in "
    "MME931) was adjusted so that the MBE pressure was 4.2×10−6 Torr in every "
    "growth."
)

TECHNIQUE_IN_GROWTH_SECTION = "migration-enhanced epitaxy"
TECHNIQUE_IN_CONCLUSIONS = "metal-modulated epitaxy"
LAB_ABBREVIATION = "MME"

# El artículo no asigna QW1 = 417 °C. La cadena es la celda de la tabla.
TRIPLET_READING = (
    "El orden QW1/QW2/QW3 de 930 y 931 es una lectura del artículo "
    "(temperaturas en descenso y el pozo final es el más frío). "
    "El artículo no escribe «QW1 = 417 °C»."
)

FINAL_WELL_QUALITATIVE = (
    "El pozo final combina la temperatura más baja de su receta con la mayor "
    "exposición de In respecto de Ga. El artículo no da el número."
)


@dataclass(frozen=True)
class ArticleSample:
    sample: str
    well_temperature: str
    barrier_GaN_C: int
    ga_on_s: int
    ga_off_s: int
    n2_sccm: str
    pmbe: Torr

    @property
    def ga_cycle(self) -> str:
        return f"{self.ga_on_s} s / {self.ga_off_s} s"


SAMPLES: tuple[ArticleSample, ...] = (
    ArticleSample("MME914", "470–490 (intervalo; no hay un valor por pozo)", 720, 2, 2, "0.30", Torr("4.2", -6)),
    ArticleSample("MME925", "427 (un solo valor)", 720, 30, 30, "0.26", Torr("4.2", -6)),
    ArticleSample("MME930", "417 / 410 / 400", 720, 30, 30, "0.26", Torr("4.2", -6)),
    ArticleSample("MME931", "400 / 390 / 380", 720, 30, 30, "0.28", Torr("4.2", -6)),
)


@dataclass(frozen=True)
class SimsCrater:
    """In/N de cráter, en orden de crecimiento. Cota inferior de x. No es consigna."""

    sample: str
    qw1: float
    qw2: float
    qw3: float

    @property
    def percent(self) -> tuple[float, float, float]:
        return (self.qw1, self.qw2, self.qw3)


SIMS: tuple[SimsCrater, ...] = (
    SimsCrater("MME914", 8.6, 8.6, 12.6),
    SimsCrater("MME925", 12.3, 11.7, 10.9),
    SimsCrater("MME930", 15.6, 18.3, 25.4),
    SimsCrater("MME931", 14.9, 17.4, 26.3),
)


@dataclass(frozen=True)
class HamiltonianLayer:
    """In/N promedio de capa que usa el Hamiltoniano. No es el pico de cráter.

    En MME914 el borrador solo da el último pozo.
    """

    sample: str
    percent: tuple[float, ...]


HAMILTONIAN: tuple[HamiltonianLayer, ...] = (
    HamiltonianLayer("MME914", (15.5,)),
    HamiltonianLayer("MME925", (13.7, 17.3, 17.9)),
    HamiltonianLayer("MME930", (16.3, 19.1, 25.4)),
    HamiltonianLayer("MME931", (16.4, 18.4, 27.1)),
)

# Anchos TEM citados. 930 no tiene ancho. 914 no aparece en esa frase.
TEM_WELL_NM: dict[str, str] = {
    "MME925": "10–12 nm",
    "MME931": "16–20 nm",
}


def by_sample(sample: str) -> ArticleSample:
    for row in SAMPLES:
        if row.sample == sample:
            return row
    raise KeyError(sample)


def sims_by_sample(sample: str) -> SimsCrater:
    for row in SIMS:
        if row.sample == sample:
            return row
    raise KeyError(sample)
