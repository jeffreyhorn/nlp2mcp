# lands: MCP Execution Error — RHS Value NA in Equation

**GitHub Issue:** [#986](https://github.com/jeffreyhorn/nlp2mcp/issues/986)
**Status:** FIXED (full pipeline success — parses, translates, compiles, solves, matches)
**Severity:** Medium
**Date:** 2026-03-03
**Fixed:** 2026-04-01

---

## Problem Summary

The lands model (stochastic programming, land allocation) parsed and translated to MCP successfully, but GAMS aborted during equation generation with `RHS value NA in equation` for `comp_dembal(mode-1)`. The parameter `d("mode-1")` was explicitly declared as NA in the original model, and the equation had no dollar condition to filter it out.

---

## Investigation

The original model declares:
```gams
Parameter d(j) 'energy demand' / mode-1 na, mode-2 3, mode-3 2 /;
```

The `d("mode-1") = na` was intentional — the value is dynamically assigned in a loop before each solve:
```gams
loop(s, d('mode-1') = dvar(s); solve det minimizing cost using lp; ...);
```

The original equation `dembal(j).. sum(i, y(i,j)) =g= d(j);` had **no dollar condition** because the model relies on temporal execution order (assignment before solve).

**Root cause:** The parameter legitimately had NA values by design, and the equation had no condition in the source to propagate.

---

## Resolution

The NA-related execution error was resolved by accumulated fixes across multiple PRs. lands now achieves full pipeline success: parses, translates, compiles cleanly, solves to MODEL STATUS 1 Optimal, and matches the reference objective.

No additional code changes needed.

---

## Files

- MCP file: `data/gamslib/mcp/lands_mcp.gms`
- Original GAMS model: `data/gamslib/raw/lands.gms`
- Parser data extraction: `src/ir/parser.py`
- Emitter: `src/emit/emit_gams.py`
