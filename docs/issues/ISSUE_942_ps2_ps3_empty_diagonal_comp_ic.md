# ps2_f_s / ps2_s / ps3_s_gic / ps3_s_scp: Empty Diagonal MCP Pair for comp_ic(i,i)

**GitHub Issue:** [#942](https://github.com/jeffreyhorn/nlp2mcp/issues/942)
**Status:** OPEN
**Models:** ps2_f_s, ps2_s, ps3_s_gic, ps3_s_scp (GAMSlib)
**Error category:** `gams_error` (EXECERROR = 2 or 3)
**Runtime error:** `MCP pair comp_ic.lam_ic has empty equation but associated variable is NOT fixed`

## Description

These four models share the same root cause: the generated MCP declares a 2D complementarity pair `comp_ic(i,j).lam_ic(i,j)`, but the equation `comp_ic(i,j)` is only meaningful for off-diagonal elements (i != j). The diagonal instances `comp_ic(i,i)` produce empty/trivial equations (they compare a firm's allocation to itself, yielding `0 >= 0`). GAMS requires that all variable instances in an MCP pair either have a non-empty equation or be fixed.

The `lam_ic(i,i)` multiplier variables are declared as `Positive Variable` and paired with `comp_ic` in the model block, but since `comp_ic(i,i)` is empty, GAMS rejects the MCP.

### Affected Models

| Model | Set Size | Diagonal Elements | EXECERROR |
|-------|----------|-------------------|-----------|
| ps2_f_s | 2 (eff, inf) | lam_ic(eff,eff), lam_ic(inf,inf) | 2 |
| ps2_s | 2 (eff, inf) | lam_ic(eff,eff), lam_ic(inf,inf) | 2 |
| ps3_s_gic | 3 (0, 1, 2) | lam_ic(0,0), lam_ic(1,1), lam_ic(2,2) | 3 |
| ps3_s_scp | 3 (0, 1, 2) | lam_ic(0,0), lam_ic(1,1), lam_ic(2,2) | 3 |

## Reproduction

```bash
# Translate and solve:
python -m src.cli data/gamslib/raw/ps2_f_s.gms -o /tmp/ps2_f_s_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/ps2_f_s_mcp.gms lo=2

# Expected error:
# **** MCP pair comp_ic.lam_ic has empty equation but associated variable is NOT fixed
#      lam_ic(eff,eff)
```

## Root Cause

The original NLP constraint is an incentive compatibility (IC) condition:

```gams
* Original: w(i) - theta(i)*x(i) >= w(j) - theta(i)*x(j) for all i,j
ic(i,j).. w(i) - theta(i)*x(i) =g= w(j) - theta(i)*x(j);
```

When `i == j`, this simplifies to `0 >= 0` (trivially true). The KKT builder correctly creates the complementarity equation `comp_ic(i,j)` and multiplier `lam_ic(i,j)` over the full `(i,j)` domain, but the equation body for diagonal elements is empty after simplification.

The emitter pairs `comp_ic.lam_ic` in the MCP model block without excluding diagonal elements:

```gams
Model mcp_model /
    ...
    comp_ic.lam_ic,    * pairs ALL (i,j) including i==j
    ...
/;
```

## Emitted MCP — Offending Equation

```gams
* comp_ic(i,j) generates for all i,j but diagonal is trivial:
comp_ic(i,j).. w(i) - theta(i) * x(i) - (w(j) - theta(i) * x(j)) =G= 0;
* When i==j: w(i) - theta(i)*x(i) - w(i) + theta(i)*x(i) = 0 =G= 0  → empty
```

## Fix Approach

**Option A: Fix diagonal variables to 0.** Add `.fx` statements for diagonal elements:
```gams
lam_ic.fx(i,i) = 0;  * diagonal multipliers are trivially zero
```

This is similar to the #826 fix for decomp. The emitter should detect when a 2D inequality constraint reduces to `0 >= 0` on diagonal elements and fix the corresponding multipliers.

**Option B: Add dollar condition to exclude diagonal.** Modify the equation and MCP pairing:
```gams
comp_ic(i,j)$(ord(i) <> ord(j)).. w(i) - theta(i) * x(i) - (w(j) - theta(i) * x(j)) =G= 0;
lam_ic.fx(i,j)$(ord(i) = ord(j)) = 0;
```

Option A is simpler and consistent with the existing #826 pattern.

**Estimated effort:** 1-2h (extend empty equation detection to 2D complementarity pairs)

## Related Issues

- #826: Decomp empty stationarity equation (similar pattern, already fixed)
- #904: power() non-integer exponent (primary blocker now fixed; this is the secondary blocker)
