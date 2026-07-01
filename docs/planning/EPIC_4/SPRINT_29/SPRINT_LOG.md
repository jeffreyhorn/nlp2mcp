# Sprint 29 Log

**Sprint:** 29 (Sprint 28 carryforwards + cold-convex robustness + AD/KKT backlog + Epic-5 scoping)
**Plan:** `PLAN.md` · **Prompts:** `prompts/PLAN_PROMPTS.md` · **Baseline:** `BASELINE_METRICS.md`
**Day-0 baseline (= Sprint 28 final):** Parse 142 · Translate 135 · Solve 107 · Match 92 · model_infeasible 7 · Tests ~4,935.
**Targets:** Solve ≥ 109 (mine + rocket, both REPLAN-gated) · Match maintain ≥ 92 / stretch ≥ 96 (genuine floor 68 → up) · model_infeasible ≤ 5 · Translate ≥ 135 · Tests ≥ 4,960 · determinism ×3 seeds.

## Cumulative Metrics Tracker

| Metric | Day 0 | Day 5 (CP1) | Day 10 (CP2) | Day 13 (final) | Target |
|---|---|---|---|---|---|
| Solve | 107 | — | — | — | ≥ 109 |
| Match (as-measured) | 92 | — | — | — | ≥ 92 / stretch 96 |
| Match (genuine floor) | 68 | — | — | — | 68 → up (cold-robustness) |
| model_infeasible | 7 | — | — | — | ≤ 5 |
| Translate | 135 | — | — | — | ≥ 135 |
| Tests | ~4,935 | — | — | — | ≥ 4,960 |

---

## Day 9 — Priority 3 #1385 translation-timeout cross-terms: smallest-target trace → **REPLAN to Sprint 30** (2026-06-30)

**Goal:** pick the smallest viable `translate_timeout` target, hand-derive its runtime-guard `stat_*` cross-terms, land the **atomic** pair (re-emit + `J_gᵀ·lam`). **Outcome: REPLAN** (hand-derivation tractable; atomic symbolic-emit implementation intractable in budget).

**Smallest target = sarf** (471 lines, vs iswnm 691 / nebrazil 1021 / mexls 1088).

**Blow-up diagnosis.** sarf times out (>200s) on **three 2-D dynamic-subset constraints**: `tbal(g,t)$taskposs(g,t)` (**384** instances), `equipb1(m,t)$equipposs(m,t)` (**648**), `equipb2(n,t)$equipposs(n,t)` (**120**). `taskposs`/`equipposs` are computed from `treq`/`tech` data (sarf.gms:371–384) → **zero concrete members at compile time** → `enumerate_equation_instances` includes the full Cartesian product → `differentiate_expr` blows up. **The existing srpchase short-circuit (`_is_blowup_dynamic_subset_equation`) is 1-D-only** (`len(eq_domain) != 1` bails) → it does **not** fire on sarf's 2-D shape, so sarf has no short-circuit at all.

