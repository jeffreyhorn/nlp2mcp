# KKT Dimension Mismatch: chem Model

**Status:** Open  
**Priority:** High  
**Component:** KKT System / MCP Generation  
**Model:** chem (GAMSLIB)  
**GitHub Issue:** #600

---

## Summary

The chem model fails to compile with GAMS Error 70 "The dimensions of the equ.var pair do not conform". The stationarity equations for indexed variable `x(c)` are being unrolled to scalar equations, but they're paired with the indexed variable `x` in the MCP declaration.

## Error Message

```
****  70  The dimensions of the equ.var pair do not conform
**** 256  Error(s) in analyzing solve statement.
**** The following MCP errors were detected in model mcp_model:
****  70 x dimensions are different
****  70 x dimensions are different
... (10 occurrences for each element of set c)
```

## Root Cause Analysis

### Generated MCP Model Declaration

```gams
Model mcp_model /
    stat_x_H.x,
    stat_x_H2.x,
    stat_x_H2O.x,
    stat_x_N.x,
    ...
/;
```

The issue is:
- Stationarity equations are unrolled to scalars: `stat_x_H`, `stat_x_H2`, etc.
- But they're paired with the indexed variable `x` (not `x("H")`, `x("H2")`, etc.)

### Expected vs Actual

**Expected (Option A - Keep indexed):**
```gams
Equations
    stat_x(c)
;
stat_x(c).. gplus(c) + log(x(c) / xb) + ... =E= 0;

Model mcp_model /
    stat_x.x,
    ...
/;
```

**Expected (Option B - Unroll both):**
```gams
Variables
    x_H, x_H2, x_H2O, ...  * Unrolled scalar variables
;
Equations
    stat_x_H, stat_x_H2, ...
;

Model mcp_model /
    stat_x_H.x_H,
    stat_x_H2.x_H2,
    ...
/;
```

**Actual (Broken - Mixed):**
```gams
Variables
    x(c)  * Indexed variable
;
Equations
    stat_x_H, stat_x_H2, ...  * Unrolled scalar equations
;

Model mcp_model /
    stat_x_H.x,  * MISMATCH: scalar equation paired with indexed variable
    stat_x_H2.x,
    ...
/;
```

## Steps to Reproduce

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/chem.gms -o /tmp/chem_mcp.gms

# Run GAMS
gams /tmp/chem_mcp.gms lo=3
```

## Technical Details

### Why Equations Are Unrolled

The stationarity equations for `x(c)` are being unrolled because:
1. The variable `x(c)` has lower bounds: `x.lo(c) = .001;`
2. Each lower bound creates a complementarity constraint
3. The bound multipliers are named `piL_x_H`, `piL_x_H2`, etc. (scalar names with element suffix)
4. The stationarity equations reference these scalar multipliers, forcing unrolling

### Observation from Generated Code

```gams
* Variables
Positive Variables
    x(c)           * Indexed
    piL_x_H        * Scalar (unrolled)
    piL_x_H2       * Scalar (unrolled)
    ...

* Stationarity equations (unrolled to match scalar multipliers)
stat_x_H.. gplus("H") + ... - piL_x_H =E= 0;
stat_x_H2.. gplus("H2") + ... - piL_x_H2 =E= 0;
```

The bound multipliers are being created as scalars instead of indexed variables. This forces the stationarity equations to unroll, but the MCP pairing still uses the indexed variable `x`.

## Files Involved

- `src/kkt/multipliers.py` - Multiplier variable generation
- `src/kkt/stationarity.py` - Stationarity equation generation  
- `src/emit/model.py` - MCP model declaration emission
- `src/emit/emit_gams.py` - Overall emission orchestration

## Suggested Fix

**Option 1: Keep bound multipliers indexed**
- Create `piL_x(c)` instead of `piL_x_H`, `piL_x_H2`, etc.
- Keep stationarity equations indexed: `stat_x(c)`
- MCP pair: `stat_x.x`

**Option 2: Unroll variables too**
- If equations must be unrolled, also unroll the primal variable
- Create `x_H`, `x_H2`, etc. as scalar variables
- MCP pairs: `stat_x_H.x_H`, `stat_x_H2.x_H2`, etc.

Option 1 is preferred as it's cleaner and more general.

## Related Issues

- May be related to how bounds with indexed variables are handled
- Similar pattern may affect other models with indexed variables that have bounds

---

## GitHub Issue

**Issue #:** 600  
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/600
