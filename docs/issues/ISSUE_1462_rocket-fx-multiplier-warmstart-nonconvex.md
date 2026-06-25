# rocket: presolve `nu_*_fx_h0` `_fx_`-multiplier warm-start + non-convex convergence

**GitHub:** #1462
**Status:** DEFERRED → Sprint 29 (carryforward; **stale-baseline correction, NOT a Sprint-28 regression**)
**Filed:** Sprint 28 Day 13 (2026-06-20)

## Summary

rocket (an optimal-control problem — `solve rocket using nlp maximizing final_velocity`, state variables `ht`/`v`/`m` over intervals `h0*h%nh%`, time-step variable `step`) does **not** reach a matching MCP solution. On the Sprint 28 Day-13 full retest it is `model_infeasible` (MS 5). The localized root cause is that the **`nu_*_fx_h0` `_fx_`-multipliers** (for the fixed initial conditions `ht.fx('h0')=h_0`, `v.fx('h0')=v_0`, `m.fx('h0')=m_0`) are **not warm-started**, leaving a nonzero `stat_*('h0')` residual; injecting `nu_*_fx_h0.l = <var>.m('h0')` moves the objective 1.137 → 1.016 but **MS 5 persists** — a deep non-convex case.

## Not a regression — stale-baseline correction

The Sprint-27 DB recorded rocket as `model_optimal_presolve` + match (1.0128), but the **actual Sprint-27 golden aborts (`EXECERROR=1`) on current `main`** (the otpop fixed-column / unmatched-`_fx_`-row pathology), so that match was **stale and does not reproduce**. The only Sprint-28 change to rocket's presolve is the #1449 Layer-4 unfix, which moved it **abort → MS5-infeasible** (a *forward* step). The true Day-0 Match baseline was therefore 61, not 62. (See `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 13".)

## Evidence (Sprint 28 Day 13)

- Cold/warm MCP → **MODEL STATUS 5** (model_infeasible).
- Warm-starting the `_fx_`-at-`h0` multipliers (`nu_*_fx_h0.l = <var>.m('h0')`) moves the objective **1.137 → 1.016** but **does not** clear MS 5 — the warm-start is **necessary but not sufficient** (Unknown 2.1).
- KKT-residual harness (Day-0, 2026-06-25): verdict **Case b**, `max_residual_row = stat_step`, rel = **0.497**, dual-transfer consistent.

## Phase 0: Acceptance Gate

> **Day-0 status (Sprint 29 Prep Task 4, 2026-06-25):** harness verdict **Case b**, `max_residual_row = stat_step`, rel = **0.497**, dual-transfer consistent → emit residual exists. The `_fx_`-multiplier warm-start is **known-necessary-but-insufficient** (objective 1.137 → 1.016, MS 5 persists); the **open question** (Unknown 2.1) is whether the residual MS 5 is (a) a fixable emit/warm-start defect — the `piL/piU` bound-complementarity activated at `h0` by the #1449 Layer-4 unfix (**Case b → PROCEED**), or (b) genuine non-convex convergence beyond the warm-start (**Case c → Sprint-30 forcing REPLAN**). rocket is **non-convex**, so the Case-c exit is live.

### Hand-Derived KKT Shape

The initial conditions are emitted as `_fx_` equations `ht_fx_h0.. ht('h0') =e= h_0` (likewise `v`, `m`), each pinned by a free multiplier `nu_*_fx_h0`. The stationarity of a state variable at `h0` must read its objective/dynamics gradient **plus** the `_fx_` multiplier:

```
stat_v('h0')..  ∂(dynamics)/∂v('h0') + nu_v_fx_h0 - piL_v('h0') + piU_v('h0')  =E= 0
```

At the NLP optimum the marginal `v.m('h0')` carries the dual of the fixed condition, so a correct warm-start sets `nu_v_fx_h0.l = v.m('h0')`. The **`step` (time-step) stationarity** `stat_step` couples every interval's dynamics constraint (`step` scales each `h→h+1` integration step), so its residual (0.497) reflects an aggregate dual imbalance across the horizon — the prime emit-residual suspect.

### Expected Emit Pattern

`rocket_mcp_presolve.gms` should (1) warm-start **all** `_fx_`-at-`h0` multipliers (`nu_ht_fx_h0.l = ht.m('h0')`, etc.), and (2) **not** leave a `piL/piU` bound-complementarity active at `h0` after the #1449 unfix re-frees the column (the bound dual must transfer or the row be dropped). The `stat_step` row must carry the full per-interval dynamics Jacobian-transpose. (Hypothesis — confirmed by the Day-0 trace.)

