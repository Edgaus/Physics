"""Monolayer balance for indium segregation and desorption.

Muraki's 1992 profile is the special case D = 0 (no desorption). Each Ga
monolayer offers the floating population plus the In that arrives during
that monolayer to three channels::

    available = theta + s
    incorporated = I * available
    theta_next = R * available
    desorbed = D * available
    I + R + D = 1

``s`` is In atoms delivered per Ga atom. Ga is taken to stick. The crystal
grown in that step is ``1 + incorporated`` cation monolayers, so a well that
keeps its In is thicker than a well that loses it. Composition of the step::

    x = incorporated / (1 + incorporated)

Inside a well of constant dose the incorporated amount has the closed form

    i_n = alpha * s * (1 - R**n),  alpha = I / (I + D)

and the barrier grown afterwards decays as

    i_{N+k} = alpha * s * (1 - R**N) * R**k
"""

from __future__ import annotations

from dataclasses import dataclass

from indium_model.regimes import Regime, Supply


@dataclass(frozen=True)
class Layer:
    x: float
    thickness_nm: float
    kind: str
    well_index: int | None
    incorporated: float
    desorbed: float
    theta_after: float


@dataclass(frozen=True)
class GrowResult:
    regime: Regime
    layers: tuple[Layer, ...]
    supplied: float
    theta_final: float

    @property
    def incorporated(self) -> float:
        return sum(layer.incorporated for layer in self.layers)

    @property
    def desorbed(self) -> float:
        return sum(layer.desorbed for layer in self.layers)


def split_monolayer(
    theta: float, supply: float, regime: Regime
) -> tuple[float, float, float]:
    """Split one monolayer. Returns incorporated, new theta, desorbed."""
    available = theta + supply
    incorporated = regime.incorporate * available
    theta_next = regime.segregate * available
    desorbed = regime.desorb * available
    return incorporated, theta_next, desorbed


def incorporated_closed_form(
    n: int, supply: float, regime: Regime, *, barrier_step: int | None = None
) -> float:
    """Incorporated In dose after ``n`` well monolayers.

    If ``barrier_step`` is k >= 1, return the dose in barrier monolayer
    N+k instead of the dose in well monolayer n.
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    alpha = regime.alpha
    segregate = regime.segregate
    if barrier_step is None:
        if n == 0:
            return 0.0
        return alpha * supply * (1.0 - segregate**n)
    if barrier_step < 1:
        raise ValueError("barrier_step starts at 1")
    return alpha * supply * (1.0 - segregate**n) * segregate**barrier_step


def grow_stack(regime: Regime, supply: Supply = Supply()) -> GrowResult:
    """Grow barrier / well / barrier / ... / well / barrier from the substrate."""
    theta = 0.0
    layers: list[Layer] = []
    supplied = 0.0

    def emit(steps: int, dose: float, kind: str, well_index: int | None) -> None:
        nonlocal theta, supplied
        for _ in range(steps):
            incorporated, theta, desorbed = split_monolayer(theta, dose, regime)
            cations = 1.0 + incorporated
            layers.append(
                Layer(
                    x=incorporated / cations,
                    thickness_nm=cations * supply.ml_nm,
                    kind=kind,
                    well_index=well_index,
                    incorporated=incorporated,
                    desorbed=desorbed,
                    theta_after=theta,
                )
            )
            supplied += dose

    emit(supply.n_ga_barrier, 0.0, "barrier", None)
    for index in range(1, supply.n_wells + 1):
        emit(supply.n_ga_well, supply.s_in_per_ga, "well", index)
        emit(supply.n_ga_barrier, 0.0, "barrier", None)

    return GrowResult(
        regime=regime,
        layers=tuple(layers),
        supplied=supplied,
        theta_final=theta,
    )
