# Truth-Recovery Validation — TruthCert-Denominator

**Repo:** mahmood726-cyber/truthcert-denominator (Denominator-First Meta-Analysis, Phase 1)
**Engine under test:** sim/meta_fixed.py — the pure pairwise pooling core
(fixed_effect = FE inverse-variance + Wald CI; random_effects_dl = DerSimonian-Laird
+ Wald CI; i_squared). Re-exported VERBATIM via truth-recovery/engine.py.
The TruthCert denominator/silent-shift-delta + Bayesian propagation overlay was
EXCLUDED; only the underlying pooling estimator is measured here.
**Date:** 2026-06-14 · seeded known-(mu, tau2) RE DGP + publication selection,
95% target, n_rep=4000, mu=-0.20 (logRR).

## VERDICT: GENUINE METHODS ENGINE — PASS (actionable gap found: no HKSJ)

This is a real pairwise MA engine (FE-IV + DL-RE pooling of logRR with Q/I^2/tau2),
sitting under a denominator-first selection-bias model. Extracted functions VERBATIM;
DL reduces exactly to FE-IV on homogeneous data (tau2=0). DGP ported faithfully from
the shared kit (step + Copas selection); all randomness via PCG64.

## Measured coverage of the true mu (95% target)

| k  | tau2 | scenario      | FE-Wald % | DL-Wald % | DL+HKSJ %* | DL bias  |
|----|------|---------------|-----------|-----------|------------|----------|
| 5  | 0.05 | none          | 74.2      | 88.6      | **96.2**   | +0.0035  |
| 8  | 0.05 | none          | 72.6      | 89.5      | **95.2**   | +0.0050  |
| 20 | 0.05 | none          | 69.9      | 91.7      | **93.8**   | +0.0006  |
| 5  | 0.10 | none          | 62.4      | 87.0      | **94.8**   | +0.0044  |
| 8  | 0.05 | step_strong   | 41.2      | 77.0      | 87.2       | +0.158   |
| 8  | 0.05 | copas_strong  | 62.8      | 78.0      | 86.9       | +0.110   |

*HKSJ is NOT implemented in this repo. The DL+HKSJ column applies a Hartung-Knapp
t_{k-1} CI (q floored to 1) ON TOP of the engine's OWN DL (mu, tau2) to quantify the
recoverable gap. It is a recommendation, not current engine behaviour.

## Findings

1. **FE-IV (fixed_effect) badly under-covers under any heterogeneity** — 62-74% vs 95%.
   Expected: FE ignores tau2, so its Wald CI is far too narrow once tau2>0. FE should
   never be the headline interval when tau2>0.
2. **DL-RE + Wald (the engine's classic arm) under-covers at small k** — 87-90% at
   k=5-8, climbing toward 92% by k=20. Textbook normal-quantile anti-conservatism.
3. **HKSJ would recover the truth — and it is MISSING from this engine.** Applying a
   Hartung-Knapp t_{k-1} CI to the engine's own DL fit lifts coverage to ~94-96%
   (+5-8 pp at k=5-8). The q<1 floor fired in 52-65% of no-selection replicates and
   never inverted the CI. This is the single biggest correctness lever for the engine.
4. **Point estimate is ~unbiased under no selection** (|DL bias| < 0.006); the coverage
   gap is purely CI width, which HKSJ fixes.
5. **Publication selection — honest negative.** Strong step selection: DL bias +0.158,
   coverage 77% (Wald) / 87% (HKSJ); strong Copas: bias +0.110, 78/87%. Classic pooling
   recovers the PUBLISHED mean, not the unconditional truth — which is precisely the
   motivation for this repo's denominator/delta layer. The pooling core alone does not,
   and is not expected to, undo selection.

## Recommendation

- **Add an HKSJ (Hartung-Knapp) t_{k-1} CI option to random_effects_dl and make it the
  default for k<30.** It is the most impactful fix: +5-8 pp coverage at small k, bringing
  the classic arm to nominal. Reference behaviour is implemented in truth-recovery/harness.py::_hksj_t_ci (q floored to 1, qt(1-a/2, k-1)).
- **Stop reporting FE-IV as a primary interval whenever tau2>0 / I^2 is non-trivial** —
  it under-covers by 20-30 pp. Reserve FE for the homogeneous case the engine already
  detects via i_squared.
- For k<10, consider REML/PM for tau2 (DL can underestimate tau2 at small k); the host
  README's >=90% coverage target is MET by DL+Wald at k>=20 but MISSED at k=5-8 — HKSJ
  closes that gap.
- The denominator/delta overlay remains the right tool for the selection-bias regime
  (T03/T08); the pooling core's selection bias here confirms why that overlay exists.

Reproduce: python truth-recovery/harness.py ; python truth-recovery/test_coverage.py (5/5 pass).