### Verification Methodology

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/rocket.gms --json /tmp/phase0_rocket.json
# Warm-start sufficiency probe (inject the _fx_-at-h0 duals, re-solve, read MODEL STATUS + objective):
.venv/bin/python -m src.cli data/gamslib/raw/rocket.gms --nlp-presolve -o /tmp/rocket_mcp_presolve.gms --quiet
cd /tmp && gams rocket_mcp_presolve.gms lo=0   # currently MS 5
# Regression guard — enumerate the Layer-4-unfix presolve models programmatically
# (the set may change; do not hard-code it):
LAYER4=$( { grep -l "#1449 (Layer 4)" data/gamslib/mcp/*_mcp_presolve.gms 2>/dev/null || true; } \
          | sed 's|.*/||; s/_mcp_presolve\.gms$//')   # || true + single sed pass; safe under set -e/pipefail and on an empty set
echo "Layer-4-unfix models: $LAYER4"   # currently: otpop chain cclinpts rocket
for m in $LAYER4; do
  .venv/bin/python -m src.cli data/gamslib/raw/$m.gms --nlp-presolve -o /tmp/${m}_p.gms --quiet
done   # byte/solve-stability must hold across this set (and the full presolve golden set)
```

- **PROCEED (Case b):** the residual MS 5 is localizable to the `_fx_`-at-`h0` warm-start + the `piL/piU`-at-`h0` bound-complementarity (the #1449 unfix). `max_residual_row = stat_step` rel ≈ 0.5 supports an emit-side residual.
- **REPLAN (Case c):** with **all** `_fx_` duals warm-started and the bound complementarity resolved, if MS 5 still persists with a clean residual → genuine non-convex convergence → **Sprint 30 forcing** (trust-region / homotopy), not an emit fix.

### PROCEED/REPLAN Signal

- **CONDITIONAL PROCEED** — Day-0 Case b on `stat_step` (✅ residual exists), but the **decision is finalized by Task 5** (Unknown 2.1): the `_fx_`-multiplier warm-start is necessary-but-insufficient, so PROCEED only if the *residual* `piL/piU`-at-`h0` question resolves to a localizable emit/warm-start fix; **REPLAN to Sprint 30** if the post-warm-start MS 5 is genuine non-convexity. **Hard requirement:** the general `nu_<var>_fx_<idx>.l = <var>.m(<idx>)` warm-start must **not regress** the presolve models that use the Layer-4 unfix — enumerate the set with `grep -l "#1449 (Layer 4)" data/gamslib/mcp/*_mcp_presolve.gms` (currently otpop/chain/cclinpts/rocket) — nor the full presolve golden set (byte + solve stability).
- **Traced Fix-Surface (Day-0):** **to be confirmed by the Day-0 trace** — the `_fx_`-multiplier warm-start emit (`src/emit/` presolve dual transfer, the `nu_*_fx_*` block) and the #1449 Layer-4 unfix (`_emit_presolve_fx_unfix`) where the `h0` bound complementarity is (re-)activated. Trace command: `--keep-files` the residual scratch, dump `nu_*_fx_h0.l` / `piL_*('h0')` / `piU_*('h0')` at the NLP point, and cite the `file:line` that omits the `_fx_`-dual warm-start or leaves the orphaned bound row.

## Acceptance

rocket presolve MCP → MODEL STATUS 1 with `compare_objective_match` to the NLP `final_velocity` reference, **and** zero byte/solve regression across the Layer-4-unfix presolve models (enumerate via `grep -l "#1449 (Layer 4)" data/gamslib/mcp/*_mcp_presolve.gms`) and the full presolve golden set. If unreachable after a complete `_fx_` warm-start + bound-complementarity fix, REPLAN the non-convex convergence to Sprint 30.

## Provenance

- #1449 Layer-4 unfix (Sprint 28, the otpop presolve PR) — repaired rocket's broken presolve golden (abort → MS 5, a forward step); introduced the `h0` bound-complementarity question.
- Stale Sprint-27 match (1.0128) does **not** reproduce on current `main` — the Day-13 retest reclassified rocket as a stale-baseline correction, filed as **#1462**, Sprint 29.
