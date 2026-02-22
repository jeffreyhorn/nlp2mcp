# Gastrans MCP: Jacobian Computation Timeout — Dynamic Subset Fallback Combinatorial Explosion

**GitHub Issue:** [#830](https://github.com/jeffreyhorn/nlp2mcp/issues/830)
**Status:** OPEN
**Severity:** High — Model cannot complete NLP→MCP translation (pipeline hangs at Jacobian)
**Date:** 2026-02-22
**Affected Models:** gastrans (and potentially any model with large dynamic subsets)

---

## Problem Summary

The gastrans model (`data/gamslib/raw/gastrans.gms`) hangs during the Jacobian computation
stage of NLP→MCP translation. The pipeline completes parsing, validation, and convexity
checking, but times out (>60s) when computing the constraint Jacobian.

The root cause is that dynamic subsets (`ap`, `as`, `aij`) have 0 static members in the IR.
When the Jacobian code iterates over equation/variable domain combinations, it falls back to
parent sets, causing a combinatorial explosion.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/gastrans.gms -o /tmp/gastrans_mcp.gms --smooth-abs
# Pipeline hangs after printing convexity warnings
# Log repeatedly prints: "Dynamic subset 'ap' has no static members; falling back to parent set 'a' (24 members)"
```

---

## Model Structure

### Sets
| Set | Members | Domain | Notes |
|-----|---------|--------|-------|
| `i` | 20 | — | Nodes (cities) |
| `a` | 24 | — | Arcs |
| `as` | 0 | `(a)` | Active arcs (subset of `a`) — dynamic |
| `ap` | 0 | `(a)` | Passive arcs (subset of `a`) — dynamic |
| `aij` | 0 | `(a, i, i)` | Arc-node mapping — dynamic |

### Equations using dynamic subsets
Most equations are indexed over `(ap, i, j)` or `(as, i, j)`:
- `weymouthp(ap, i, j)`, `weymouthp2(ap, i, j)`, `defsig(ap, i, j)`, `flo(ap, i, j)`, `fup(ap, i, j)`, `pilo(ap, i, j)`, `piup(ap, i, j)`
- `weymoutha(as, i, j)`

### Variables
- `f(a, i, j)`, `sig(a, i, j)`, `b(a, i, j)` — 3-dimensional over `(a, i, i)`
- `s(i)`, `pi(i)` — 1-dimensional
- `sc`, `h` — scalars

### Combinatorial explosion
With fallback to parent sets:
- Each `(ap, i, j)` equation expands to `24 × 20 × 20 = 9,600` tuples
- 7 equations × 9,600 tuples × 7 variables = **470,400** Jacobian entry computations
- This causes the pipeline to hang (>60s timeout)

---

## Root Cause

The dynamic subsets `ap`, `as`, and `aij` are populated at runtime in GAMS via:

```gams
Set ap(a) passive arcs / a01*a19 /;
Set as(a) active arcs  / a20*a24 /;
Set aij(a,i,i) arc-node mapping /
  a01.(Zeebrugge.Dudzele), a02.(Dudzele.Brugge), ...
/;
```

However, the IR parser records these as having 0 members because:
1. The range notation `a01*a19` may not be expanded to individual elements during parsing
2. The tuple data in `aij` may not be preserved in `SetDef.members`

When the Jacobian computation encounters a dynamic subset domain with 0 members, it falls
back to iterating over the parent set, causing the explosion.

---

## Suggested Fix

Several approaches (not mutually exclusive):

### Option A: Preserve dynamic subset members during parsing
Ensure that `a01*a19` range notation in subset data blocks is expanded and stored in
`SetDef.members`. This would give `ap` 19 members and `as` 5 members, and the `aij`
mapping its 24 tuple members. The Jacobian would then iterate over the correct (smaller)
domain.

### Option B: Jacobian timeout/limit
Add a configurable timeout or iteration limit to the Jacobian computation to prevent
infinite hangs. When exceeded, report a clear error message indicating the model is too
large for the current domain resolution.

### Option C: Sparse Jacobian with domain analysis
Instead of iterating over all possible index combinations, analyze which variables actually
appear in each equation and only compute derivatives for those (variable, index) pairs that
have non-zero contributions. This would be a more fundamental performance improvement.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/ir/parser.py` | Set member parsing — why dynamic subsets have 0 members |
| `src/ad/constraint_jacobian.py` | Jacobian computation loop and dynamic subset fallback |
| `data/gamslib/raw/gastrans.gms` | Original model with dynamic subset definitions |

---

## Context

This issue was uncovered after fixing #825 (signpower AD support). The signpower fix allows
gastrans to proceed past the AD function dispatch, but the model now hangs at the Jacobian
computation stage due to this pre-existing dynamic subset fallback issue.
