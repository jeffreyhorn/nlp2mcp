# gangesx: Translation Timeout — Economic Framework for India (Tracking)

**GitHub Issue:** [#930](https://github.com/jeffreyhorn/nlp2mcp/issues/930)
**Status:** OPEN
**Severity:** Medium — Model parses but translation times out (>60s)
**Date:** 2026-02-26
**Affected Models:** gangesx
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `gangesx.gms` model (GAMSlib SEQ=123, "Economic Framework for India - Tracking") parses successfully but times out during KKT translation (>60s). This is the tracking variant of the ganges model and shares the same root cause.

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 123 |
| Solve Type | NLP |
| Convexity | likely_convex |
| Reference Objective | 6395.5444 |
| Parse Status | success (slow, >90s) |
| Translate Status | timeout (>60s) |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/gangesx.gms -o /tmp/gangesx_mcp.gms
# Or:
python scripts/gamslib/run_full_test.py --model gangesx --only-translate --verbose
```

---

## Root Cause

Same as ganges — large NLP macroeconomic model where symbolic Jacobian computation generates too many entries to complete within the 60-second timeout.

---

## Possible Fixes

Same as ganges — sparsity-aware Jacobian, increased timeout, or instance threshold.

---

## Related Issues

- ganges: Parent model, same timeout
- #885 (sarf): Same timeout pattern
- dinam, egypt, ferts, iswnm, nebrazil: Same timeout category

---

## Progress (2026-03-29)

LP fast path implemented (PR #1152) but does not apply to this NLP model. The timeout requires either a sparsity-aware Jacobian or increased timeout limits.
