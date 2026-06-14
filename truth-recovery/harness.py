"""harness.py — Truth-recovery coverage harness for the TruthCert-Denominator
pooling engine.

Inject a KNOWN (mu, tau2) random-effects model (+ optional publication
selection), then measure how often the engine's OWN pooling intervals cover the
true mu. The engine here exposes ONLY Wald (z) CIs:
  - fixed_effect()      (FE-IV, Wald)
  - random_effects_dl() (DL-RE, Wald)
No HKSJ is implemented in this repo, so we ALSO compute a Hartung-Knapp t_{k-1}
CI on top of the engine's OWN DL tau2 estimate (using tau2 + mu reported by the
engine) to quantify exactly how much coverage HKSJ would recover. This is the
KEY truth-recovery question for this engine.

All point estimates / tau2 come from the repo's own meta_fixed functions.
"""
import os
import sys

import numpy as np
from scipy.stats import t as student_t

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dgp import generate  # noqa: E402
from engine import fixed_effect, random_effects_dl  # noqa: E402


def _hksj_t_ci(yi, se, mu, tau2, alpha=0.05):
    """Hartung-Knapp-Sidik-Jonkman CI from the engine's own (mu, tau2).

    q = (1/(k-1)) * sum w_i (y_i - mu)^2, floored to 1 (Cochrane small-k rule),
    se_HK = sqrt(q / sum w_i), CI = mu +/- t_{k-1} * se_HK.
    """
    yi = np.asarray(yi, float)
    se = np.asarray(se, float)
    k = len(yi)
    w = 1.0 / (se ** 2 + tau2)
    q_raw = float(np.sum(w * (yi - mu) ** 2) / (k - 1)) if k > 1 else float("nan")
    q = max(1.0, q_raw)
    se_hk = np.sqrt(q / np.sum(w))
    tcrit = student_t.ppf(1 - alpha / 2, k - 1)
    return mu - tcrit * se_hk, mu + tcrit * se_hk, q_raw < 1.0


def run_cell(mu=-0.20, tau2=0.05, k=8, scenario="none", n_rep=4000, seed=12345):
    rng = np.random.Generator(np.random.PCG64(seed))
    acc = {
        "fe_wald": 0, "dl_wald": 0, "dl_hksj": 0,
        "dl_bias": 0.0, "fe_width": 0.0, "dl_width": 0.0, "hksj_width": 0.0,
        "q_bounded": 0,
    }
    degenerate = 0
    for _ in range(n_rep):
        yi, vi, info = generate(mu, tau2, k, scenario, rng)
        if info["degenerate"]:
            degenerate += 1
        se = np.sqrt(vi)

        fe = fixed_effect(yi, se)
        dl = random_effects_dl(yi, se)

        if fe["ci_low"] <= mu <= fe["ci_high"]:
            acc["fe_wald"] += 1
        if dl["ci_low"] <= mu <= dl["ci_high"]:
            acc["dl_wald"] += 1
        acc["dl_bias"] += dl["mu"] - mu
        acc["fe_width"] += fe["ci_high"] - fe["ci_low"]
        acc["dl_width"] += dl["ci_high"] - dl["ci_low"]

        lo, hi, bounded = _hksj_t_ci(yi, se, dl["mu"], dl["tau2"])
        if lo <= mu <= hi:
            acc["dl_hksj"] += 1
        acc["hksj_width"] += hi - lo
        if bounded:
            acc["q_bounded"] += 1

    return {
        "mu": mu, "tau2": tau2, "k": k, "scenario": scenario,
        "n_rep": n_rep, "degenerate": degenerate,
        "fe_wald_cover": acc["fe_wald"] / n_rep,
        "dl_wald_cover": acc["dl_wald"] / n_rep,
        "dl_hksj_cover": acc["dl_hksj"] / n_rep,
        "dl_bias": acc["dl_bias"] / n_rep,
        "fe_width": acc["fe_width"] / n_rep,
        "dl_width": acc["dl_width"] / n_rep,
        "hksj_width": acc["hksj_width"] / n_rep,
        "q_bounded_frac": acc["q_bounded"] / n_rep,
    }


def main():
    cells = [
        dict(k=5, tau2=0.05, scenario="none"),
        dict(k=8, tau2=0.05, scenario="none"),
        dict(k=20, tau2=0.05, scenario="none"),
        dict(k=5, tau2=0.10, scenario="none"),
        dict(k=8, tau2=0.05, scenario="step_strong"),
        dict(k=8, tau2=0.05, scenario="copas_strong"),
    ]
    print("mu=-0.20 (logRR) | 95% target | n_rep=4000\n")
    print("k  tau2  scenario      |  FE-Wald  DL-Wald  DL-HKSJ   bias    qBnd%")
    print("-" * 72)
    for c in cells:
        r = run_cell(mu=-0.20, **c)
        print(
            f"{str(c['k']):<2} {c['tau2']:.2f}  {c['scenario']:<13} | "
            f"{r['fe_wald_cover']*100:7.1f}  {r['dl_wald_cover']*100:6.1f}  "
            f"{r['dl_hksj_cover']*100:6.1f}  {r['dl_bias']:7.4f}  "
            f"{r['q_bounded_frac']*100:5.0f}"
        )
    print("-" * 72)


if __name__ == "__main__":
    main()
