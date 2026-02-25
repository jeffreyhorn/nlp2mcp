# camcge: Subset Bound Complementarity and Fix-Equation MCP Matching

**GitHub Issue:** [#882](https://github.com/jeffreyhorn/nlp2mcp/issues/882)
**Status:** OPEN
**Severity:** High — Model compiles but 12 MCP matching errors block solve
**Date:** 2026-02-25
**Affected Models:** camcge

---

## Problem Summary

The camcge MCP has 12 "unmatched equation" errors from two related issues:

1. **Bound complementarity equations generated over full set instead of subset**: Lower bound
   equations like `comp_lo_e(i)` are generated for all elements of `i`, but the original model
   only sets `e.lo(it) = 0.01` for the traded subset `it`. For non-traded elements where `e`
   is fixed to 0, the bound equation is meaningless and unmatched.

2. **Scalar fix-equations for non-subset elements**: The emitter generates scalar equations
   like `e_fx_publiques` and `e_fx_services` (for elements NOT in `it`), but these are not
   properly matched in the MCP model block.

---

## Error Details

```
**** MCP pair e_fx_publiques.nu_e_fx_publiques has unmatched equation
**** MCP pair e_fx_services.nu_e_fx_services has unmatched equation
**** MCP pair m_fx_publiques.nu_m_fx_publiques has unmatched equation
**** MCP pair m_fx_services.nu_m_fx_services has unmatched equation
**** MCP pair comp_lo_e.piL_e has unmatched equation       (x2)
**** MCP pair comp_lo_m.piL_m has unmatched equation       (x2)
**** MCP pair comp_lo_pm.piL_pm has unmatched equation     (x2)
**** MCP pair comp_lo_pwe.piL_pwe has unmatched equation   (x2)
**** SOLVE from line 703 ABORTED, EXECERROR = 12
```

---

## Root Cause

### Part 1: Bound Complementarity Over Wrong Domain

The original model sets bounds only on the traded subset:

```gams
e.lo(it) = .01;   m.lo(it) = .01;   pm.lo(it) = .01;   pwe.lo(it) = .01;
```

And fixes non-traded elements:

```gams
e.fx(in) = 0;   m.fx(in) = 0;
```

But the emitter generates complementarity equations for the full set `i`:

```gams
comp_lo_e(i).. e(i) - 0.01 =G= 0;       * Should be comp_lo_e(it)
comp_lo_m(i).. m(i) - 0.01 =G= 0;       * Should be comp_lo_m(it)
comp_lo_pm(i).. pm(i) - 0.01 =G= 0;     * Should be comp_lo_pm(it)
comp_lo_pwe(i).. pwe(i) - 0.01 =G= 0;   * Should be comp_lo_pwe(it)
```

For non-`it` elements (like `publiques`, `services`), the variables are fixed to 0, so
the lower bound constraint `e('services') - 0.01 >= 0` is violated (0 < 0.01). These
equations shouldn't exist for fixed variables.

The corresponding multiplier variables `piL_e(i)`, `piL_m(i)`, etc. are also declared over
the full set `i` but should only exist over `it`.

### Part 2: Scalar Fix-Equations Not Matched

The emitter generates fix-equations for per-instance `.fx` assignments:

```gams
e_fx_publiques.. e("publiques") - 0 =E= 0;
e_fx_services.. e("services") - 0 =E= 0;
```

These scalar equations are paired with scalar multipliers in the model block:

```gams
e_fx_publiques.nu_e_fx_publiques,
e_fx_services.nu_e_fx_services,
```

But GAMS reports these as "unmatched equation" — likely because the variable `e` is already
fixed via `e.fx(i)$(not it(i)) = 0`, making the equation redundant. When a variable is `.fx`-ed,
GAMS removes it from the model, so the equation referencing it has no active variable.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/camcge.gms -o /tmp/camcge_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/camcge_mcp.gms lo=0 o=/tmp/camcge_mcp.lst

# Check for MCP errors:
grep 'unmatched equation\|MCP pair' /tmp/camcge_mcp.lst

# Verify bound equations over wrong domain:
grep 'comp_lo_e\|comp_lo_m\|comp_lo_pm\|comp_lo_pwe' /tmp/camcge_mcp.gms | grep '\.\.'

# Compare with original bounds:
grep 'e\.lo\|m\.lo\|pm\.lo\|pwe\.lo' data/gamslib/raw/camcge.gms
```

---

## Suggested Fix

### Fix 1: Restrict Bound Complementarity to Subset Domain

When generating `comp_lo_e(i)`, detect that the `.lo` bound was only set for subset `it` and
restrict the equation domain accordingly:

```gams
comp_lo_e(it).. e(it) - 0.01 =G= 0;    * Only over it, not all i
piL_e(it)                                 * Multiplier also restricted
```

This requires the KKT builder to track which subset a bound was applied to and use that subset
as the complementarity equation domain.

### Fix 2: Don't Generate Fix-Equations for `.fx`-ed Variables

When a variable is fixed via `.fx`, GAMS removes it from the active model. The emitter should
not generate separate fix-equations (`e_fx_publiques`, etc.) for variables that are already
fixed via the `.fx` assignment. Instead, just the `.fx` assignment is sufficient — GAMS handles
the rest.

Alternatively, if fix-equations are needed for MCP correctness, they should be integrated as
indexed equations with dollar conditions rather than separate scalar equations:

```gams
* Instead of separate scalar equations:
e_fx(i)$(not it(i)).. e(i) =E= 0;
```

**Effort estimate:** ~4-6h

---

## Files Likely Affected

| File | Change |
|------|--------|
| `src/kkt/assemble.py` | Track subset domain for variable bounds |
| `src/emit/emit_gams.py` or `src/emit/templates.py` | Restrict bound complementarity equation domain to bound subset |
| `src/emit/templates.py` | Don't emit scalar fix-equations when variable already `.fx`-ed |

---

## Related Issues

- **Issue #879** (fixed): camcge Jacobian domain index propagation — prerequisite, now resolved
- **Issue #871** (fixed): camcge stationarity subset conditioning
- **Issue #767**: Per-instance bound multipliers not index-guarded — related pattern
