# Plan: Fix bearing Model Infeasibility (#757, #1199)

**Goal:** Resolve bearing MODEL STATUS 5 (Locally Infeasible) so the MCP
solves to the same optimal value as the original NLP (PL = 19517.332).

**Estimated effort:** 4-6 hours
**Models unblocked:** bearing (and potentially other non-convex models:
chain, lnts, mathopt3, robustlp, agreste)

---

## Current State

The bearing KKT/stationarity equations are **mathematically correct** —
all 13 stationarity equations have been hand-verified. The failure is
purely a PATH solver convergence issue caused by:

1. **Poor default initialization**: All dual variables start at 0, but
   the NLP optimal duals span 14 orders of magnitude (from ~0.1 to ~6.7e8)
2. **Non-convexity**: The model has bilinear/trilinear terms throughout,
   so PATH needs a good starting point
3. **Extreme coefficient range**: 1e-6 to 1e8 in the equation system

Variable scaling IS already emitted (`mu.scale = 1e-6`, `scaleOpt = 1`).
Scaling alone does not fix the problem — PATH needs dual initialization.

Testing confirms that **neither primal nor dual initialization alone
suffices** — both are needed simultaneously to reach MODEL STATUS 1.

---

## Model Structure

| Item | Count | Details |
|------|-------|---------|
| Primal variables | 14 | R, R0, mu, Q, PL, P0, Ef, Ep, h, delta_t, t, W, tmp1, tmp2 |
| Equality constraints | 10 | power_loss, pumping_energy, friction, temp_rise, load_capacity, inlet_pressure, oil_viscosity, temperature, temp1, temp2 |
| Inequality constraints | 3 | radius (≥), limit1 (≥), limit2 (≥) |
| MCP variables | 44 | 14 primal + 10 eq mult + 3 ineq mult + 12 lower bound + 5 upper bound |
| MCP equations | 44 | 13 stationarity + 3 comp + 10 original + 12 comp_lo + 6 comp_up |

NLP optimal: PL = 19517.332
Key duals at optimum: nu_friction = 678.8, nu_inlet_pressure = -6.67e8,
nu_temp1 = 145408.7, nu_temp2 = -4553.1

---

## Fix: NLP Pre-Solve Warm-Start

The proven approach is to add an NLP pre-solve step in the emitted MCP
file that:

1. Defines a temporary NLP model using the original equations
2. Solves the NLP to get primal and dual values
3. Transfers NLP marginals to MCP dual variable initialization
4. Solves the MCP with warm-started primal + dual variables

### Why This Works

