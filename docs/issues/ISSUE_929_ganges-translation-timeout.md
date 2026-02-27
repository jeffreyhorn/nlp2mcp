# ganges: Translation Timeout — Macroeconomic Framework for India

**GitHub Issue:** [#929](https://github.com/jeffreyhorn/nlp2mcp/issues/929)
**Status:** OPEN
**Severity:** Medium — Model parses but translation times out (>60s)
**Date:** 2026-02-26
**Affected Models:** ganges
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `ganges.gms` model (GAMSlib SEQ=122, "Macroeconomic Framework for India") parses successfully but times out during KKT translation (>60s). This is a large NLP macroeconomic model where the symbolic differentiation pipeline cannot complete within the time limit.

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 122 |
| Solve Type | NLP |
| Convexity | likely_convex |
| Reference Objective | 6395.5444 |
| Parse Status | success (slow, >90s) |
| Translate Status | timeout (>60s) |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/ganges.gms -o /tmp/ganges_mcp.gms
# Or:
python scripts/gamslib/run_full_test.py --model ganges --only-translate --verbose
```

---

## Root Cause

The ganges model is a large NLP macroeconomic model with many multi-dimensional variables and equations. The symbolic Jacobian computation generates too many variable instance × equation instance entries to complete within the 60-second timeout. Unlike LP timeout models, the NLP derivatives are genuinely nonlinear and require full symbolic differentiation.

---

## Possible Fixes

| Approach | Impact | Effort |
|----------|--------|--------|
| Sparsity-aware Jacobian (only compute interacting variable/equation pairs) | High | High |
| Increase timeout limit | Low — may succeed with longer timeout | Trivial |
| Variable instance threshold with early abort | Low | Low |

---

## Related Issues

- gangesx: Sister model (same framework, tracking variant), same timeout
- #885 (sarf): Same timeout pattern
- dinam, egypt, ferts, iswnm, nebrazil: Same timeout category
