# sambal/qsambal: Objective Mismatch (MCP=1028 vs NLP=3.97)

**GitHub Issue:** [#1239](https://github.com/jeffreyhorn/nlp2mcp/issues/1239)
**Status:** OPEN
**Severity:** Medium — Models solve optimally but objectives differ from NLP
**Date:** 2026-04-09
**Last Updated:** 2026-04-09
**Affected Models:** sambal, qsambal

---

## Problem Summary

After fixing NA values (#1195), both sambal and qsambal solve to MODEL STATUS 1
Optimal but with MCP obj=1028.0 vs NLP obj=3.9682 — a massive mismatch. The KKT
system produces a valid but incorrect optimum.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success
- **PATH solve**: MODEL STATUS 1 Optimal, SOLVER STATUS 1 Normal Completion
- **Objective**: MCP=1028.0, NLP=3.9682
- **Pipeline category**: model_optimal (mismatch)
- **Previous fixes**: #862 (dollar condition), #1195 (NA values)

---

## Root Cause (Investigation Needed)

The model minimizes squared deviations from a SAM (Social Accounting Matrix):

```gams
devsqr.. dev =e= sum((i,j)$xw(i,j), xw(i,j)*sqr(xb(i,j)-x(i,j))/xb(i,j))
              +  sum(i$tw(i), tw(i)*sqr(tb(i)-t(i))/tb(i));
```

Possible causes:

1. **NA cleanup side effect**: Setting `tb(i)$(NA) = 1` and `xb(i,j)$(NA) = 1`
   changes parameter values from NA to 1, which may affect the objective
   function evaluation even for conditioned terms.

2. **Gradient condition not fully propagated**: The gradient condition `$(tw(i))`
   is detected but not applied as an equation-level condition because `t` has
   unconditioned access in `rbal` and `cbal`. The gradient contribution may
   have incorrect terms for NA-affected instances.

3. **Dollar condition in objective sum**: `sum((i,j)$xw(i,j), ...)` and
   `sum(i$tw(i), ...)` — the AD engine's differentiation through conditioned
   sums may not correctly propagate the condition to all derivative terms.

4. **Quadratic form derivative**: `sqr(xb(i,j) - x(i,j)) / xb(i,j)` — the
   derivative involves `2*(xb-x)*(-1)/xb` which should be straightforward,
   but the `$xw(i,j)` condition must be preserved.

---

## Reproduction

**Prerequisite:** GAMSlib raw sources must be downloaded into `data/gamslib/raw/`
(run `python scripts/gamslib/download_models.py`).

```bash
.venv/bin/python -m src.cli data/gamslib/raw/sambal.gms -o /tmp/sambal_mcp.gms --quiet
gams /tmp/sambal_mcp.gms lo=0

# Output:
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      1 Optimal
# nlp2mcp_obj_val = 1028.000 (NLP: 3.9682)
```

Same for qsambal.

---

## Potential Fix Approaches

1. **Verify derivative of conditioned sum**: Hand-compute `∂devsqr/∂x(i,j)`
   and `∂devsqr/∂t(i)` and compare against generated stationarity terms.
   Check that `$xw(i,j)` and `$tw(i)` conditions are correctly preserved.

2. **Check NA cleanup impact**: Try setting NA to a different value (e.g., the
   mean of non-NA values) and see if the objective changes.

3. **Debug stationarity equations**: Compare `stat_x` and `stat_t` against
   hand-computed KKT conditions term by term.

---

## Files Involved

- `src/ad/derivative_rules.py` — Sum differentiation with dollar conditions
- `src/ad/gradient.py` — Objective gradient with conditioned sums
- `src/kkt/stationarity.py` — Stationarity equation assembly
- `data/gamslib/raw/sambal.gms` — Original model (~100 lines)

---

## Related Issues

- #1195 (FIXED) — NA values in stationarity equations
- #862 (FIXED) — Dollar condition + wrong index reference

## Phase 0: Acceptance Gate

> **Day-0 status (Sprint 29 Prep Task 3/4, 2026-06-25):** the MCP=1028 vs NLP=3.97 mismatch above is **stale**. On the current Day-0 DB both sambal and qsambal **match warm** (`model_optimal_presolve`, 3.9682 ≈ 3.9682) and the harness verdict is **Case b**, `max_residual_row = stat_x`, rel = **0.780** (identical signature for both), dual-transfer consistent → **PROCEED**. Because they already match *warm*, the fix is **cold-robustness**, not headline +Match — **REMOVE from the P6 +Match projection** (methodology-already-banked, per `docs/planning/EPIC_4/SPRINT_29/BASELINE_METRICS.md` §3; Class A in COLD_CONVEX_COHORT_SURVEY).

### Hand-Derived KKT Shape

The objective minimizes squared SAM deviations:
`devsqr..  dev =e= sum((i,j)$xw(i,j), xw(i,j)*sqr(xb(i,j)-x(i,j))/xb(i,j)) + sum(i$tw(i), tw(i)*sqr(tb(i)-t(i))/tb(i))`.

For a flow variable `x(i,j)` (where `xw(i,j)` holds), the objective gradient is `-2·xw(i,j)·(xb(i,j)-x(i,j))/xb(i,j)`, and `stat_x(i,j)` must add the constraint Jacobian-transpose from the balance rows (`rbal`/`cbal`) in which `x(i,j)` appears:

```
stat_x(i,j)$xw(i,j)..  -2·xw(i,j)·(xb(i,j)-x(i,j))/xb(i,j) + sum(g∈{rbal,cbal}, ∂g/∂x(i,j)·nu_g)  =E= 0
```

A `stat_x` residual of **0.780** (identical for sambal/qsambal) indicates a dropped/mis-conditioned term — most likely the `$xw(i,j)` dollar-condition not fully propagated to all derivative terms, or an `rbal`/`cbal` cross-term omitted where `x` has unconditioned access.

### Expected Emit Pattern

`sambal_mcp.gms` / `qsambal_mcp.gms` `stat_x(i,j)` should carry the conditioned quadratic gradient **and** the full `rbal`/`cbal` Jacobian-transpose terms, with the `$xw(i,j)` condition preserved on every term. (Hypothesis — to be confirmed by the Day-0 trace.)

### Verification Methodology

```bash
for m in sambal qsambal; do
  .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms --json /tmp/phase0_$m.json
done
```

- **PROCEED (Case b):** `max_residual_row = stat_x`, rel ≈ 0.78 (both). ✅ confirmed Day-0.
- **REPLAN (Case c):** clean residual but cold PATH diverges → Sprint 30. (Not the case here.)
- Post-fix: residual → 0 (Case a) and `compare_objective_match` on the **cold** solve for both models.

### PROCEED/REPLAN Signal

- **PROCEED (cold-robustness)** — Day-0 Case b on `stat_x`, rel ≈ 0.78 for both (✅). Not a +Match; lifts the genuine floor.
- **Traced Fix-Surface (Day-0):** **to be confirmed by the Day-0 trace** — the dollar-condition propagation in the AD layer (`src/ad/derivative_rules.py`) and/or the conditioned-sum gradient in `src/kkt/stationarity.py`. Trace command: regenerate `sambal_mcp.gms`, grep `stat_x`, and confirm which term is dropped/mis-conditioned vs the hand-derived shape; cite the `file:line`.
