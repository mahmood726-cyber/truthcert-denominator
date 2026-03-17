"""Test posterior validity: sums to 1, non-negative, constraint di >= dn."""

import sys
import os

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sim.config_schema import TopicConfig
from sim.seed import make_rng
from sim.generate_truth import generate_truth
from sim.generate_trials import generate_trials
from sim.oracle import apply_oracle_shift
from sim.selection import apply_selection
from sim.observed_world import build_observed_world
from sim.meta_fixed import fixed_effect
from sim.fit_delta import fit_delta


def _make_test_topic() -> TopicConfig:
    return TopicConfig(**{
        "topic_id": "T_post",
        "label": "Posterior Validity",
        "node_grid": {
            "phenotypes": ["P1", "P2"],
            "classes": ["C1"],
            "endpoints": ["E1", "E2"]
        },
        "trial_count": {
            "n_trials_total": 40,
            "min_trials_per_node": 3,
            "dispersion": 1.0
        },
        "sponsor": {"industry_rate": 0.6},
        "truth": {
            "mu_global": -0.12,
            "node_effect_structure": "smooth",
            "mu_node_sd": 0.12,
            "tau_base": 0.10,
            "tau_sd": 0.03,
            "discontinuity": {"enabled": False}
        },
        "baseline_risk": {
            "control_event_rate": {"E1": [0.08, 0.20], "E2": [0.10, 0.30]}
        },
        "sample_size": {
            "n_per_arm": [60, 300],
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
                "base_rate_by_endpoint": {"E1": 0.9, "E2": 0.9},
                "coef": {"industry": 0.0, "signif_benefit": 0.0, "se": 0.0}
            },
            "silent_shift_delta": {
                "enabled": True,
                "delta_by_endpoint": {
                    "E1": {"industry": 0.05, "nonindustry": 0.02},
                    "E2": {"industry": 0.04, "nonindustry": 0.02}
                },
                "constraint": "industry_ge_nonindustry",
                "multiplier_by_endpoint": {"E1": 1.0, "E2": 1.0}
            }
        },
        "engine": {
            "delta_bayes": {
                "grid": {"di_max": 0.3, "dn_max": 0.2, "step": 0.03},
                "prior": {"type": "half_normal",
                          "sigma_industry": 0.2,
                          "sigma_nonindustry": 0.15},
                "temperature_T": 1.0,
                "grouping": "class"
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


def test_posterior_validity():
    """Posterior sums to 1, all probs >= 0, constraint di >= dn enforced."""
    topic = _make_test_topic()
    rng = make_rng(42, topic.topic_id, 0)

    node_params = generate_truth(topic, rng)
    trials_df = generate_trials(topic, node_params, rng)
    trials_df = apply_oracle_shift(trials_df, topic, rng)
    trials_df = apply_selection(trials_df, topic, rng)
    observed_effects, node_denoms = build_observed_world(trials_df, topic)

    observed_metas = {}
    for nid, grp in observed_effects.groupby("node_id"):
        observed_metas[nid] = fixed_effect(
            grp["logRR"].values, grp["se"].values)

    delta_posteriors = fit_delta(observed_metas, node_denoms, topic)

    grid_di = delta_posteriors["E1"]["grid_di"]
    grid_dn = delta_posteriors["E1"]["grid_dn"]

    for ep, dp in delta_posteriors.items():
        post = dp["posterior_2d"]

        # All probabilities >= 0
        assert np.all(post >= -1e-15), \
            f"Negative posterior mass in endpoint {ep}"

        # Sums to 1
        total = post.sum()
        assert abs(total - 1.0) < 1e-6, \
            f"Posterior sum={total} for endpoint {ep}"

        # Constraint: di >= dn (no mass where di < dn)
        for i in range(len(grid_di)):
            for j in range(len(grid_dn)):
                if grid_di[i] < grid_dn[j] - 1e-12:
                    assert post[i, j] < 1e-15, \
                        f"Mass at di={grid_di[i]} < dn={grid_dn[j]} in {ep}"

    print("PASS: test_posterior_validity")


if __name__ == "__main__":
    test_posterior_validity()
