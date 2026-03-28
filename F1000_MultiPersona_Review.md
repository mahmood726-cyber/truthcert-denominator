# TruthCert Denominator-First Engine: multi-persona peer review

This memo applies the recurring concerns in the supplied peer-review document to the current F1000 draft for this project (`truthcert-denominator-phase1`). It distinguishes changes already made in the draft from repository-side items that still need to hold in the released repository and manuscript bundle.

## Detected Local Evidence
- Detected documentation files: `README.md`, `f1000_artifacts/tutorial_walkthrough.md`.
- Detected environment capture or packaging files: `requirements.txt`.
- Detected validation/test artifacts: `f1000_artifacts/validation_summary.md`, `tests/test_posterior_validity.py`, `tests/test_reproducibility.py`, `tests/test_scoring_sanity.py`.
- Detected browser deliverables: no HTML file detected.
- Detected public repository root: `https://github.com/mahmood726-cyber/truthcert-denominator`.
- Detected public source snapshot: Fixed public commit snapshot available at `https://github.com/mahmood726-cyber/truthcert-denominator/tree/1ab7a8f9e5bb1c18294c8c4dafaaf9476644293b`.
- Detected public archive record: No project-specific DOI or Zenodo record URL was detected locally; archive registration pending.

## Reviewer Rerun Companion
- `F1000_Reviewer_Rerun_Manifest.md` consolidates the shortest reviewer-facing rerun path, named example files, environment capture, and validation checkpoints.

## Detected Quantitative Evidence
- `outputs/runs_v2/f778092f0316/global_metrics.csv` reports coverage 100.0%, 12 topics, 50 replications.
- `outputs/runs/e97458121909/global_metrics.csv` reports coverage 69.4%, 12 topics, 2 replications.
- `outputs/runs/f778092f0316/global_metrics.csv` reports coverage 100.0%, 12 topics, 50 replications.

## Current Draft Strengths
- States the project rationale and niche explicitly: Meta-analysis usually treats the published literature as the complete evidence base, even when registry data imply a substantial silent-trial denominator. Phase 1 of TruthCert explores whether a denominator-first Bayesian delta engine can reduce false reassurance under missing-not-at-random selection.
- Names concrete worked-example paths: `configs/suite_12topics_phase1.json` for the packaged simulation suite; `outputs/runs/` for manifest and metric outputs; `README.md` for the engine design and acceptance targets.
- Points reviewers to local validation materials: `tests/test_reproducibility.py`, `test_posterior_validity.py`, and `test_scoring_sanity.py`; Acceptance targets for false reassurance reduction, coverage, and convergence documented in the README; Deterministic seeding via PCG64 with hash chaining for exact reruns.
- Moderates conclusions and lists explicit limitations for TruthCert Denominator-First Engine.

## Remaining High-Priority Fixes
- Keep one minimal worked example public and ensure the manuscript paths match the released files.
- Ensure README/tutorial text, software availability metadata, and public runtime instructions stay synchronized with the manuscript.
- Confirm that the cited repository root resolves to the same fixed public source snapshot used for the submission package.
- Mint and cite a Zenodo DOI or record URL for the tagged release; none was detected locally.
- Reconfirm the quoted benchmark or validation sentence after the final rerun so the narrative text stays synchronized with the shipped artifacts.

## Persona Reviews

### Reproducibility Auditor
- Review question: Looks for a frozen computational environment, a fixed example input, and an end-to-end rerun path with saved outputs.
- What the revised draft now provides: The revised draft names concrete rerun assets such as `configs/suite_12topics_phase1.json` for the packaged simulation suite; `outputs/runs/` for manifest and metric outputs and ties them to validation files such as `tests/test_reproducibility.py`, `test_posterior_validity.py`, and `test_scoring_sanity.py`; Acceptance targets for false reassurance reduction, coverage, and convergence documented in the README.
- What still needs confirmation before submission: Before submission, freeze the public runtime with `requirements.txt` and keep at least one minimal example input accessible in the external archive.

