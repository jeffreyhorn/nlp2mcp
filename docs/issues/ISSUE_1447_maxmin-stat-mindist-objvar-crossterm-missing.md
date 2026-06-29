# maxmin: stat_mindist stationarity residual (Case b) — objective-variable cross-term missing

**GitHub:** #1447
**Status:** **Sprint 29 Day 3 (2026-06-29): objvar multi-model-scoping fix LANDED** (`gradient.py`; `stat_mindist` gains the `-1`, residual 1.0→0, maxmin-only blast radius). **Remaining `stat_point` 0.31 offset-alias residual → Day 4** (with himmel16/polygon). _(was: DEFERRED → Sprint 29)_
**Filed:** Sprint 28 Day 5 (2026-06-16)

## Summary

`maxmin` (circle-packing: `solve maxmin1a max mindist using dnlp;`) emits an MCP whose **`stat_mindist` stationarity row is wrong** (Case b). The model reaches MODEL STATUS 1 but at a **wrong objective** (mismatch).

## How it surfaced

**Surfaced, not caused, by #1388** (Sprint 28 Day 5, PR #1446). Before #1388, maxmin's MCP was `path_solve_terminated`. The #1388 offset-cross-term condition-guard fix (correct) changed maxmin's `stat` emit so PATH now converges to a (wrong) MODEL STATUS 1, exposing this separate, pre-existing `stat_mindist` bug.

## Evidence

