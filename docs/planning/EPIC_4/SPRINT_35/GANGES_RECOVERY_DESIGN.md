# Sprint 35 — ganges/gangesx Multi-Root Recovery Design (Priority 4)

**Prep Task:** 5 (Critical, on the critical path) · **Date:** 2026-07-24 · **Owner:** Sprint 35 prep (emit/AD)
**Day-0 code anchor:** `78ceaead` (S34 close) · **Measurement tree:** `5080fca2` (`main` at the S35 prep Task-4 merge) — docs-only ahead of the anchor, `src/`/`scripts/` byte-identical
**Scope:** docs/design only — re-validates the banked `$141` fix (in a scratch tree, reverted), designs the `$145` skip, specifies the `$149` correction from Task 4, and sequences the landing. **No `src/` change ships in this task.**

---

## Executive summary

P4 recovers **ganges and gangesx** — and only those two — by landing **three independent root fixes together**: `$141` (NaN-cleanup over presolve-gated `.l`-calibration params), `$145` (NaN-cleanup over a universal-set `*`-domain param), and `$149` (the CES/LES product-rule AD bug, Task 4). Task 4 already established that `$149` is a *code, not a root* and that dinam/indus/turkpow/clearlak are **not** P4 beneficiaries; this task confirms the same multi-root structure from the other direction and pins the landing sequence.

**The central empirical result — the multi-root sequencing is now proven, not asserted.** Re-emitting ganges with **only** the `$141` fix applied (reconstructed in a scratch tree) and compiling gives:

| Stage | `$141` | `$145` | `$149` | Compiles? |
|---|---:|---:|---:|---|
| Day-0 (no fix) | 15 | 3 | 9 | ✗ |
| **+`$141` fix only** | **0** | **3** | **9** | **✗ — still fails** |
| +`$141`+`$145` (design) | 0 | 0 | 9 | ✗ — still fails |
| +`$141`+`$145`+`$149` (design) | 0 | 0 | 0 | ✓ (target) |

So the S34 finding is confirmed directly: **fixing `$141` alone removes its 15 markers but recovers nothing** — ganges still fails to compile on `$145` and `$149`. **No bucket moves until all three land.** A mid-sequence flat KPI is the *expected* state, not a failure, and the landing must be read that way.

**The three roots and their surfaces:**

| Root | Cause | Fix surface | Status |
|---|---|---|---|
| **`$141`** ×15 | NaN-cleanup guard emitted over `.l`-calibration params (`adst(i)=dst.l(i)/…`) that are presolve-gated → declared-but-unassigned in the cold MCP | `src/emit/original_symbols.py:emit_post_assignment_na_cleanup` — skip params whose assignment references a `VarRef` attribute | **banked + re-validated (15→0)** |
| **`$145`** ×3 | NaN-cleanup guard emitted over `series(*,years)` — a **universal-set `*`-domain** param; `*` is invalid as an assignment index | same function — skip params whose domain contains `*` | **designed (independence confirmed)** |
| **`$149`** ×9 | CES/LES `prod(j, (pc(j)/pc00(j))**ac(j,r))` derivative leaves `j` free (Task 4) | **AD layer** — `src/ad/derivative_rules.py:_diff_prod` (~3395) | **spec from Task 4** |

**turkey `$161` → P6, not P4.** turkey shares no root or fix surface with ganges (a dotted-tuple set-declaration emit issue; turkey has *no* `$149`). It belongs in the P6 residual cohort as a separate, small item.

**Collateral (a design consideration the landing must handle).** The `$141` fix is a *general* cleanup-pass change: it removes the NA-cleanup guard for **every** param whose assignment references `.l`, across all models. Beyond ganges/gangesx that touches ~9 more `.l`-calibration models (chakra, dinam, gancnsx, prolog, saras, senstran, shale, tfordy, turkey) — **but not the data-calibrated CGE cluster** (irscge/lrgcge/moncge/stdcge calibrate from data params like `Xp0`/`Y0`/`F0`, not `.l`, verified). That is **golden-byte drift with no bucket change** (removing a no-op guard on a finite param), so it is `--resolve-changed`-safe but forces those goldens to be regenerated. Task 3's measured budget covers the 4 slow models; the collateral adds mostly fast models plus shale/gancnsx, all enumerated and regenerated at landing via the scoped `--models` regen.

