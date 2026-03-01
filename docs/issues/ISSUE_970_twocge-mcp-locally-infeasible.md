# twocge: MCP Locally Infeasible (MODEL STATUS 5)

**GitHub Issue:** [#970](https://github.com/jeffreyhorn/nlp2mcp/issues/970)
**Model:** twocge (GAMSlib)
**Error category:** `gams_error` (MODEL STATUS 5 — Locally Infeasible)
**Prerequisite:** Issue #968 (table continuation overwrite) must be fixed first

## Description

After fixing the SAM table parsing bug (#968), the twocge MCP compiles and runs
without execution errors (0 EXECERROR). The PATH solver completes normally
(SOLVER STATUS 1) but reports the model as **Locally Infeasible** (MODEL STATUS 5).

The infeasibility is in the stationarity equations for the utility variable `UU`:

```
stat_uu(JPN)..  nu_eqUU(JPN) =E= 1 ; (LHS = 0, INFES = 1)
stat_uu(USA)..  nu_eqUU(USA) =E= 1 ; (LHS = 0, INFES = 1)
```

The stationarity equation `stat_uu` requires `nu_eqUU = 1` (from the objective
gradient ∂SW/∂UU = 1), but the solver converges with `nu_eqUU = 0`.

Additionally, the `eqUU` equations show significant infeasibility:
```
eqUU(JPN).. -0.51*Xp(BRD,JPN) - 0.51*Xp(MLK,JPN) + UU(JPN) =E= 0 ; (INFES = 25.5)
eqUU(USA).. -0.50*Xp(BRD,USA) - 0.50*Xp(MLK,USA) + UU(USA) =E= 0 ; (INFES = 30.0)
```

## Root Cause (Hypothesis)

The original NLP model maximizes `SW = sum(r, UU(r))` subject to constraints. The
KKT stationarity for `UU(r)` is `1 - nu_eqUU(r) = 0` → `nu_eqUU(r) = 1`. This is
correct but may conflict with the complementarity conditions or the initial point.

Possible causes:
1. **Initial point**: The `.l` initialization may not provide a feasible starting point
   for the MCP. The original NLP solver finds the optimum from scratch; the MCP solver
   needs a good initial point near the solution.
2. **Missing variable bounds**: Some variables may need tighter bounds or different
   initial values for the PATH solver to converge.
3. **Nonconvexity**: The model has 37 potential nonconvex patterns (prod, power terms).
   The KKT conditions are necessary but not sufficient for nonconvex problems.

## Reproduction

```bash
# Generate MCP (requires #968 fix)
python -m src.cli data/gamslib/raw/twocge.gms -o /tmp/twocge_mcp.gms

# Run through GAMS
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/twocge_mcp.gms lo=3

# Check results
grep "SOLVER STATUS\|MODEL STATUS" /tmp/twocge_mcp.lst
# SOLVER STATUS 1 Normal Completion
# MODEL STATUS  5 Locally Infeasible

grep "INFES" /tmp/twocge_mcp.lst | head -10
```

## Solver Details

```
Path 5.2.01
312 row/cols, 1301 non-zeros, 1.34% dense
6017 iterations
Inf-Norm of Complementarity: 2.91e+00  eqn: stat_q(MLK,USA)
Inf-Norm of Normal Map:      1.20e+00  eqn: stat_uu(USA)
```

## Fix Approach

1. **Improve initial point**: Use the original NLP solution as starting values for
   the MCP variables. This requires solving the NLP first and extracting `.l` values.
2. **Check stationarity construction**: Verify that `stat_uu` is built correctly —
   the objective `SW = sum(r, UU(r))` should produce `∂SW/∂UU(r) = 1`.
3. **Check complementarity pairs**: Verify that `eqUU ⊥ UU` pairing is correct and
   that bounds on `UU` are appropriate.

**Files to investigate:**
- `src/kkt/stationarity.py` — stationarity equation construction
- `src/emit/emit_gams.py` — variable `.l` initialization
- `src/emit/model.py` — MCP model pairing

**Estimated effort:** 4-8h (diagnosis + fix)

## Related Issues

- [#968](https://github.com/jeffreyhorn/nlp2mcp/issues/968) — Table continuation overwrite (RESOLVED — prerequisite)
- [#967](https://github.com/jeffreyhorn/nlp2mcp/issues/967) — Explicit zeros in parameter emission (RESOLVED)
