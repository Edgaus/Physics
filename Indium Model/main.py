"""Build the three-region indium profiles and write figures plus tables.

Run from this directory:

    python main.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from indium_model.export import write_profiles, write_summary
from indium_model.figures import plot_balance, plot_regions, plot_stacks, plot_trends
from indium_model.growth import grow_stack
from indium_model.profiles import make_profile, report
from indium_model.regimes import REGIMES, SUPPLY


def main() -> None:
    figure_dir = ROOT / "figures"
    data_dir = ROOT / "data" / "processed"
    figure_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for regime in REGIMES:
        result = grow_stack(regime, SUPPLY)
        profile = make_profile(result)
        rows.append((result, profile, report(result, profile)))

    plot_regions(rows, figure_dir / "tres_regiones.png")
    plot_stacks(rows, figure_dir / "perfiles_sims.png")
    plot_balance([item[2] for item in rows], figure_dir / "balance_indio.png")
    plot_trends([item[2] for item in rows], figure_dir / "tendencia_temperatura.png")
    write_summary([item[2] for item in rows], data_dir / "resumen.csv")
    write_profiles([(item[0], item[1]) for item in rows], data_dir / "perfiles.csv")

    print(f"Suministro s = {SUPPLY.s_in_per_ga:.4f} átomos de In por átomo de Ga")
    print(f"Pozos: {SUPPLY.n_ga_well} ML de Ga; barreras: {SUPPLY.n_ga_barrier} ML de Ga")
    print()
    header = (
        f"{'muestra':<8} {'T':>6} {'λ nm':>7} {'x max':>7} {'ancho':>7} "
        f"{'pozo':>7} {'cola':>7} {'desorb':>7}"
    )
    print(header)
    for _, _, sample in rows:
        well = sample.wells[-1]
        print(
            f"{sample.sample:<8} {sample.temperature_c:6.0f} "
            f"{sample.segregation_length_nm:7.2f} {100 * well.x_max:6.1f}% "
            f"{well.thickness_nm:6.1f} "
            f"{100 * sample.incorporated_wells / sample.supplied:6.1f}% "
            f"{100 * sample.incorporated_barriers / sample.supplied:6.1f}% "
            f"{100 * sample.desorbed / sample.supplied:6.1f}%"
        )
    print()
    print("SIMS convolucionado (FWHM y x máximo) frente al cráter experimental:")
    for result, _, sample in rows:
        print(f"  {sample.sample}")
        for well, crater in zip(sample.wells, result.regime.sims_peaks):
            print(
                f"    QW{well.well_index}  modelo {100 * well.sims_x_max:5.1f}%  "
                f"FWHM {well.sims_fwhm_nm:5.1f} nm  cráter {100 * crater:5.1f}%  "
                f"profundidad {well.sims_peak_depth_nm:5.1f} nm"
            )


if __name__ == "__main__":
    main()
