# cesam2: GAMS Error 141 — wbar3 parameter unassigned (loop body assignment not emitted)

**GitHub Issue:** [#1025](https://github.com/jeffreyhorn/nlp2mcp/issues/1025)
**Status:** OPEN
**Severity:** High — compilation error blocks solve
**Date:** 2026-03-09
**Affected Models:** cesam2

---

## Problem Summary

After fixing Issue #1022 ($187 errors), cesam2 compiles with 2 residual errors. The parameter `wbar3(i,j,jwt)` is declared and referenced in equations and `.l` assignments, but its values are never emitted. This is because the parameter is assigned inside a `loop((ii,jj)$NONZERO(ii,jj), ...)` block in the original model, and the IR's `LoopStatement` body assignments are not extracted into parameter values by the emitter.

GAMS Error $141: "Symbol declared but no values have been assigned."
GAMS Error $257: "Solve statement not checked because of previous errors." (follow-on)

---

## Error Details

```
 284  W2.l(macro,jwt) = wbar2(macro,jwt);
 285  W3.l(ii,jj,jwt) = wbar3(ii,jj,jwt);
****                        $141
**** 141  Symbol declared but no values have been assigned.
 449  Solve mcp_model using MCP;
****                           $257
**** 257  Solve statement not checked because of previous errors
```

---

## Root Cause

In the original cesam2 model (lines 321-334):
```gams
loop((ii,jj)$NONZERO(ii,jj),
   sigmay3(ii,jj)$ival(ii,jj)   = stderr3*ABS(sam0(ii,jj));
   sigmay3(ii,jj)$icoeff(ii,jj) = stderr3;
   vbar3(ii,jj,"1") = -3*sigmay3(ii,jj);
   vbar3(ii,jj,"2") =  0;
   vbar3(ii,jj,"3") =  3*sigmay3(ii,jj);
   wbar3(ii,jj,"1") =  1/18;
   wbar3(ii,jj,"2") = 16/18;
   wbar3(ii,jj,"3") =  1/18;
);
```

The parameter `wbar3` is assigned constant values (`1/18`, `16/18`, `1/18`) inside a loop over `(ii,jj)$NONZERO(ii,jj)`. These are not expression-based — they're simple numeric constants, but conditioned on the loop domain.

The IR captures this as a `LoopStatement` with body statements, but the emitter does not extract parameter assignments from loop bodies into `ParameterDef.values` or `ParameterDef.expressions`. As a result, `wbar3` has 0 values and 0 expressions in the IR, and the emitter declares it but never assigns values.

Note: `vbar3` and `sigmay3` (also assigned in the same loop) have the same problem, but `wbar3` is the one that triggers the $141 error because it's referenced in a `.l` initialization before the solve.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/cesam2.gms -o /tmp/cesam2_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/cesam2_mcp.gms lo=0 o=/tmp/cesam2_mcp.lst

# Check for $141 errors:
grep '$141' /tmp/cesam2_mcp.lst

# Verify wbar3 is declared but never assigned:
grep -n 'wbar3' /tmp/cesam2_mcp.gms
# Expected: declared on line ~47, used in .l init and equations, but no assignment
```

---

## Suggested Fix

Two possible approaches:

### Option A: Emit loop body assignments directly
Extend the emitter to recognize parameter assignments inside `LoopStatement` bodies and emit them as GAMS loop statements in the MCP output. This would preserve the original semantics exactly:
```gams
loop((ii,jj)$NONZERO(ii,jj),
   wbar3(ii,jj,"1") = 1/18;
   wbar3(ii,jj,"2") = 16/18;
   wbar3(ii,jj,"3") = 1/18;
);
```

### Option B: Flatten loop assignments for constant cases
For the specific pattern where loop body assignments are simple constants (not dependent on the loop indices), compute and emit them as flat parameter assignments with the loop condition as a dollar condition:
```gams
wbar3(ii,jj,"1")$NONZERO(ii,jj) = 1/18;
wbar3(ii,jj,"2")$NONZERO(ii,jj) = 16/18;
wbar3(ii,jj,"3")$NONZERO(ii,jj) = 1/18;
```

Option A is more general and handles expression-dependent assignments (like `vbar3(ii,jj,"1") = -3*sigmay3(ii,jj)`).

**Effort estimate:** 4-6h (Option A), 2-3h (Option B)

---

## Files Likely Affected

| File | Change |
|------|--------|
| `src/emit/emit_gams.py` | Add loop statement emission in the parameter assignment section |
| `src/ir/model_ir.py` | Possibly extend LoopStatement to be more easily traversable |
| `src/emit/original_symbols.py` | Extract/emit parameter assignments from loop bodies |

---

## Related Issues

- Issue #1022: cesam2 $187 errors (FIXED — alias of dynamic subset used as domain)
- Issue #881: cesam missing dollar conditions (sibling model)
- Issue #810: lmp2 doubly-nested loop solve
