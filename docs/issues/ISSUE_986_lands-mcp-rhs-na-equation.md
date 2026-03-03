# lands: MCP Execution Error — RHS Value NA in Equation

**GitHub Issue:** [#986](https://github.com/jeffreyhorn/nlp2mcp/issues/986)
**Status:** OPEN
**Severity:** Medium — Model translates but PATH solver never runs (path_solve_terminated)
**Date:** 2026-03-03
**Affected Models:** lands

---

## Problem Summary

The lands model (stochastic programming, land allocation) parses and translates to MCP successfully, but GAMS aborts during equation generation with `RHS value NA in equation` for `comp_dembal(mode-1)`. The NA value indicates an undefined/missing parameter in the RHS of the demand balance complementarity equation. PATH never runs.

---

## Reproduction

```bash
python scripts/gamslib/run_full_test.py --model lands --verbose
# Output: [SOLVE] FAILURE: path_solve_terminated

# Direct GAMS execution:
gams data/gamslib/mcp/lands_mcp.gms lo=3
# RHS value NA in equation below is illegal
# comp_dembal(mode-1)
# SOLVE from line 153 ABORTED, EXECERROR = 1
```

---

## Root Cause Analysis

The complementarity equation is:

```gams
comp_dembal(j).. sum(i, y(i,j)) - d(j) =G= 0;
```

The parameter `d(j)` provides demand values. When `d("mode-1")` is NA (not assigned), GAMS treats the equation RHS as undefined. This happens because the original model may define `d(j)` only for a subset of `j` elements, or `d` may be assigned conditionally.

The issue is in the **emitter or parser**: either:
1. The parameter `d` is not fully populated from the original model's data section
2. The domain `j` in the MCP has elements for which `d(j)` was never assigned (only valid for some `j` elements)
3. The original equation had a dollar condition `dembal(j)$(d(j))` that filtered out elements where `d` is undefined, but this condition was lost in translation

---

## Suggested Fix

1. **Check if the original equation has a dollar condition** — if `dembal(j)$(d(j) > 0)` or similar, the emitter must propagate this condition to the complementarity equation.
2. **Check parameter population** — verify that the parser extracts all data assignments for `d(j)` from the original model.
3. **Initialize undefined parameters to 0** — add `d(j) = 0;` before conditional assignment if the parameter may have gaps.

---

## Files

- MCP file: `data/gamslib/mcp/lands_mcp.gms`
- Original GAMS model: `data/gamslib/gms/lands.gms`
- Parser data extraction: `src/ir/parser.py`
- Emitter: `src/emit/emit_gams.py`
