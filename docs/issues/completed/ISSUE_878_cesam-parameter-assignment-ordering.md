# cesam: Computed Parameter Assignments Emitted in Wrong Order

**GitHub Issue:** [#878](https://github.com/jeffreyhorn/nlp2mcp/issues/878)
**Status:** FIXED
**Severity:** High — Model compiles with 3 errors ($141), solve blocked
**Date:** 2026-02-25
**Affected Models:** cesam

---

## Problem Summary

The cesam model's emitted MCP code has computed parameter assignments in the wrong order.
Three parameters (`T1`, `sigmay1`, `sigmay2`) are used before they are assigned, causing
GAMS $141 errors ("Symbol declared but no values have been assigned").

---

## Root Cause: Missing Topological Sort

The emitter grouped computed parameter assignments by parameter name but did not perform
a topological sort based on read/write dependencies. This caused three ordering violations:
SAM used T1 before assignment, vbar1 used sigmay1 before assignment, vbar2 used sigmay2
before assignment.

The challenge was that same-parameter reassignment (e.g., SAM has both early static totals
and late T1-dependent totals) creates intra-parameter dependency boundaries that a simple
parameter-level sort cannot handle.

---

## Fix Details

Implemented a **phase-based topological sort** in `_topological_sort_statements()`:

1. **Phase splitting**: Each parameter's statement chain is split at dependency boundaries.
   A new phase starts when a statement introduces a new external dependency. For example,
   SAM gets split into phase 0 (self-contained totals + rescale) and phase 1 (T1-dependent
   totals).

2. **Kahn's algorithm**: Phases are sorted using Kahn's algorithm with predecessor
   constraints (phases of the same parameter must maintain their original order).

3. **Cycle breaking**: When all remaining phases have unmet dependencies, the algorithm
   breaks cycles by marking parameters with static values as "defined" (since GAMS
   initializes them to their data values).

### Files Changed

| File | Change |
|------|--------|
| `src/emit/original_symbols.py` | Added `_topological_sort_statements()` with phase-based sort; refactored `emit_computed_parameter_assignments()` to collect→sort→emit pattern |

### Result
- cesam: **0 compilation errors** (was 4: three $141 + one $257)
- Remaining execution errors (Abar0/Abar1 division by zero) are pre-existing dollar-condition issues, not ordering
- All 3783 tests pass
