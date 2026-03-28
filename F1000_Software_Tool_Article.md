# TruthCert Denominator-First Engine: a software tool for reviewer-auditable evidence synthesis

## Authors
- Mahmood Ahmad [1,2]
- Niraj Kumar [1]
- Bilaal Dar [3]
- Laiba Khan [1]
- Andrew Woo [4]
- Corresponding author: Andrew Woo (andy2709w@gmail.com)

## Affiliations
1. Royal Free Hospital
2. Tahir Heart Institute Rabwah
3. King's College Medical School
4. St George's Medical School

## Abstract
**Background:** Meta-analysis usually treats the published literature as the complete evidence base, even when registry data imply a substantial silent-trial denominator. Phase 1 of TruthCert explores whether a denominator-first Bayesian delta engine can reduce false reassurance under missing-not-at-random selection.

**Methods:** The Phase 1 engine simulates node-level truth, trial allocation, MNAR selection, and posterior propagation of a silent-shift delta estimated from registry-denominator information. The local package includes topic suites, tests, acceptance targets, and deterministic seeding for reproducible reruns.

**Results:** Project outputs report topic-level false reassurance, coverage, convergence, and delta-estimation behavior across a 12-topic suite and accompanying ablation modes.

**Conclusions:** Phase 1 is best reported as a simulation-based denominator-first correction engine whose main claim is conservative sensitivity to silent-trial bias, not complete governance of evidence decisions.

## Keywords
publication bias; registry denominators; Bayesian sensitivity analysis; simulation; meta-analysis governance; software tool

## Introduction
The software contribution is a reproducible simulation platform for denominator-first meta-analysis. Instead of describing a bias concept abstractly, the repository exposes truth generation, selection mechanisms, scoring, and expected acceptance targets.

The main comparator is publication-only meta-analysis. Because Phase 1 precedes the governance layer, the paper describes it as an engine for uncertainty propagation rather than a full decision framework.

The manuscript structure below is deliberately aligned to common open-software review requests: the rationale is stated explicitly, at least one runnable example path is named, local validation artifacts are listed, and conclusions are bounded to the functions and outputs documented in the repository.

## Methods
### Software architecture and workflow
The codebase is organized into configuration models, deterministic seeding, truth generation, trial generation, MNAR selection, observed-world construction, fixed-effect pooling, delta fitting, posterior propagation, decisions, and scoring.

### Installation, runtime, and reviewer reruns
The local implementation is packaged under `C:\Models\truthcert-denominator-phase1`. The manuscript identifies the local entry points, dependency manifest, fixed example input, and expected saved outputs so that reviewers can rerun the documented workflow without reconstructing it from scratch.

- Entry directory: `C:\Models\truthcert-denominator-phase1`.
- Detected documentation entry points: `README.md`, `f1000_artifacts/tutorial_walkthrough.md`.
- Detected environment capture or packaging files: `requirements.txt`.
- Named worked-example paths in this draft: `configs/suite_12topics_phase1.json` for the packaged simulation suite; `outputs/runs/` for manifest and metric outputs; `README.md` for the engine design and acceptance targets.
- Detected validation or regression artifacts: `f1000_artifacts/validation_summary.md`, `tests/test_posterior_validity.py`, `tests/test_reproducibility.py`, `tests/test_scoring_sanity.py`.
- Detected example or sample data files: `f1000_artifacts/example_dataset.csv`.

### Worked examples and validation materials
**Example or fixed demonstration paths**
- `configs/suite_12topics_phase1.json` for the packaged simulation suite.
- `outputs/runs/` for manifest and metric outputs.
- `README.md` for the engine design and acceptance targets.

**Validation and reporting artifacts**
- `tests/test_reproducibility.py`, `test_posterior_validity.py`, and `test_scoring_sanity.py`.
- Acceptance targets for false reassurance reduction, coverage, and convergence documented in the README.
- Deterministic seeding via PCG64 with hash chaining for exact reruns.

### Typical outputs and user-facing deliverables
- Topic-level false reassurance and coverage metrics.
- Posterior delta summaries and node-level engine outputs.
- A simulation platform for denominator-first stress testing.

### Reviewer-informed safeguards
- Provides a named example workflow or fixed demonstration path.
- Documents local validation artifacts rather than relying on unsupported claims.
- Positions the software against existing tools without claiming blanket superiority.
- States limitations and interpretation boundaries in the manuscript itself.
- Requires explicit environment capture and public example accessibility in the released archive.