- The original NLP equations are **already emitted** in the MCP file
  (they're paired with dual variables in the model statement)
- GAMS allows multiple solve statements in one file
- The NLP solve provides both primal values (via `.l`) and dual values
  (via `.m`) that together give PATH a feasible starting point

### Implementation Plan

#### Phase 1: Emit NLP Pre-Solve Block (2-3h)

**File:** `src/emit/emit_gams.py`

1. **Add a CLI flag** `--nlp-presolve` (or detect automatically for
   non-convex models with convexity warnings)

2. **Emit NLP model statement** before the MCP model statement:
   ```gams
   Model nlp_presolve / power_loss, pumping_energy, friction, ... /;
   Solve nlp_presolve minimizing PL using nlp;
   ```
   Use the original equations from `kkt.model_ir.equalities` and
   `kkt.model_ir.inequalities`, and the objective variable from
   `extract_objective_info()`.

3. **Emit dual transfer assignments** between the NLP solve and MCP solve:
   ```gams
   * Transfer NLP duals to MCP multiplier initialization
   nu_friction.l = friction.m;
   nu_pumping_energy.l = pumping_energy.m;
   ...
   lam_limit1.l = abs(limit1.m);
   lam_limit2.l = abs(limit2.m);
   lam_radius.l = abs(radius.m);
   ```
   - For equality constraints: `nu_<eq>.l = <eq>.m`
   - For inequality constraints: `lam_<eq>.l = abs(<eq>.m)`
     (abs because GAMS ≥ marginals are ≤ 0 but MCP λ must be ≥ 0)

4. **Emit bound multiplier initialization:**
   ```gams
   piL_<var>.l$(abs(<var>.l - <var>.lo) < 1e-6) = <var>.m;
   piU_<var>.l$(abs(<var>.l - <var>.up) < 1e-6) = -<var>.m;
   ```

#### Phase 2: Test and Verify (1-2h)

1. Generate bearing MCP with `--nlp-presolve`
2. Verify MODEL STATUS 1, PL = 19517.332
3. Run full test suite — no regressions
4. Test on other Category B models (chain, lnts, robustlp) to see if
   the approach generalizes

#### Phase 3: Generalize (1h, optional)

1. Consider auto-detecting when pre-solve is needed:
   - Non-convex models (convexity warnings present)
   - Models with extreme coefficient ranges
   - Models with many nonlinear equalities
2. Add test coverage for the pre-solve emission path

---

## Alternative Approaches Considered

### A. Better heuristic initialization (rejected)

Hand-crafting multiplier guesses for each model is not scalable. The NLP
pre-solve automates this for any model where the original NLP solves.

### B. Scaling-only fix (insufficient)

Variable scaling is already emitted. Testing confirmed it does not
suffice — PATH also needs dual initialization.

### C. Accept as unsolvable (rejected)

bearing is a standard GAMSlib model. The KKT is correct. The NLP
pre-solve approach proves it IS solvable with proper initialization.

---

## Reproduction

```bash
# Current (fails)
.venv/bin/python -m src.cli data/gamslib/raw/bearing.gms -o /tmp/bearing_mcp.gms --quiet
cd /tmp && gams bearing_mcp.gms lo=0
# MODEL STATUS 5 Locally Infeasible

# With manual NLP pre-solve (works)
# See verification script below
```

### Verification Script (manual pre-solve proof)

```gams
$onMultiR
$include /tmp/bearing_mcp.gms

Model nlp_presolve / power_loss, pumping_energy, friction, temp_rise,
    load_capacity, inlet_pressure, oil_viscosity, temperature,
    temp1, temp2, radius, limit1, limit2 /;

Solve nlp_presolve minimizing PL using nlp;

* Transfer duals
nu_power_loss.l = power_loss.m;
nu_pumping_energy.l = pumping_energy.m;
nu_friction.l = friction.m;
nu_temp_rise.l = temp_rise.m;
nu_inlet_pressure.l = inlet_pressure.m;
nu_load_capacity.l = load_capacity.m;
nu_oil_viscosity.l = oil_viscosity.m;
nu_temperature.l = temperature.m;
nu_temp1.l = temp1.m;
nu_temp2.l = temp2.m;
lam_radius.l = abs(radius.m);
lam_limit1.l = abs(limit1.m);
lam_limit2.l = abs(limit2.m);

Solve mcp_model using MCP;
display PL.l;
* MODEL STATUS 1 Optimal, PL = 19517.332
```

---

## Key Design Decisions

1. **CLI flag vs auto-detect**: Start with explicit `--nlp-presolve` flag
   for simplicity. Auto-detection can come later.

2. **Model name**: Use `nlp_presolve` to avoid conflicts with the
   original model name or `mcp_model`.

3. **Solve type**: Use `nlp` for general nonlinear, `lp` if the model
   is linear. The original solve type is available in `model_ir`.

4. **Dual sign convention**:
   - Equality (=E=): `nu.l = eq.m` (free sign)
   - Inequality ≤ (negated to ≥ in comp_): `lam.l = eq.m` (already ≥ 0)
   - Inequality ≥: `lam.l = -eq.m` (negate to get ≥ 0)
   - Use `abs()` for safety since the ≤/≥ handling is already in the
     complementarity pairing

---

## Risk Assessment

**Low risk.** The NLP pre-solve is purely additive — it adds a solve
statement before the MCP solve without changing any MCP equations or
structure. The `--nlp-presolve` flag ensures it's opt-in. No regression
risk to existing models.

---

## Files Involved

| File | Change |
|------|--------|
| `src/emit/emit_gams.py` | Add NLP pre-solve emission between model and solve |
| `src/cli.py` | Add `--nlp-presolve` CLI flag |
| `docs/issues/ISSUE_757_*.md` | Update status → FIXED |
| `docs/issues/ISSUE_1199_*.md` | Update status → FIXED |

---

## Related Issues

- #757 — bearing MCP locally infeasible (original report)
- #1199 — bearing model infeasible (Sprint 24 triage)
- #672 — bearing MCP pairing (FIXED)
- #835 — bearing scale attribute emission (FIXED)
