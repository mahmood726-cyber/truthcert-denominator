# truthcert-denominator-phase1 — Code Review Findings

**Reviewer:** Claude Opus 4.6 (1M context)
**Date:** 2026-04-03
**Files:** index.html (45 lines, landing page), sim/ (14 Python modules), e156-submission/

## P0 — Critical (must fix)

None found.

## P1 — Important

### P1-1: I-squared formula outputs percentage (0-100), not proportion (0-1)
**File:** sim/meta_fixed.py, line 74
**Status:** PASS — `I2 = max(0.0, (Q - df) / Q * 100)` correctly outputs percentage. Consistent with Higgins & Thompson (2002).

### P1-2: DL tau2 edge case k=1
**File:** sim/meta_fixed.py, lines 58-64
**Status:** PASS — returns tau2=0, I2=0 for single study. Correct.

### P1-3: Division by zero guard in C calculation
**File:** sim/meta_fixed.py, line 73
**Status:** PASS — `if c > 1e-20 else 0.0` guards against zero denominator.

### P1-4: `index.html` is a static landing page with dashboard link
**Status:** No interactive JS, no user input, no CSV. No security concerns.

## P2 — Minor

### P2-1: `</html>` closing tag present in index.html
**Line:** 46
**Status:** PASS.

### P2-2: No `eval`/`exec`/`subprocess` calls in sim/ code
**Status:** PASS — no code execution from user input.

### P2-3: `NUL` file exists in project root (likely Windows artifact)
**Issue:** A file named `NUL` exists. This is likely created by a Windows `> NUL` redirect error. Harmless but should be cleaned up.

## Summary

| Severity | Count |
|----------|-------|
| P0       | 0     |
| P1       | 4     |
| P2       | 3     |

## Statistics Verification

- **Fixed-effect meta-analysis:** Inverse-variance weighted. PASS.
- **DL random-effects:** Q-based tau2, I2. All formulas correct. PASS.
- **I-squared:** `max(0, (Q-df)/Q * 100)`. PASS.
