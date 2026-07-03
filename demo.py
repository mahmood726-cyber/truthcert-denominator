"""Reproducible end-to-end demo for the Phase-1 engine.

Runs the fast 12-topic smoke suite (2 replications per topic, ~5-10s) and
then evaluates the resulting run against the documented acceptance
targets, printing a summary. This is a worked example of the full
pipeline: config -> run_suite -> topic_metrics.csv -> check_acceptance.

Usage:
    python demo.py                      # smoke config, writes to demo_out/
    python demo.py --config configs/suite_12topics_phase1.json
    python demo.py --out demo_out/mine

The demo output directory (default ``demo_out/``) is gitignored; the demo
never overwrites the curated runs under ``outputs/``.

Exit status mirrors the acceptance check: 0 if all targets pass, 1 if any
target fails, 2 on an error. Note that the fast smoke config uses only 2
replications, so it is expected to be noisier than the full suite and may
not clear every target -- it exists to prove the pipeline runs, not to
certify results.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sim.check_acceptance import _format_report, check_acceptance
from sim.run_suite import run_suite


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the smoke suite and check acceptance targets.")
    parser.add_argument(
        "--config", default="configs/_smoke.json",
        help="Suite config JSON (default: fast 12-topic smoke config)")
    parser.add_argument(
        "--out", default="demo_out",
        help="Output base directory (default: demo_out/, gitignored)")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    if not config_path.exists():
        print(f"ERROR: config not found: {config_path}")
        return 2

    print(f"[1/2] Running suite with config: {config_path}")
    print("-" * 64)
    run_dir = run_suite(str(config_path), args.out)

    print()
    print(f"[2/2] Evaluating acceptance targets for: {run_dir}")
    print("-" * 64)
    try:
        result = check_acceptance(run_dir)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2

    print(_format_report(result))
    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
