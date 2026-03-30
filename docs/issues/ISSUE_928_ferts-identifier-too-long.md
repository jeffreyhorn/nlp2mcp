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

## Current Status (2026-03-29)

**Translation timeout: FIXED** by LP fast path (PR #1172).

**Current blocker: Generated identifier names exceed 63-char GAMS limit (26 errors)**
- $109 Identifier too long (18 occurrences) — hash-suffixed variable names like `nu_xi_fx_sulf_acid_c8324d9c_kafr_el_zt_4b0342d5_kafr_el_zt_4b0342d5` exceed the 63-character GAMS limit
- $108 Suffix identifier too long (4 occurrences)
- $141/$257 cascading from above

Fix: Truncate or shorten the naming scheme for generated MCP variables when element names are long.

Parse: ~35s | Translate: completes | Compile: FAIL | Solve: N/A
