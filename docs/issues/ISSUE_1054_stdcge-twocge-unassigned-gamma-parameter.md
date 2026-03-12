# stdcge / twocge: Unassigned Parameter `gamma` in MCP ($66 Error)

**GitHub Issue:** [#1054](https://github.com/jeffreyhorn/nlp2mcp/issues/1054)
**Status:** OPEN
**Severity:** High — path_syntax_error, model fails to compile
**Date:** 2026-03-11
**Affected Models:** stdcge, twocge

---

## Problem Summary

The stdcge and twocge models' generated MCP files declare the parameter `gamma` but never assign its values. GAMS reports error $66 ("Use of a symbol that has not been defined or assigned") when the stationarity equations reference `gamma`.

Both models are CGE (Computable General Equilibrium) models that share the same Armington function structure and the same root cause.

---

## Error Details

GAMS compilation error (stdcge):
```
Solve mcp_model using MCP;
                           $66,256
****  66  Use of a symbol that has not been defined or assigned
**** 256  Error(s) in analyzing solve statement.
**** The following MCP errors were detected in model mcp_model:
****  66 equation stat_d.. symbol "gamma" has no values assigned
```

GAMS compilation error (twocge):
```
Solve mcp_model using MCP;
                           $66,256
****  66 equation stat_d.. symbol "gamma" has no values assigned
```

---

## Root Cause

In the original GAMS models, `gamma(i)` is a **computed parameter** — its values are assigned via a formula after declaration:

**stdcge:**
```gams
Parameter gamma(i) 'scale par. in Armington func.';
gamma(i) = Q0(i) / (deltam(i)*M0(i)**eta(i) + deltad(i)*D0(i)**eta(i))**(1/eta(i));
```

**twocge:**
```gams
Parameter gamma(i,r) 'scale par. in Armington func.';
gamma(i,r) = Q0(i,r) / (deltam(i,r)*M0(i,r)**eta(i) + deltad(i,r)*D0(i,r)**eta(i))**(1/eta(i));
```

The MCP emitter correctly declares `gamma` as a Parameter and its values appear in the stationarity equations (e.g., `stat_d(i)` contains `gamma(i) * ...`). However, the **assignment statement** that computes `gamma`'s values is not emitted to the MCP file. GAMS sees `gamma` declared but with no data, hence the $66 error.

The emitter needs to either:
1. Evaluate the assignment and emit the resulting data as a data block (`gamma(i) / ... /`)
2. Emit the assignment statement itself (`gamma(i) = Q0(i) / ...`)

---

## Reproduction

```bash
# stdcge
python -m src.cli data/gamslib/raw/stdcge.gms -o /tmp/stdcge_mcp.gms
gams /tmp/stdcge_mcp.gms lo=2
# Error $66: symbol "gamma" has no values assigned

# twocge
python -m src.cli data/gamslib/raw/twocge.gms -o /tmp/twocge_mcp.gms
gams /tmp/twocge_mcp.gms lo=2
# Error $66: symbol "gamma" has no values assigned
```

---

## Verification

Check the generated MCP files:
```bash
grep -n 'gamma' /tmp/stdcge_mcp.gms | head -5
# Shows: declaration and usage in stationarity, but NO assignment
```

---

## Proposed Fix

The MCP emitter (`src/kkt/emitter.py` or similar) must track parameters that are:
1. Declared
2. Used in the emitted stationarity/complementarity equations
3. But whose values come from **computed assignments** rather than data blocks

For such parameters, the emitter should emit the assignment statement (or the evaluated data). This likely requires the emitter to track which parameters have expression-based values (`p_expr` in `ParameterDef`) and emit those assignment statements.

The same pattern may affect other computed parameters like `theta`, `deltam`, `deltad`, `eta`, `phi`, `xie`, `xid` — check that these are also properly assigned.

---

## Related

- #970 twocge MCP locally infeasible (different issue — about KKT correctness)
- #906 twocge missing USA SAM post-solve trade equations (different issue)
- This is a pre-existing issue on main; re-translation with current code exposes the bug
- Other CGE models (irscge, korcge, moncge, splcge, lrgcge, quocge) may share this pattern
