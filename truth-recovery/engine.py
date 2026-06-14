"""engine.py — VERBATIM re-export of the TruthCert-Denominator pooling core.

The pure pairwise meta-analysis pooling estimators live in sim/meta_fixed.py:
  - fixed_effect()      : inverse-variance fixed-effect pooling + Wald CI
  - random_effects_dl() : DerSimonian-Laird random-effects + Wald CI
  - i_squared()         : Cochran-Q I^2

The TruthCert denominator/delta governance + Bayesian propagation overlay is
intentionally NOT imported here; this file isolates the underlying pooling
estimator so its truth-recovery (coverage of the true mu) can be measured.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim.meta_fixed import fixed_effect, random_effects_dl, i_squared  # noqa: E402

__all__ = ["fixed_effect", "random_effects_dl", "i_squared"]
