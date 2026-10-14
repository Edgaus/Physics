"""Calibrated regimes for the four cubic InGaN multi-quantum-well samples.

The samples are not a pure temperature series: MME914 also differs in Ga
shutter cycle and in the pressure written in the logbook. Temperature is
still the axis along which the SIMS shapes fall into three regions, so each
sample is one (I, R, D) point and not a point on a forced Arrhenius curve.
"""

from __future__ import annotations

from dataclasses import dataclass


# Zincblende GaN, cation plane spacing along [001] is a/2.
A_GAN_NM = 0.450
ML_NM = A_GAN_NM / 2.0

# Cold-sample crater maximum. With burial dominating, x approaches this
# value, so it is the In/(In+Ga) dose that actually arrives during the well.
X_SUPPLY_LIMIT = 0.26
S_IN_PER_GA = X_SUPPLY_LIMIT / (1.0 - X_SUPPLY_LIMIT)

BARRIER_NM = 40.0
N_GA_BARRIER = int(round(BARRIER_NM / ML_NM))
# Same Ga dose in every well, as in the note that the wells shared a growth
# time. 48 Ga monolayers are ~10.8 nm of GaN before adding incorporated In.
N_GA_WELL = 48
N_WELLS = 3

# SIMS crater In/N in growth order (QW1 is the deepest), from the draft.
# These are peak ratios, not layer averages.


def _branch(alpha: float, segregate: float) -> tuple[float, float, float]:
    """Return (I, R, D) with I + R + D = 1.

    alpha = I / (I + D) is the fraction of In that eventually incorporates
    rather than desorbs. R is the fraction that stays in the floating layer
    after one Ga monolayer.
    """
    if not 0.0 <= alpha <= 1.0:
        raise ValueError(f"alpha out of range: {alpha}")
    if not 0.0 <= segregate < 1.0:
        raise ValueError(f"R out of range: {segregate}")
    remaining = 1.0 - segregate
    incorporate = alpha * remaining
    desorb = (1.0 - alpha) * remaining
    return incorporate, segregate, desorb


@dataclass(frozen=True)
class Regime:
    sample: str
    region: int
    temperature_c: float
    incorporate: float
    segregate: float
    desorb: float
    # Crater In/N of QW1, QW2, QW3 in growth order.
    sims_peaks: tuple[float, float, float]
    note: str

    def __post_init__(self) -> None:
        total = self.incorporate + self.segregate + self.desorb
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"{self.sample}: I+R+D = {total}, expected 1")

    @property
    def alpha(self) -> float:
        retained = self.incorporate + self.desorb
        if retained == 0.0:
            return 1.0
        return self.incorporate / retained

    @property
    def segregation_length_nm(self) -> float:
        """Decay length of the floating layer, -h / ln(R)."""
        if self.segregate <= 0.0:
            return 0.0
        if self.segregate >= 1.0:
            return float("inf")
        from math import log

        return -ML_NM / log(self.segregate)


def _regime(
    sample: str,
    region: int,
    temperature_c: float,
    alpha: float,
    segregate: float,
    sims_peaks: tuple[float, float, float],
    note: str,
) -> Regime:
    incorporate, segregate, desorb = _branch(alpha, segregate)
    return Regime(
        sample=sample,
        region=region,
        temperature_c=temperature_c,
        incorporate=incorporate,
        segregate=segregate,
        desorb=desorb,
        sims_peaks=sims_peaks,
        note=note,
    )


# alpha sets the plateau composition. R sets how many monolayers the
# floating In rides. The two are independent given I + R + D = 1, and a
# high R leaves little probability per monolayer for either burial or
# desorption — that is the shoulder regime.
REGIMES: tuple[Regime, ...] = (
    _regime(
        "MME914",
        1,
        470.0,
        alpha=0.32,
        segregate=0.90,
        sims_peaks=(0.086, 0.086, 0.126),
        note="Meseta baja y cola corta: el In flotante se desorbe antes de recorrer la barrera.",
    ),
    _regime(
        "MME925",
        2,
        427.0,
        alpha=0.42,
        segregate=0.96,
        sims_peaks=(0.123, 0.117, 0.109),
        note="Meseta similar, pero el In flota varias nm y reaparece como hombro en la barrera.",
    ),
    _regime(
        "MME930",
        3,
        417.0,
        alpha=0.90,
        segregate=0.22,
        sims_peaks=(0.156, 0.183, 0.254),
        note="Enterrado al llegar: pozo abrupto y composición cerca del límite de suministro.",
    ),
    _regime(
        "MME931",
        3,
        400.0,
        alpha=0.98,
        segregate=0.12,
        sims_peaks=(0.149, 0.174, 0.263),
        note="Misma región que MME930. Bajar de 417 a 400 °C ya no cambia el perfil.",
    ),
)


@dataclass(frozen=True)
class Supply:
    """Cation dose delivered while a shutter is open, per Ga monolayer."""

    s_in_per_ga: float = S_IN_PER_GA
    n_ga_well: int = N_GA_WELL
    n_ga_barrier: int = N_GA_BARRIER
    n_wells: int = N_WELLS
    ml_nm: float = ML_NM


SUPPLY = Supply()
