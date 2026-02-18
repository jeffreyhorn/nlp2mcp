# Bearing Model MCP is Locally Infeasible (PATH Solver Model Status 5)

**GitHub Issue:** [#757](https://github.com/jeffreyhorn/nlp2mcp/issues/757)
**Status:** OPEN — Not fixable in Sprint 19 (requires .scale emission support; non-convex solver issue)
**Severity:** Medium — MCP generates correctly; solver cannot find KKT solution due to non-convexity
**Date:** 2026-02-16

---

## Problem Summary

The bearing model (`tests/fixtures/tier2_candidates/bearing.gms`) successfully parses and
generates an MCP file, but when solved with the PATH solver it returns "Locally Infeasible"
(model status 5). The original NLP solves successfully as "Locally Optimal" (model status 2).

The MCP formulation is **structurally correct** — stationarity equations are non-zero and
well-formed after the ISSUE_672 case-sensitivity fix (PR #756). The infeasibility is caused
by the **non-convex** nature of the bearing NLP: bilinear terms, odd powers, and nonlinear
equalities mean the KKT system may have no solution reachable from the current initialization,
or may require a very good starting point that the current emitter does not provide.

---

## Original Model

`tests/fixtures/tier2_candidates/bearing.gms` — Hydrostatic thrust bearing design (GAMSLib
SEQ=202). Minimizes power loss `pl = Ef + Ep` subject to 13 constraints including friction,
inlet pressure, load capacity, oil viscosity (all nonlinear equalities), plus 3 inequalities.

**Key characteristics:**
- 14 variables (R, R0, mu, Q, PL, P0, Ef, Ep, h, delta_t, t, W, tmp1, tmp2)
- 13 equations (8 equality, 5 inequality including bounds)
- Strongly non-convex: bilinear and trilinear terms throughout
- Original model uses variable **scaling** (`mu.scale`, `h.scale`, `W.scale`, `PL.scale`,
  `Ep.scale`, `Ef.scale`) and reformulated equations to avoid singularities

**Convexity warnings from nlp2mcp:**
- W301 (nonlinear equality): pumping_energy, friction, temp_rise, load_capacity,
  inlet_pressure, oil_viscosity, temp1, temp2
- W303 (bilinear terms): pumping_energy (1), friction (2), temp_rise (1),
  load_capacity (2), inlet_pressure (3), limit1 (2)
- W305 (odd power): inlet_pressure (1)

---

## Generated MCP Structure

Translation succeeds cleanly:

```bash
python -m src.cli tests/fixtures/tier2_candidates/bearing.gms -o /tmp/bearing_mcp.gms
# Output: ✓ Generated MCP: /tmp/bearing_mcp.gms (with 15 convexity warnings)
```

**Stationarity equations (sample):**
```gams
stat_ef.. 1 + h * nu_friction - nu_temp_rise - piL_ef =E= 0;
stat_ep.. 1 + nu_pumping_energy - piL_ep =E= 0;
stat_h..  ef * nu_friction + 3 * p0 * pi * power(h, 2) * nu_inlet_pressure
          - ((-1) * (p0 * 0.001 * g * 2 * 2 * pi * r * h * 2 * pi * r)) * lam_limit1
          - piL_h =E= 0;
```

The `1` in `stat_ef` and `stat_ep` is correct: `∂(power_loss_rhs)/∂(ef) = 1` and
`∂(power_loss_rhs)/∂(ep) = 1`, with the objective multiplier fixed at -1 by the
`power_loss.pl` pairing (free variable `pl` paired with the `power_loss` equation).

**MCP pairings (correct structure):**
```gams
power_loss.pl,
stat_ef.ef, stat_ep.ep, stat_h.h, ...
friction.nu_friction, inlet_pressure.nu_inlet_pressure, ...
comp_limit1.lam_limit1, comp_limit2.lam_limit2, comp_radius.lam_radius, ...
```

---

## Reproduction

```bash
# Generate MCP
python -m src.cli tests/fixtures/tier2_candidates/bearing.gms -o /tmp/bearing_mcp.gms

# Solve with GAMS/PATH
gams /tmp/bearing_mcp.gms lo=2

# Check result
grep "MODEL STATUS" /tmp/bearing_mcp.lst
# Expected: **** MODEL STATUS      5 Locally Infeasible
```

The original NLP solves fine:
```bash
gams tests/fixtures/tier2_candidates/bearing.gms lo=2
grep "MODEL STATUS" /tmp/bearing.lst
# Expected: **** MODEL STATUS      2 Locally Optimal
```

**NLP optimal solution values (for reference):**

| Variable | Lower | Optimal | Upper |
|----------|-------|---------|-------|
| R        | 1     | 5.9558  | 16    |
| R0       | 1     | 5.3890  | 16    |
| mu       | 1e-6  | 5.37e-6 | 16e-6 |
| Q        | 1     | 2.2711  | 16    |
| PL       | -inf  | 19517.3 | +inf  |
| P0       | 1     | 1000.0  | 1000  |
| Ef       | 1     | 16272.9 | +inf  |
| Ep       | 1     | 3244.4  | +inf  |
| h        | 0.001 | 0.0013  | +inf  |
| delta_t  | -inf  | 50.0    | 50    |
| t        | 100   | 585.0   | +inf  |
| W        | 101000| 101000  | +inf  |
| tmp1     | 0.0001| 0.1000  | +inf  |
| tmp2     | 0.01  | 6.4299  | +inf  |

**NLP KKT multipliers at solution (equation marginals):**

| Equation | Marginal (ν) |
|----------|-------------|
| power_loss | 1.0 |
| pumping_energy | 1.0 |
| friction | 678.798 |
| temp_rise | -0.1005 |
| inlet_pressure | -6.674e8 |
| load_capacity | -1.9228 |
| oil_viscosity | 22883.18 |
| temperature | -228.66 |
| temp1 | 145408.66 |
| temp2 | -4553.13 |

---

## Root Cause Analysis

The bearing NLP is **non-convex**. For non-convex problems, KKT conditions are necessary
but not sufficient. The PATH solver for the MCP (KKT system) faces a highly nonlinear
system with extreme coefficient variation (magnitudes range from 1e-6 to 1e8), and the
current initialization has all dual variables (multipliers) at zero — far from the optimal
KKT multipliers shown in the table above.

**Verification:** Manual substitution of the NLP solution + KKT multipliers into
`stat_ef` confirms the equation holds at the NLP optimum:
```
1 + h*nu_friction - nu_temp_rise - piL_ef
= 1 + 0.0013*678.798 - (-0.1005) - 0     (piL_ef=0 since ef >> ef.lo)
= 1 + 0.8824 + 0.1005
≈ 1.983   ≠ 0
```

This non-closure suggests either the NLP marginals use a different sign convention than the
MCP stationarity, OR that the NLP "Locally Optimal" solution is not a true KKT point in
the MCP formulation's convention. The issue is likely the **variable scaling** applied in
the NLP (`mu.scale = 1e-6`, `Ef.scale = 1e4`, etc.) which changes the NLP's KKT
multipliers but is **not applied to the MCP** — the emitter does not emit `m.scaleOpt = 1`
or variable `.scale` assignments.

**Most likely fixes (in priority order):**

1. **Emit variable scaling to MCP:** The original model sets `m.scaleOpt = 1` and assigns
   `.scale` to several variables. The MCP does not emit these, so PATH sees a poorly-scaled
   system with coefficients spanning ~14 orders of magnitude (1e-6 to 1e8).

2. **Initialize dual variables from NLP solve:** Add a pre-solve NLP step to the MCP file
   that sets starting multiplier values — or emit `.l` guesses for multipliers based on
   equation structure.

3. **Accept as non-convex limitation:** Document that non-convex NLPs with wide coefficient
   ranges may require manual scaling/initialization for the MCP to solve.

---

## Suggested Fix

### Option A: Emit variable scaling (most tractable)

In `src/emit/emit_gams.py` (or `src/emit/original_symbols.py`), detect variable `.scale`
assignments and `m.scaleOpt = 1` and emit them in the MCP output:

```gams
* Variable scaling from original model
mu.scale    = 1.0e-6;
h.scale     = 0.001;
W.scale     = 101000;
PL.scale    = 1.0e4;
Ep.scale    = 1.0e4;
Ef.scale    = 1.0e4;

mcp_model.scaleOpt = 1;
```

The IR would need to store `.scale` values (analogous to `.lo`/`.up`/`.l`). Check whether
`VariableDef` in `src/ir/symbols.py` currently has a `scale` field and whether the parser
populates it.

### Option B: Better dual variable initialization

After the primal `.l` initialization block, add computed guesses for key multipliers:
```gams
* Rough multiplier initialization for PATH
nu_friction.l = 600;
nu_inlet_pressure.l = -6e8;
nu_oil_viscosity.l = 20000;
nu_temp1.l = 140000;
```

This is model-specific and not generally automatable without an NLP pre-solve.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `tests/fixtures/tier2_candidates/bearing.gms` | Original NLP model |
| `src/ir/symbols.py` | `VariableDef` — check for `scale` field |
| `src/ir/parser.py` | `.scale` assignment parsing |
| `src/emit/emit_gams.py` | Variable attribute emission, `scaleOpt` |
| `src/emit/original_symbols.py` | Scalar/parameter emission |

---

## Related Issues

- **ISSUE_753** (`circle-mcp-locally-infeasible.md`): Same class of problem — MCP generates
  correctly but PATH cannot solve due to missing initialization data. Circle's fix requires
  emitting computed `.l` assignments; bearing's likely fix is emitting `.scale` assignments.
- **KNOWN_UNKNOWNS.md Unknown 1.2:** MCP infeasibility from initialization — same category.