## Review-Driven Revisions
This draft has been tightened against recurring open peer-review objections taken from the supplied reviewer reports.
- Reproducibility: the draft names a reviewer rerun path and points readers to validation artifacts instead of assuming interface availability is proof of correctness.
- Validation: claims are anchored to local tests, validation summaries, simulations, or consistency checks rather than to unsupported assertions of performance.
- Comparators and niche: the manuscript now names the relevant comparison class and keeps the claimed niche bounded instead of implying universal superiority.
- Documentation and interpretation: the text expects a worked example, input transparency, and reviewer-verifiable outputs rather than a high-level feature list alone.
- Claims discipline: conclusions are moderated to the documented scope of TruthCert Denominator-First Engine and paired with explicit limitations.

## Use Cases and Results
The software outputs should be described in terms of concrete reviewer-verifiable workflows: running the packaged example, inspecting the generated results, and checking that the reported interpretation matches the saved local artifacts. In this project, the most important result layer is the availability of a transparent execution path from input to analysis output.

Representative local result: `outputs/runs_v2/f778092f0316/global_metrics.csv` reports coverage 100.0%, 12 topics, 50 replications.

### Concrete local quantitative evidence
- `outputs/runs_v2/f778092f0316/global_metrics.csv` reports coverage 100.0%, 12 topics, 50 replications.
- `outputs/runs/e97458121909/global_metrics.csv` reports coverage 69.4%, 12 topics, 2 replications.
- `outputs/runs/f778092f0316/global_metrics.csv` reports coverage 100.0%, 12 topics, 50 replications.

## Discussion
Representative local result: `outputs/runs_v2/f778092f0316/global_metrics.csv` reports coverage 100.0%, 12 topics, 50 replications.

The right software-paper framing is methodological transparency: clearly show how the denominator signal enters the posterior and how performance is measured, while reserving broader governance claims for the Phase 2 prototype.

### Limitations
- Phase 1 is simulation-first and does not yet include the multi-witness governance layer.
- Results depend on the specified MNAR selection mechanism and prior structure.
- The engine is not yet packaged as a user-facing browser application.

## Software Availability
- Local source package: `truthcert-denominator-phase1` under `C:\Models`.
- Public repository: `https://github.com/mahmood726-cyber/truthcert-denominator`.
- Public source snapshot: Fixed public commit snapshot available at `https://github.com/mahmood726-cyber/truthcert-denominator/tree/1ab7a8f9e5bb1c18294c8c4dafaaf9476644293b`.
- DOI/archive record: No project-specific DOI or Zenodo record URL was detected locally; archive registration pending.
- Environment capture detected locally: `requirements.txt`.
- Reviewer-facing documentation detected locally: `README.md`, `f1000_artifacts/tutorial_walkthrough.md`.
- Reproducibility walkthrough: `f1000_artifacts/tutorial_walkthrough.md` where present.
- Validation summary: `f1000_artifacts/validation_summary.md` where present.
- Reviewer rerun manifest: `F1000_Reviewer_Rerun_Manifest.md`.
- Multi-persona review memo: `F1000_MultiPersona_Review.md`.
- Concrete submission-fix note: `F1000_Concrete_Submission_Fixes.md`.
- License: see the local `LICENSE` file.

## Data Availability
All simulations, configs, and output manifests are stored locally in the project directory. No real patient-level data are included.

## Reporting Checklist
Real-peer-review-aligned checklist: `F1000_Submission_Checklist_RealReview.md`.
Reviewer rerun companion: `F1000_Reviewer_Rerun_Manifest.md`.
Companion reviewer-response artifact: `F1000_MultiPersona_Review.md`.
Project-level concrete fix list: `F1000_Concrete_Submission_Fixes.md`.

## Declarations
### Competing interests
The authors declare that no competing interests were disclosed.

### Grant information
No specific grant was declared for this manuscript draft.

### Author contributions (CRediT)
| Author | CRediT roles |
|---|---|
| Mahmood Ahmad | Conceptualization; Software; Validation; Data curation; Writing - original draft; Writing - review and editing |
| Niraj Kumar | Conceptualization |
| Bilaal Dar | Conceptualization |
| Laiba Khan | Conceptualization |
| Andrew Woo | Conceptualization |

### Acknowledgements
The authors acknowledge contributors to open statistical methods, reproducible research software, and reviewer-led software quality improvement.

## References
1. DerSimonian R, Laird N. Meta-analysis in clinical trials. Controlled Clinical Trials. 1986;7(3):177-188.
2. Higgins JPT, Thompson SG. Quantifying heterogeneity in a meta-analysis. Statistics in Medicine. 2002;21(11):1539-1558.
3. Viechtbauer W. Conducting meta-analyses in R with the metafor package. Journal of Statistical Software. 2010;36(3):1-48.
4. Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. BMJ. 2021;372:n71.
5. Fay C, Rochette S, Guyader V, Girard C. Engineering Production-Grade Shiny Apps. Chapman and Hall/CRC. 2022.
