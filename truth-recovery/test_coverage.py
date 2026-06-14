"""Truth-recovery coverage tests for the denominator pooling engine.

Run: python -m unittest truth-recovery/test_coverage.py
 or: python truth-recovery/test_coverage.py
"""
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import run_cell, _hksj_t_ci  # noqa: E402
from engine import fixed_effect, random_effects_dl  # noqa: E402


class TestPoolingTruthRecovery(unittest.TestCase):

    def test_dl_matches_known_reference(self):
        # DL-RE point estimate is a deterministic IV-weighted mean.
        yi = np.array([0.20, 0.50, -0.10, 0.30, 0.40])
        se = np.array([0.20, 0.22, 0.24, 0.17, 0.22])
        r = random_effects_dl(yi, se)
        # Homogeneous -> tau2 == 0 -> DL reduces to FE-IV.
        fe = fixed_effect(yi, se)
        self.assertAlmostEqual(r["mu"], fe["mu"], places=10)
        self.assertGreaterEqual(r["tau2"], 0.0)

    def test_fe_undercovers_under_heterogeneity(self):
        # Fixed-effect ignores tau2 -> severe under-coverage when tau2 > 0.
        r = run_cell(mu=-0.20, tau2=0.05, k=8, scenario="none", n_rep=3000, seed=2)
        self.assertLess(r["fe_wald_cover"], 0.85,
                        f"FE should under-cover, got {r['fe_wald_cover']}")

    def test_dl_wald_undercovers_and_hksj_recovers(self):
        # DL+Wald under-covers at small k; HKSJ (absent in repo) recovers >=~95%.
        r = run_cell(mu=-0.20, tau2=0.05, k=5, scenario="none", n_rep=4000, seed=5)
        self.assertLess(r["dl_wald_cover"], 0.93,
                        f"DL-Wald should under-cover at k=5, got {r['dl_wald_cover']}")
        self.assertGreaterEqual(r["dl_hksj_cover"], 0.93,
                                f"HKSJ should ~recover nominal, got {r['dl_hksj_cover']}")
        self.assertGreaterEqual(r["dl_hksj_cover"] - r["dl_wald_cover"], 0.03,
                                "HKSJ should beat DL-Wald by >=3pp")

    def test_selection_biases_pooled_mu(self):
        # Strong step selection biases mu away from truth; no method undoes it.
        r = run_cell(mu=-0.20, tau2=0.05, k=8, scenario="step_strong",
                     n_rep=3000, seed=3)
        self.assertGreater(abs(r["dl_bias"]), 0.08,
                           f"expected selection bias, got {r['dl_bias']}")
        self.assertLess(r["dl_hksj_cover"], 0.92,
                        f"coverage should degrade under selection, got {r['dl_hksj_cover']}")

    def test_hksj_q_floor(self):
        # Near-homogeneous data -> q_raw < 1 -> floored to 1; CI stays ordered.
        yi = np.array([-0.20, -0.205, -0.195, -0.20, -0.198])
        se = np.array([0.20, 0.20, 0.20, 0.20, 0.20])
        dl = random_effects_dl(yi, se)
        lo, hi, bounded = _hksj_t_ci(yi, se, dl["mu"], dl["tau2"])
        self.assertTrue(bounded, "expected q<1 to be detected/floored")
        self.assertLess(lo, hi, "CI must be ordered")


if __name__ == "__main__":
    unittest.main(verbosity=2)
