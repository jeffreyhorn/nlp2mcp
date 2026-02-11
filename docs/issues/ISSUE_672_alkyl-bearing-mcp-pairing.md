# Alkyl/Bearing: MCP Equation Pairing Mismatch

**GitHub Issue:** [#672](https://github.com/jeffreyhorn/nlp2mcp/issues/672)

**Issue:** The alkyl and bearing models compile successfully but fail at solve time with "unmatched equation" errors in MCP pairing.

**Status:** Open  
**Severity:** High - Models compile but don't solve  
**Affected Models:** alkyl, bearing  
**Date:** 2026-02-10

---

## Problem Summary

After fixing the case sensitivity bug in bound multiplier keys (Sprint 18 Day 5), alkyl and bearing models now compile successfully. However, they fail during PATH solver execution with MCP pairing errors indicating that some equations have no matching variables.

---

## Reproduction

### Test Case: alkyl.gms

```bash
# Translate the model
nlp2mcp data/gamslib/raw/alkyl.gms -o data/gamslib/mcp/alkyl_mcp.gms

# Run GAMS
cd data/gamslib/mcp && gams alkyl_mcp.gms lo=2

# Check errors
grep "unmatched" alkyl_mcp.lst
```

**Error Output:**
```
**** MCP pair AcidBal.nu_AcidBal has unmatched equation
**** MCP pair AcidDef.nu_AcidDef has unmatched equation
**** MCP pair AlkylDef.nu_AlkylDef has unmatched equation
**** MCP pair AlkylShrnk.nu_AlkylShrnk has unmatched equation
**** MCP pair F4Def.nu_F4Def has unmatched equation
**** MCP pair IsoButBal.nu_IsoButBal has unmatched equation
**** MCP pair OctDef.nu_OctDef has unmatched equation
**** SOLVE from line 287 ABORTED, EXECERROR = 7
```

### Test Case: bearing.gms

```bash
# Translate the model
nlp2mcp data/gamslib/raw/bearing.gms -o data/gamslib/mcp/bearing_mcp.gms

# Run GAMS
cd data/gamslib/mcp && gams bearing_mcp.gms lo=2

# Check errors
grep "unmatched" bearing_mcp.lst
```

**Error Output:**
```
**** MCP pair comp_radius.lam_radius has unmatched equation
**** MCP pair pumping_energy.nu_pumping_energy has unmatched equation
**** SOLVE from line 311 ABORTED, EXECERROR = 2
```

---

## Technical Details

### What "Unmatched Equation" Means

In an MCP (Mixed Complementarity Problem), each equation must be paired with a variable:
- Equality constraint `eq..` pairs with free multiplier `nu_eq`
- Inequality constraint `ineq..` pairs with non-negative multiplier `lam_ineq`

An "unmatched equation" error means:
1. The equation exists in the model
2. But the paired variable either doesn't exist or has the wrong dimension

### Possible Causes

1. **Dimension Mismatch**: The equation and its paired multiplier have different index domains
2. **Missing Multiplier**: The multiplier variable was not declared
3. **Domain Mismatch**: The equation uses a subset but the multiplier uses the full set

### Investigation Needed

Check the generated MCP file for:
```gams
* Look at equation definitions
AcidBal.. ...

* Look at multiplier declarations
Variables
    nu_AcidBal  * Should match equation domain
;

* Look at model statement
Model alkyl_mcp / ... AcidBal.nu_AcidBal ... /;
```

---

## Proposed Investigation Steps

1. **Compare domains**: Check if `AcidBal` equation domain matches `nu_AcidBal` variable domain
2. **Check original model**: See what domain the original equation uses
3. **Trace multiplier generation**: Follow the code path in `src/kkt/` that generates multipliers

### Key Files to Investigate

- `src/kkt/assemble.py`: KKT system assembly
- `src/kkt/stationarity.py`: Stationarity equation generation
- `src/emit/emit_gams.py`: MCP model statement generation

---

## Workaround

Currently none. These models compile but cannot be solved.

---

## Progress Note

These models previously had GAMS Error 69/483 (variable dimension unknown) due to a case sensitivity bug in bound multiplier key generation. That bug was fixed in Sprint 18 Day 5 by changing `partition.py` to use `.keys()` instead of `.items()` for variable iteration.

The models now advance further in the pipeline but encounter this new MCP pairing issue.

---

## References

- GAMS MCP Documentation
- Sprint 18 Day 5 fix for case sensitivity bug
- PATH Solver Documentation
