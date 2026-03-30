# iswnm: Translation Timeout — Indus Surface Water Network Submodule

**GitHub Issue:** [#931](https://github.com/jeffreyhorn/nlp2mcp/issues/931)
**Status:** OPEN
**Severity:** Medium — Model parses but translation times out (>60s)
**Date:** 2026-02-26
**Affected Models:** iswnm
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `iswnm.gms` model (GAMSlib SEQ=164, "Indus Surface Water Network Submodule") parses successfully but times out during KKT translation (>60s).

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 164 |
| Solve Type | LP |
| Convexity | verified_convex |
| Reference Objective | 114.0397 |
| Parse Status | success (~33s) |
| Translate Status | timeout (>60s) |
| Variables | 4 |
| Equations | 2 |
| Sets | 13 |
| Parameters | 31 |

### Key Variables

| Variable | Domain |
|----------|--------|
| rcont | (n,m) |
| canaldiv | (c,m) |
| f | (n,n1,m) |
| vol | — |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/iswnm.gms -o /tmp/iswnm_mcp.gms
# Or:
python scripts/gamslib/run_full_test.py --model iswnm --only-translate --verbose
```

---

## Root Cause

Despite having only 4 variables and 2 equations, the 3-dimensional variable `f(n,n1,m)` over large network sets creates a combinatorial explosion of variable instances. The symbolic Jacobian must evaluate derivatives for each instance pair, exceeding the 60-second timeout. As an LP model, all derivatives are constant, making symbolic differentiation unnecessarily expensive.

---

## Possible Fixes

Same as other LP timeout models — LP-specific fast path, sparsity-aware Jacobian, or instance threshold.

---

## Related Issues

- indus: Related model (same Indus basin system)
- #885 (sarf): Same timeout pattern
- dinam, egypt, ferts, ganges, gangesx, nebrazil: Same LP/NLP timeout category

---

## Current Status (2026-03-29)

**Current blocker: Translation timeout (>300s).** LP fast path (PR #1172, basic simplification) implemented but differentiation itself is the bottleneck — the 3-dimensional variable `f(n,n1,m)` over large network sets creates too many variable/equation instances. Needs coefficient extraction with sum-bound index handling, or a sparsity-aware Jacobian.

Parse: ~58s | Translate: TIMEOUT | Compile: N/A | Solve: N/A
