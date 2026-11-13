"""Write profile and summary tables."""

from __future__ import annotations

import csv
from pathlib import Path

from indium_model.growth import GrowResult
from indium_model.profiles import DepthProfile, SampleReport
from indium_model.regimes import REGIMES


def write_summary(reports: list[SampleReport], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "sample",
        "region",
        "temperature_c",
        "segregation_length_nm",
        "fraction_in_wells",
        "fraction_in_barriers",
        "fraction_desorbed",
        "fraction_floating",
        "well",
        "well_thickness_nm",
        "x_max",
        "x_mean",
        "tail_incorporated_ml",
        "tail_length_90_nm",
        "sims_x_max",
        "sims_fwhm_nm",
        "sims_peak_depth_nm",
        "sims_crater",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        peaks = {regime.sample: regime.sims_peaks for regime in REGIMES}
        for report in reports:
            for well in report.wells:
                crater = peaks[report.sample][well.well_index - 1]
                writer.writerow(
                    {
                        "sample": report.sample,
                        "region": report.region,
                        "temperature_c": f"{report.temperature_c:.0f}",
                        "segregation_length_nm": f"{report.segregation_length_nm:.3f}",
                        "fraction_in_wells": f"{report.incorporated_wells / report.supplied:.4f}",
                        "fraction_in_barriers": f"{report.incorporated_barriers / report.supplied:.4f}",
                        "fraction_desorbed": f"{report.desorbed / report.supplied:.4f}",
                        "fraction_floating": f"{report.floating / report.supplied:.4f}",
                        "well": well.well_index,
                        "well_thickness_nm": f"{well.thickness_nm:.2f}",
                        "x_max": f"{well.x_max:.4f}",
                        "x_mean": f"{well.x_mean:.4f}",
                        "tail_incorporated_ml": f"{well.tail_incorporated:.3f}",
                        "tail_length_90_nm": f"{well.tail_length_nm:.2f}",
                        "sims_x_max": f"{well.sims_x_max:.4f}",
                        "sims_fwhm_nm": f"{well.sims_fwhm_nm:.2f}",
                        "sims_peak_depth_nm": f"{well.sims_peak_depth_nm:.2f}",
                        "sims_crater": f"{crater:.4f}",
                    }
                )


def write_profiles(
    rows: list[tuple[GrowResult, DepthProfile]],
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["sample", "region", "temperature_c", "depth_nm", "x_true", "x_sims"]
        )
        for result, profile in rows:
            regime = result.regime
            for depth, true, sims in zip(profile.depth_nm, profile.x, profile.x_sims):
                writer.writerow(
                    [
                        regime.sample,
                        regime.region,
                        f"{regime.temperature_c:.0f}",
                        f"{depth:.3f}",
                        f"{true:.6f}",
                        f"{sims:.6f}",
                    ]
                )
