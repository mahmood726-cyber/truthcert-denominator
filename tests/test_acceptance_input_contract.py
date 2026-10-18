"""Software fixtures for malformed run metrics; no scientific outputs changed."""
import subprocess
import sys

import pandas as pd
import pytest

from sim.check_acceptance import check_acceptance


@pytest.fixture
def valid_metrics(tmp_path):
    rows = [{"topic_id": topic, "classic_false_reassurance_mean": 0.5,
             "engine_false_reassurance_mean": 0.2, "coverage_engine_mean": 0.95,
             "convergence_mean_abs_diff": 0.01}
            for topic in ["T01", "T02", "T03", "T08", "T11"]]
    return tmp_path, pd.DataFrame(rows)


def write_metrics(case):
    path, df = case
    df.to_csv(path / "topic_metrics.csv", index=False)
    return path


def test_duplicate_topic_cannot_hide_failure(valid_metrics):
    path, df = valid_metrics
    failed = df.iloc[[0]].copy()
    failed["coverage_engine_mean"] = 0.1
    write_metrics((path, pd.concat([failed, df], ignore_index=True)))
    with pytest.raises(ValueError, match="topic_id"):
        check_acceptance(path)


@pytest.mark.parametrize("topic", [None, "", "   "])
def test_empty_topic_rejected(valid_metrics, topic):
    path, df = valid_metrics
    df.loc[0, "topic_id"] = topic
    with pytest.raises(ValueError, match="topic_id"):
        check_acceptance(write_metrics((path, df)))


@pytest.mark.parametrize("column,value", [
    ("classic_false_reassurance_mean", -0.1),
    ("engine_false_reassurance_mean", -0.1),
    ("coverage_engine_mean", 1.2),
    ("convergence_mean_abs_diff", -1),
    ("convergence_mean_abs_diff", float("inf")),
])
def test_invalid_metrics_rejected(valid_metrics, column, value):
    path, df = valid_metrics
    df[column] = value
    with pytest.raises(ValueError, match=column):
        check_acceptance(write_metrics((path, df)))


@pytest.mark.parametrize("kwargs", [
    {"high_silence_topics": []}, {"moderate_topics": []},
    {"high_silence_topics": ["T03", "T03"]},
    {"coverage_min": -1}, {"coverage_min": float("nan")},
    {"fr_reduction_pct": -1}, {"fr_reduction_pct": 101},
    {"convergence_max": float("inf")}, {"convergence_max": -1},
])
def test_invalid_target_configuration_rejected(valid_metrics, kwargs):
    with pytest.raises(ValueError):
        check_acceptance(write_metrics(valid_metrics), **kwargs)


def test_missing_convergence_remains_explicit_no_data(valid_metrics):
    path, df = valid_metrics
    df["convergence_mean_abs_diff"] = float("nan")
    result = check_acceptance(write_metrics((path, df)))
    assert not result["overall_pass"]
    assert result["targets"][2]["details"]["status"] == "no_data"


def test_invalid_run_cli_exits_with_error(valid_metrics):
    path, df = valid_metrics
    df["coverage_engine_mean"] = 2.0
    write_metrics((path, df))
    result = subprocess.run([sys.executable, "-m", "sim.check_acceptance",
                             "--run", str(path)], capture_output=True, text=True,
                            timeout=30)
    assert result.returncode == 2
    assert "coverage_engine_mean" in result.stdout
    assert "OVERALL: PASS" not in result.stdout
