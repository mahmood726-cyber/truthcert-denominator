# TruthCert Denominator-First Engine: concrete submission fixes

This file converts the multi-persona review into repository-side actions that should be checked before external submission of the F1000 software paper for `truthcert-denominator-phase1`.

## Detectable Local State
- Documentation files detected: `README.md`, `f1000_artifacts/tutorial_walkthrough.md`.
- Environment lock or container files detected: `requirements.txt`.
- Package manifests detected: none detected.
- Example data files detected: `f1000_artifacts/example_dataset.csv`.
- Validation artifacts detected: `f1000_artifacts/validation_summary.md`, `tests/test_posterior_validity.py`, `tests/test_reproducibility.py`, `tests/test_scoring_sanity.py`.
- Detected public repository root: `https://github.com/mahmood726-cyber/truthcert-denominator`.
- Detected public source snapshot: Fixed public commit snapshot available at `https://github.com/mahmood726-cyber/truthcert-denominator/tree/1ab7a8f9e5bb1c18294c8c4dafaaf9476644293b`.
- Detected public archive record: No project-specific DOI or Zenodo record URL was detected locally; archive registration pending.

## High-Priority Fixes
- Check that the manuscript's named example paths exist in the public archive and can be run without repository archaeology.
- Confirm that the cited repository root (`https://github.com/mahmood726-cyber/truthcert-denominator`) resolves to the same fixed public source snapshot used for submission.
- Archive the tagged release and insert the Zenodo DOI or record URL once it has been minted; no project-specific archive DOI was detected locally.
- Reconfirm the quoted benchmark or validation sentence after the final rerun so the narrative text matches the shipped artifacts.

## Numeric Evidence Available To Quote
- `outputs/runs_v2/f778092f0316/global_metrics.csv` reports coverage 100.0%, 12 topics, 50 replications.
- `outputs/runs/e97458121909/global_metrics.csv` reports coverage 69.4%, 12 topics, 2 replications.
- `outputs/runs/f778092f0316/global_metrics.csv` reports coverage 100.0%, 12 topics, 50 replications.

## Manuscript Files To Keep In Sync
- `F1000_Software_Tool_Article.md`
- `F1000_Reviewer_Rerun_Manifest.md`
- `F1000_MultiPersona_Review.md`
- `F1000_Submission_Checklist_RealReview.md` where present
- README/tutorial files and the public repository release metadata
