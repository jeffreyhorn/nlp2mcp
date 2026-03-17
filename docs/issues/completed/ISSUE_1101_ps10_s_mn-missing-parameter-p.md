# ps10_s_mn: Missing Parameter `p(i)` in MCP Output ($140)

**GitHub Issue:** [#1101](https://github.com/jeffreyhorn/nlp2mcp/issues/1101)
**Model:** ps10_s_mn (GAMSlib SEQ=369)
**Status:** FIXED
**Error Category:** Compilation — $140 Unknown symbol
**Severity:** Medium — model translates but GAMS compilation fails (3 errors)
**Sprint:** 22 Day 12

---

## Problem Summary

After resolving the empty parameter declaration issue (#917), the ps10_s_mn MCP still fails to compile because the parameter `p(i)` is referenced in stationarity equations but never declared or assigned. The parameter `p(i)` is a loop-local variable assigned inside the solve loop as `p(i) = pt(i,t)`.

---

## Error Details

### Primary error: $140 Unknown symbol `p` (line 124)

```gams
stat_b(i).. ((-1) * p(i)) + nu_rev(i) - piL_b(i) =E= 0;
****                  $140
```

`p(i)` also appears in:
- Line 125: `stat_w(i).. ((-1) * (p(i) * (-1))) - lam_pc(i) - ...`
- Line 138: `obj.. util =E= sum(i, p(i) * (b(i) - w(i)));`

### Cascading: 2 errors

- **$257 (line 181)**: Solve statement not checked
- **$141 (line 184)**: `Util.l` has no value

---

## Root Cause

In the original `ps10_s_mn.gms`, `p(i)` is assigned inside the solve loop:

```gams
loop(t,
   p(i) = pt(i,t);              <- p(i) set from random data pt(i,t)
   solve SB_lic maximizing Util using nlp;
   Util_lic(t) = Util.l;
   ...
);
```

The KKT transformation extracts the inner NLP model `SB_lic` and builds stationarity conditions that reference `p(i)`. However, the emitter does not declare `p(i)` as a parameter or emit the assignment because:

1. `p(i)` is declared as a `Parameter` in the original source but has no static values
2. Its only assignment is inside the loop body
3. Issue #917 fix correctly removed the empty declaration for `p(i)` (it had no values and no expressions)
4. The loop body containing `solve` is skipped by the emitter

---

## Fix Details

**Files modified:**
- `src/emit/original_symbols.py`: Added `emit_pre_solve_param_assignments()` function (~150 lines) that:
  1. Finds loops containing `solve` statements
  2. Extracts pre-solve parameter assignments (statements before the first `solve`)
  3. Emits them with the loop index substituted by the first element of its set
  4. Emits `Parameter` declarations for params that were skipped by the #917 logic
- `src/emit/emit_gams.py`: Added import and call site for the new function

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
- #1102: ps5_s_mn — identical root cause, same fix

---

## Impact

1 primary compilation error. Model now compiles and solves successfully.
