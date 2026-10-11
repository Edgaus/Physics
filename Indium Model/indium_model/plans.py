"""Planes de crecimiento. Receta prevista, no el registro de la libreta.

El plan 932 es un crecimiento posterior. No es MME914, MME925, MME930 ni MME931.
"""

from __future__ import annotations

from dataclasses import dataclass

from indium_model.units import Torr

# Celdas. El Ga queda fijo. El In de la rampa y el In ya estable son momentos distintos.
GA_BEP = Torr("2.93", -7)
GA_CELL_C = 898
IN_BEP_DURING_RAMP = Torr("2.7", -7)
IN_CELL_DURING_RAMP_C = 565
IN_BEP_STABLE = Torr("2.79", -7)
IN_CELL_STABLE_C = 569


@dataclass(frozen=True)
class CellMoment:
    when: str
    ga_bep: Torr | None
    ga_cell_C: int | None
    in_bep: Torr | None
    in_cell_C: int | None
    in_note: str


CELL_MOMENTS: tuple[CellMoment, ...] = (
    CellMoment(
        "Durante la rampa / desorción",
        GA_BEP,
        GA_CELL_C,
        IN_BEP_DURING_RAMP,
        IN_CELL_DURING_RAMP_C,
        "≈ 565 °C",
    ),
    CellMoment(
        "En los toques de Ga",
        GA_BEP,
        GA_CELL_C,
        IN_BEP_STABLE,
        IN_CELL_STABLE_C,
        "≈ 569 °C",
    ),
    CellMoment(
        "En el buffer (solo Ga)",
        GA_BEP,
        GA_CELL_C,
        None,
        None,
        "no se reescribe",
    ),
)


@dataclass(frozen=True)
class PlannedWell:
    name: str
    ga_open_s: int
    pause_only_n_s: int
    in_open_s: int
    pause_s: int
    expected_in_percent: int | None
    written_duration: str
    pulses: int

    def seconds_omitting_final_pause(self) -> int:
        """Suma de aperturas por pulso, más las pausas entre pulsos.

        QW1 del plan 913-914 cae en 4 min 38 s con esta cuenta. El plan no
        escribe la fórmula; el archivo solo registra el tiempo escrito.
        """

        openings = self.ga_open_s + self.pause_only_n_s + self.in_open_s
        return self.pulses * openings + (self.pulses - 1) * self.pause_s


def time_fraction_scale_percent(t_ga_s: float, t_in_s: float) -> float:
    """(100/3) · t_In / (t_In + t_Ga).

    Redondeado al entero, reproduce 11, 17 y 22 del plan 913-914. Es una
    relación entre los números escritos. El plan no la formula, no es SIMS
    y no es un modelo de desorción.
    """

    if t_ga_s < 0 or t_in_s < 0 or t_ga_s + t_in_s == 0:
        raise ValueError("Los tiempos de obturador tienen que ser positivos.")
    return (100.0 / 3.0) * t_in_s / (t_in_s + t_ga_s)


@dataclass(frozen=True)
class BarrierNote:
    name: str
    thickness_nm: int | None
    temperature: str
    ga_sequence: str
    written_duration: str
    cycles: int | None = None


PREPARATION = (
    "Sustrato 3C-SiC(001). Desengrase 10 min en ultrasonido "
    "(xileno, acetona, isopropanol). BOE 30 s. Portasustrato de tantalio de 3 pulgadas. "
    "Desorción 1 h hasta Tsus = 1050 °C ≈ Tpiro = 850 °C. Rampas de In y Ga en 40 min. "
    "Cinco toques de Ga de 1 s. Bajada a Tpiro ≈ 720 °C y 1 monocapa de Ga (4 s)."
)

BUFFER = (
    "Buffer a Tsus = 720 °C, 4 nm/min, 240 nm en 1 h. "
    "Se abre Ga y el nitrógeno 2 s después."
)


@dataclass(frozen=True)
class GrowthPlan:
    plan_id: str
    filename: str
    date: str
    objective: str
    crew: tuple[str, ...]
    applies_to_samples: tuple[str, ...]
    stack: str
    plasma: str
    barriers: tuple[BarrierNote, ...]
    wells: tuple[PlannedWell, ...]
    preparation: str = PREPARATION
    buffer: str = BUFFER
    cell_moments: tuple[CellMoment, ...] = CELL_MOMENTS
    scope_note: str = ""


