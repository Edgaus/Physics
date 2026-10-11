"""Presión en Torr escrita como en las hojas, sin redondeo binario."""

from __future__ import annotations

from dataclasses import dataclass

_SUPER = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


@dataclass(frozen=True)
class Torr:
    """Mantisa tal como está escrita (``"4.2"``, ``"2.93"``) y exponente decimal."""

    mantissa: str
    exponent: int

    def as_float(self) -> float:
        return float(self.mantissa) * 10.0 ** self.exponent

    def __str__(self) -> str:
        exponent = f"{self.exponent:+d}".translate(_SUPER).replace("⁺", "")
        return f"{self.mantissa}×10{exponent}"


def flow_percent_to_sccm(percent: float) -> float:
    """La libreta anota el flujo en por ciento.

    La hoja no da la equivalencia con sccm, así que esta conversión no existe.
    """

    raise ValueError(
        f"El flujo {percent} % de la libreta no tiene equivalencia a sccm en la hoja."
    )
