# otpop: MODEL STATUS 5 (Locally Infeasible) — KKT Mismatch

**GitHub Issue:** [#1234](https://github.com/jeffreyhorn/nlp2mcp/issues/1234)
**Status:** OPEN
**Severity:** Medium — Model compiles and PATH solves, but KKT system is infeasible
**Date:** 2026-04-08
**Last Updated:** 2026-04-08
**Affected Models:** otpop

---

## Problem Summary

After fixing compilation errors (#1178) and MCP pairing (#1232), otpop now
compiles and PATH attempts to solve, but reports MODEL STATUS 5 (Locally
Infeasible) with 148 infeasible rows. The MCP objective (1487.96) differs
significantly from the NLP objective (4217.80), indicating incorrect KKT
formulation.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success
- **PATH solve**: MODEL STATUS 5 (Locally Infeasible), 148 INFEASIBLE rows
- **Objective**: MCP=1487.96, NLP=4217.80
- **Pipeline category**: model_infeasible
- **Previous fixes**: #1178 (compilation), #1232 (MCP pairing)

---

## Root Cause (Investigation Needed)

The model has several complex features that may cause KKT formulation issues:

1. **Scalar-constant lead/lag offset**: `pd(tt-l)` where `l /4/` is a scalar
   parameter. This produces `IndexOffset("tt", SymbolRef("l"))` which may not
   be differentiated correctly by the AD engine.

2. **Multi-solve model**: otpop has 3 solve statements (otpop2, otpop3, otpop1).
   nlp2mcp reformulates the last one (otpop1). Post-solve assignments from
   earlier solves may affect variable initialization.

3. **Time-reversal index**: `p(t + (card(t) - ord(t)))` in the objective
   equation `zdef`. While the compilation issue is fixed (#1178), the
   derivative through this complex offset may be incorrect.

4. **Subset domain mismatch**: Variable `d(tt)` is accessed over subset `t`
   in some equations and with lead/lag in conditioned equations. The Jacobian
   contributions may be incomplete.

---

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/otpop.gms -o /tmp/otpop_mcp.gms --quiet
gams /tmp/otpop_mcp.gms lo=0

# Output:
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      5 Locally Infeasible
# **** REPORT SUMMARY :  0 NONOPT, 148 INFEASIBLE
# nlp2mcp_obj_val = 1487.957 (NLP: 4217.80)
```

---

## Potential Fix Approaches

1. **Resolve scalar-constant offsets at IR build time**: Convert `pd(tt-l)`
   → `pd(tt-4)` by evaluating scalar `l /4/` during parsing. This would make
   the Jacobian builder handle it as a standard integer offset.

2. **Debug stationarity equations**: Compare `stat_d`, `stat_p`, `stat_x`
   against hand-computed KKT conditions to identify missing or incorrect
   Jacobian terms.

3. **Verify time-reversal derivative**: Check that `∂zdef/∂x` correctly
   handles the `p(t + (card(t) - ord(t)))` index arithmetic.

---

## Files Involved

- `src/ad/constraint_jacobian.py` — Jacobian computation
- `src/kkt/stationarity.py` — Stationarity equation assembly
- `src/ir/parser.py` — Scalar constant resolution
- `data/gamslib/raw/otpop.gms` — Original model (136 lines)

---

## Related Issues

- #1178 (FIXED) — Compilation errors from malformed index expressions
- #1232 (FIXED) — MCP pairing error (9 unmatched stat_d instances)
- #1224 — mine: ParamRef index offsets unsupported (similar pattern)
