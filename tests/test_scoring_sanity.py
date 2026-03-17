"""Test scoring sanity: in a clean setting (delta~0, low missingness),
classic and engine false reassurance should both be low, and the engine
should not be worse than classic.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sim.config_schema import TopicConfig
from sim.run_suite import run_topic
from sim.score import compute_scores


def _make_clean_topic() -> TopicConfig:
    """Near-zero delta, very low missingness -> minimal bias."""
    return TopicConfig(**{
        "topic_id": "T_clean",
        "label": "Sanity: Clean Setting",
        "node_grid": {
            "phenotypes": ["P1"],
            "classes": ["C1"],
            "endpoints": ["E1"]
        },
        "trial_count": {
            "n_trials_total": 30,
            "min_trials_per_node": 10,
            "dispersion": 1.0
        },
        "sponsor": {"industry_rate": 0.5},
        "truth": {
            "mu_global": -0.20,
            "node_effect_structure": "smooth",
            "mu_node_sd": 0.05,
            "tau_base": 0.06,
            "tau_sd": 0.02,
            "discontinuity": {"enabled": False}
        },
        "baseline_risk": {
            "control_event_rate": {"E1": [0.10, 0.25]}
        },
        "sample_size": {
            "n_per_arm": [100, 400],
            "size_distribution": "uniform",
            "size_sigma": 0.5
        },
        "missingness": {
            "results_posting": {
                "base_rate": 0.95,
                "coef": {"industry": 0.0, "signif_benefit": 0.0,
                         "signif_harm": 0.0, "se": 0.0, "post2015": 0.0}
            },
            "publication": {
                "base_rate": 0.90,
                "coef": {"industry": 0.0, "signif_benefit": 0.0,
                         "signif_harm": 0.0, "se": 0.0, "post2015": 0.0,
                         "results_posted": 0.0}
            },
            "endpoint_reporting": {
                "enabled": False,
                "base_rate_by_endpoint": {"E1": 0.99},
                "coef": {"industry": 0.0, "signif_benefit": 0.0, "se": 0.0}
            },
            "silent_shift_delta": {
                "enabled": True,
                "delta_by_endpoint": {
                    "E1": {"industry": 0.001, "nonindustry": 0.0005}
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


def test_scoring_sanity():
    """In clean settings, both FR should be low and engine <= classic."""
    topic = _make_clean_topic()
    seed = 42
    n_reps = 10

    rep_results = run_topic(topic, seed, n_reps)
    scores = compute_scores(rep_results, topic)
    tm = scores["topic_metrics"]

    cfr = tm["classic_false_reassurance_mean"]
    efr = tm["engine_false_reassurance_mean"]
    cov = tm["coverage_engine_mean"]

    print(f"  Classic FR:  {cfr:.4f}")
    print(f"  Engine FR:   {efr:.4f}")
    print(f"  Coverage:    {cov:.4f}")

    # In a clean setting with strong benefit, FR should be low
    assert cfr < 0.30, f"Classic FR too high in clean setting: {cfr}"
    assert efr < 0.30, f"Engine FR too high in clean setting: {efr}"

    # Engine should not be dramatically worse than classic
    assert efr <= cfr + 0.10, \
        f"Engine FR ({efr}) much worse than classic ({cfr})"

    # Coverage should be reasonable
    assert cov > 0.50, f"Coverage too low: {cov}"

    print("PASS: test_scoring_sanity")


if __name__ == "__main__":
    test_scoring_sanity()
