 #!/usr/bin/env python3
"""Theoretical XRD peak positions from Bragg's law.
2θ is computed from λ (Kα) and the lattice parameter(s):
    nλ = 2 d_hkl sinθ
    2θ = 2 arcsin( n λ / (2 d_hkl) )
Cubic:      d_hkl = a / sqrt(h² + k² + l²)
Hexagonal:  1/d²  = (4/3)(h² + hk + k²)/a² + l²/c²
Examples
--------
    python xrd_peaks.py --material 3C-SiC
    python xrd_peaks.py --material 3C-SiC --a 4.3596 --radiation CuKa1
    python xrd_peaks.py --material Si --lambda 1.5406 --tmax 110
    python xrd_peaks.py --material c-AlN --a 4.38 --radiation CuKa
    python xrd_peaks.py --material w-AlN --a 3.111 --c 4.981
    python xrd_peaks.py --structure zincblende --a 4.36 --radiation CuKa
"""
from __future__ import annotations
import argparse
import math
from dataclasses import dataclass
from typing import Iterator, List, Optional, Sequence, Tuple
# ---------------------------------------------------------------------------
# Common X-ray wavelengths (Å). Cu Kα (weighted) ≈ 2/3 Kα1 + 1/3 Kα2.
# ---------------------------------------------------------------------------
RADIATION: dict[str, float] = {
    "CuKa": 1.54184,
    "CuKa1": 1.540598,
    "CuKa2": 1.544426,
    "CuKb": 1.392218,
    "CoKa": 1.79026,
    "CoKa1": 1.788996,
    "CoKa2": 1.792850,
    "MoKa": 0.71073,
    "MoKa1": 0.709317,
    "MoKa2": 0.713607,
    "CrKa": 2.29100,
    "CrKa1": 2.28970,
    "CrKa2": 2.293606,
}
# Default lattice parameters (Å) for materials used with 3C-SiC / c-AlN work.
MATERIALS: dict[str, dict] = {
    "3C-SiC": {
        "structure": "zincblende",
        "a": 4.3596,
        "note": "cubic SiC, F-43m; ICDD 29-1129",
    },
    "Si": {
        "structure": "diamond",
        "a": 5.4309,
        "note": "diamond cubic, Fd-3m",
    },
    "c-AlN": {
        "structure": "zincblende",
        "a": 4.38,
        "note": "cubic AlN (zincblende); a varies with strain (~4.37 to 4.45 A)",
    },
    "w-AlN": {
        "structure": "wurtzite",
        "a": 3.111,
        "c": 4.981,
        "note": "hexagonal AlN, P6_3mc",
    },
    "2H-SiC": {
        "structure": "wurtzite",
        "a": 3.076,
        "c": 5.048,
        "note": "wurtzite SiC",
    },
    "4H-SiC": {
        "structure": "hexagonal",
        "a": 3.073,
        "c": 10.053,
        "note": "hexagonal 4H-SiC (all hkl allowed in this simple model)",
    },
    "6H-SiC": {
        "structure": "hexagonal",
        "a": 3.073,
        "c": 15.117,
        "note": "hexagonal 6H-SiC (all hkl allowed in this simple model)",
    },
}
@dataclass(frozen=True)
class Peak:
    h: int
    k: int
    l: int
    d: float
    two_theta: float
    n: int = 1
    @property
    def hkl(self) -> str:
        return f"({self.h}{self.k}{self.l})"
    @property
    def multiplicity_index(self) -> int:
        return self.h * self.h + self.k * self.k + self.l * self.l
def d_cubic(a: float, h: int, k: int, l: int) -> float:
    n2 = h * h + k * k + l * l
    if n2 == 0:
        raise ValueError("000 is not a reflection")
    return a / math.sqrt(n2)
def d_hexagonal(a: float, c: float, h: int, k: int, l: int) -> float:
    planar = h * h + h * k + k * k
    if planar == 0 and l == 0:
        raise ValueError("000 is not a reflection")
    inv_d2 = (4.0 / 3.0) * planar / (a * a) + (l * l) / (c * c)
    return 1.0 / math.sqrt(inv_d2)
