"""Tests for sim.check_acceptance.

These tests build small synthetic ``topic_metrics.csv`` files in a temp
directory and assert the acceptance evaluator classifies them correctly.
They do not depend on any stored simulation output and never alter
scientific results.
"""

import os
import sys
import tempfile

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sim.check_acceptance import check_acceptance  # noqa: E402


def _write_run(tmpdir, rows):
    """Write a topic_metrics.csv with the given list-of-dict rows."""
    pd.DataFrame(rows).to_csv(
        os.path.join(tmpdir, "topic_metrics.csv"), index=False)
    return tmpdir


def _row(topic_id, classic_fr, engine_fr, coverage, conv):
    return {
        "topic_id": topic_id,
        "classic_false_reassurance_mean": classic_fr,
        "engine_false_reassurance_mean": engine_fr,
        "coverage_engine_mean": coverage,
        "convergence_mean_abs_diff": conv,
        "label": topic_id,
        "n_replications": 10,
    }


def test_all_targets_pass():
    """A run that clears every threshold reports overall_pass=True."""
    with tempfile.TemporaryDirectory() as d:
        rows = [
            # High-silence topics: 40% FR reduction (0.5 -> 0.3).
            _row("T03", 0.50, 0.30, 0.95, 0.01),
            _row("T08", 0.40, 0.24, 0.95, 0.01),
            # Moderate topics: coverage >= 0.90.
            _row("T01", 0.0, 0.0, 0.95, 0.02),
            _row("T02", 0.0, 0.0, 0.92, 0.02),
            _row("T11", 0.0, 0.0, 0.90, 0.02),
        ]
        _write_run(d, rows)
        result = check_acceptance(d)

    assert result["overall_pass"] is True, result
    names = {t["name"]: t["pass"] for t in result["targets"]}
    assert names["fr_reduction_high_silence"] is True
    assert names["coverage_moderate"] is True
    assert names["convergence_low_silence"] is True
    print("PASS: test_all_targets_pass")


def test_fr_reduction_insufficient_fails():
    """Only a 10% FR reduction fails the >=30% FR target."""
    with tempfile.TemporaryDirectory() as d:
        rows = [
            _row("T03", 0.50, 0.45, 0.95, 0.01),   # 10% reduction
            _row("T08", 0.40, 0.36, 0.95, 0.01),   # 10% reduction
            _row("T01", 0.0, 0.0, 0.95, 0.02),
            _row("T02", 0.0, 0.0, 0.95, 0.02),
            _row("T11", 0.0, 0.0, 0.95, 0.02),
        ]
        _write_run(d, rows)
        result = check_acceptance(d)

    fr = next(t for t in result["targets"]
              if t["name"] == "fr_reduction_high_silence")
    assert fr["pass"] is False
    assert result["overall_pass"] is False
    print("PASS: test_fr_reduction_insufficient_fails")


def test_low_coverage_fails():
    """Coverage below 0.90 in a moderate topic fails the coverage target."""
    with tempfile.TemporaryDirectory() as d:
        rows = [
            _row("T03", 0.50, 0.30, 0.95, 0.01),
            _row("T08", 0.40, 0.24, 0.95, 0.01),
            _row("T01", 0.0, 0.0, 0.80, 0.02),   # below 0.90
            _row("T02", 0.0, 0.0, 0.95, 0.02),
            _row("T11", 0.0, 0.0, 0.95, 0.02),
        ]
        _write_run(d, rows)
        result = check_acceptance(d)

    cov = next(t for t in result["targets"]
               if t["name"] == "coverage_moderate")
    assert cov["pass"] is False
    assert result["overall_pass"] is False
    print("PASS: test_low_coverage_fails")


def test_convergence_too_high_fails():
    """Mean |engine - classic| >= 0.05 fails the convergence target."""
    with tempfile.TemporaryDirectory() as d:
        rows = [
            _row("T03", 0.50, 0.30, 0.95, 0.09),
            _row("T08", 0.40, 0.24, 0.95, 0.09),
            _row("T01", 0.0, 0.0, 0.95, 0.09),
            _row("T02", 0.0, 0.0, 0.95, 0.09),
            _row("T11", 0.0, 0.0, 0.95, 0.09),
        ]
        _write_run(d, rows)
        result = check_acceptance(d)

    conv = next(t for t in result["targets"]
                if t["name"] == "convergence_low_silence")
    assert conv["pass"] is False
    print("PASS: test_convergence_too_high_fails")


def test_missing_topic_fails_gracefully():
    """A target topic absent from the run is reported missing and fails."""
    with tempfile.TemporaryDirectory() as d:
        rows = [
            _row("T03", 0.50, 0.30, 0.95, 0.01),
            # T08 deliberately omitted.
            _row("T01", 0.0, 0.0, 0.95, 0.02),
            _row("T02", 0.0, 0.0, 0.95, 0.02),
            _row("T11", 0.0, 0.0, 0.95, 0.02),
        ]
        _write_run(d, rows)
        result = check_acceptance(d)

    fr = next(t for t in result["targets"]
              if t["name"] == "fr_reduction_high_silence")
    assert fr["pass"] is False
    statuses = {d_["topic_id"]: d_["status"] for d_ in fr["details"]}
    assert statuses.get("T08") == "missing"
    print("PASS: test_missing_topic_fails_gracefully")


def test_missing_csv_raises():
    """Pointing at a directory without topic_metrics.csv raises."""
    with tempfile.TemporaryDirectory() as d:
        try:
            check_acceptance(d)
        except FileNotFoundError:
            print("PASS: test_missing_csv_raises")
            return
        raise AssertionError("expected FileNotFoundError")


def test_zero_classic_fr_engine_zero_passes():
    """When classic FR is 0 and engine FR is also 0, target 1 is vacuously
    satisfied (no false reassurance to reduce, engine no worse)."""
    with tempfile.TemporaryDirectory() as d:
        rows = [
            _row("T03", 0.0, 0.0, 0.95, 0.01),
            _row("T08", 0.0, 0.0, 0.95, 0.01),
            _row("T01", 0.0, 0.0, 0.95, 0.02),
            _row("T02", 0.0, 0.0, 0.95, 0.02),
            _row("T11", 0.0, 0.0, 0.95, 0.02),
        ]
        _write_run(d, rows)
        result = check_acceptance(d)

    fr = next(t for t in result["targets"]
              if t["name"] == "fr_reduction_high_silence")
    assert fr["pass"] is True, fr
    print("PASS: test_zero_classic_fr_engine_zero_passes")


if __name__ == "__main__":
    test_all_targets_pass()
    test_fr_reduction_insufficient_fails()
    test_low_coverage_fails()
    test_convergence_too_high_fails()
    test_missing_topic_fails_gracefully()
    test_missing_csv_raises()
    test_zero_classic_fr_engine_zero_passes()
    print("All check_acceptance tests passed.")
