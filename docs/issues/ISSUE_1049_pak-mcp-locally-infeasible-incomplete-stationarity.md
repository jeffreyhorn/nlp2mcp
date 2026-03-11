# pak: MCP Locally Infeasible — Incomplete Stationarity at stat_s('1985')

**GitHub Issue:** #1049 (https://github.com/jeffreyhorn/nlp2mcp/issues/1049)
**Status:** Open
**Severity:** Medium — Model translates without structural errors, but PATH reports locally infeasible
**Date:** 2026-03-11
**Affected Models:** pak

---

## Problem Summary

After fixing the structural MCP errors (#1042 unmatched equation, resolved by #1045 lead/lag fix), the pak model now reaches the PATH solver without structural pairing errors. However, PATH reports **Locally Infeasible** (MODEL STATUS 5, SOLVER STATUS 1). The largest infeasibility is at `stat_s('1985')` with a normal map residual of 1.163e+05.

---

## Root Cause Analysis

The stationarity equation for variable `s(t)` appears incomplete:

```gams
stat_s(t).. ((-1) * nu_invd(t)) + lam_savl(t) - piL_s(t) =E= 0;
```

This only includes contributions from:
1. `invd(t).. inv(t) =E= ks(t+1) - (1 - delta) * ks(t) + s(t)` — gives `-nu_invd(t)`
2. `savl(t).. s(t) =L= sb + alpha * (gnp(t) - gnpb)` — gives `lam_savl(t)`
3. Lower bound on `s(t)` — gives `-piL_s(t)`

However, the original model may have additional constraints referencing `s` with lead/lag expressions that should contribute additional terms to the stationarity. The large residual at `t='1985'` (the terminal period) suggests missing terminal condition terms or investment-savings identity terms.

### PATH Solver Output

```
SOLVER STATUS     1 Normal Completion
MODEL STATUS      5 Locally Infeasible

FINAL STATISTICS
Inf-Norm of Complementarity . .  2.6259e+04 eqn: (stat_s('1985'))
Inf-Norm of Normal Map. . . . .  1.1630e+05 eqn: (stat_s('1985'))
Inf-Norm of Minimum Map . . . .  1.6599e+01 eqn: (incd('1963'))
Inf-Norm of Fischer Function. .  3.0734e+01 eqn: (comp_conl('1963'))

771 row/cols, 5218 non-zeros
20,625 iterations
```

The solver ran 20,625 iterations before concluding the system is locally infeasible. The maximum variable value is `nu_invd('1985') = 1.163e+05`, suggesting the investment dual variable diverges at the terminal period.

---

## How to Reproduce

```bash
python -m src.cli data/gamslib/raw/pak.gms -o data/gamslib/mcp/pak_mcp.gms
cd data/gamslib/mcp && gams pak_mcp.gms
# Check pak_mcp.lst for: "MODEL STATUS 5 Locally Infeasible"
# and "Inf-Norm of Normal Map... stat_s('1985')"
```

---

## Suggested Investigation

1. Compare `stat_s` in the generated MCP with the correct KKT conditions derived manually from `pak.gms`
2. Check if any constraints involving `s` with lead/lag expressions are missing Jacobian entries (related to the #1045 lead/lag fix — some patterns may not be covered)
3. Check if the terminal conditions (transversality conditions) for `s` at `t='1985'` are correctly handled
4. Verify the investment equation `invd(t).. inv(t) =E= ks(t+1) - (1 - delta) * ks(t) + s(t)` generates correct Jacobian entries for `s(t)` across all instances

---

## Related Issues

- #1042 — pak MCP unmatched equation comp_conl(1962) — FIXED (by #1045)
- #1045 — etamac MCP lead/lag stationarity — FIXED (PR #1047)

---

## Files Involved

- `src/ad/constraint_jacobian.py` — Jacobian computation (may need further lead/lag coverage)
- `src/kkt/stationarity.py` — Stationarity equation assembly
- `data/gamslib/mcp/pak_mcp.gms` — Generated MCP file
- `data/gamslib/raw/pak.gms` — Original model