WELLS_913: tuple[PlannedWell, ...] = (
    PlannedWell("QW1", 2, 2, 1, 2, 11, "4 min 38 s", 40),
    PlannedWell("QW2", 2, 2, 2, 2, 17, "3 min 54 s", 40),
    PlannedWell("QW3", 1, 2, 2, 2, 22, "4 min", 40),
)

PLAN_913_914 = GrowthPlan(
    plan_id="913-914",
    filename="Plan de Crecimiento 913-914 01-10-25 Copy.pdf",
    date="01/10/25",
    objective=(
        "Pozos de InGaN por MME para ver la incorporación de indio "
        "según el tiempo de apertura de los obturadores."
    ),
    crew=(
        "Mario Alberto Zambrano",
        "Luis Vargas Hernández",
        "Edgar Agustín Contreras",
        "Marco Hinojosa",
    ),
    applies_to_samples=("MME914",),
    stack=(
        "3C-SiC / buffer GaN 240 nm / barrera 1 40 nm / QW1 / "
        "barrera 2 40 nm / QW2 / barrera 3 40 nm / QW3 / barrera 4 40 nm"
    ),
    plasma=(
        "Modo bajo al 6 %, modo brillante al 4 %, 150 W, "
        "flujo para PMBE = 4.6×10⁻⁶ Torr."
    ),
    barriers=(
        BarrierNote(
            "Barreras 1 a 3",
            40,
            "Tpiro = 450 °C",
            "N abierto. Ga 2 s abierto, 2 s cerrado y 2 s solo con nitrógeno.",
            "≈ 16 min",
        ),
        BarrierNote(
            "Barrera 4",
            40,
            "A los 5 min sube a Tsus = 720 °C en 10 min",
            "El mismo ciclo que las barreras 1 a 3",
            "≈ 16 min",
        ),
    ),
    wells=WELLS_913,
    scope_note=(
        "El PDF también numera el crecimiento 913. "
        "Lo transcrito aquí es la receta que agents.md contrasta con MME914."
    ),
)

def _well_932(name: str) -> PlannedWell:
    """Misma secuencia en los tres pozos. El plan no escribe un In %."""

    return PlannedWell(name, 2, 2, 2, 2, None, "2 min 36 s", 20)


PLAN_932 = GrowthPlan(
    plan_id="932",
    filename="Plan de Crecimiento 932 19_11_25 Copy.pdf",
    date="19/11/25",
    objective=(
        "Subir la incorporación de In (15 % hasta entonces) cambiando "
        "la potencia de plasma de un pozo al siguiente."
    ),
    crew=(
        "Mario Alberto Zambrano",
        "Luis Vargas Hernández",
        "Marco Hinojosa",
    ),
    applies_to_samples=(),
    stack=(
        "3C-SiC(001) / buffer 240 nm / barrera 1 de 5 nm / QW1 10 nm / "
        "barrera 2 de 30 nm / QW2 10 nm / barrera 3 de 30 nm / QW3 10 nm / "
        "barrera 4 de 30 nm"
    ),
    plasma="Ignición a 150 W. PMBE prevista = 3×10⁻⁶ Torr.",
    barriers=(
        BarrierNote(
            "Barrera 1",
            5,
            "Tpiro = 430 °C, bajada de 5 min con obturadores cerrados",
            "Ga 7 s abierto y pausa de 10 s",
            "≈ 1 min 15 s",
            cycles=5,
        ),
        BarrierNote(
            "Barreras 2 a 4",
            30,
            "No hay rampa a 720 °C en la cuarta barrera",
            "26 ciclos",
            "7 min 30 s",
            cycles=26,
        ),
    ),
    wells=(_well_932("QW1"), _well_932("QW2"), _well_932("QW3")),
    scope_note="Es un crecimiento posterior. No es MME914, MME925, MME930 ni MME931.",
)

# La potencia es el parámetro que el plan 932 cambia de pozo a pozo.
PLAN_932_PLASMA_W = {"QW1": 170, "QW2": 190, "QW3": 210}
PLAN_932_WELL_NM = 10

FOUR_SAMPLES = ("MME914", "MME925", "MME930", "MME931")


def plan_932_is_outside_the_four() -> bool:
    return PLAN_932.applies_to_samples == ()