**REPLAN exit:** the deep risk is `$149` (Task 4's AD-layer surgery). If the `_diff_prod` correction proves to require a general AD-core restructure of `prod` differentiation that risks the 18-model regression set, land `$141`+`$145` (which still recover nothing alone — so **no `src/` ships**, per the discipline) and REPLAN `$149` to a dedicated AD effort; the freed P4 budget goes to P6/P7.

---

## §1. `$141` — banked fix re-validated against the current tree (Unknown 4.1)

### Root

The NaN-cleanup pass (`emit_post_assignment_na_cleanup`, Issue #1322) emits `param(d)$(NOT (param(d) > -inf and param(d) < inf)) = 0;` for every indexed param whose assignment contains a division. ganges's calibration params — `adst`, `aex`, `aid`, `an`, `as`, `av`, `az`, `cg`, `deltan/s/v/x/z`, … — are computed from a **solved base-year equilibrium stored in variable levels**:

```
adst(i)  = dst.l(i)/sum(j, dst.l(j));       aid(i)  = id.l(i)/sum(j, id.l(j));
deltax(i) = (z.l(i)/g.l(i))**(1/sigmax(i))*pz.l(i)/pg.l(i);   cg(i) = dat("pub-cons",i)/pc.l(i);
```

These assignments reference variable levels (`dst.l`, `id.l`, `z.l`, `pc.l`, …), so nlp2mcp emits them **only under `--nlp-presolve`** (they need the warm-start solve). In the **cold** MCP the assignment is absent, so the param is **declared but never assigned**, and the cleanup guard `adst(i)$(NOT (adst(i) > -inf …))` reads an unassigned symbol → GAMS **`$141`** ("Symbol declared but no values assigned"), ×15.

*(Distinct from the CGE cluster: irscge's `alpha(i)=Xp0(i)/sum(j,Xp0(j))`, `b(j)=Y0(j)/prod(h,F0(h,j)**beta(h,j))` etc. calibrate from **data** params `Xp0`/`Y0`/`F0`, which are assigned unconditionally — so those models never hit `$141`, and the fix below does not touch them.)*

### Fix (reconstructed + re-validated, then reverted)

Add a helper mirroring `_param_assignment_has_division` and a skip in the cleanup loop:

```python
def _expr_contains_varref_attr(expr: Expr) -> bool:
    # True if any subexpression is a VarRef with a non-empty attribute (.l/.m/…)
    if isinstance(expr, VarRef) and expr.attribute:
        return True
    return any(_expr_contains_varref_attr(c) for c in expr.children())

def _param_assignment_references_varref_attr(param_def: ParameterDef) -> bool:
    return any(_expr_contains_varref_attr(expr) for _key, expr in param_def.expressions)
```

and, in `emit_post_assignment_na_cleanup`, immediately after the existing division filter:

```python
        if _param_assignment_references_varref_attr(param_def):
            continue   # presolve-gated calibration → unassigned in the cold MCP → $141
```

`VarRef` is already imported at module scope; `.attribute` is the AST field carrying `"l"`/`"m"`/`"lo"`/`"up"` (`src/ir/ast.py:53`). This matches the S34 banked fix (`SPRINT_34/DAY11_PROGRESS_NOTES.md`) exactly.

### Re-validation (empirical, this task)

Applied the fix in a scratch tree, re-emitted ganges (`.venv/bin/python -m src.cli`, ~200 s), compiled (`gams a=c`):

- **`$141`: 15 → 0.** ✓ Clean apply against the current tree (`_param_assignment_has_division` at `:137`, `emit_post_assignment_na_cleanup` at `:152`, unchanged).
- **`$145×3` and `$149×9` remain** — ganges still fails to compile. This is the multi-root proof (§4): `$141` alone recovers nothing.
- Scratch patch **reverted**; `src/` is clean (this is a design task, not the landing).

### Collateral

The fix is general — it drops the cleanup guard for any `.l`-referencing division param, model-wide. Scanned the corpus for `.l`-and-division param assignments: beyond ganges/gangesx, the affected set is **chakra, dinam, gancnsx, prolog, saras, senstran, shale, tfordy, turkey** (≈ 9), and **not** the CGE cluster. The change is a no-op on those models' *solutions* (it removes a guard that was harmless on their finite, assigned params) → **golden-byte drift only, no bucket change** — so `--resolve-changed` stays GO but the goldens must be regenerated. **Warm-context note:** in the presolve emit the `.l`-param *is* assigned (finite base-year calibration), so the removed guard was a no-op there too — safe — but the landing's `--resolve-changed` must confirm bucket-stability on any collateral model that has a presolve golden (e.g. shale). Enumerate the exact drift set with `--resolve-changed --since-commit 78ceaead` at landing; regenerate via the scoped `--models` path (Task 3).

---

## §2. `$145` — universal-set (`*`-domain) skip (Unknown 4.2)

### Root, and its independence from `$141`

`series(*,years)` is declared `Table series(*,years)` — its **first domain is the universal set `*`**. Its assignments contain division (`series("pim1",years) = series("pim1",years)/series("usdefl",years)`), so the cleanup filter fires and emits:

```
series(*,years)$(NOT (series(*,years) > -inf and series(*,years) < inf)) = 0;
```

`*` is a valid domain placeholder in a *declaration* but **not a valid index in an assignment/`$`-guard** → GAMS **`$145`** ("Set identifier or quoted element expected"), ×3 (on the `series(*,years)` references).

**Independent of `$141`, confirmed two ways:** (a) `series` references **no `.l`** (it divides one `series` element by another), so the `$141` `_param_assignment_references_varref_attr` skip does **not** cover it; (b) `series` **is** assigned (unconditionally, source lines 310+), so it is not a declared-unassigned `$141` — it is a `*`-syntax error. The re-validation in §1 confirms it directly: with the `$141` fix applied, the 3 `$145` **remain**.

### Fix design

In the same `emit_post_assignment_na_cleanup` loop, skip params whose domain contains the universal set:

```python
        if any(d == "*" for d in param_def.domain):
            continue   # universal-set domain: '*' is invalid as an assignment index → $145
```

Placed alongside the `$141` skip. Rationale: a `*`-domain param has no named index set the guard can iterate; the guard is structurally malformed regardless of NA-ness. (An alternative — emit the guard over the param's *concrete* runtime labels — is far more complex and unnecessary: a `*`-domain data table like `series` is not the division-by-zero NA source Issue #1322 targets.) **Minimal reproducing shape** for a fixture: `Table p(*,s) / a.s1 1, a.s2 2 /` with an assignment `p("a",s) = p("a",s)/q(s);` → the cleanup emits `p(*,s)$(NOT …)` → `$145`.

**Blast radius:** any model with a `*`-domain param that has a division assignment. This is rare (universal-set params are almost always pure data tables); enumerate at landing via `--resolve-changed`. Confirmed present on ganges/gangesx (`series`); to be checked corpus-wide at landing.

---

## §3. `$149` — product-rule correction (spec from Task 4; Unknown 4.3 contribution)

Task 4 (`GANGES_149_PRODUCT_RULE_ANALYSIS.md`) is the primary. Summary of what P4 lands:

- **Root:** differentiating `prod(j, (pc(j)/pc00(j))**ac(j,r))` w.r.t. `pc(i)` emits a `body_deriv/body` factor that references the product's bound `j` **outside** the `prod(j,…)` scope → `j` uncontrolled → `$149`, ×9, all on `stat_pc(i)`.
- **Correct cross-term (hand-derived):** `prod(j, (pc(j)/pc00(j))**ac(j,r)) * ac(i,r)/pc(i)` — `i` controlled, no free `j`.
- **Surface:** the AD layer — `src/ad/derivative_rules.py:_diff_prod` (~3395, the Issue-#1330 `symbolic_name_match` collapsed branch that emits `expr * (body_deriv/body)` and delegates index-safety to the emitter's aliasing, which does not cover the sibling-factor case). **Not** `src/kkt/stationarity.py` (the prior is refuted). Recommended fix at `_diff_prod`: rebind the derivative factor to the controlled stationarity index `i` (form 1/2 of Task 4 §2).
- **Distinguishing feature:** the **cross-index** case (prod over `j`, differentiate w.r.t. `pc(i)`, `j ≠ i`). The 18 other prod-in-stationarity models that compile today use the name-match case and are the regression set the fix must not break (lmp2 flagged).

This is the **deepest** of the three roots and carries P4's REPLAN risk (§7).

---

## §4. Landing sequence + per-step expected bucket outcome (Unknown 4.4)

**Order: `$141` → `$145` → `$149`** (cheapest-and-verified first, deepest last). Each root lands as its own `--resolve-changed`-gated change with its own golden refresh, so a regression on any step is isolated.

| Step | Change | `--resolve-changed --since 78ceaead` | ganges compile | **Expected bucket** |
|---|---|---|---|---|
| 1 | `$141` skip | GO (collateral goldens regen; no bucket move) | `$145×3 + $149×9` remain — **still fails** | **path_syntax_error (unchanged)** |
| 2 | `$145` skip | GO (ganges/gangesx + any `*`-param goldens regen) | `$149×9` remain — **still fails** | **path_syntax_error (unchanged)** |
| 3 | `$149` AD fix | GO (+ the 18 prod-model regression set byte-stable) | **0 errors — compiles** | **path_syntax_error → model_optimal (+match if it solves)** |

> **⚠️ No bucket moves until step 3.** Steps 1 and 2 are *correct and necessary* but individually recover **nothing** — ganges/gangesx stay `path_syntax_error` until all three land. This is the S34 finding, now re-proven (§1). **A mid-sequence flat KPI is the expected state, not a failure**, and the "no bucket → no `src/`" rule means steps 1–2 do **not** ship on their own (they would touch collateral goldens for 0 bucket — exactly why S34 banked `$141`). **The three roots ship as one coherent P4 landing**, gated together, or not at all.

---

## §5. Per-model verification protocol (Unknown 4.4 — the multi-root discipline)

Run for **ganges and gangesx independently** — never infer one from the other, even though they share an NLP objective (6395.5444) and, per Task 4, identical root profiles. This *is* a deliverable:

```
for M in ganges gangesx:
  1. emit    : .venv/bin/python -m src.cli data/gamslib/raw/$M.gms -o /tmp/$M.gms   (recursion 50000; ~150–200 s)
  2. compile : gams /tmp/$M.gms a=c   → count residual $NNN by code   (assert: 0 for all)
  3. translate : confirm nlp2mcp_translate.status = success (already true at Day 0)
  4. solve   : run_full_test cold AND presolve; ASSERT modelstat before reading the objective
  5. bucket  : model_optimal / model_optimal_presolve / model_infeasible / path_syntax_error
  6. match   : solution_comparison vs the NLP (6395.5444); classify cold-match (genuine floor) vs presolve-only (methodology)
```

**Acceptance for a P4 recovery claim:** compile-clean **and** solve **and** match, per model. A model that compiles but does not solve is *not* recovered (it moved `path_syntax_error → model_infeasible`, a different bucket) — report it as such, not as a win. Encode this protocol into the P4 Phase-0 gate (Task 10) so it cannot be skipped under time pressure.

---

## §6. Golden-regeneration plan (folded in from Task 3)

Task 3 measured the slow-emit budget and refuted the S34 "un-regenerable" premise. For the P4 landing:

- **Scope of regen:** ganges + gangesx (the recovered models) **plus the `$141`/`$145` collateral** (chakra, dinam, gancnsx, prolog, saras, senstran, shale, tfordy, turkey) **plus** any byte-drift the `$149` fix causes on the 18 prod-in-stationarity models (expected: none, since the fix must be surgical — but `--resolve-changed` verifies).
- **Invocation (per the P4 landing day):**
  ```bash
  # after $141 + $145 + $149 land in src/
  check_golden_staleness.py --models ganges,gangesx,clearlak,turkpow,chakra,dinam,gancnsx,prolog,saras,senstran,shale,tfordy,turkey --fix
  run_full_test.py --resolve-changed --since-commit 78ceaead
  ```
  **Never the unscoped `make regen-goldens`** (the 170-golden sweep whose contention caused the S34 soft-timeout — Task 3).
- **Budget:** the 4 slow models ≈ 8.2 min scoped (Task 3); the collateral is mostly fast; a `--fix` pass costs 2 emits per drifted golden (determinism guard). **Fits a normal ≤ 12 h day** (Task 3's verdict holds; the collateral adds fast models, not slow ones). Determinism ×3 `{0,1,42}` on the recovered goldens per PR12.

---

## §7. turkey `$161` — scoped separately → P6 (Unknown 4.6)

turkey's `ao` set is declared with dotted-tuple elements (`grains.wheat, grains.corn, …, industrial.tea, fruits.grape, …`) with inconsistent quoting; the emit produces set elements GAMS rejects → **`$161`**, ×6, on the set declaration. This is a **set-declaration emit** surface, **disjoint** from all three ganges roots (no NA-cleanup, no product-rule), and **turkey has no `$149`** (Task 4). Its `$141`/`$257` are cascades of `$161`.

**Placement decision: P6, not P4.** Rationale: turkey shares no root, no fix surface, and no model with the ganges recovery; folding it into P4 would conflate two unrelated efforts and dilute the P4 gate. It is a bounded, standalone item (quote dotted-tuple set elements consistently in the set-declaration emit) for the P6 residual cohort, with its own `--resolve-changed` gate. Note it is a `verified_convex`-adjacent `likely_convex` candidate, so a recovery would be +1 Solve — but on its own P6 track.

---

## §8. REPLAN exit + budget reallocation

**The `$141` and `$145` fixes are low-risk** (bounded cleanup-pass skips, re-validated / independence-confirmed). **The `$149` AD fix carries P4's REPLAN risk:** Task 4's surface is `_diff_prod`'s collapsed-form branch, and the fix must correct the cross-index case **without** perturbing the 18 name-match prod-models (lmp2 most sensitive).

**REPLAN trigger:** if the `_diff_prod` correction cannot be made surgical — i.e. it requires a general restructure of `prod` differentiation that drifts or breaks any of the 18 regression-set goldens in a `/tmp` control — then:
- **Do not ship `$141`/`$145` alone.** They recover nothing without `$149` (§4), and shipping them would churn ~11 goldens for 0 bucket — exactly the S34-banked outcome. Bank all three (the `$141` fix is already verified; the `$145` design and the `$149` analysis are complete) for a dedicated AD-core effort.
- **Reallocate P4's budget** (14–20 h) to **P6** (the residual cohort + turkey `$161`, which are independent and may yield a bucket) and **P7** (fixtures + the genuine-floor recompute).

**Conversely, the PROCEED path:** if the `/tmp` `_diff_prod` control drives ganges's `$149` → 0 with the 18 regression goldens byte-stable, land all three roots together, regenerate the scoped golden set, and expect **+2 Solve / +2 Match / −2 path_syntax_error** (and **+2 genuine floor** if ganges/gangesx **cold**-match — to be classified per §5, since a presolve-only match is methodology, not floor).

---

## §9. Known Unknowns verified by this task

- **Unknown 4.1** — ✅ **VERIFIED.** The banked `$141` fix applies cleanly to the current tree (surfaces unchanged at `:137`/`:152`) and **removes all 15 `$141`** (re-emitted + compiled in a scratch tree, then reverted). Collateral enumerated (~9 `.l`-calibration models; not the data-calibrated CGE cluster) — golden-byte drift, no bucket change, `--resolve-changed`-gated at landing.
- **Unknown 4.2** — ✅ **VERIFIED.** `$145` is `series(*,years)`'s universal-set `*`-domain guard (invalid assignment index), **independent of `$141`** (no `.l`; the param is assigned) — confirmed directly by the `$141`-only re-emit leaving `$145×3`. Fix designed (skip `*`-domain params) + minimal reproducing shape given.
- **Unknown 4.3 (Task-5 contribution)** — the `$149` correction is specified from Task 4 (AD-layer `_diff_prod`, form 1/2) and slotted as the deepest, REPLAN-bearing step of the P4 sequence. Task 4 remains the primary.
- **Unknown 4.4** — 🔍 **DESIGN-SPECIFIED (not executed).** The per-model recovery *protocol* and the landing *sequence* are designed, and the multi-root structure is empirically confirmed (`$141` alone leaves `$145×3+$149×9`). But **the recovery verdict itself — that all three roots together make ganges *and* gangesx compile, solve, and match — is NOT executed here** (the `$149` AD fix is not built; `$149`/`$145` were not applied). Marked DESIGN-SPECIFIED deliberately: this is the exact assumption Sprint 34 got wrong, and it becomes ✅ only when the in-sprint P4 execution runs §5's protocol per model.
- **Unknown 4.6** — ✅ **VERIFIED.** turkey `$161` is a dotted-tuple set-declaration emit root, disjoint from the ganges roots (turkey has no `$149`); scoped to **P6** with its own gate.

**Handed to Task 10 (Phase-0 gate):** the three-root sequence, each `--resolve-changed`-gated; the `$149` `/tmp` control against the 18-model regression set; the per-model verification protocol (§5) encoded so it cannot be skipped. **Handed to Task 11 (projection):** P4 = **+2 (ganges, gangesx)**, contingent on all three roots landing together and the `$149` AD fix being surgical; `$141`/`$145` low-risk, `$149` REPLAN-bearing.

---

**Document Status:** ✅ Complete — Sprint 35 Prep Task 5
**Last Updated:** 2026-07-24
**Owner:** Sprint 35 Planning Team
