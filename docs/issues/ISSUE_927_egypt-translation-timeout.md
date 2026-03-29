# egypt: Translation Timeout — Large LP Agricultural Model

**GitHub Issue:** [#927](https://github.com/jeffreyhorn/nlp2mcp/issues/927)
**Status:** OPEN
**Severity:** Medium — Model parses but translation times out (>60s)
**Date:** 2026-02-26
**Affected Models:** egypt
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `egypt.gms` model (GAMSlib SEQ=94, "Egypt Agricultural Model") parses successfully but times out during KKT translation (>60s). This is a large LP agricultural model with multi-dimensional variables that cause combinatorial explosion during Jacobian computation.

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 94 |
| Solve Type | LP |
| Convexity | verified_convex |
| Reference Objective | 4134175.7019 |
| Parse Status | success (~34s) |
| Translate Status | timeout (>60s) |
| Variables | 11 |
| Equations | 11 |
| Sets | 19 |
| Parameters | 62 |

### Key Variables

| Variable | Domain | Description |
|----------|--------|-------------|
| xcrop | (r,c) | Crop allocation by region |
| imports | (c) | Import quantities |
| exports | (c) | Export quantities |
| natq | (c,g) | National quantities |
| anut | (nt,r) | Available nutrients |
| sales | (c) | Sales |
| trans | (c,r,rp) | Transportation (3-dim) |
| fodder | (r,c) | Fodder allocation |
| tlab | (r,tm) | Total labor |
| flab | (r,tm) | Family labor |
| cps | — | Scalar |

---

## Reproduction

```bash
# Generate MCP (will timeout)
python -m src.cli data/gamslib/raw/egypt.gms -o /tmp/egypt_mcp.gms

# Or via pipeline runner:
python scripts/gamslib/run_full_test.py --model egypt --only-translate --verbose
```

---

## Root Cause

The model has 11 variables and 11 equations but with multi-dimensional domains (including 3-dimensional `trans(c,r,rp)` and many 2-dimensional variables over large sets with 19 set definitions and 62 parameters). The symbolic KKT differentiation pipeline generates a combinatorial explosion of variable instance × equation instance Jacobian entries. For LP models, all derivatives are constant, making symbolic differentiation unnecessarily expensive.

---

## Possible Fixes

| Approach | Impact | Effort |
|----------|--------|--------|
| LP-specific fast path (coefficient extraction instead of symbolic differentiation) | High | Medium-High |
| Sparsity-aware Jacobian (only compute interacting pairs) | High | High |
| Variable instance threshold with early abort | Low | Low |

---

## Related Issues

- #885 (sarf): Same timeout pattern
- dinam, ferts, ganges, gangesx, iswnm, nebrazil: Same LP/NLP timeout category

---

## Progress (2026-03-29)

**Translation timeout: FIXED** by LP fast path (PR #1152). Added `solve_type` field to ModelIR and use basic simplification instead of advanced for LP models, reducing differentiation overhead.

Translation now completes successfully. However, the generated MCP has secondary compilation errors ($140 unknown symbol, $149/$171 dimension/domain issues) that are separate blocking issues requiring further investigation.
