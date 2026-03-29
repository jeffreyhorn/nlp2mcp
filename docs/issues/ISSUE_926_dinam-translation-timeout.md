# dinam: Translation Timeout — Large LP with Multi-Dimensional Variables

**GitHub Issue:** [#926](https://github.com/jeffreyhorn/nlp2mcp/issues/926)
**Status:** OPEN
**Severity:** Medium — Model parses but translation times out (>60s)
**Date:** 2026-02-26
**Affected Models:** dinam
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `dinam.gms` model (GAMSlib SEQ=89, "DINAMICO A Dynamic Multi-Sectoral Multi-Skill Model") parses successfully but times out during KKT translation (>60s). This is a large LP model where the symbolic differentiation pipeline cannot complete within the time limit.

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 89 |
| Solve Type | LP |
| Convexity | verified_convex |
| Reference Objective | 251.366 |
| Parse Status | success (slow, >90s with default settings) |
| Translate Status | timeout (>60s) |

---

## Reproduction

```bash
# Generate MCP (will timeout)
python -m src.cli data/gamslib/raw/dinam.gms -o /tmp/dinam_mcp.gms

# Or via pipeline runner:
python scripts/gamslib/run_full_test.py --model dinam --only-translate --verbose
```

---

## Root Cause

The model is a large dynamic multi-sectoral LP. Applying symbolic KKT differentiation to large LP models is computationally excessive — the Jacobian computation generates a combinatorial explosion of variable instances multiplied by equation instances. For LP models, all derivatives are constant (linear terms), so the symbolic differentiation machinery is doing far more work than necessary.

---

## Possible Fixes

| Approach | Impact | Effort |
|----------|--------|--------|
| LP-specific fast path (skip symbolic differentiation, use coefficient extraction) | High — would handle all LP timeout models | Medium-High |
| Increase timeout limit | Low — just delays the inevitable for very large models | Trivial |
| Sparsity-aware Jacobian (only compute derivatives for variable/equation pairs that actually interact) | High — fundamental architecture improvement | High |
| Variable instance threshold with early abort | Low — skip rather than timeout | Low |

---

## Related Issues

- #885 (sarf): Same timeout pattern from combinatorial explosion
- #830 (gastrans): Jacobian timeout from dynamic subset conditions
- egypt, ferts, ganges, gangesx, iswnm, nebrazil: Same LP/NLP timeout category

---

## Progress (2026-03-29)

**Translation timeout: FIXED** by LP fast path (PR #1152). Added `solve_type` field to ModelIR and use basic simplification instead of advanced for LP models, reducing differentiation overhead.

Translation now completes successfully. However, the generated MCP has secondary compilation errors ($140 unknown symbol, $149/$171 dimension/domain issues) that are separate blocking issues requiring further investigation.
