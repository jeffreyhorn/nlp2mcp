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

> **Day-0 status (Sprint 29 Prep Task 4, 2026-06-25):** harness verdict **Case b**, `max_residual_row = stat_step`, rel = **0.497**, dual-transfer consistent → emit residual exists. The `_fx_`-multiplier warm-start is **known-necessary-but-insufficient** (objective 1.137 → 1.016, MS 5 persists); the **open question** (Unknown 2.2) is whether the residual MS 5 is (a) a fixable emit/warm-start defect — the `piL/piU` bound-complementarity activated at `h0` by the #1449 Layer-4 unfix (**Case b → PROCEED**), or (b) genuine non-convex convergence beyond the warm-start (**Case c → Sprint-30 forcing REPLAN**). rocket is **non-convex**, so the Case-c exit is live.

### Hand-Derived KKT Shape

The initial conditions are emitted as `_fx_` equations `ht_fx_h0.. ht('h0') =e= h_0` (likewise `v`, `m`), each pinned by a free multiplier `nu_*_fx_h0`. The stationarity of a state variable at `h0` must read its objective/dynamics gradient **plus** the `_fx_` multiplier:

```
stat_v('h0')..  ∂(dynamics)/∂v('h0') + nu_v_fx_h0 - piL_v('h0') + piU_v('h0')  =E= 0
```

At the NLP optimum the marginal `v.m('h0')` carries the dual of the fixed condition, so a correct warm-start sets `nu_v_fx_h0.l = v.m('h0')`. The **`step` (time-step) stationarity** `stat_step` couples every interval's dynamics constraint (`step` scales each `h→h+1` integration step), so its residual (0.497) reflects an aggregate dual imbalance across the horizon — the prime emit-residual suspect.

### Expected Emit Pattern

`rocket_mcp_presolve.gms` should (1) warm-start **all** `_fx_`-at-`h0` multipliers (`nu_ht_fx_h0.l = ht.m('h0')`, etc.), and (2) **not** leave a `piL/piU` bound-complementarity active at `h0` after the #1449 unfix re-frees the column (the bound dual must transfer or the row be dropped). The `stat_step` row must carry the full per-interval dynamics Jacobian-transpose. (Hypothesis — to be confirmed by the Day-0 trace.)

