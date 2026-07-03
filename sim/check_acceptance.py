"""Evaluate a completed run against the Phase-1 acceptance targets.

The three acceptance targets documented in the README are:

  1. Engine reduces classic false reassurance (FR) by >= 30% in the
     high-silence topics (default T03, T08).
  2. Coverage of the engine 95% CrI is >= 0.90 in moderate settings
     (default T01, T02, T11).
  3. Convergence: mean |engine - classic| < 0.05 when the silent rate is
     low (< 15%), aggregated over the whole suite.

This module reads the ``topic_metrics.csv`` produced by
``sim.run_suite`` and reports PASS/FAIL per target. It exits with a
non-zero status if any target fails, so it can be used as a CI gate.

Usage:
    python -m sim.check_acceptance --run outputs/runs/<run_id>
    python -m sim.check_acceptance --run outputs/runs/<run_id> --json
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

# Default target thresholds and the topics they apply to. These mirror the
# README "Acceptance Targets" section; they can be overridden via CLI flags.
DEFAULT_FR_REDUCTION_PCT = 30.0
DEFAULT_HIGH_SILENCE_TOPICS = ["T03", "T08"]
DEFAULT_COVERAGE_MIN = 0.90
DEFAULT_MODERATE_TOPICS = ["T01", "T02", "T11"]
DEFAULT_CONVERGENCE_MAX = 0.05


def _finite(x) -> bool:
    try:
        return x is not None and math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def _load_topic_metrics(run_dir: Path) -> pd.DataFrame:
    """Load ``topic_metrics.csv`` from a run directory.

    Raises FileNotFoundError if the run directory or CSV is missing, and
    ValueError if the CSV is empty or missing required columns.
    """
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory does not exist: {run_dir}")
    csv_path = run_dir / "topic_metrics.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"topic_metrics.csv not found in {run_dir}")

    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError(f"topic_metrics.csv is empty: {csv_path}")

    required = {
        "topic_id",
        "classic_false_reassurance_mean",
        "engine_false_reassurance_mean",
        "coverage_engine_mean",
        "convergence_mean_abs_diff",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"topic_metrics.csv missing required columns: "
            f"{sorted(missing)} (found: {sorted(df.columns)})")
    return df


def check_acceptance(
    run_dir,
    fr_reduction_pct: float = DEFAULT_FR_REDUCTION_PCT,
    high_silence_topics: Optional[List[str]] = None,
    coverage_min: float = DEFAULT_COVERAGE_MIN,
    moderate_topics: Optional[List[str]] = None,
    convergence_max: float = DEFAULT_CONVERGENCE_MAX,
) -> Dict:
    """Evaluate the acceptance targets for a completed run.

    Args:
        run_dir: path to a run directory containing ``topic_metrics.csv``.
        fr_reduction_pct: minimum required classic->engine FR reduction (%).
        high_silence_topics: topic IDs the FR-reduction target applies to.
        coverage_min: minimum required engine coverage.
        moderate_topics: topic IDs the coverage target applies to.
        convergence_max: maximum allowed mean |engine - classic|.

    Returns a dict with an ``overall_pass`` flag and a ``targets`` list of
    per-target result dicts. Topics named in a target's scope that are
    absent from the run are reported as ``missing`` and fail that target.
    """
    high_silence_topics = list(high_silence_topics
                               if high_silence_topics is not None
                               else DEFAULT_HIGH_SILENCE_TOPICS)
    moderate_topics = list(moderate_topics
                           if moderate_topics is not None
                           else DEFAULT_MODERATE_TOPICS)

    df = _load_topic_metrics(Path(run_dir))
    by_topic = {row["topic_id"]: row for _, row in df.iterrows()}

    targets: List[Dict] = []

    # ── Target 1: FR reduction in high-silence topics ──────────────────
    t1_details = []
    t1_pass = True
    for tid in high_silence_topics:
        row = by_topic.get(tid)
        if row is None:
            t1_details.append({"topic_id": tid, "status": "missing"})
            t1_pass = False
            continue
        c = row["classic_false_reassurance_mean"]
        e = row["engine_false_reassurance_mean"]
        if not _finite(c) or not _finite(e):
            t1_details.append({"topic_id": tid, "status": "undefined",
                               "classic_fr": c, "engine_fr": e})
            t1_pass = False
            continue
        c, e = float(c), float(e)
        if c <= 0.0:
            # No classic false reassurance to reduce. If the engine also
            # has none, the target is vacuously satisfied; otherwise the
            # engine is strictly worse and the target fails.
            if e <= 0.0:
                reduction = 0.0
                ok = True
            else:
                reduction = float("-inf")
                ok = False
        else:
            reduction = (c - e) / c * 100.0
            ok = reduction >= fr_reduction_pct
        t1_pass = t1_pass and ok
        t1_details.append({
            "topic_id": tid, "status": "ok",
            "classic_fr": c, "engine_fr": e,
            "fr_reduction_pct": (None if reduction == float("-inf")
                                 else round(reduction, 2)),
            "pass": ok,
        })
    targets.append({
        "name": "fr_reduction_high_silence",
        "description": (f">= {fr_reduction_pct:.0f}% classic->engine FR "
                        f"reduction in {high_silence_topics}"),
        "pass": t1_pass,
        "details": t1_details,
    })

    # ── Target 2: coverage in moderate settings ────────────────────────
    t2_details = []
    t2_pass = True
    for tid in moderate_topics:
        row = by_topic.get(tid)
        if row is None:
            t2_details.append({"topic_id": tid, "status": "missing"})
            t2_pass = False
            continue
        cov = row["coverage_engine_mean"]
        if not _finite(cov):
            t2_details.append({"topic_id": tid, "status": "undefined",
                               "coverage": cov})
            t2_pass = False
            continue
        cov = float(cov)
        ok = cov >= coverage_min
        t2_pass = t2_pass and ok
        t2_details.append({"topic_id": tid, "status": "ok",
                           "coverage": round(cov, 4), "pass": ok})
    targets.append({
        "name": "coverage_moderate",
        "description": (f"engine coverage >= {coverage_min:.2f} in "
                        f"{moderate_topics}"),
        "pass": t2_pass,
        "details": t2_details,
    })

    # ── Target 3: convergence when silent rate is low ──────────────────
    conv_vals = [float(v) for v in df["convergence_mean_abs_diff"].tolist()
                 if _finite(v)]
    if conv_vals:
        conv_mean = sum(conv_vals) / len(conv_vals)
        t3_pass = conv_mean < convergence_max
        t3_details = {"status": "ok",
                      "convergence_mean_abs_diff": round(conv_mean, 4),
                      "n_topics_with_low_silence": len(conv_vals)}
    else:
        # No topic had any low-silence nodes to measure convergence on.
        conv_mean = None
        t3_pass = False
        t3_details = {"status": "no_data",
                      "reason": "no topic produced a low-silence "
                                "convergence measurement"}
    targets.append({
        "name": "convergence_low_silence",
        "description": (f"mean |engine - classic| < {convergence_max} when "
                        f"silent rate < 15%"),
        "pass": t3_pass,
        "details": t3_details,
    })

    overall = all(t["pass"] for t in targets)
    return {
        "run_dir": str(run_dir),
        "overall_pass": overall,
        "targets": targets,
    }


def _format_report(result: Dict) -> str:
    lines = []
    lines.append(f"Acceptance check for run: {result['run_dir']}")
    lines.append("=" * 64)
    for t in result["targets"]:
        status = "PASS" if t["pass"] else "FAIL"
        lines.append(f"[{status}] {t['name']}")
        lines.append(f"        {t['description']}")
        det = t["details"]
        if isinstance(det, list):
            for d in det:
                lines.append(f"          - {d}")
        else:
            lines.append(f"          {det}")
    lines.append("=" * 64)
    overall = "PASS" if result["overall_pass"] else "FAIL"
    lines.append(f"OVERALL: {overall}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate a run against Phase-1 acceptance targets.")
    parser.add_argument("--run", required=True,
                        help="Run directory containing topic_metrics.csv")
    parser.add_argument("--fr-reduction-pct", type=float,
                        default=DEFAULT_FR_REDUCTION_PCT,
                        help="Min classic->engine FR reduction percent")
    parser.add_argument("--coverage-min", type=float,
                        default=DEFAULT_COVERAGE_MIN,
                        help="Min engine coverage in moderate topics")
    parser.add_argument("--convergence-max", type=float,
                        default=DEFAULT_CONVERGENCE_MAX,
                        help="Max mean |engine - classic| in low-silence")
    parser.add_argument("--high-silence-topics", nargs="+",
                        default=None,
                        help="Topic IDs for the FR-reduction target")
    parser.add_argument("--moderate-topics", nargs="+", default=None,
                        help="Topic IDs for the coverage target")
    parser.add_argument("--json", action="store_true",
                        help="Emit machine-readable JSON instead of text")
    args = parser.parse_args(argv)

    try:
        result = check_acceptance(
            args.run,
            fr_reduction_pct=args.fr_reduction_pct,
            high_silence_topics=args.high_silence_topics,
            coverage_min=args.coverage_min,
            moderate_topics=args.moderate_topics,
            convergence_max=args.convergence_max,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(_format_report(result))

    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
