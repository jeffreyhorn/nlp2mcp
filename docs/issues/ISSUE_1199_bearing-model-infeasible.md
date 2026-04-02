# bearing: MCP Model Infeasible (MODEL STATUS 5)

**GitHub Issue:** [#1199](https://github.com/jeffreyhorn/nlp2mcp/issues/1199)
**Model:** bearing (GAMSlib SEQ=12, "Design of a Stepping Bearing")
**Error category:** `model_infeasible`
**Severity:** Medium

## Description

bearing translates and compiles cleanly but PATH returns MODEL STATUS 5 (Locally Infeasible). The stationarity equations `stat_ef` and `stat_ep` have constant RHS=-1 (objective gradient) but LHS evaluates to 0 at the initial point, indicating the multipliers don't balance.

Multiple constraint equations also show large infeasibilities, suggesting the KKT conditions have structural issues — likely incorrect or missing Jacobian entries.

## Key Findings

- `stat_ef.. (0)*h + (0.001)*nu_friction - nu_temp_rise - piL_ef =E= -1` — objective gradient term correct (-1 from d(PL)/d(Ef)), but multiplier terms insufficient
- `stat_ep.. nu_pumping_energy - piL_ep =E= -1` — same pattern
- Constraint equations (`comp_limit2`, `friction`, `load_capacity`, etc.) show large infeasibilities at initial point

## Reproduction

```bash
python -m src.cli data/gamslib/raw/bearing.gms -o /tmp/bearing_mcp.gms --skip-convexity-check
(cd /tmp && gams bearing_mcp.gms lo=2)
# MODEL STATUS 5 Locally Infeasible
```

## Fix Approach

1. Verify constraint Jacobian entries are correct (check derivatives of nonlinear constraints)
2. Check if variable initialization is appropriate for this model
3. May be related to the alias differentiation accuracy (#1111 family)
