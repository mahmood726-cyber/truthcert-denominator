"""Main simulation suite runner.

Usage:
    python -m sim.run_suite --config configs/suite_12topics_phase1.json --out outputs/runs
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from .config_schema import SimulationConfig, TopicConfig
from .decision import decide, decide_denom_only
from .fit_delta import fit_delta
from .generate_trials import generate_trials
from .generate_truth import generate_truth
from .meta_fixed import fixed_effect, random_effects_dl
from .observed_world import build_observed_world
from .oracle import apply_oracle_shift, oracle_meta_per_node
from .propagate_engine import propagate
from .score import compute_scores
from .seed import make_rng
from .selection import apply_selection


def run_topic(topic_cfg: TopicConfig, seed_master: int,
              n_reps: int) -> list:
    """Run all replications for a single topic.

    Returns list of per-replication result dicts.
    """
    rep_results = []

    for rep in range(n_reps):
        rng = make_rng(seed_master, topic_cfg.topic_id, rep)

        # 1. Truth
        node_params = generate_truth(topic_cfg, rng)

        # 2. Trials
        trials_df = generate_trials(topic_cfg, node_params, rng)

        # 3. Oracle shift
        trials_df = apply_oracle_shift(trials_df, topic_cfg, rng)

        # 4. Selection
        trials_df = apply_selection(trials_df, topic_cfg, rng)

        # 5. Observed world
        observed_effects, node_denoms = build_observed_world(
            trials_df, topic_cfg)

        # 6. Classic meta (published only, RE for fair comparison)
        classic_metas = {}
        pub_obs = observed_effects[observed_effects["has_pub"]]
        for nid, grp in pub_obs.groupby("node_id"):
            classic_metas[nid] = random_effects_dl(
                grp["logRR"].values, grp["se"].values)

        # 7. Observed meta (all effects with endpoint data, RE)
        observed_metas = {}
        for nid, grp in observed_effects.groupby("node_id"):
            observed_metas[nid] = random_effects_dl(
                grp["logRR"].values, grp["se"].values)

        # 8. Fit delta
        delta_posteriors = fit_delta(observed_metas, node_denoms, topic_cfg)

        # 9. Propagate
        propagated = propagate(
            observed_metas, node_denoms, delta_posteriors, topic_cfg, rng,
            observed_effects_df=observed_effects)

        # 10. Oracle meta (all trials, oracle outcomes)
        oracle_metas = oracle_meta_per_node(trials_df)

        # 11. Decisions
        denom_dict = {}
        for _, row in node_denoms.iterrows():
            denom_dict[row["node_id"]] = row.to_dict()

        decisions = {}
        denom_only_decisions = {}
        for nid in set(list(propagated) + list(oracle_metas)):
            dd = denom_dict.get(nid, {})
            if nid in propagated:
                decisions[nid] = decide(propagated[nid], dd, topic_cfg)
            else:
                decisions[nid] = {"label": "Insufficient",
                                  "reason": "no propagated estimate"}
            denom_only_decisions[nid] = decide_denom_only(dd)

        # Assemble node results
        all_nodes = set(list(observed_metas) + list(oracle_metas)
                        + list(propagated))
        node_results = {}
        for nid in all_nodes:
            node_results[nid] = {
                "observed_meta": observed_metas.get(nid, {}),
                "classic_meta": classic_metas.get(nid, {}),
                "oracle_meta": oracle_metas.get(nid, {}),
                "engine_propagated": propagated.get(nid, {}),
                "engine_decision": decisions.get(nid, {}),
                "denom_only_decision": denom_only_decisions.get(nid, {}),
                "node_denom": denom_dict.get(nid, {}),
            }

        rep_results.append({
            "topic_id": topic_cfg.topic_id,
            "rep": rep,
            "node_results": node_results,
            "delta_posteriors": {
                ep: {"summary": dp["summary"]}
                for ep, dp in delta_posteriors.items()
            },
        })

    return rep_results


def run_suite(config_path: str, out_dir: str) -> Path:
    """Run the full simulation suite and write outputs."""
    with open(config_path, "r") as f:
        raw = json.load(f)
    cfg = SimulationConfig(**raw)

    # Hash config content (not path) for cross-machine reproducibility
    config_bytes = json.dumps(raw, sort_keys=True).encode()
    run_id = hashlib.sha256(
        f"{cfg.seed_master}:".encode() + config_bytes).hexdigest()[:12]
    run_dir = Path(out_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Run ID:       {run_id}")
    print(f"Output:       {run_dir}")
    print(f"Topics:       {len(cfg.topics)}")
    print(f"Replications: {cfg.n_replications}")
    print()

    all_topic_rows = []
    all_delta_rows = []
    g_cfr, g_efr, g_cov = [], [], []

    for topic_cfg in cfg.topics:
        t0 = time.time()
        print(f"  [{topic_cfg.topic_id}] {topic_cfg.label} ...", end=" ",
              flush=True)

        rep_results = run_topic(topic_cfg, cfg.seed_master,
                                cfg.n_replications)
        scores = compute_scores(rep_results, topic_cfg)
        tm = scores["topic_metrics"]
        dm = scores["delta_metrics"]

        tm["topic_id"] = topic_cfg.topic_id
        tm["label"] = topic_cfg.label
        all_topic_rows.append(tm)

        for ep, ep_dm in dm.items():
            ep_dm["topic_id"] = topic_cfg.topic_id
            ep_dm["endpoint"] = ep
            all_delta_rows.append(ep_dm)

        g_cfr.append(tm.get("classic_false_reassurance_mean", np.nan))
        g_efr.append(tm.get("engine_false_reassurance_mean", np.nan))
        g_cov.append(tm.get("coverage_engine_mean", np.nan))

        elapsed = time.time() - t0
        print(f"({elapsed:.1f}s) FR_cl={g_cfr[-1]:.3f} "
              f"FR_eng={g_efr[-1]:.3f} cov={g_cov[-1]:.3f}")

    # Write CSVs
    pd.DataFrame(all_topic_rows).to_csv(
        run_dir / "topic_metrics.csv", index=False)
    pd.DataFrame(all_delta_rows).to_csv(
        run_dir / "delta_metrics.csv", index=False)

    # Global metrics
    fr_cl = float(np.nanmean(g_cfr))
    fr_en = float(np.nanmean(g_efr))
    cov = float(np.nanmean(g_cov))
    fr_red = (fr_cl - fr_en) / fr_cl * 100 if fr_cl > 0 else 0.0

    global_row = {
        "classic_false_reassurance_global": fr_cl,
        "engine_false_reassurance_global": fr_en,
        "coverage_global": cov,
        "fr_reduction_pct": fr_red,
        "n_topics": len(cfg.topics),
        "n_replications": cfg.n_replications,
    }
    pd.DataFrame([global_row]).to_csv(
        run_dir / "global_metrics.csv", index=False)

    # Manifest
    manifest = {
        "run_id": run_id,
        "config_path": str(config_path),
        "schema_version": cfg.schema_version,
        "seed_master": cfg.seed_master,
        "n_replications": cfg.n_replications,
        "n_topics": len(cfg.topics),
        "outputs": {
            "topic_metrics": "topic_metrics.csv",
            "delta_metrics": "delta_metrics.csv",
            "global_metrics": "global_metrics.csv",
        },
    }
    with open(run_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print()
    print("=" * 64)
    print(f"GLOBAL  (topics={len(cfg.topics)}, reps={cfg.n_replications})")
    print(f"  Classic FR:    {fr_cl:.4f}")
    print(f"  Engine FR:     {fr_en:.4f}")
    print(f"  FR reduction:  {fr_red:.1f}%")
    print(f"  Coverage:      {cov:.4f}")
    print("=" * 64)

    return run_dir


def main():
    parser = argparse.ArgumentParser(
        description="TruthCert Denominator-First Phase-1 Simulation Suite")
    parser.add_argument("--config", required=True,
                        help="Path to suite config JSON")
    parser.add_argument("--out", default="outputs/runs",
                        help="Output base directory")
    args = parser.parse_args()
    run_suite(args.config, args.out)


if __name__ == "__main__":
    main()
