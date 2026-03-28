# TruthCert Denominator-First Engine: reviewer rerun manifest

This manifest is the shortest reviewer-facing rerun path for the local software package. It lists the files that should be sufficient to recreate one worked example, inspect saved outputs, and verify that the manuscript claims remain bounded to what the repository actually demonstrates.

## Reviewer Entry Points
- Project directory: `C:\Models\truthcert-denominator-phase1`.
- Preferred documentation start points: `README.md`, `f1000_artifacts/tutorial_walkthrough.md`.
- Detected public repository root: `https://github.com/mahmood726-cyber/truthcert-denominator`.
- Detected public source snapshot: Fixed public commit snapshot available at `https://github.com/mahmood726-cyber/truthcert-denominator/tree/1ab7a8f9e5bb1c18294c8c4dafaaf9476644293b`.
- Detected public archive record: No project-specific DOI or Zenodo record URL was detected locally; archive registration pending.
- Environment capture files: `requirements.txt`.
- Validation/test artifacts: `f1000_artifacts/validation_summary.md`, `tests/test_posterior_validity.py`, `tests/test_reproducibility.py`, `tests/test_scoring_sanity.py`.

## Worked Example Inputs
- Manuscript-named example paths: `configs/suite_12topics_phase1.json` for the packaged simulation suite; `outputs/runs/` for manifest and metric outputs; `README.md` for the engine design and acceptance targets; f1000_artifacts/example_dataset.csv.
- Auto-detected sample/example files: `f1000_artifacts/example_dataset.csv`.

## Expected Outputs To Inspect
- Topic-level false reassurance and coverage metrics.
- Posterior delta summaries and node-level engine outputs.
- A simulation platform for denominator-first stress testing.

## Minimal Reviewer Rerun Sequence
- Start with the README/tutorial files listed below and keep the manuscript paths synchronized with the public archive.
- Create the local runtime from the detected environment capture files if available: `requirements.txt`.
- Run at least one named example path from the manuscript and confirm that the generated outputs match the saved validation materials.
- Quote one concrete numeric result from the local validation snippets below when preparing the final software paper.

## Local Numeric Evidence Available
- `outputs/runs_v2/f778092f0316/global_metrics.csv` reports coverage 100.0%, 12 topics, 50 replications.
- `outputs/runs/e97458121909/global_metrics.csv` reports coverage 69.4%, 12 topics, 2 replications.
- `outputs/runs/f778092f0316/global_metrics.csv` reports coverage 100.0%, 12 topics, 50 replications.