### Verification Methodology

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/rocket.gms --json /tmp/phase0_rocket.json
# Baseline reproduction: the CURRENT --nlp-presolve emit (it does NOT yet warm-start
# the _fx_-at-h0 duals — that injection is the proposed fix below; currently MS 5):
.venv/bin/python -m src.cli data/gamslib/raw/rocket.gms --nlp-presolve -o /tmp/rocket_mcp_presolve.gms --quiet
gams /tmp/rocket_mcp_presolve.gms lo=0 o=/tmp/rocket_mcp_presolve.lst ScrDir=/tmp   # run from the REPO ROOT (currently MS 5): the emit's `$include "data/gamslib/raw/rocket.gms"` is repo-relative, so do NOT cd to /tmp; o= puts the listing in /tmp
# Warm-start sufficiency probe (the FIX): add `nu_<var>_fx_h0.l = <var>.m('h0')` for
# ht/v/m to the presolve emit (src/emit/, or hand-edit /tmp/rocket_mcp_presolve.gms),
# then re-run the GAMS solve above and read MODEL STATUS + objective (Day-13: 1.137 -> 1.016, MS 5 persists).
# Regression guard — enumerate the Layer-4-unfix presolve models programmatically
# (the set may change; do not hard-code it):
LAYER4=$( { grep -l "#1449 (Layer 4)" data/gamslib/mcp/*_mcp_presolve.gms 2>/dev/null || true; } \
          | sed 's|.*/||; s/_mcp_presolve\.gms$//')   # || true + single sed pass; safe under set -e/pipefail and on an empty set
echo "Layer-4-unfix models: $LAYER4"   # currently: otpop chain cclinpts rocket
for m in $LAYER4; do
  .venv/bin/python -m src.cli data/gamslib/raw/$m.gms --nlp-presolve -o /tmp/${m}_p.gms --quiet   # re-emit (byte-stability)
  gams /tmp/${m}_p.gms lo=0 o=/tmp/${m}_p.lst ScrDir=/tmp                                                      # re-solve from REPO ROOT (repo-relative $include); o= -> /tmp
done   # both byte- and solve-stability must hold across this set (and the full presolve golden set)
```

- **PROCEED (Case b):** the residual MS 5 is localizable to the `_fx_`-at-`h0` warm-start + the `piL/piU`-at-`h0` bound-complementarity (the #1449 unfix). `max_residual_row = stat_step` rel ≈ 0.5 supports an emit-side residual.
- **REPLAN (Case c):** with **all** `_fx_` duals warm-started and the bound complementarity resolved, if MS 5 still persists with a clean residual → genuine non-convex convergence → **Sprint 30 forcing** (trust-region / homotopy), not an emit fix.

### PROCEED/REPLAN Signal

- **CONDITIONAL PROCEED** — Day-0 Case b on `stat_step` (✅ residual exists), but the **decision is finalized by Task 5** (Unknown 2.2): the `_fx_`-multiplier warm-start is necessary-but-insufficient, so PROCEED only if the *residual* `piL/piU`-at-`h0` question resolves to a localizable emit/warm-start fix; **REPLAN to Sprint 30** if the post-warm-start MS 5 is genuine non-convexity. **Hard requirement:** the general `nu_<var>_fx_<idx>.l = <var>.m(<idx>)` warm-start must **not regress** the presolve models that use the Layer-4 unfix — enumerate the set with `grep -l "#1449 (Layer 4)" data/gamslib/mcp/*_mcp_presolve.gms 2>/dev/null || true` (currently otpop/chain/cclinpts/rocket) — nor the full presolve golden set (byte + solve stability).
- **Traced Fix-Surface (Day-0) — CONFIRMED (Sprint 29 Day 0, 2026-06-29):** harness re-confirmed **Case b**, `max_residual_row = stat_step`, rel = **0.497** (raw 2.27), dual transfer **CONSISTENT** (`/tmp/day0_rocket.json`). The regenerated `rocket_mcp_presolve.gms` shows the `_fx_` multipliers `nu_v_fx_h0` / `nu_ht_fx_h0` / `nu_m_fx_h0` are **declared** (lines 61-63) and **used** in `stat_ht`/`stat_m`/`stat_v` as `nu_*_fx_h0$(sameas(h,'h0'))` (lines 175/176/179), but the presolve dual-transfer block in **`src/emit/emit_gams.py` `_emit_nlp_presolve`** (the `lam`/`piL`/`piU` transfers at `1281`/`1297`/`1310`) emits **no `nu_*_fx_*.l = <var>.m(...)` init** → the `_fx_` multipliers start at 0 at the warm point, leaving the residual that surfaces as `stat_step` (the scalar row carries `- piL_step` and accumulates the un-warm-started `h0` contributions). The #1449 Layer-4 unfix that activates the `h0` bound complementarity is **`src/emit/emit_gams.py:1090` `_emit_presolve_fx_unfix`** (its banner is emitted at `rocket_mcp_presolve.gms:120-122`). **Fix surface = add the `nu_*_fx_*` warm-start transfer near `emit_gams.py:1281`** (sibling to the lam/piL/piU transfers), gated on the residual `piL/piU`-at-`h0` question (Task 5). Trace command rerun: `kkt_residual.py data/gamslib/raw/rocket.gms --json /tmp/day0_rocket.json`.

## Acceptance

rocket presolve MCP → MODEL STATUS 1 with `compare_objective_match` to the NLP `final_velocity` reference, **and** zero byte/solve regression across the Layer-4-unfix presolve models (enumerate via `grep -l "#1449 (Layer 4)" data/gamslib/mcp/*_mcp_presolve.gms 2>/dev/null || true`) and the full presolve golden set. If unreachable after a complete `_fx_` warm-start + bound-complementarity fix, REPLAN the non-convex convergence to Sprint 30.

## Provenance

- #1449 Layer-4 unfix (Sprint 28, the otpop presolve PR) — repaired rocket's broken presolve golden (abort → MS 5, a forward step); introduced the `h0` bound-complementarity question.
- Stale Sprint-27 match (1.0128) does **not** reproduce on current `main` — the Day-13 retest reclassified rocket as a stale-baseline correction, filed as **#1462**, Sprint 29.