**Hand-derivation (the gate deliverable — DONE, tractable).** The 4-D `task(g,t,mn,mn)` is touched by five guarded constraints (tbal, labor, equipb1, equipb2, acost3) + the special `tadj("harvest-c","cotton-p","self-prop")` term. The complete `stat_task(g,t,m,n)$taskposs(g,t)` cross-term shape is banked in `ISSUE_1385` (5 terms + the tadj special term, all `$taskposs`/`$equipposs`-guarded, sum indices = the stat equation's own domain → **no quoted-set-name multiplier indices**, avoiding the Day-4 `nu_slack("srn")` bug).

**Why REPLAN (the implementation, not the derivation).** Landing it needs (a) extending the short-circuit gate to the **2-D** shape AND (b) a **new symbolic runtime-guard cross-term emit path** in `stationarity.py` — because the short-circuited equations enumerate **zero** instances, the cross-terms must be built by symbolically differentiating each body parametrically in `(g,t,m,n)`, not assembled from per-instance Jacobian entries. **This is exactly the architecture that FAILED in Sprint 26 Day 4** (commit `243fe578`, reverted — the set-name-literal-index bug + dropped cross-terms). sarf is **strictly harder than srpchase** (4-D `task` × 5 guarded constraints × **nested** `taskposs`/`equipposs`). The **atomicity constraint** (Unknown 3.1) forbids a translate-only landing, so it's all-or-nothing — and the "all" is a high-risk architectural rewrite the ~7h budget can't de-risk against the Sprint-26 failure. **→ REPLAN to Sprint 30** as a dedicated builder-pipeline-aware symbolic-emit workstream (sarf = reference target; the hand-derivation = banked spec). **No +Translate this sprint** (sarf stays `translate_timeout`; Translate holds 135).

**Unknowns resolved:** 3.2 (smallest target = sarf), 3.3 (cross-term shape hand-derived), 3.1 (atomicity holds → no partial landing → REPLAN).

**Docs-only** (the diagnosis was probes — timeout reproduction, per-equation instance-count + blow-up profiling; no `src/`/golden/DB changes).

---

## Day 8 — Priority 6 #1236 hhfair (the only live +Match): blocker root-cause → **REPLAN to Sprint 30** (2026-06-30)

**Goal:** fix the residual-emit compile blocker (`$184` first error → `$257`/`$141` cascade), read the CES/`prod` verdict, PROCEED (Case b, +1 Match) or REPLAN (Case c). **Outcome: REPLAN.**

**Root-cause refined the Day-0 attribution.** The Day-0 trace pinned the `$141` (dual-transfer over the widened `tl` domain) as the surface — but a full-execution run shows the **first** error is **`$184` at `hhfair.gms(43)`** under the `$onMultiR $include`, which cascades to `$257` (solve skipped) → the `$141` (marginals never assigned). The `$141` was a *downstream symptom*, not the root.

**The `$184` is the #1449 widened-symbol conflict, but for a VARIABLE.** Source declares `n(t)` (line 43); the MCP widens it to `n(tl)` (`var_domain_widenings={'n':('tl',)}`) because `n` appears in `stat_m(tl)`/`stat_c`/`stat_n` over `tl` — from the bilinear `timemoney(t).. n(t)*(m(t)-gamma1*p*c(t)) =e= gamma2` (∂/∂m = n). The `$include` re-declaring `n(t)` collides with the widened `n(tl)` under `$onMultiR`.

**Why it's not an ≤8h fix.** The #1449 param fix declares the widened param at source domain + a `<p>__pw` companion at the widened domain post-include. **That does NOT transfer to `n`** — `n` is a *live nonlinear-stat coefficient* (it's optimized via `stat_n` AND used as a coefficient in `stat_m`), not a value-copy, so it needs a companion *variable* + value-coupling (an emit-architecture workstream). **`--gdx` does not bypass it** either: the residual MCP `$include`s the source for *declarations*, not just the solve, so `$184` fires regardless.

**The +Match needs the warm-start anyway (so the blocker is the gate).** The **cold** MCP compiles + solves to MS-1 but **mismatches** (72.1 vs NLP 87.2) — hhfair is non-convex (W301 nonlinear-equality on `utility` and `timemoney`; W303 bilinear on `timemoney`; plus the CES `prod(t,u(t)**ufact(t))` objective nest), so PATH cold-converges to a spurious KKT point. Recovering the match requires warm-starting from the NLP optimum — exactly what the `$184` presolve `$include` would provide, and exactly what it blocks. So **the CES `stat_*` verdict (Case b/c) is unreadable until the #1449 widened-variable fix lands.**

**Decision: REPLAN to Sprint 30.** File the #1449-widened-variable presolve fix as the prerequisite carryforward (`ISSUE_1236`, Unknown 6.1 resolved). **hhfair Match stays mismatched — no headline +Match this sprint** (it was the only live P6 +Match). **Match holds 92.**

