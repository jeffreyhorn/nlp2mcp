# lands: MCP Execution Error — RHS Value NA in Equation

**GitHub Issue:** [#986](https://github.com/jeffreyhorn/nlp2mcp/issues/986)
**Status:** OPEN (deferred — requires NA-aware equation conditioning)
**Severity:** Medium — Model translates but PATH solver never runs (path_solve_terminated)
**Date:** 2026-03-03
**Affected Models:** lands

---

## Problem Summary

The lands model (stochastic programming, land allocation) parses and translates to MCP successfully, but GAMS aborts during equation generation with `RHS value NA in equation` for `comp_dembal(mode-1)`. The parameter `d("mode-1")` is explicitly declared as NA in the original model, and the equation has no dollar condition to filter it out.

---

## Investigation

The original model declares:
```gams
Parameter d(j) 'energy demand' / mode-1 na, mode-2 3, mode-3 2 /;
```

The `d("mode-1") = na` is intentional — the value is dynamically assigned in a loop before each solve:
```gams
loop(s, d('mode-1') = dvar(s); solve det minimizing cost using lp; ...);
```

The original equation `dembal(j).. sum(i, y(i,j)) =g= d(j);` has **no dollar condition** because the model relies on temporal execution order (assignment before solve). The MCP transformation makes all statements simultaneous, losing this ordering.

**Root cause:** Not a parser or emitter bug. The parameter legitimately has NA values by design, and the equation has no condition in the source to propagate.

**Complexity:** Medium. Would require the emitter to detect parameters with NA values and auto-add `$(param <> na)` dollar conditions to equations that reference them. This is a general capability not specific to lands.

---

## Files

- MCP file: `data/gamslib/mcp/lands_mcp.gms`
- Original GAMS model: `data/gamslib/raw/lands.gms`
- Parser data extraction: `src/ir/parser.py`
- Emitter: `src/emit/emit_gams.py`