- Cold solve (post-#1388): **MODEL STATUS 1, obj ≈ 0.104** — a mismatch.
- KKT-residual harness: **Case b**, max-residual row **`stat_mindist`**, residual ≈ **1.0** at the NLP KKT point.

## Root cause (hypothesis)

`mindist` is the **objective variable** (`max mindist`) and appears in `mindist1a(low(n,nn)).. mindist =l= sqrt(sum(d, sqr(point(n,d) - point(nn,d))))`. The objective-variable stationarity should be:

```
stat_mindist..  (-1) + sum(low, lam_mindist1a(low))  =E= 0     (sum of constraint multipliers = 1)
```

A residual of **exactly 1.0** = the bare objective gradient (`-1`) with **nothing balancing it** → the `sum(low, lam_mindist1a)` cross-term is **missing** (or mis-emitted) from `stat_mindist`. `low(n,nn)` is a 2-D subset and `mindist` is scalar, so the gap is plausibly a scalar-objvar ← 2-D-subset-domain-constraint Jacobian-transpose path.

## Scope

- **Sprint 29.** Not a Sprint-28 target. maxmin was already failing (`path_solve_terminated`) — not a regression of a previously-correct behavior, but it now mis-solves (a confident wrong answer).
- maxmin uses **DNLP** (`sqrt` non-smooth at 0; pairwise distances > 0 at a feasible packing) — verify the fix against the NLP/DNLP reference objective once `stat_mindist` is corrected.

## Acceptance

`stat_mindist` residual → 0 at the NLP KKT point (harness Case a), and maxmin's MCP objective matches the NLP/DNLP reference (`compare_objective_match`).

## Phase 0: Acceptance Gate

> **Day-0 status (Sprint 29 Prep Task 3/4, 2026-06-25):** harness verdict **Case b**, `max_residual_row = stat_mindist`, rel = **1.000**, dual-transfer consistent. **PROCEED** confirmed. maxmin already matches *warm* (`model_optimal_presolve`), so the fix is **cold-robustness** (removes the warm-start dependency), not headline +Match — see `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md` (Class A, the lead).

### Hand-Derived KKT Shape

maxmin maximizes the scalar objective variable `mindist` subject to the pairwise lower-bounding constraints
`mindist1a(low(n,nn))..  mindist =l= sqrt(sum(d, sqr(point(n,d) - point(nn,d))))`.

Lagrangian (write the maximize as minimize `-mindist`, so the objective-variable gradient is `-1`; `=l=` constraint `mindist - rhs(low) ≤ 0` with multipliers `lam_mindist1a ≥ 0`):

```
L = -mindist + sum(low, lam_mindist1a(low) · (mindist - rhs(low)))
∂L/∂mindist = -1 + sum(low, lam_mindist1a(low)) · (+1) = 0
⇒  stat_mindist..  (-1) + sum(low, lam_mindist1a(low))  =E= 0
```

The objective-variable stationarity must carry the **`sum(low, lam_mindist1a)` constraint-multiplier cross-term**. A residual of exactly **1.0** = the bare objective gradient (`-1`) with that cross-term **absent** (scalar objvar ← 2-D subset-domain `=l=` constraint Jacobian-transpose path).

### Expected Emit Pattern

`maxmin_mcp.gms` `stat_mindist` should read (modulo sign convention):

```
stat_mindist..  -1 + sum(low(n,nn), lam_mindist1a(n,nn))  =E= 0 ;
```

i.e. the bare `-1` gradient **plus** the full `sum(low, lam_mindist1a(low))` term. (Hypothesis — the actual builder `file:line` is to be confirmed by the Day-0 trace.)

### Verification Methodology

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/maxmin.gms --json /tmp/phase0_maxmin.json
```

- **PROCEED (Case b):** `max_residual_row = stat_mindist`, relative residual ≈ 1.0 (the missing cross-term). ✅ confirmed Day-0.
- **REPLAN (Case c):** clean residual but cold PATH diverges → non-convexity, warm-start not emit fix → Sprint 30. (Not the case here.)
- Post-fix: residual → 0 (Case a) **and** `compare_objective_match` against the NLP/DNLP reference on the **cold** solve.

### PROCEED/REPLAN Signal

> **🟡 PARTIAL FIX LANDED — Sprint 29 Day 3 (2026-06-29).** The Day-0 root was refined again: the dropped `-1` is a **multi-model objective-scoping bug**, not a stationarity-assembly omission. maxmin declares 4 models sharing objvar `mindist`; the solved model `maxmin1a / mindist1a /` has only the indexed `=l=` constraint `mindist1a`, so the objective is the **bare objvar** `mindist` (gradient `-1` after MAX→min). But `find_objective_expression` (`src/ad/gradient.py`) scanned **all** equations and matched `mindist2.. mindist =e= smin(low, dist)` (from the *unsolved* `maxmin2`), differentiating `smin(low, dist)` (no `mindist`) → the `-1` vanished. **Fix:** scope the defining-equation search to `get_solved_model_equations()` (`gradient.py`, #1447). `stat_mindist` now emits `-1 + sum(low, lam_mindist1a) = 0` ✅; harness `stat_mindist` residual 1.0 → 0. **Blast radius: maxmin golden ONLY** (+5 bytes, the `-1 +`; 159 goldens checked, 0 others drifted, 0 failed). 2 unit tests.
>   **Not yet Case a:** the fix exposed a **second** maxmin residual — `stat_point(p6,x)` rel **0.312** — the offset-alias cross-term enumeration over the `low(n,nn)` pair subset (the same `_diff_sum`/`_try_diff_sum_offset_crossterms` class as himmel16/polygon). That is the **Day-4 offset-alias work** (Unknown 7.2 REPLAN gate). maxmin reaches Case a only after BOTH the objvar-scoping fix (landed) and the offset-alias fix (Day 4).

- **PROCEED** — Day-0 Case b on `stat_mindist`, rel ≈ 1.0 (✅ confirmed). _[Day-3: objvar half landed via the gradient-scoping fix; the residual `stat_point` 0.31 offset-alias term → Day 4.]_
- **Traced Fix-Surface (Day-0) — CONFIRMED + hypothesis CORRECTED (Sprint 29 Day 0, 2026-06-29):** harness re-confirmed **Case b**, `max_residual_row = stat_mindist`, rel = **1.00** (raw 1.00), dual transfer **CONSISTENT** (`/tmp/day0_maxmin.json`). **⚠️ The prep hypothesis named the wrong dropped term (PR24 catch).** The regenerated `maxmin_mcp.gms:98` emits `stat_mindist.. sum((n,nn)$(low(n,nn)), lam_mindist1a(n,nn)$(nn(nn))) =E= 0` — the constraint sum **is present**; what is dropped is the **objective-gradient term**. maxmin **maximizes `mindist`**, so its stationarity must read `-1 + sum((n,nn)$low, lam_mindist1a) = 0`; the emitted row omits the leading `-1` → residual exactly **1.0** (= |objective gradient|). So the bug is the **missing objective-gradient coefficient on the objvar's own stationarity row**, not a dropped constraint cross-term. **Surface:** the objective-variable stationarity assembly in `src/kkt/stationarity.py` — `build_stationarity_equations` (:2090, the `should_skip_objvar` branch at :2129 correctly keeps mindist's row because it appears in constraints) → `_build_indexed_stationarity_expr` (:2650) / the objective-gradient merge at :2222 — which omits the objvar's own objective-gradient contribution when the objvar *also* carries a stationarity row. Trace command: `kkt_residual.py data/gamslib/raw/maxmin.gms --json /tmp/day0_maxmin.json` + `grep stat_mindist maxmin_mcp.gms`. The exact integer residual (1.0) shared with himmel16 (`stat_area` 2.0) / like (`stat_p` 2.0) supports a **shared Class-A fix** (COLD_CONVEX_COHORT_SURVEY §4) — though note himmel16/polygon route additionally through the offset-alias AD (#1146/#1143), so "shared" = the objvar/defining-row gradient assembly, not necessarily a single line.

## Provenance

- #1388 camshape offset-cross-term guard fix (Sprint 28 Day 5, PR #1446) — surfaced this. maxmin's `_mcp.gms` golden was regenerated there (the correct guard re-index); its `stat_mindist` cross-term gap is **this** issue.
