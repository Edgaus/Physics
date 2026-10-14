"""Conservation, the Muraki limit, and the three-region ordering."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from indium_model.growth import grow_stack, incorporated_closed_form, split_monolayer
from indium_model.profiles import make_profile, report
from indium_model.regimes import REGIMES, SUPPLY


class SplitTests(unittest.TestCase):
    def test_probabilities_sum_to_one(self) -> None:
        for regime in REGIMES:
            total = regime.incorporate + regime.segregate + regime.desorb
            self.assertAlmostEqual(total, 1.0)

    def test_closed_form_matches_recursion(self) -> None:
        regime = REGIMES[1]
        theta = 0.0
        supply = SUPPLY.s_in_per_ga
        for step in range(1, 40):
            incorporated, theta, _ = split_monolayer(theta, supply, regime)
            self.assertAlmostEqual(
                incorporated,
                incorporated_closed_form(step, supply, regime),
                places=12,
            )
        for barrier_step in range(1, 25):
            incorporated, theta, _ = split_monolayer(theta, 0.0, regime)
            self.assertAlmostEqual(
                incorporated,
                incorporated_closed_form(39, supply, regime, barrier_step=barrier_step),
                places=12,
            )

    def test_muraki_limit_without_desorption(self) -> None:
        """D = 0 recovers i_n = s (1 - R^n), Muraki's dose."""
        from indium_model.regimes import Regime

        regime = Regime(
            sample="muraki",
            region=0,
            temperature_c=0.0,
            incorporate=0.2,
            segregate=0.8,
            desorb=0.0,
            sims_peaks=(0.0, 0.0, 0.0),
            note="",
        )
        supply = 0.05
        theta = 0.0
        for step in range(1, 15):
            incorporated, theta, desorbed = split_monolayer(theta, supply, regime)
            self.assertAlmostEqual(desorbed, 0.0)
            self.assertAlmostEqual(incorporated, supply * (1.0 - 0.8**step))


class StackTests(unittest.TestCase):
    def test_indium_is_conserved(self) -> None:
        for regime in REGIMES:
            result = grow_stack(regime, SUPPLY)
            accounted = result.incorporated + result.desorbed + result.theta_final
            self.assertAlmostEqual(accounted, result.supplied, places=9)

    def test_three_regions_separate(self) -> None:
        reports = []
        for regime in REGIMES:
            result = grow_stack(regime, SUPPLY)
            reports.append(report(result, make_profile(result)))
        by_sample = {item.sample: item for item in reports}
        hot = by_sample["MME914"]
        mid = by_sample["MME925"]
        cold = by_sample["MME931"]
        self.assertGreater(mid.segregation_length_nm, 2.0 * hot.segregation_length_nm)
        self.assertLess(cold.segregation_length_nm, 1.0)
        self.assertGreater(mid.incorporated_barriers, 2.0 * hot.incorporated_barriers)
        self.assertLess(cold.incorporated_barriers, hot.incorporated_barriers)
        self.assertGreater(cold.wells[0].x_max, 0.24)
        self.assertLess(hot.wells[0].x_max, 0.12)
        self.assertLess(abs(hot.wells[0].x_max - mid.wells[0].x_max), 0.04)
        self.assertGreater(cold.wells[0].thickness_nm, hot.wells[0].thickness_nm)
        # The tail rides toward the surface: the barrier grown before a well
        # stays empty, and the barrier grown after it carries the shoulder.
        mid_result = grow_stack(REGIMES[1], SUPPLY)
        layers = mid_result.layers
        well = [index for index, layer in enumerate(layers) if layer.well_index == 2]
        self.assertLess(layers[well[0] - 1].x, 1e-3)
        self.assertGreater(layers[well[-1] + 1].x, 0.05)
        # 40 nm of GaN between wells drains the floating layer.
        for item in reports:
            doses = [well.incorporated for well in item.wells]
            self.assertLess(abs(doses[0] - doses[1]) / doses[0], 1e-3)
            self.assertLess(abs(doses[1] - doses[2]) / doses[1], 1e-3)


if __name__ == "__main__":
    unittest.main()
