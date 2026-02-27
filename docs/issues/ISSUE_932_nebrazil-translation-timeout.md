# nebrazil: Translation Timeout — North-East Brazil Regional Agricultural Model

**GitHub Issue:** [#932](https://github.com/jeffreyhorn/nlp2mcp/issues/932)
**Status:** OPEN
**Severity:** Medium — Model parses but translation times out (>60s)
**Date:** 2026-02-26
**Affected Models:** nebrazil
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `nebrazil.gms` model (GAMSlib SEQ=230, "North-East Brazil Regional Agricultural Model") parses successfully but times out during KKT translation (>60s).

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 230 |
| Solve Type | LP |
| Convexity | verified_convex |
| Reference Objective | 3385.433 |
| Parse Status | success (~23s) |
| Translate Status | timeout (>60s) |
| Variables | 29 |
| Equations | 25 |
| Sets | 37 |
| Parameters | 61 |

### Key Variables (selected multi-dimensional)

| Variable | Domain | Description |
|----------|--------|-------------|
| xcrop | (p,s,f,zz) | Crop allocation (4-dim) |
| xcrops | (p,s,f,zz) | Crop allocation summary (4-dim) |
| regq | (c,zz,g) | Regional quantities (3-dim) |
| consp | (dr,f,zz) | Consumption primary (3-dim) |
| conss | (dr,f,zz) | Consumption secondary (3-dim) |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/nebrazil.gms -o /tmp/nebrazil_mcp.gms
# Or:
python scripts/gamslib/run_full_test.py --model nebrazil --only-translate --verbose
```

---

## Root Cause

The model has 29 variables (many multi-dimensional, including 4-dimensional `xcrop` and `xcrops`) and 25 equations over 37 sets and 61 parameters. This is the largest model in the timeout category by variable/equation count. The symbolic Jacobian computation generates an enormous number of variable instance × equation instance entries. As an LP model, all derivatives are constant, making symbolic differentiation unnecessarily expensive.

---

## Possible Fixes

Same as other LP timeout models — LP-specific fast path, sparsity-aware Jacobian, or instance threshold.

---

## Related Issues

- #885 (sarf): Same timeout pattern
- dinam, egypt, ferts, ganges, gangesx, iswnm: Same LP/NLP timeout category
