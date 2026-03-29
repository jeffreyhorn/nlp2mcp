# ferts: Translation Timeout — Egypt Static Fertilizer Model

**GitHub Issue:** [#928](https://github.com/jeffreyhorn/nlp2mcp/issues/928)
**Status:** OPEN
**Severity:** Medium — Model parses but translation times out (>60s)
**Date:** 2026-02-26
**Affected Models:** ferts
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `ferts.gms` model (GAMSlib SEQ=110, "Egypt - Static Fertilizer Model") parses successfully but times out during KKT translation (>60s).

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 110 |
| Solve Type | LP |
| Convexity | verified_convex |
| Reference Objective | 58793.8227 |
| Parse Status | success (~20s) |
| Translate Status | timeout (>60s) |
| Variables | 11 |
| Equations | 8 |
| Sets | 18 |
| Parameters | 28 |

### Key Variables

| Variable | Domain | Description |
|----------|--------|-------------|
| z | (p,i) | Production activity |
| xf | (c,i,j) | Fertilizer flow (3-dim) |
| xi | (c,i,i) | Inter-plant transfer (3-dim) |
| vf | (c,j) | Final product value |
| vr | (c,i) | Raw material value |
| u | (c,i) | Utilization |
| psi, psip, psil, psii | — | Scalars |
| zl | — | Scalar |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/ferts.gms -o /tmp/ferts_mcp.gms
# Or:
python scripts/gamslib/run_full_test.py --model ferts --only-translate --verbose
```

---

## Root Cause

The 3-dimensional variables `xf(c,i,j)` and `xi(c,i,i)` create a large number of variable instances. The symbolic Jacobian computation explodes combinatorially when computing derivatives for every variable instance against every equation instance. As an LP model, all derivatives are constant, making symbolic differentiation unnecessarily expensive.

---

## Possible Fixes

Same as other LP timeout models — LP-specific fast path, sparsity-aware Jacobian, or instance threshold.

---

## Related Issues

- #885 (sarf): Same timeout pattern
- dinam, egypt, ganges, gangesx, iswnm, nebrazil: Same LP/NLP timeout category

---

## Progress (2026-03-29)

**Translation timeout: FIXED** by LP fast path (PR #1152). Added `solve_type` field to ModelIR and use basic simplification instead of advanced for LP models, reducing differentiation overhead.

Translation now completes successfully. However, the generated MCP has secondary compilation errors ($140 unknown symbol, $149/$171 dimension/domain issues) that are separate blocking issues requiring further investigation.
