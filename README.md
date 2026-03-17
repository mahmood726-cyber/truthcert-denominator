# TruthCert Denominator-First Meta-Analysis Engine -- Phase 1

## Installation
Use the dependency files in this directory (for example `requirements.txt`, `environment.yml`, `DESCRIPTION`, or equivalent project-specific files) to create a clean local environment before running analyses.
Document any package-version mismatch encountered during first run.

## Concept

Traditional meta-analysis only sees **published trials**, creating *false reassurance* when silent trials have systematically worse outcomes (MNAR -- Missing Not At Random).

This engine uses **registry denominators** (all registered trials, not just published) and models a **silent-shift delta** to estimate how much the observed evidence is biased by selection. The delta posterior is then propagated to node-level effect estimates with honest uncertainty.

### Key Claims Tested

1. Using a registry denominator + Bayesian delta estimation reduces **false reassurance** compared to publication-only meta-analysis.
2. The engine maintains **>= 90% coverage** in moderate settings.
3. When silent rates are low, the engine **converges** to classic meta-analysis.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full 12-topic suite (50 replications each)
python -m sim.run_suite --config configs/suite_12topics_phase1.json --out outputs/runs

# Run tests
python tests/test_reproducibility.py
python tests/test_posterior_validity.py
python tests/test_scoring_sanity.py
```

## Architecture

```
sim/
  config_schema.py   Pydantic models for all configuration
  seed.py            Deterministic seeding (hash32 + PCG64)
  generate_truth.py  Node-level ground truth (mu, tau, p_control)
  generate_trials.py Dirichlet-multinomial trial allocation + binomial events
  oracle.py          Silent-shift delta mechanism + oracle meta
  selection.py       Two-stage MNAR selection (results posting + publication)
  observed_world.py  Build observed effects + node denominators
  meta_fixed.py      Fixed-effect (inverse-variance) pooling
  fit_delta.py       Bayesian delta posterior via coherence-likelihood grid
  propagate_engine.py  Posterior propagation to node-level estimates
  decision.py        Decision rules (Recommend/Consider/Research/DoNot)
  score.py           Scoring metrics (FR, coverage, convergence, delta bias)
  run_suite.py       Main orchestrator
```

## Outputs

After running, find results at:

```
outputs/runs/{run_id}/
  manifest.json       Run metadata
  topic_metrics.csv   Per-topic: classic_FR, engine_FR, coverage, convergence
  delta_metrics.csv   Per-topic-endpoint: delta bias, coverage
  global_metrics.csv  Aggregated across all topics
```

## 12-Topic Suite

| ID  | Label                    | Key Feature                          |
|-----|--------------------------|--------------------------------------|
| T01 | Clean Control            | Low missingness, delta ~ 0           |
| T02 | Moderate Publication Bias| Typical academic publication bias    |
| T03 | High Publication Bias    | Aggressive selection on significance |
| T04 | Endpoint-Selective       | Results posted but endpoints missing |
| T05 | Industry-Dominated       | 90% industry, large industry delta   |
| T06 | Small Trials             | 20-100 per arm, high SE              |
| T07 | High Heterogeneity       | tau = 0.25                           |
| T08 | Reversal Stress          | Very high missingness + large delta  |
| T09 | Discontinuous Truth      | Phenotype-flip in true effect        |
| T10 | Low Trial Count          | Only 24 trials across 12 nodes       |
| T11 | Strong Benefit Signal    | mu_global = -0.30                    |
| T12 | Near-Null Effect         | mu_global = -0.01                    |

## Interpreting Results

- **False Reassurance (FR)**: Rate at which an analysis declares benefit when the oracle says otherwise. Lower is better. The engine should have lower FR than classic, especially in high-silence topics (T03, T08).
- **Coverage**: Rate at which the engine's 95% CrI contains the oracle mu. Target >= 0.90.
- **Convergence**: When silent rate is very low (< 15%), engine and classic estimates should agree closely.
- **Delta Identifiability**: Bias and coverage of the estimated delta vs. true delta.

## Acceptance Targets

1. Engine reduces classic FR by **>= 30%** in high-silence topics (T03, T08).
2. Coverage **>= 0.90** in moderate settings (T01, T02, T11).
3. Convergence: mean |engine - classic| < 0.05 when silent rate < 15%.

## Ablation Modes

- **denom_only**: Ignore delta; decide solely from silent-rate thresholds.
- **delta_only**: Full delta fit + propagation + decision.

Both are reported alongside the main engine for comparison.

## Reproducibility

All randomness flows through `numpy.random.Generator(PCG64(seed))` with deterministic seed derivation:
```
seed_topic = hash32(seed_master, topic_id)
seed_rep   = hash32(seed_topic, rep_index)
```

Running with the same config produces identical outputs.
