"""Pozo de potencial finito con masa efectiva constante."""

import numpy as np
from scipy.optimize import root_scalar


# Constantes físicas (eV, Å, s)
hbar = 6.58211957e-16  # eV·s
c = 3e18  # Å/s
m0 = 5.11e5 / c**2  # eV·s²/Å²


class WellStructure:
    def __init__(self, V_meV: float, mass_m0: float, lp: float):
        self.V_meV = V_meV
        self.mass_m0 = mass_m0
        self.lp = lp

    @property
    def V(self) -> float:
        return self.V_meV * 1e-3

    @property
    def mass(self) -> float:
        return self.mass_m0 * m0

    @property
    def L(self) -> float:
        return self.lp

    @property
    def a(self) -> float:
        return 0.5 * self.L


class BoundState:
    """Un nivel ligado del pozo."""

    def __init__(
        self,
        index: int,
        energy_eV: float,
        parity: str,
        P_barrier: float,
        P_well: float,
    ):
        self.index = index
        self.energy_eV = energy_eV
        self.parity = parity  # "even" | "odd"
        self.P_barrier = P_barrier
        self.P_well = P_well

    @property
    def energy_meV(self) -> float:
        return self.energy_eV * 1e3


class FiniteWell:
    """
    Pozo finito simétrico [-L/2, L/2] con la misma masa efectiva
    en pozo y barrera.

    Resuelve las condiciones:
      pares:   √E tan(k L/2) = √(V-E)
      impares: -√E cot(k L/2) = √(V-E)
    y la probabilidad en la barrera vía normalización.
    """

    def __init__(self, structure):
        if isinstance(structure, dict):
            structure = WellStructure(
            V_meV=float(structure["V_meV"]),
            mass_m0=float(structure["mass_m0"]),
            lp=float(structure["lp"]),
        )
        self.structure = structure
        self.k0 = np.sqrt(2.0 * structure.mass / hbar**2)
        self.lim = (np.pi * hbar) ** 2 / (2.0 * structure.mass * structure.L**2)
        self._states = None

    @property
    def n_max_estimate(self) -> int:
        V, m, L = self.structure.V, self.structure.mass, self.structure.L
        return 1 + int(np.sqrt((2.0 * m * V * L**2) / (np.pi * hbar) ** 2))

    def _f_even(self, E: float) -> float:
        V = self.structure.V
        return np.sqrt(E) * np.tan(self.k0 * self.structure.L * np.sqrt(E) / 2) - np.sqrt(
            V - E
        )

    def _f_odd(self, E: float) -> float:
        V = self.structure.V
        return (
            -np.sqrt(E) / np.tan(self.k0 * self.structure.L * np.sqrt(E) / 2)
            - np.sqrt(V - E)
        )

    def _alpha(self, E: float, even: bool) -> float:
        xi = self.k0 * self.structure.L * np.sqrt(E) / 2
        return 1.0 / np.cos(xi) if even else 1.0 / np.sin(xi)

    def _P_II(self, k_n: float, even: bool) -> float:
        L, a = self.structure.L, self.structure.a
        term = np.sin(2.0 * k_n * a) / (2.0 * k_n)
        return L / 2 + term if even else L / 2 - term

    def _barrier_probability(self, E: float, even: bool) -> float:
        V = self.structure.V
        k_n = self.k0 * np.sqrt(E)
        kappa_n = self.k0 * np.sqrt(V - E)
        P_I = 1.0 / kappa_n
        alpha = self._alpha(E, even)
        P_II = self._P_II(k_n, even)
        B2 = 1.0 / (P_I + alpha**2 * P_II)
        return  100*round(float(B2 * P_I), 3)

    def _bracket(self, i: int) -> tuple[float, float] | None:
        V = self.structure.V
        if i == 0:
            Emin = 1e-12
            Emax = min(0.9999 * self.lim, 0.9999 * V)
        else:
            Emin = (i**2) * self.lim + 1e-10
            Emax = min(0.999 * ((i + 1) ** 2) * self.lim, 0.999 * V)
        if Emin >= Emax or Emin >= V:
            return None
        return Emin, Emax

    def solve(self, *, force: bool = False) -> list[BoundState]:
        """Calcula niveles ligados y probabilidades. Cachea el resultado."""
        if self._states is not None and not force:
            return self._states

        states: list[BoundState] = []
        for i in range(self.n_max_estimate):
            bracket = self._bracket(i)
            if bracket is None:
                break

            even = i % 2 == 0
            f = self._f_even if even else self._f_odd
            try:
                E = float(root_scalar(f, bracket=list(bracket)).root)
            except ValueError:
                break

            P_b = self._barrier_probability(E, even)
            states.append(
                BoundState(
                    index=i,
                    energy_eV=E,
                    parity="even" if even else "odd",
                    P_barrier=P_b,
                    P_well=1.0 - P_b,
                )
            )

        self._states = states
        return states

    def energies_meV(self) -> list[float]:
        return [s.energy_meV for s in self.solve()]

    def barrier_probabilities(self) -> list[float]:
        return [s.P_barrier for s in self.solve()]

