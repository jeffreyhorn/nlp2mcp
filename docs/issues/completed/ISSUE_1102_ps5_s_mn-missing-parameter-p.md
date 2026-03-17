# ps5_s_mn: Missing Parameter `p(i)` in MCP Output ($140)

**GitHub Issue:** [#1102](https://github.com/jeffreyhorn/nlp2mcp/issues/1102)
**Model:** ps5_s_mn (GAMSlib SEQ=368)
**Status:** FIXED
**Error Category:** Compilation — $140 Unknown symbol
**Severity:** Medium — model translates but GAMS compilation fails (3 errors)
**Sprint:** 22 Day 12

---

## Problem Summary

After resolving the empty parameter declaration issue (#917), the ps5_s_mn MCP still fails to compile because the parameter `p(i)` is referenced in stationarity equations but never declared or assigned. This is the same root cause as the ps10_s_mn issue — `p(i)` is a loop-local variable assigned inside the solve loop.

---

## Error Details

### Primary error: $140 Unknown symbol `p` (line 119)

```gams
stat_b(i).. ((-1) * p(i)) + nu_rev(i) - piL_b(i) =E= 0;
****                  $140
```

`p(i)` also appears in:
- Line 120: `stat_w(i).. ((-1) * (p(i) * (-1))) - lam_pc(i) - ...`
- Line 133: `obj.. util =E= sum(i, p(i) * (b(i) - w(i)));`

### Cascading: 2 errors

- **$257 (line 176)**: Solve statement not checked
- **$141 (line 179)**: `Util.l` has no value

---

## Root Cause

Identical to ps10_s_mn (#1101). In the original `ps5_s_mn.gms`, `p(i)` is assigned inside the solve loop:

```gams
loop(t,
   p(i) = pt(i,t);
   solve SB_lic maximizing Util using nlp;
   ...
);
```

The KKT transformation references `p(i)` in stationarity equations and the objective, but the parameter is neither declared nor initialized in the MCP output because its only assignment is loop-local.

---

## Fix Details

Fixed by the same `emit_pre_solve_param_assignments()` function as #1101:

**Files modified:**
- `src/emit/original_symbols.py`: `emit_pre_solve_param_assignments()` detects loop-body parameter assignments before `solve` statements and emits them with the loop index substituted by the first element
- `src/emit/emit_gams.py`: Calls the new function

**Output:**
```gams
Parameter p(i);
p(i) = pt(i,'1');
```

**Verification:**
- GAMS compilation: 0 errors (was 3)
- MODEL STATUS 1 (Optimal)
- All 4209 tests pass, no regressions

---

## Related Issues

- #917: Empty parameter declarations removed (prerequisite fix)
- #1101: ps10_s_mn — identical root cause, same fix

---

## Impact

1 primary compilation error. Model now compiles and solves successfully.
