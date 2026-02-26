# launch: Scalar-Unrolled Stationarity Equations Paired with Indexed Variables

**GitHub Issue:** [#903](https://github.com/jeffreyhorn/nlp2mcp/issues/903)
**Model:** launch (GAMSlib)
**Error category:** `path_syntax_error`
**GAMS error:** `$70` — The dimensions of the equ.var pair do not conform
**Subcategory:** J (MCP pairing dimension mismatch)

## Description

The `launch` model has 4 indexed variables (`length(s)`, `ms(s)`, `t2w(s)`, `vfac(s)`) with per-element bounds that differ by element. The translator correctly unrolls the stationarity equations into per-element scalar equations (e.g., `stat_length_stage_1`, `stat_length_stage_2`, `stat_length_stage_3`), but pairs each scalar equation with the original indexed variable `length(s)` in the MCP model declaration. GAMS requires both sides of an MCP pairing to have the same dimensionality, producing 12 instances of `$70`.

## Reproduction

```bash
# Run emitted MCP through GAMS:
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams \
    data/gamslib/mcp/launch_mcp.gms lo=3 o=/tmp/launch_test.lst

# Check the error:
grep -A2 'Error  70' /tmp/launch_test.lst
```

Output:
```
*** Error  70 in launch_mcp.gms
    The dimensions of the equ.var pair do not conform
*** The following MCP errors were detected in model mcp_model:
     70 length dimensions are different
     70 ms dimensions are different
     70 t2w dimensions are different
     70 vfac dimensions are different
```

## GAMS Source Context — Per-Element Bounds (lines 90–113)

```gams
length.lo('stage-1') = 125;  length.up('stage-1') = 150;
length.lo('stage-2') =  75;  length.up('stage-2') = 100;
length.lo('stage-3') =  50;  length.up('stage-3') =  70;

ms.lo('stage-1') = .25;  ms.up('stage-1') = .30;
ms.lo('stage-2') = .24;  ms.up('stage-2') = .29;
ms.lo('stage-3') = .16;  ms.up('stage-3') = .21;

t2w.lo('stage-1') = 1.2;  t2w.up('stage-1') = 1.4;
t2w.lo('stage-2') =  .6;  t2w.up('stage-2') =  .75;
t2w.lo('stage-3') =  .7;  t2w.up('stage-3') =  .9;

vfac.lo('stage-1') = 240;  vfac.up('stage-1') = 290;
vfac.lo('stage-2') = 240;  vfac.up('stage-2') = 290;
vfac.lo('stage-3') = 340;  vfac.up('stage-3') = 375;
```

## Emitted MCP Model Pairing (launch_mcp.gms, ~line 380)

```gams
Model mcp_model /
    stat_length_stage_1.length,    * scalar eq (0-dim) paired with indexed var (1-dim) → $70
    stat_length_stage_2.length,
    stat_length_stage_3.length,
    stat_ms_stage_1.ms,            * same mismatch
    stat_ms_stage_2.ms,
    stat_ms_stage_3.ms,
    stat_t2w_stage_1.t2w,
    ...
/;
```

## Root Cause

The translator's bound-handling logic unrolls stationarity equations when per-element bounds differ across elements, because each element needs its own bound multiplier values. However, the MCP pairing generation still maps the unrolled scalar equations back to the original indexed variable.

**Working example (uniform bounds):** Variable `aweight(s)` has uniform bounds (`aweight.lo(s) = 1`), so both equation and variable stay indexed:
```gams
stat_aweight(s).. ... =E= 0;     * 1-dimensional
...
stat_aweight.aweight               * both 1-dim → OK
```

**Failing example (per-element bounds):** Variable `length(s)` has different bounds per element, so the equation is unrolled to scalars:
```gams
stat_length_stage_1.. ... =E= 0;  * 0-dimensional (scalar)
...
stat_length_stage_1.length         * scalar vs 1-dim → $70!
```

## Fix Approach

**Option A (Keep indexed, use conditional bounds):** Instead of unrolling to scalars, keep the stationarity equation indexed over `s` and encode per-element bounds via indexed parameters:
```gams
Parameter length_lo(s), length_up(s);
length_lo('stage-1') = 125; length_lo('stage-2') = 75; length_lo('stage-3') = 50;
length_up('stage-1') = 150; length_up('stage-2') = 100; length_up('stage-3') = 70;

stat_length(s).. ... - piL_length(s) + piU_length(s) =E= 0;
comp_lo_length(s).. length(s) - length_lo(s) =G= 0;
comp_up_length(s).. length_up(s) - length(s) =G= 0;
...
stat_length.length    * both 1-dim → OK
```

**Option B (Unroll variable too):** Create per-element scalar variables and pair accordingly. More invasive — requires rewriting all equation references.

**Recommendation:** Option A is simpler and more maintainable.

**Estimated effort:** 3–4h (translator bound-handling refactor + tests)

## Related Issues

- Primary Subcategory D ($445 negative exponent) already fixed in PR #900
- This $70 error was previously masked by the $445 compile-time errors
- Similar per-element bound patterns may exist in other models
