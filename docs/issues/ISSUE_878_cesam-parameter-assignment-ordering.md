# cesam: Computed Parameter Assignments Emitted in Wrong Order

**GitHub Issue:** [#878](https://github.com/jeffreyhorn/nlp2mcp/issues/878)
**Status:** OPEN
**Severity:** High — Model compiles with 3 errors ($141), solve blocked
**Date:** 2026-02-25
**Affected Models:** cesam

---

## Problem Summary

The cesam model's emitted MCP code has computed parameter assignments in the wrong order.
Three parameters (`T1`, `sigmay1`, `sigmay2`) are used before they are assigned, causing
GAMS $141 errors ("Symbol declared but no values have been assigned").

---

## Error Details

```
  91  SAM(ii,"total") = sum(jj, T1(ii,jj));
****                             $141

 105  vbar1(ii,"1") = (-3) * sigmay1(ii);
****                               $141

 109  vbar2(macro,"1") = (-3) * sigmay2(macro);
****                                  $141
```

Plus cascading $257 ("solve not checked") on the Solve statement.

---

## Root Cause: Missing Topological Sort

The emitter groups computed parameter assignments by parameter name but does not perform
a topological sort based on read/write dependencies. This causes three ordering violations:

### Violation 1: `SAM` uses `T1` before `T1` is assigned

| Line | Statement | Status |
|------|-----------|--------|
| 91 | `SAM(ii,"total") = sum(jj, T1(ii,jj))` | **READS T1** — not yet assigned |
| 97 | `T1(ii,jj) = T0(ii,jj) - redsam(ii,jj)` | First assignment to T1 |

Required order: T0 → T1 → SAM("total") aggregation

### Violation 2: `vbar1` uses `sigmay1` before `sigmay1` is assigned

| Line | Statement | Status |
|------|-----------|--------|
| 105 | `vbar1(ii,"1") = (-3) * sigmay1(ii)` | **READS sigmay1** — not yet assigned |
| 113 | `sigmay1(ii) = 0.05 * target0(ii)` | First assignment to sigmay1 |

Required order: target0 → sigmay1 → vbar1

### Violation 3: `vbar2` uses `sigmay2` before `sigmay2` is assigned

| Line | Statement | Status |
|------|-----------|--------|
| 109 | `vbar2(macro,"1") = (-3) * sigmay2(macro)` | **READS sigmay2** — not yet assigned |
| 114 | `sigmay2("gdpfc2") = 0.05 * gdpfc0` | First assignment to sigmay2 |

Required order: T1 → gdpfc0/gdp0 → sigmay2 → vbar2

### Full Dependency Chain

```
redsam → T0 → T1 → T1(Total) aggregation → SAM(total) aggregation
                ↓
          gdp0, gdpfc0 → sigmay2 → vbar2

target0 → sigmay1 → vbar1
```

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/cesam.gms -o /tmp/cesam_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/cesam_mcp.gms action=c

# Check ordering:
grep -n 'T1\|sigmay1\|sigmay2\|vbar1\|vbar2\|SAM.*total' /tmp/cesam_mcp.gms | head -30
# Shows SAM uses T1 at line 91, but T1 assigned at line 97
```

---

## Suggested Fix

The emitter's `emit_computed_parameter_assignments()` in `src/emit/original_symbols.py`
needs to perform a **topological sort** at the individual assignment statement level:

1. **Build a dependency graph**: For each assignment statement `LHS = RHS`, identify
   which parameters appear on the RHS. An assignment to `vbar1(ii,"1") = (-3) * sigmay1(ii)`
   depends on `sigmay1`.

2. **Sort topologically**: Emit assignments in dependency order so that every parameter
   is defined before it's used.

3. **Handle same-parameter reassignment**: The same parameter can appear on both LHS and
   RHS across different assignments (e.g., `SAM` is first loaded from data, then
   overwritten with `sum(jj, T1(ii,jj))`). The dependency graph must be at the
   **individual statement level**, not the parameter level.

4. **Handle cycles**: If a parameter references itself (e.g., `p(i) = p(i) * scale`),
   that's a single-statement self-reference that should be preserved in place.

**Effort estimate:** ~3-4h

---

## Files Likely Affected

| File | Change |
|------|--------|
| `src/emit/original_symbols.py` | Add topological sort to `emit_computed_parameter_assignments()` |

---

## Related Issues

- **Issue #741**: Parameter expression ordering (list vs dict storage) — related but different
