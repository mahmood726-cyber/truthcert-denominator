"""Test deterministic reproducibility: same seed -> same output."""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sim.config_schema import TopicConfig
from sim.run_suite import run_topic


def _make_test_topic() -> TopicConfig:
    return TopicConfig(**{
        "topic_id": "T_repro",
        "label": "Reproducibility Test",
        "node_grid": {
            "phenotypes": ["P1"],
            "classes": ["C1"],
            "endpoints": ["E1"]
        },
        "trial_count": {
            "n_trials_total": 20,
            "min_trials_per_node": 5,
            "dispersion": 1.0
        },
        "sponsor": {"industry_rate": 0.5},
        "truth": {
            "mu_global": -0.15,
            "node_effect_structure": "smooth",
            "mu_node_sd": 0.10,
            "tau_base": 0.08,
            "tau_sd": 0.02,
            "discontinuity": {"enabled": False}
        },
        "baseline_risk": {
            "control_event_rate": {"E1": [0.1, 0.3]}
        },
        "sample_size": {
            "n_per_arm": [50, 200],
            "size_distribution": "uniform",
            "size_sigma": 0.5
        },
        "missingness": {
            "results_posting": {
                "base_rate": 0.70,
                "coef": {"industry": 0.2, "signif_benefit": 0.3,
                         "signif_harm": -0.2, "se": -0.1, "post2015": 0.2}
            },
            "publication": {
                "base_rate": 0.60,
                "coef": {"industry": 0.1, "signif_benefit": 0.5,
                         "signif_harm": 0.2, "se": -0.3, "post2015": 0.1,
                         "results_posted": 0.3}
            },
            "endpoint_reporting": {
                "enabled": False,
                "base_rate_by_endpoint": {"E1": 0.9},
                "coef": {"industry": 0.1, "signif_benefit": 0.2, "se": -0.1}
            },
            "silent_shift_delta": {
                "enabled": True,
                "delta_by_endpoint": {
                    "E1": {"industry": 0.05, "nonindustry": 0.02}
                },
                "constraint": "industry_ge_nonindustry",
                "multiplier_by_endpoint": {"E1": 1.0}
            }
        },
        "engine": {
            "delta_bayes": {
                "grid": {"di_max": 0.3, "dn_max": 0.2, "step": 0.05},
                "prior": {"type": "half_normal",
                          "sigma_industry": 0.2,
                          "sigma_nonindustry": 0.15},
                "temperature_T": 1.0,
                "grouping": "endpoint"
            },
            "propagation": {
                "n_posterior_samples": 500,
                "include_mu_obs_uncertainty": True
            },
            "decision_rule": {
                "benefit_threshold": 1.0,
                "recommend": {"p_benefit": 0.80, "upper": 1.0,
                              "silent_rate_max": 0.50},
                "consider": {"p_benefit": 0.60, "p_harm": 0.20,
                             "silent_rate_max": 0.70},
                "research": {"silent_rate_min": 0.40}
            },
            "ablation_modes": ["denom_only", "delta_only"]
        }
    })


def test_reproducibility():
    """Two runs with identical seed produce identical results."""
    topic = _make_test_topic()
    seed = 42
    n_reps = 2

    results1 = run_topic(topic, seed, n_reps)
    results2 = run_topic(topic, seed, n_reps)

    for i in range(n_reps):
        r1 = results1[i]
        r2 = results2[i]

        for nid in r1["node_results"]:
            n1 = r1["node_results"][nid]
            n2 = r2["node_results"][nid]

            # Oracle meta must match exactly
            om1 = n1["oracle_meta"]
            om2 = n2["oracle_meta"]
            for key in ("mu", "se", "ci_low", "ci_high", "k"):
                v1, v2 = om1.get(key), om2.get(key)
                if v1 is None:
                    assert v2 is None, f"Oracle mismatch ({key})"
                elif math.isnan(v1):
                    assert math.isnan(v2), f"Oracle NaN mismatch ({key})"
                else:
                    assert abs(v1 - v2) < 1e-12, \
                        f"Oracle mismatch rep={i} node={nid} {key}: {v1} vs {v2}"

            # Engine propagated
            ep1 = n1["engine_propagated"]
            ep2 = n2["engine_propagated"]
            for key in ("mu_median", "mu_cri_low", "mu_cri_high"):
                v1, v2 = ep1.get(key), ep2.get(key)
                if v1 is not None and v2 is not None:
                    if not (math.isnan(v1) and math.isnan(v2)):
                        assert abs(v1 - v2) < 1e-10, \
                            f"Propagation mismatch rep={i} node={nid} {key}"

    print("PASS: test_reproducibility")


if __name__ == "__main__":
    test_reproducibility()