def bragg_two_theta(d: float, wavelength: float, order: int = 1) -> Optional[float]:
    """Return 2θ in degrees, or None if the reflection is inaccessible."""
    arg = (order * wavelength) / (2.0 * d)
    if arg < 0.0 or arg > 1.0:
        return None
    return 2.0 * math.degrees(math.asin(arg))
def _cubic_indices(h_max: int) -> Iterator[Tuple[int, int, int]]:
    for h in range(h_max + 1):
        for k in range(h_max + 1):
            for l in range(h_max + 1):
                if h == 0 and k == 0 and l == 0:
                    continue
                yield h, k, l
def allowed_cubic(h: int, k: int, l: int, structure: str) -> bool:
    """Kinematic selection rules (unmixed indices = FCC translation)."""
    all_even = (h % 2 == 0) and (k % 2 == 0) and (l % 2 == 0)
    all_odd = (h % 2 == 1) and (k % 2 == 1) and (l % 2 == 1)
    if structure in {"primitive", "simple"}:
        return True
    if not (all_even or all_odd):
        return False
    if structure in {"fcc", "zincblende", "3C"}:
        # Zincblende: (200), (222), ... are allowed (f_A ≠ f_B).
        return True
    if structure == "diamond":
        # Diamond: extra extinction when h+k+l = 4n+2 (e.g. 200, 222).
        return (h + k + l) % 4 != 2
    raise ValueError(f"Unknown cubic structure: {structure}")
def allowed_wurtzite(h: int, k: int, l: int) -> bool:
    """P6_3mc: 00l and hhl require l even."""
    if h == 0 and k == 0 and l % 2 != 0:
        return False
    if h == k and l % 2 != 0:
        return False
    return True
def _unique_cubic_family(h: int, k: int, l: int) -> Tuple[int, int, int]:
    return tuple(sorted((abs(h), abs(k), abs(l)), reverse=True))  # type: ignore[return-value]
def theoretical_peaks(
    *,
    structure: str,
    wavelength: float,
    a: float,
    c: Optional[float] = None,
    two_theta_max: float = 110.0,
    two_theta_min: float = 5.0,
    h_max: int = 8,
    order: int = 1,
) -> List[Peak]:
    """Compute unique (hkl) families below two_theta_max."""
    structure = structure.lower()
    peaks: List[Peak] = []
    seen: set[Tuple[int, int, int]] = set()

    if structure in {"zincblende", "diamond", "fcc", "primitive", "simple", "3c"}:
        for h, k, l in _cubic_indices(h_max):
            if not allowed_cubic(h, k, l, structure):
                continue
            fam = _unique_cubic_family(h, k, l)
            if fam in seen:
                continue
            d = d_cubic(a, *fam)
            tt = bragg_two_theta(d, wavelength, order)
            if tt is None or tt < two_theta_min or tt > two_theta_max:
                continue
            seen.add(fam)
            peaks.append(Peak(fam[0], fam[1], fam[2], d, tt, order))
    elif structure in {"wurtzite", "hexagonal"}:
        if c is None:
            raise ValueError("Hexagonal/wurtzite structures need lattice parameter c")
        for h in range(h_max + 1):
            for k in range(h_max + 1):
                for l in range(h_max + 1):
                    if h == 0 and k == 0 and l == 0:
                        continue
                    if structure == "wurtzite" and not allowed_wurtzite(h, k, l):
                        continue
                    d = d_hexagonal(a, c, h, k, l)
                    tt = bragg_two_theta(d, wavelength, order)
                    if tt is None or tt < two_theta_min or tt > two_theta_max:
                        continue
                    peaks.append(Peak(h, k, l, d, tt, order))
    else:
        raise ValueError(f"Unknown structure: {structure}")

    peaks.sort(key=lambda p: (p.two_theta, p.h, p.k, p.l))
    return peaks


