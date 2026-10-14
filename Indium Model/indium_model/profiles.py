"""Depth profiles, per-well metrics, and a depth-dependent SIMS blur."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from indium_model.growth import GrowResult
from indium_model.regimes import ML_NM


# Illustrative sputter blur, not a fit to the crater peaks.
# sigma(depth) = 1.6 nm + 0.028 * depth. It is strong enough to widen the
# deepest well, and too crude to be read as the instrument function.
SIMS_SIGMA0_NM = 1.6
SIMS_SIGMA_SLOPE = 0.028


@dataclass(frozen=True)
class DepthProfile:
    """z_nm is measured from the substrate; depth_nm from the surface."""

    z_nm: np.ndarray
    depth_nm: np.ndarray
    x: np.ndarray
    x_sims: np.ndarray


@dataclass(frozen=True)
class WellReport:
    well_index: int
    thickness_nm: float
    x_max: float
    x_mean: float
    incorporated: float
    tail_incorporated: float
    tail_length_nm: float
    sims_x_max: float
    sims_fwhm_nm: float
    sims_peak_depth_nm: float


@dataclass(frozen=True)
class SampleReport:
    sample: str
    region: int
    temperature_c: float
    supplied: float
    incorporated_wells: float
    incorporated_barriers: float
    desorbed: float
    floating: float
    segregation_length_nm: float
    wells: tuple[WellReport, ...]


def _paint(result: GrowResult, dz_nm: float) -> tuple[np.ndarray, np.ndarray]:
    total = sum(layer.thickness_nm for layer in result.layers)
    n_points = int(round(total / dz_nm))
    x = np.zeros(n_points, dtype=float)
    cursor = 0.0
    for layer in result.layers:
        start = int(round(cursor / dz_nm))
        cursor += layer.thickness_nm
        stop = int(round(cursor / dz_nm))
        if stop > start:
            x[start:stop] = layer.x
    z_nm = (np.arange(n_points) + 0.5) * dz_nm
    return z_nm, x


def convolve_sims(
    x: np.ndarray,
    dz_nm: float,
    *,
    sigma0_nm: float = SIMS_SIGMA0_NM,
    slope: float = SIMS_SIGMA_SLOPE,
) -> np.ndarray:
    """Blur ``x`` with a Gaussian whose width grows with depth from the surface.

    ``x[0]`` is the substrate side. Sputtering starts at the last point.
    """
    n_points = x.size
    depth_nm = (n_points - np.arange(n_points) - 0.5) * dz_nm
    blurred = np.empty_like(x)
    for index in range(n_points):
        sigma_nm = sigma0_nm + slope * depth_nm[index]
        half = max(1, int(np.ceil(4.0 * sigma_nm / dz_nm)))
        left = max(0, index - half)
        right = min(n_points, index + half + 1)
        offsets = (np.arange(left, right) - index) * dz_nm
        kernel = np.exp(-0.5 * (offsets / sigma_nm) ** 2)
        kernel /= kernel.sum()
        blurred[index] = np.dot(kernel, x[left:right])
    return blurred


def make_profile(
    result: GrowResult,
    *,
    dz_nm: float = 0.1,
    sigma0_nm: float = SIMS_SIGMA0_NM,
    slope: float = SIMS_SIGMA_SLOPE,
) -> DepthProfile:
    z_nm, x = _paint(result, dz_nm)
    x_sims = convolve_sims(x, dz_nm, sigma0_nm=sigma0_nm, slope=slope)
    depth_nm = z_nm[-1] - z_nm if z_nm.size else z_nm
    # z is the center of each bin, so the surface sits half a bin past the end.
    depth_nm = (z_nm[-1] + 0.5 * dz_nm) - z_nm
    return DepthProfile(z_nm=z_nm, depth_nm=depth_nm, x=x, x_sims=x_sims)


def _fwhm(depth_nm: np.ndarray, values: np.ndarray, peak_index: int) -> float:
    half = 0.5 * values[peak_index]
    if half <= 0.0:
        return 0.0
    left = peak_index
    while left > 0 and values[left] >= half:
        left -= 1
    right = peak_index
    limit = values.size - 1
    while right < limit and values[right] >= half:
        right += 1
    return float(abs(depth_nm[left] - depth_nm[right]))


def _tail_length(incorporated: list[float], ml_nm: float) -> float:
    """Thickness that still contains the first 90% of the barrier In dose."""
    total = sum(incorporated)
    if total <= 0.0:
        return 0.0
    running = 0.0
    for count, dose in enumerate(incorporated, start=1):
        running += dose
        if running >= 0.9 * total:
            return count * ml_nm
    return len(incorporated) * ml_nm


def report(result: GrowResult, profile: DepthProfile) -> SampleReport:
    layers = result.layers
    wells: list[WellReport] = []
    incorporated_wells = 0.0
    incorporated_barriers = 0.0

    well_spans = [index for index, layer in enumerate(layers) if layer.kind == "well"]
    # Group consecutive well layers. Barriers between them carry that well's tail.
    groups: list[tuple[int, int, int]] = []
    start = well_spans[0]
    current = layers[start].well_index
    for offset, layer_index in enumerate(well_spans[1:], start=1):
        if layers[layer_index].well_index != current or layer_index != well_spans[offset - 1] + 1:
            groups.append((current, start, well_spans[offset - 1]))
            start = layer_index
            current = layers[layer_index].well_index
    groups.append((current, start, well_spans[-1]))

    barrier_after: list[list[int]] = []
    for position, (_, _, last) in enumerate(groups):
        nxt = groups[position + 1][1] if position + 1 < len(groups) else len(layers)
        barrier_after.append(
            [index for index in range(last + 1, nxt) if layers[index].kind == "barrier"]
        )

    for (well_index, first, last), barrier_indexes in zip(groups, barrier_after):
        slab = layers[first : last + 1]
        thickness = sum(layer.thickness_nm for layer in slab)
        incorporated = sum(layer.incorporated for layer in slab)
        incorporated_wells += incorporated
        tail = [layers[index].incorporated for index in barrier_indexes]
        tail_dose = sum(tail)
        incorporated_barriers += tail_dose
        # Map the well onto the painted profile by thickness, then read SIMS.
        z_start = sum(layer.thickness_nm for layer in layers[:first])
        z_stop = z_start + thickness
        mask = (profile.z_nm >= z_start) & (profile.z_nm < z_stop + sum(
            layers[index].thickness_nm for index in barrier_indexes
        ))
        window = np.flatnonzero(mask)
        peak_index = int(window[np.argmax(profile.x_sims[window])])
        mean_x = incorporated / (thickness / ML_NM)
        wells.append(
            WellReport(
                well_index=well_index,
                thickness_nm=thickness,
                x_max=max(layer.x for layer in slab),
                x_mean=mean_x,
                incorporated=incorporated,
                tail_incorporated=tail_dose,
                tail_length_nm=_tail_length(tail, ML_NM),
                sims_x_max=float(profile.x_sims[peak_index]),
                sims_fwhm_nm=_fwhm(profile.depth_nm, profile.x_sims, peak_index),
                sims_peak_depth_nm=float(profile.depth_nm[peak_index]),
            )
        )

    return SampleReport(
        sample=result.regime.sample,
        region=result.regime.region,
        temperature_c=result.regime.temperature_c,
        supplied=result.supplied,
        incorporated_wells=incorporated_wells,
        incorporated_barriers=incorporated_barriers,
        desorbed=result.desorbed,
        floating=result.theta_final,
        segregation_length_nm=result.regime.segregation_length_nm,
        wells=tuple(wells),
    )
