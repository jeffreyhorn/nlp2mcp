# spatequ: MCP Empty Equation with Unfixed Paired Variable

**GitHub Issue:** [#1021](https://github.com/jeffreyhorn/nlp2mcp/issues/1021)
**Status:** OPEN
**Severity:** High — 12 execution errors, solve aborted
**Date:** 2026-03-08
**Affected Models:** spatequ

---

## Problem Summary

The spatequ model (spatial price equilibrium) translates to MCP without compilation errors, but GAMS reports 12 execution errors at solve time: "MCP pair has empty equation but associated variable is NOT fixed." The equations `comp_DOM_TRAD(r,rr,c)` and `comp_PDIF(r,rr,c)` are trivially satisfied (reduce to `0 >= 0`) when `r = rr` because `TCost(r,r,c) = 0` (no trade cost for same-region pairs). The MCP solver requires that variables paired with empty equations be fixed to zero.

---

## Error Details

```
**** MCP pair comp_DOM_TRAD.lam_DOM_TRAD has empty equation but associated variable is NOT fixed
     lam_DOM_TRAD(Reg1,Reg1,Com1)
**** MCP pair comp_DOM_TRAD.lam_DOM_TRAD has empty equation but associated variable is NOT fixed
     lam_DOM_TRAD(Reg1,Reg1,Com2)
...
**** MCP pair comp_PDIF.lam_PDIF has empty equation but associated variable is NOT fixed
     lam_PDIF(Reg1,Reg1,Com1)
...
**** SOLVE from line 210 ABORTED, EXECERROR = 12
```

Total: 12 execution errors (6 for DOM_TRAD same-region pairs, 6 for PDIF same-region pairs), solve aborted.

---

## Root Cause

The parameter `TCost(r,rr,c)` only has data for cross-region pairs:
```gams
TCost(r,rr,c) /Reg1.Reg2.Com1 2, Reg1.Reg2.Com2 3, ..., Reg3.Reg2.Com2 2/
```

Same-region pairs (e.g., `Reg1.Reg1.Com1`) default to 0. This makes the equations trivial:
- `comp_DOM_TRAD(r,r,c)`: `p(r,c) + 0 - p(r,c) =G= 0` → `0 >= 0` (always true, empty)
- `comp_PDIF(r,r,c)`: `-(p(r,c) - p(r,c) - 0) =G= 0` → `0 >= 0` (always true, empty)

In the original NLP model, empty equations are harmless — the solver simply ignores trivially-true constraints. But in MCP, each equation is paired with a variable, and the MCP solver requires that empty equations have their paired variables fixed (typically to 0). Otherwise the complementarity matching is ill-defined.

The emitter's `.fx` logic only fixes variables for instances excluded by explicit dollar conditions (e.g., `$(ord(t) > 1)`). It does not detect data-driven trivially-empty equations.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/spatequ.gms -o /tmp/spatequ_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/spatequ_mcp.gms lo=0 o=/tmp/spatequ_mcp.lst

# Check for empty equation errors:
grep 'empty equation' /tmp/spatequ_mcp.lst

# Verify TCost has no same-region data:
grep 'TCost' /tmp/spatequ_mcp.gms
```

---

## Suggested Fix

Two possible approaches:

### Approach A: Detect data-driven empty equations (preferred)
After generating the MCP, analyze each inequality complementarity equation to detect instances where all variable coefficients are zero (making the equation trivially satisfied). For these instances, emit `.fx` statements to fix the paired multiplier variable to 0.

This requires symbolic or numeric analysis of equation bodies with parameter data substitution, which is complex but general.

### Approach B: Propagate implicit conditions from parameter sparsity
Detect that `TCost(r,rr,c)` is only defined for `r <> rr` and add a dollar condition `$(not sameas(r,rr))` to equations that depend on TCost as their only non-trivial term. This is simpler but less general.

### Approach C: Add global `.fx` for diagonal pairs
For equations with repeated set indices like `(r,rr,c)` where `r` and `rr` share a domain, add `.fx` statements for same-index pairs. This handles the common case of trade/transport models.

**Effort estimate:** 3-6h depending on approach

---

## Files Likely Affected

| File | Change |
|------|--------|
| `src/emit/emit_gams.py` | Detect trivially-empty equation instances and emit `.fx` |
| `src/ad/index_mapping.py` | Possibly extend instance enumeration to detect empty equations |

---

## Related Issues

- Issue #862: sambal KKT domain conditioning (similar pattern of conditioned equations)
- Issue #882: camcge subset bound complementarity (related MCP matching issue)