def format_table(
    peaks: Sequence[Peak],
    *,
    material: str,
    wavelength: float,
    radiation: str,
    a: float,
    c: Optional[float],
) -> str:
    header = [
        f"Material     : {material}",
        f"Radiation    : {radiation}   lambda = {wavelength:.6f} A",
        f"Lattice a    : {a:.5f} A",
    ]
    if c is not None:
        header.append(f"Lattice c    : {c:.5f} A")
    header.append(f"Bragg order n: {peaks[0].n if peaks else 1}")
    header.append("")
    header.append(f"{'hkl':<10} {'d (A)':>10} {'2theta (deg)':>12}")
    header.append("-" * 34)
    lines = header
    for p in peaks:
        lines.append(f"{p.hkl:<10} {p.d:10.5f} {p.two_theta:12.4f}")
    if not peaks:
        lines.append("(no reflections in the requested 2theta window)")
    return "\n".join(lines)


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Theoretical XRD 2θ positions from Kα wavelength and lattice parameter(s)."
    )
    p.add_argument(
        "--material",
        choices=sorted(MATERIALS),
        help="Preset material (lattice + selection rules). Override with --a / --c.",
    )
    p.add_argument(
        "--structure",
        choices=["zincblende", "diamond", "fcc", "primitive", "wurtzite", "hexagonal"],
        help="Crystal system if you do not use a preset material.",
    )
    p.add_argument("--a", type=float, help="Lattice parameter a in Å")
    p.add_argument("--c", type=float, help="Lattice parameter c in Å (hexagonal)")
    g = p.add_mutually_exclusive_group()
    g.add_argument(
        "--radiation",
        default="CuKa",
        choices=sorted(RADIATION),
        help="Anode / line (default: CuKa weighted average)",
    )
    g.add_argument(
        "--lambda",
        dest="wavelength",
        type=float,
        help="Custom wavelength in Å (overrides --radiation)",
    )
    p.add_argument(
        "--both-ka",
        action="store_true",
        help="Print Cu Kα1 and Kα2 tables (useful to see the split)",
    )
    p.add_argument("--tmin", type=float, default=5.0, help="Min 2θ in degrees")
    p.add_argument("--tmax", type=float, default=110.0, help="Max 2θ in degrees")
    p.add_argument("--hmax", type=int, default=8, help="Max |h|,|k|,|l| to generate")
    p.add_argument("--csv", action="store_true", help="CSV output instead of a table")
    return p.parse_args(argv)


def _resolve_crystal(args: argparse.Namespace) -> Tuple[str, str, float, Optional[float]]:
    if args.material:
        spec = MATERIALS[args.material]
        structure = args.structure or spec["structure"]
        a = args.a if args.a is not None else spec["a"]
        c = args.c if args.c is not None else spec.get("c")
        return args.material, structure, a, c
    if args.structure is None or args.a is None:
        raise SystemExit("Provide --material, or both --structure and --a")
    if args.structure in {"wurtzite", "hexagonal"} and args.c is None:
        raise SystemExit("Hexagonal/wurtzite needs --c")
    return "custom", args.structure, args.a, args.c


def _wavelengths(args: argparse.Namespace) -> List[Tuple[str, float]]:
    if args.wavelength is not None:
        return [("custom", args.wavelength)]
    if args.both_ka:
        return [("CuKa1", RADIATION["CuKa1"]), ("CuKa2", RADIATION["CuKa2"])]
    return [(args.radiation, RADIATION[args.radiation])]


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = _parse_args(argv)
    material, structure, a, c = _resolve_crystal(args)

    for name, wl in _wavelengths(args):
        peaks = theoretical_peaks(
            structure=structure,
            wavelength=wl,
            a=a,
            c=c,
            two_theta_max=args.tmax,
            two_theta_min=args.tmin,
            h_max=args.hmax,
        )
        if args.csv:
            print("material,radiation,lambda_A,a_A,c_A,h,k,l,d_A,two_theta_deg")
            c_out = "" if c is None else f"{c:.5f}"
            for p in peaks:
                print(
                    f"{material},{name},{wl:.6f},{a:.5f},{c_out},"
                    f"{p.h},{p.k},{p.l},{p.d:.6f},{p.two_theta:.6f}"
                )
        else:
            print(
                format_table(
                    peaks,
                    material=material,
                    wavelength=wl,
                    radiation=name,
                    a=a,
                    c=c,
                )
            )
            if args.material:
                print(f"\nNote: {MATERIALS[args.material]['note']}")
            print()


if __name__ == "__main__":
    main()