**Unknown 6.2 (sambal/qsambal #1112 consolidation check):** both **match cold** already (Match-neutral, confirming Task 9). `xw(i,j)` is a *parameter* (cell weights: `xw(i,j) = 1$xb(i,j)`), not a constraint dollar-condition routing through the offset-alias #1112 → **no #1112 consolidation needed; no overlap.**

**Docs-only** (the experiments were probes — cold-MCP compile check, NLP→GDX solve, manual residual attempt; no `src/`/golden/DB changes).

---

## Day 7 — Priority 1 #1443 mine: close-or-REPLAN → **REPLAN to Sprint 30** (2026-06-29)

**Scope:** the close-or-REPLAN decision. **No `src/` change** (REPLAN; the Site-2 experiment was a hand-edit probe). Docs-only.

### The decisive experiment (sharpens Day 6)
Hand-fixed **Site 2** (`lam_pr.l(k,l,i,j)$(ord(l) <= card(l) - 1) = abs(pr.m(k,l+1,i,j))`) and evaluated the MCP at the NLP optimum (`iterlim=0`):
- **`nw` direction** (`li=lj=0`, no parameter offset) → **clears** (residuals 0.0001–0.5).
- **`ne`/`se`/`sw` directions** (`li(k)`/`lj(k)` active) → **still ~1e10** comp_pr infeasibility (e.g. `se.1.2.1` 1.715e10).

So the bug is the **coupling of the `l+1` head-offset with the `i+li(k)`/`j+lj(k)` parameter offsets** in `comp_pr` — a coordinated multi-site index map, not a single-site dual-transfer fix. Even warm-started from the NLP optimum with corrected duals, mine does NOT reach MS 1 → the PROCEED criterion (`MS 1 + compare_objective_match`) is not met.

### Decision — REPLAN to Sprint 30
This is an emit-architecture re-derivation of the head-domain-offset (the IR collapses the `l+1` head to the base domain + a bool flag, so `comp_pr` / the dual transfer / `stat_x` must each re-apply it consistently *together with* the `li(k)`/`lj(k)` offsets). Not an ≤8h fix. **REPLAN** (`ISSUE_1443` → Sprint 30; Unknown 1.1 RESOLVED = distributed). mine stays `model_infeasible` — **realizes the "Risk if Wrong" -1 Solve** (the firm Solve path is now 107, with both headline movers mine + rocket REPLAN'd). **Freed ~10–16 h → Day-12 Class-C cold-convex** (per the plan). Sharper-than-Day-6 Sprint-30 starting point: Site 2 (`pr.m` head index) confirmed; the remaining work is the `comp_pr` head×parameter-offset index map + `stat_x` consistency.

### Honest correction
The Day-6 entry framed this as "grossly distributed/systemic"; Day-7's precise residual measurement refined that — the head-offset *dual transfer* (Site 2) is a real, isolable sub-fix (clears `nw`), and the residual gates specifically on the **offset-bearing directions**. The conclusion (REPLAN, multi-site) is unchanged, but Sprint 30 inherits a much sharper surface.

---

## Day 6 — Priority 1 #1443 mine: head-offset diagnosis (start) → leans REPLAN (2026-06-29)

**Scope:** clear the `ISSUE_1443` gate, map the cold-INFES by row-type, attempt the coordinated 3-site head-offset index map, drive toward feasibility. **No `src/` change** (diagnosis day; the Site-2 experiment was a hand-edit probe) — docs plus one CI-config edit: the fast-test perf-budget bumped 45s→50s (`.github/workflows/performance-check.yml`, after the count grew with the sprint's new tests/fixtures).

### Confirmed + mapped
Harness Case b `stat_x(4,1,1)` 1.33, dual-transfer CONSISTENT. Cold solve = **MS5, 49 INFES + 10 REDEF**. The 49 INFES are the **`comp_pr` precedence rows by direction `k`** (nw 6 / ne 9 / se 12 / sw 11 = 38) + the `def` objective row + bound rows — **all from the `pr(k,l+1,i,j)$c(l,i,j)` head-domain-offset**. `x.up=1` is emitted, so the 4.07e10 is the **comp_pr LCP residual** (the precedence complementarity can't be satisfied with the mis-indexed `lam_pr`), not an x blowup.

### The head-offset (3-site)
IR: `pr.has_head_domain_offset=True`, domain stored as base `(k,l,i,j)`, body `x(l,i+li(k),j+lj(k)) ⊥ x(l+1,i,j)`.
- **Site 1 — `comp_pr`:** `comp_pr(k,l,i,j)$((c(l,i,j)) and (ord(l) <= card(l) - 1)).. x(l,i+li(k),j+lj(k)) - x(l+1,i,j) =G= 0` (base-`l`).
- **Site 2 — dual transfer (CONFIRMED wrong):** `lam_pr.l(k,l,i,j) = abs(pr.m(k,l,i,j))` reads `pr.m` at the **base** `l`, but `pr.m` is keyed at the **head** `l+1` (`pr.m(k,1,·)=0`). Correct = `pr.m(k,l+1,i,j)`.
- **Site 3 — `stat_x` (#1224 landed):** `sum(k, lam_pr(k,l,i-li(k),j-lj(k)) - lam_pr(k,l-1,i,j))` (base-`l`).

### Decisive experiment — Site 2 alone is INSUFFICIENT (structural, not warm-start)
Hand-edited the presolve dual transfer to `lam_pr.l(k,l,i,j)$(ord(l) <= card(l) - 1) = abs(pr.m(k,l+1,i,j))` and solved the MCP **warm-started from the NLP optimum** → **still MS5.** So the NLP optimum is NOT a solution of the emitted cold LCP even with corrected duals → the head-offset bug is in the **LCP structure** (the base-`l` vs head-`l+1` mismatch pairs `lam_pr(k,l,·)` with the wrong precedence row across all three sites), not just the warm-start.

### Day-7 lean: REPLAN
This is a coordinated multi-site re-derivation of the head-domain-offset emit (the IR collapses the `l+1` head to the base domain + a bool flag, so comp_pr / the dual transfer / stat_x must each independently re-apply the lost offset — and they currently disagree). Not an ≤8h single-site fix (Task-5 lean-REPLAN confirmed; the Sprint-28 Day-4 "22/30 stat_x systemic" probe corroborates). **No metric change** (mine stays `model_infeasible`). Day 7 formalizes the PROCEED/REPLAN decision.

---

## Day 5 — Checkpoint 1: re-solve caught a polygon regression → Day-4 fix REVERTED (2026-06-29)

**Scope:** Checkpoint 1 (re-solve the changed-golden set, bucket-diff vs the committed DB, GO/NO-GO) + PR25 re-baseline tally. (`--resolve-changed` mode is the Day-11 P8 build; done manually here via `changed_emit_artifacts.py` + `run_full_test.py --model`.)

### Re-solve of the 6 changed goldens (since Day-0 `38ac7a20`)
`changed_emit_artifacts.py` → cclinpts/chain/maxmin/otpop/polygon/rocket. Re-solved each vs the **true git-HEAD DB baseline** (run_full_test mutates the DB in-tree — restored after each measurement):

| Model | Baseline | Re-solve | Verdict |
|---|---|---|---|
| maxmin | match (cold) | **match** (presolve-retry) | OK — path shift, no Match loss |
| cclinpts | match | match | OK |
| otpop | match | match | OK |
| chain | mismatch | mismatch | OK (unchanged) |
| rocket | not_tested | not solved | OK (Day-2 REPLAN) |
| **polygon** | **match (0.7797)** | **MISMATCH (0.0)** | **🔴 REGRESSION** |

### 🔴 polygon regression — Day-4 #1143 fix REVERTED
Checkpoint 1 caught what Day-4's verification missed: Day 4 relied on golden-staleness + harness-residual (0.49→0) but **never re-solved polygon** — the "Match-neutral" claim was unverified. The full-pipeline solve shows polygon went **match (0.7797) → mismatch (spurious 0.0 optimum)**. Root cause: the Day-4 fix made polygon's *objective gradient* correct, but polygon has a SECOND independent bug — the `distance(i,j)` **constraint-Jacobian symmetry** (`stat_r` drops the second-index `r(j)` term; "Multi-pattern Jacobian: skipping correction" warning). The now-complete gradient + the inconsistent KKT admits a degenerate solution. This breaks the **Match ≥ 92 maintain floor** → NO-GO. **Per the user's call, the Day-4 fix was REVERTED** (representative-selection + `_distinct_base_offsets` removed from `stationarity.py`; polygon golden restored byte-identical to pre-Day-4; `shape8` test → strict xfail). polygon re-solves to **match** again ✓. Re-deferred to Sprint 30 **coupled** with the distance-Jacobian fix (`ISSUE_1143`). **This is the rocket-#1462 lesson in action: golden-stability does not catch a broken solve — only the checkpoint re-solve does.**

### Checkpoint outcome
**GO** after the revert — all 6 changed models at-or-above baseline (maxmin path-shifted cold→presolve but still match; polygon restored). Sprint-29 metrics intact: Solve 107, Match 92 (maintain floor held). **Genuine-floor net Days 3–4 revised: +1** (maxmin objvar `-1` + catmix recovery; **polygon reverted**, so its +1 floor is withdrawn until Sprint 30). PR25: no methodology change landed Days 1–5 that shifts the genuine/methodology split (the Day-3/4 fixes were cold-correctness, Match-neutral); the re-baseline stays genuine 68 / methodology ~24.

### Class-C cold-convex
Not started — the Checkpoint-1 investigation + the polygon revert consumed the Day-5 budget. Class-C (tforss/markov/robert/harker) carries to a later slack day.

---

## Day 4 — Priority 4/7: offset-alias successor cross-term (#1143 polygon) + fixtures (2026-06-29)

**Scope:** extend the Class-A work to the offset-alias cross-term; add the shape7/shape8 property-test fixtures. Decision under Unknown 7.2 (local vs alias-AD core).

### catmix RECOVERED for free (Day-3 side-effect)
Re-checking the cohort on `main` (post Day-3): **catmix is now Case A** (healthy, residual 1.45e-7) — the Day-3 multi-model objective-scoping fix (#1447) cleared it too. **Genuine-floor +1.** (like remains Case b — a *separate* objective-gradient bug in the nested `log-sum-exp`, not offset-alias; deferred.)

### #1143 polygon — successor-offset objective cross-term FIXED (PROCEED, not REPLAN)
Diagnosed precisely: the AD enumeration (`_try_diff_sum_offset_crossterms`) and re-symbolization (`_resymbolize_offset_gradient`) **both already work** — the drop was purely **representative-instance selection** in `src/kkt/stationarity.py` `_build_indexed_gradient_term`. It used the first nonzero instance — polygon's `theta('i1')`, a **boundary** column whose predecessor row is out of range, so its gradient holds only the `+1` offset (interior columns hold `{-1,+1}`) — and generalized that incomplete gradient to every interior row. **Fix:** when the gradient carries the offset signature, re-select the representative as the nonzero instance with the **maximal distinct-offset set** (new `_distinct_base_offsets` helper). `stat_theta(i)` + `stat_r(i)` now carry BOTH the successor `$(j(i))` and predecessor `$(j(i-1))` cross-terms; harness `stat_theta` residual **0.49 → 0**. **This is PROCEED under Unknown 7.2 — no alias-AD-core threading** (the AD/re-symbolization were correct; only the representative pick was wrong).

### Blast radius — polygon only
Targeted golden-staleness over the 12 offset-bearing-objective candidates (chain/cclinpts/catmix/himmel16/dinam/polygon/maxmin/like/robot/otpop/mine/kand): **exactly 1 drifted — `polygon_mcp.gms` (+117 bytes**, the added predecessor cross-terms), 0 others. **cclinpts BYTE-IDENTICAL** (the existing #1387 model — no regression). ganges/gangesx confirmed unaffected (objective has no offset signature). Match-neutral (polygon matches warm — genuine-floor robustness).

### Honest scoping — what did NOT land
- **polygon not full Case a:** residual moved `stat_theta` 0.49 → `stat_r(i14)` **0.12** — a **separate** `distance(i,j)` constraint-Jacobian symmetry bug (`r(i)` as both indices, only one direction summed; the "Multi-pattern Jacobian: skipping correction" warning). Distinct from the objective-gradient fix; remaining polygon work.
- **himmel16 (#1146) unchanged** (`stat_area` 2.0): confirmed **NOT a missing term** — the circular `i++1` decomposition (`nu_areadef(i-1)$(ord>1)` + `nu_areadef(i+5)$(ord<=card-5)`) is structurally present. The 2.0 is a **numeric/sign** defect in the objvar-gradient interaction (Day-0 candidate b), deferred (`ISSUE_1146`).
- **maxmin `stat_point` 0.31** unchanged: a 2-D `low(n,nn)` pair-subset offset, different shape; deferred.

### Fixtures (Task 9 Part C)
Added `tests/fixtures/crossterm_shapes/shape8_offset_alias_successor.gms` (passing — asserts both successor + predecessor terms, the #1143 regression guard) + `shape7_offset_alias_cyclic.gms` (passing structural smoke test — asserts the circular decomposition is present; the numeric #1146 correctness is documented as deferred). 8 crossterm-shape tests pass.

### Net Day 4
**genuine-floor +2** (catmix Case A from Day-3 + polygon objective-gradient correct). Match-neutral (both match warm). Deferred: polygon distance-Jacobian, himmel16 numeric/sign (#1146), maxmin 2-D subset, like nested-gradient.

---

## Day 3 — Priority 4/7: cold-convex Class-A — maxmin objvar multi-model scoping fix (#1447) (2026-06-29)

**Scope:** start the cold-convex Class-A + offset-alias shared fix. Landed the maxmin objvar half; the offset-alias half (himmel16/polygon + maxmin's residual) is Day-4 continuation.

### Root cause refined (a 2nd PR24-style correction)
The Day-0 trace corrected the prep hypothesis (dropped term = objective gradient `-1`, not the constraint sum). Day-3 refined it further: the `-1` is a **multi-model objective-scoping bug**. maxmin declares 4 models sharing objvar `mindist`; the solved model `maxmin1a / mindist1a /` has only the indexed `=l=` constraint, so the objective is the **bare objvar** `mindist` (gradient `-1`). But `find_objective_expression` (`src/ad/gradient.py`) scanned **all** equations and matched `mindist2.. mindist =e= smin(low, dist)` from the *unsolved* `maxmin2`, differentiating `smin(low, dist)` (no `mindist`) → the `-1` vanished.

### Fix — `src/ad/gradient.py` (#1447)
`find_objective_expression`'s Case-2 defining-equation search is now scoped to `model_ir.get_solved_model_equations()` (None → search all, the single-anonymous-model fallback). `stat_mindist` now emits `-1 + sum(low, lam_mindist1a) = 0`; harness `stat_mindist` residual **1.0 → 0**.

### Blast radius — maxmin golden ONLY
Golden-staleness over **159 goldens**: exactly **1 drifted — `maxmin_mcp.gms` (+5 bytes**, the `-1 +`), 0 others, 0 failed. Surgical. maxmin matches warm → **Match-neutral genuine-floor lift**. 2 unit tests (`tests/unit/ad/test_objective_expr_model_scoping.py`: scoped-to-solved-model returns bare objvar; control where the `=e=` def IS in the solved model still uses it).

### Not yet Case a — 2nd residual exposed → Day 4
Clearing `stat_mindist` exposed `stat_point(p6,x)` rel **0.312** — the offset-alias cross-term enumeration over the `low(n,nn)` pair subset (the `_diff_sum`/`_try_diff_sum_offset_crossterms` class shared with himmel16 `stat_area` 2.0 / polygon `stat_theta` 0.49). **himmel16/polygon are unchanged** by today's fix (confirmed) — their bug is purely offset-alias. That fix threads the #1387/#1111/#1112 AD core → **Day-4 work under the Unknown 7.2 REPLAN gate**.

### Decision
Day-3 lands the maxmin objvar-scoping fix (correct, isolated, verified). The offset-alias fix (maxmin `stat_point` + himmel16 + polygon) is the substantive **Day-4** deliverable, where the PROCEED/REPLAN call on threading the alias-AD core is made. **No metric change** (all Class-A models match warm).

---

## Day 2 — Priority 2 #1462: rocket residual → **REPLAN to Sprint 30** (2026-06-29)

**Scope:** resolve the residual MS-5 question (Unknown 2.2) — is the post-warm-start MS 5 a localizable emit/warm-start fix (PROCEED) or intrinsic non-convexity (REPLAN)? **No `src/` change** (the warm-start landed Day 1; the Day-2 probe was a diagnostic that didn't pan out, so nothing new is landed). Docs-only.

### Experiments
- **Complete `_fx_`-at-`h0` warm-start (already in from Day 1 — all ht/v/m):** solving `rocket_mcp_presolve.gms` → embedded NLP **MS 2** (obj **1.00412** ≈ NLP ref 1.0128) but the MCP `mcp_model` → **MS 5 (Locally Infeasible)**, PATH `** EXIT - other error` at the **initial Jacobian** (1307 elements, 903 nonlinear).
- **Degenerate-bound suppression probe (the prescribed Day-2 experiment):** the lone degenerate fix is **v('h0')=0** (fixed value = relaxed lower bound 0; ht/m fix to 1 ≠ bound 0). Suppressing the redundant `v_fx_h0` `_fx_` equation + pinning v('h0')=0 by bound → **still MS 5**, identical `EXIT - other error`, identical NLP obj. **The degeneracy is not the MS-5 driver.**
- **Residual not cleanable by warm-start value:** the harness residual moves with the warm-start value (`nu_*_fx=0` → `stat_step` 0.497; `=var.m` → `stat_ht(h0)` 1.00; negating only flips the sign) — the transferred NLP duals don't make the NLP point an exact MCP KKT point (the **Case-c boundary** for this non-convex model: bilinear + division-by-variable + nonlinear-equality). Converging NLP + non-converging MCP-from-warm-point = **intrinsic non-convergence**.

### Decision — REPLAN to Sprint 30
Both prescribed interventions (complete warm-start + degenerate-bound suppression) leave rocket at **MS 5**; the operational gate (PROCEED iff MS 1) is not met. **REPLAN to Sprint 30 forcing** (trust-region / homotopy / perturbed-restart). The Day-1 `_fx_` warm-start **stays** as firm presolve robustness; rocket's **+1 Solve / +1 Match is DEFERRED to Sprint 30** (`ISSUE_1462` → REPLAN-DEFERRED). **Freed ~4–8 h → Day-8 hhfair (Priority 6).** Unknown 2.2 resolved. **No metric change** (rocket was already `not_tested`/MS 5).

---

## Day 1 — Priority 2 #1462: `_fx_`-multiplier presolve warm-start (2026-06-29)

**Scope:** land the **general** `nu_<var>_fx_<idx>.l = <var>.m(<idx>)` `_fx_`-multiplier warm-start in the presolve dual transfer — sprint-wide presolve robustness, firm regardless of rocket's Day-2 outcome.

### Implementation
`src/emit/emit_gams.py`: new `_emit_presolve_fx_warmstart(kkt, suppressed_fx, add_comments)` helper, called at the end of `_emit_nlp_presolve`'s dual-transfer block. It iterates `var_def.fx_map` and emits `nu_<var>_fx_<idx>.l = <var>.m(<idx>);` for exactly the active `_fx_` multipliers, mirroring `_emit_presolve_fx_unfix`'s `eq_paired_in_mcp` gate (`in equalities` ∧ not suppressed ∧ referenced). The general transfer loop skipped these because the `_fx_` equations are not original NLP equations — the NLP fixes the column via `.fx`, so the fix dual surfaces as the *variable* marginal, not an equation marginal.

### Blast radius — exactly the 4 Layer-4-unfix models, additive-only
`grep -l "#1449 (Layer 4)" data/gamslib/mcp/*_mcp_presolve.gms` → **chain / cclinpts / otpop / rocket** (the only presolve goldens with `_fx_` multipliers). Each golden diff is purely additive (the new warm-start block): chain `nu_x_fx_i0/i50`, cclinpts `nu_b_fx_s1/s30`, otpop `nu_x_fx_1974`, rocket `nu_v_fx_h0/nu_ht_fx_h0/nu_m_fx_h0` — **16 inserted lines, nothing else changed.**

### Zero regression — proven
- **Cold MCP files BYTE-IDENTICAL** for all 4 (the change is inside `_emit_nlp_presolve`, presolve-only). The committed DB solves these via the **cold** file (`mcp_file_used=None`: otpop/cclinpts match, chain mismatch, rocket not_tested), so the DB Solve/Match results are unaffected by construction.
- **All 4 presolve goldens compile clean** (`gams action=c`, 0 errors); rocket + otpop also solve via the harness without abort.

### Rocket residual — necessary-but-insufficient (Day-2 question), as the gate predicted
Harness on rocket *with* the warm-start: the max-residual row **moved** from `stat_step` rel 0.497 → `stat_ht(h0)` rel 1.00 (a `_fx_` element row). Negating the transfer only flips the sign of the same magnitude, so this is **not** a sign error — the `_fx_` warm-start alone leaves a residual at the fixed element, exactly the **necessary-but-insufficient** finding from the Sprint-28 Day-13 diagnosis (obj 1.137 → 1.016, MS 5 persists). The residual `piL/piU`-at-`h0` interaction is the **Day-2 PROCEED/REPLAN question** (Unknown 2.2). Day-1 does **not** claim rocket is fixed.

### Tests + gate
3 new unit tests (`tests/unit/emit/test_presolve_fx_warmstart.py`: helper emits the line for a fixed boundary element; empty for a fix-free model; appears in the full `--nlp-presolve` emit). Goldens regen'd; golden-staleness + quality gate green. **No Solve/Match metric change** (firm robustness landed; rocket's +1 is the Day-2 decision).

## Day 0 — Kickoff + Day-0 Traces (2026-06-29)

**Scope:** baseline confirmation + Day-0 `kkt_residual.py` traces (PR24) for the REPLAN-prone + lead tracks; fill each Phase-0 gate's `Traced Fix-Surface (Day-0)` line. **No `src/` change** (per the Day-0 prompt). Docs-only.

### Baseline gate — PASS
`git diff 803a259a..HEAD -- src/ scripts/` is **empty** → `src/` + `scripts/` are byte-identical to the Sprint-28 baseline commit, so the committed `gamslib_status.json` stands as the Day-0 baseline (Solve 107 / Match 92 / model_infeasible 7). No fresh retest (Unknown 8.3 ✅). **Tooling (Task 6):** the KKT-residual harness, divergence detector, and golden-staleness gate are present and audited-ready — no Day-0 extension.

### Day-0 harness verdicts — all 8 RE-CONFIRMED vs the prep-time (Task 4) Day-0 status

| Track | Model | Verdict | max-residual row | rel | Prep | Note |
|---|---|---|---|---|---|---|
| P1 #1443 | mine | Case b | `stat_x(4,1,1)` | 1.33 | 1.333 | ✅ convex LP, dual-transfer CONSISTENT |
| P2 #1462 | rocket | Case b | `stat_step` | 0.497 | 0.497 | ✅ `_fx_`-at-`h0` warm-start absent |
| P4/P7 #1447 | maxmin | Case b | `stat_mindist` | 1.00 | 1.000 | ✅ **hypothesis corrected** (see below) |
| P4/P7 #1146 | himmel16 | Case b | `stat_area(1)` | 2.00 | 2.000 | ✅ cyclic + objvar-gradient sign |
| P4/P7 #1143 | polygon | Case b | `stat_theta(i12)` | 0.492 | 0.492 | ✅ dropped offset-image cross-term |
| P4 (Class-A) | like | Case b | `stat_p(three)` | 2.00 | 2.0 | ✅ folds into the Class-A lead (#1447) |
| P4 (Class-A) | catmix | Case b | `stat_x1(0)` | 0.952 | 0.95 | ✅ folds into the Class-A lead |
| P6 #1236 | hhfair | **ERROR** (blocker) | — | — | `$141`/`$257` | ✅ blocker reproduced + root localized |

Every prep verdict held on current `main` — **no drift**. JSON reports in `/tmp/day0_<model>.json`.

### Traced fix-surfaces (PR24) — filled in each Phase-0 gate
- **mine #1443:** three sites pinned — `stat_x` cross-term (landed #1224) `src/kkt/stationarity.py:5562-5570`; presolve dual transfer `src/emit/emit_gams.py:1281` (`lam_pr.l = abs(pr.m)`, same-index, sign-discarding); `comp_pr` head var `x(l+1,i,j)`. Residual is in the LP row despite consistent dual transfer → the `l+1`/`±li`/`±lj` correspondence is not aligned across the three sites (corroborates Task-5 lean-REPLAN).
- **rocket #1462:** `nu_*_fx_h0` declared + used in `stat_ht/m/v` but the presolve dual-transfer block (`emit_gams.py:1281-1310`) emits **no `nu_*_fx_*` init** → starts at 0 → `stat_step` residual. Layer-4 unfix `_emit_presolve_fx_unfix` at `emit_gams.py:1090`.
- **maxmin #1447 — ⚠️ prep hypothesis CORRECTED (PR24 catch):** the dropped term is the **objective gradient `-1`** (maxmin maximizes `mindist`), not the constraint sum (the `sum((n,nn)$low, lam_mindist1a)` **is** present). Surface: the objvar stationarity assembly in `src/kkt/stationarity.py` (`build_stationarity_equations`:2090 → `_build_indexed_stationarity_expr`:2650 / objective-gradient merge :2222).
- **himmel16 #1146:** two candidate surfaces (root disambiguates Day 3) — (a) cyclic `i++1` decomposed into `i+5`$(ord≤card-5)+`i-1`$(ord>1) in `stat_x`/`stat_y` (`derivative_rules.py` circular branch ~:1866); (b) the `stat_area` `-1` objvar-defining gradient interacting with the signed `nu_areadef` transfer (raw -2.0). Integer 2.0 = 2× maxmin's 1.0.
- **polygon #1143:** clean **dropped predecessor offset-image cross-term** — `stat_theta` has the own-row gradient but not the `+0.5*r(i)*r(i-1)*cos(...)` term from the `i-1` row (where `theta(i+1)` resolves to `theta(i)`). Surface: `derivative_rules.py` non-circular successor branch (~:1989/:2022) over `j(i+1)`.
- **hhfair #1236:** `$141` blocker reproduced (13 errors); root = the dual-transfer block emits multiplier inits over the **widened `tl` domain** (`nu_budget.l(tl) = -(budget.m(tl))`) reading unpopulated `.m('0')` (set split `tl /'0'..'3'/` vs active `t /'1'..'3'/`, propagated by the domain-widened `n(tl)`). Fix surface = restrict the transfer to the active subset (`emit_gams.py:1281-1310`); verdict gated on the Day-8 compile fix.

### PR25 Day-0 tally (genuine vs methodology)
- **As-measured baseline:** Solve 107 · Match 92 (= **genuine 68 + ~24 methodology**).
- **Firm headline path:** mine (#1443) + rocket (#1462), both `model_infeasible`/MS-5 → Solve, **both REPLAN-gated** (Task 5). hhfair (#1236) the lone live +Match (gated on the compile fix).
- **Cold-convex Class-A (maxmin/himmel16/polygon/like/catmix):** all **Case b but already match warm** → **Match-neutral genuine-floor lift** (68 → up), not as-measured Match.
- **No `src/` change today** → metrics unchanged from baseline.

### Deliverables
6 Phase-0 gates updated (`docs/issues/ISSUE_{1443,1462,1447,1146,1143,1236}_*.md`) + this Day-0 SPRINT_LOG entry. Docs-only; no quality-gate-relevant source touched.
