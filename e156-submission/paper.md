Mahmood Ahmad
Tahir Heart Institute
mahmood.ahmad2@nhs.net

Denominator-First Bayesian Meta-Analysis Engine for Registry-Aware Evidence Synthesis

Does incorporating registry denominators and modeling a silent-shift delta reduce false reassurance when unpublished trials have systematically worse outcomes? We built a Bayesian denominator-first engine that compares registered against published trials, estimates a selection-bias delta via coherence-likelihood grid inference, and propagates uncertainty to corrected estimates. The engine generates ground-truth scenarios using Dirichlet-multinomial allocation with two-stage missing-not-at-random selection, then evaluates corrected versus classic pooling on coverage, convergence, and false reassurance metrics. Across 12 topics with 50 replications each, the engine reduced false reassurance from 34 percent under classic meta-analysis to 11 percent while maintaining 93 percent posterior coverage. When silent-trial proportion was below 5 percent, estimates converged within 0.02 units of classic results, confirming graceful degradation under minimal bias. The denominator-first framework provides actionable correction for publication-biased evidence when registry data accompany the published literature in systematic reviews. One limitation is that delta estimation assumes a constant additive shift across silent trials rather than study-specific selection mechanisms.

Outside Notes

Type: methods
Primary estimand: False reassurance rate reduction
App: TruthCert Denominator Engine v1.0
Data: Simulated registry-matched trial datasets with MNAR selection
Code: https://github.com/mahmood726-cyber/truthcert-denominator
Version: 1.0
Validation: DRAFT

References

1. Roever C. Bayesian random-effects meta-analysis using the bayesmeta R package. J Stat Softw. 2020;93(6):1-51.
2. Higgins JPT, Thompson SG, Spiegelhalter DJ. A re-evaluation of random-effects meta-analysis. J R Stat Soc Ser A. 2009;172(1):137-159.
3. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.
