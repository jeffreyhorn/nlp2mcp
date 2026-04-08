# kand: Multi-Solve Model — Objective Mismatch (Wrong Comparison Target)

**GitHub Issue:** [#1225](https://github.com/jeffreyhorn/nlp2mcp/issues/1225)
**Status:** OPEN
**Severity:** High — objective mismatch (92.5%)
**Date:** 2026-04-06
**Affected Models:** kand
**Supersedes:** #1141 (originally misattributed to alias differentiation)

---

## Problem Summary

The kand model (Kandler's Structural Optimization, GAMSlib) contains TWO solve
statements for two different models:

1. `model kand / all /;` — the full LP model
2. `model kandsp / obj, bal, dembalx /;` — a subproblem (sparse subset of equations)

nlp2mcp reformulates the LAST solve statement (`kandsp`), but the comparison
pipeline compares the MCP objective against the first model (`kand`). Since
`kandsp` contains only a subset of equations, its KKT system is structurally
different from `kand`, producing a different (correct for kandsp) objective.

| Metric | Value |
|--------|-------|
| LP Objective (kand) | 2613.0 |
| MCP Objective (kandsp) | 195.0 |
| Relative Difference | 92.5% |

This is NOT an alias bug. The `Alias(n,nn)` is present but is not the root cause.

---

## Root Cause

The pipeline always reformulates the last `solve` statement in the file. When a
model contains multiple solves, the last one may be a subproblem, sensitivity
analysis, or auxiliary computation — not the primary model whose objective is
used for comparison.

In kand.gms:
- First solve: `solve kand using lp minimizing z;` (full model, all equations)
- Second solve: `solve kandsp using lp minimizing z;` (subproblem: obj, bal, dembalx only)

The comparison reference objective (2613.0) comes from the first solve (`kand`),
but the MCP is built from the second solve (`kandsp`), which naturally produces
a different objective (195.0).

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/kand.gms -o /tmp/kand_mcp.gms
gams /tmp/kand_mcp.gms lo=2
# MCP objective: ~195 (from kandsp subproblem)
# Expected comparison target: ~2613 (from kand full model)
```

---

## Model Structure

- **File**: `data/gamslib/raw/kand.gms` (104 lines)
- **Aliases**: `Alias(n, nn)`
- **Model 1**: `kand / all /` — full model with all equations
- **Model 2**: `kandsp / obj, bal, dembalx /` — subproblem with 3 equations
- **Solve type**: LP (gamslib_type: LP)

---

## Potential Fix Approaches

1. **Multi-solve detection**: Detect models with multiple solve statements and
   either (a) reformulate the first/primary solve, or (b) flag for manual review
2. **Comparison target alignment**: When multiple solves exist, match the MCP
   objective against the solve that was actually reformulated
3. **User selection**: Allow specifying which solve statement to reformulate
4. **Skip in pipeline**: Mark multi-solve models as unsupported category

---

## Files Involved

- `data/gamslib/raw/kand.gms` — Source model (104 lines)
- `src/ir/parser.py` — Solve statement extraction (last-solve-wins)
- `scripts/gamslib/run_full_test.py` — Comparison pipeline
- `docs/issues/ISSUE_1141_kand-alias-tree-mismatch.md` — Superseded issue