### Validation and Benchmarking Statistician
- Review question: Checks whether the paper shows evidence that outputs are accurate, reproducible, and compared against known references or stress tests.
- What the revised draft now provides: The manuscript now cites concrete validation evidence including `tests/test_reproducibility.py`, `test_posterior_validity.py`, and `test_scoring_sanity.py`; Acceptance targets for false reassurance reduction, coverage, and convergence documented in the README; Deterministic seeding via PCG64 with hash chaining for exact reruns and frames conclusions as being supported by those materials rather than by interface availability alone.
- What still needs confirmation before submission: Concrete numeric evidence detected locally is now available for quotation: `outputs/runs_v2/f778092f0316/global_metrics.csv` reports coverage 100.0%, 12 topics, 50 replications; `outputs/runs/e97458121909/global_metrics.csv` reports coverage 69.4%, 12 topics, 2 replications.

### Methods-Rigor Reviewer
- Review question: Examines modeling assumptions, scope conditions, and whether method-specific caveats are stated instead of implied.
- What the revised draft now provides: The architecture and discussion sections now state the method scope explicitly and keep caveats visible through limitations such as Phase 1 is simulation-first and does not yet include the multi-witness governance layer; Results depend on the specified MNAR selection mechanism and prior structure.
- What still needs confirmation before submission: Retain method-specific caveats in the final Results and Discussion and avoid collapsing exploratory thresholds or heuristics into universal recommendations.

### Comparator and Positioning Reviewer
- Review question: Asks what gap the tool fills relative to existing software and whether the manuscript avoids unsupported superiority claims.
- What the revised draft now provides: The introduction now positions the software against an explicit comparator class: The main comparator is publication-only meta-analysis. Because Phase 1 precedes the governance layer, the paper describes it as an engine for uncertainty propagation rather than a full decision framework.
- What still needs confirmation before submission: Keep the comparator discussion citation-backed in the final submission and avoid phrasing that implies blanket superiority over better-established tools.

### Documentation and Usability Reviewer
- Review question: Looks for a README, tutorial, worked example, input-schema clarity, and short interpretation guidance for outputs.
- What the revised draft now provides: The revised draft points readers to concrete walkthrough materials such as `configs/suite_12topics_phase1.json` for the packaged simulation suite; `outputs/runs/` for manifest and metric outputs; `README.md` for the engine design and acceptance targets and spells out expected outputs in the Methods section.
- What still needs confirmation before submission: Make sure the public archive exposes a readable README/tutorial bundle: currently detected files include `README.md`, `f1000_artifacts/tutorial_walkthrough.md`.

### Software Engineering Hygiene Reviewer
- Review question: Checks for evidence of testing, deployment hygiene, browser/runtime verification, secret handling, and removal of obvious development leftovers.
- What the revised draft now provides: The draft now foregrounds regression and validation evidence via `f1000_artifacts/validation_summary.md`, `tests/test_posterior_validity.py`, `tests/test_reproducibility.py`, `tests/test_scoring_sanity.py`, and browser-facing projects are described as self-validating where applicable.
- What still needs confirmation before submission: Before submission, remove any dead links, exposed secrets, or development-stage text from the public repo and ensure the runtime path described in the manuscript matches the shipped code.

### Claims-and-Limitations Editor
- Review question: Verifies that conclusions are bounded to what the repository actually demonstrates and that limitations are explicit.
- What the revised draft now provides: The abstract and discussion now moderate claims and pair them with explicit limitations, including Phase 1 is simulation-first and does not yet include the multi-witness governance layer; Results depend on the specified MNAR selection mechanism and prior structure; The engine is not yet packaged as a user-facing browser application.
- What still needs confirmation before submission: Keep the conclusion tied to documented functions and artifacts only; avoid adding impact claims that are not directly backed by validation, benchmarking, or user-study evidence.

### F1000 and Editorial Compliance Reviewer
- Review question: Checks for manuscript completeness, software/data availability clarity, references, and reviewer-facing support files.
- What the revised draft now provides: The revised draft is more complete structurally and now points reviewers to software availability, data availability, and reviewer-facing support files.
- What still needs confirmation before submission: Confirm repository/archive metadata, figure/export requirements, and supporting-file synchronization before release.
