# Sprint 26 Log

**Sprint:** 26 — Pattern C Generalization + Pattern A Reclassification + Phase E Carryforward + Translation Timeout Option 1 Short-Circuit + AD Residuals (#1334 / #1335)
**Duration:** 14 days (Day 0 – Day 13)
**Baseline:** Parse 142/142, Translate 130/142, Solve 104, Match 60, Tests 4,735 (frozen Day 0 per Sprint 26 prep Task 9 + PR15 scope freeze; see [`BASELINE_METRICS.md`](BASELINE_METRICS.md))

---

## Sprint 26 Targets

| Metric | Baseline (142-scope) | Target | Stretch |
|---|---|---|---|
| Parse | 142/142 (100%) | ≥ 142/142 | — |
| Translate | 130/142 (91.5%) | ≥ 135/142 | ≥ 137/142 |
| Solve | 104 | ≥ 108 | ≥ 110 |
| Match | 60 | ≥ 64 | ≥ 66 |
| path_syntax_error | 9 | ≤ 6 | ≤ 4 |
| path_solve_terminated | 5 | ≤ 5 | ≤ 4 |
| model_infeasible | 4 | ≤ 4 | ≤ 3 |
| Tests | 4,735 | ≥ 4,750 | — |

See [`PLAN.md`](PLAN.md) for the full 14-day schedule and [`prompts/PLAN_PROMPTS.md`](prompts/PLAN_PROMPTS.md) for per-day execution prompts.

---

## Daily Progress

### Day 0 — Setup & Kickoff

**Status:** COMPLETE (2026-05-11)
**Branch:** `sprint26-day0-kickoff`

| Task | Status |
|---|---|
| Verify Day 0 baseline matches `BASELINE_METRICS.md` §2 | ✅ Parse 142/142, Translate 130/142, Solve 104, Match 60 (exact match — all 9 buckets in §2.1/§2.2/§2.3 match live `gamslib_status.json`) |
| Initialize `SPRINT_LOG.md` Day 0 entry | ✅ This entry |
| Confirm GitHub issue labels (`sprint-26` + `sprint-27`) | ✅ See §"Issue label confirmation" below |
| Read Task 3–10 prep-task outputs as briefing material | ✅ All 7 documents read; key findings captured in §"Prep-task briefing summary" below |

#### Baseline verification (per-bucket)

| Bucket | BASELINE_METRICS.md | Day 0 live | Match |
|---|---|---|---|
| `compare_match` | 60 | 60 | ✅ |
| `compare_mismatch` | 38 | 38 | ✅ |
| `compare_skipped` | 6 | 6 | ✅ |
| `solve_path_syntax_error` | 9 | 9 | ✅ |
| `solve_path_solve_license` | 8 | 8 | ✅ |
| `solve_path_solve_terminated` | 5 | 5 | ✅ |
| `solve_model_infeasible` | 4 | 4 | ✅ |
| `translate_timeout` | 8 | 8 | ✅ |
| `translate_internal_error` | 4 | 4 | ✅ |
| **Total in-scope** | **142** | **142** | ✅ |

Headline metrics: Parse 142/142, Translate 130/142, Solve 104, Match 60 — exact match to `BASELINE_METRICS.md` §2 frozen by PR #1373 (commit `f1cdb91f`).

#### Issue label confirmation

**`sprint-26` label** (Sprint 26 Day 1–13 in-scope work):

- Priority 1 (Pattern C generalization): #1306, #1307, #1354, #1355
- Priority 2 (Pattern A cohort reclassification — mechanical closures per Task 4): #1138, #1139, #1140, #1142, #1145, #1150
- Priority 3 (Pattern E carryforward — kand only per Task 5): #1141, #1144, #1147
- Priority 4 (Translation timeout Option 1 short-circuit): #885, #931, #932, #1185, #1228
- Priority 5 (AD residuals): #1334, #1335

**`sprint-27` label** (deferred work — must NOT carry `sprint-26`):

- #1357 (otpop `comp_up` subset/superset; deferred per Task 7 AD_RESIDUALS_RECAP.md)
- #1356 (fawley `comp_up`; deferred per Task 4 PATTERN_A_RECLASSIFICATION_PLAN.md)
- #1374 (emit duplicate-init bugs; surfaced during Task 9 PR review)
- #1224 (mine `ParamRef` IndexOffset; deferred per Task 6 DESIGN_OPTION_1_SHORT_CIRCUIT.md)

**Label-state fix-up performed during Day 0** (verified all 20 `sprint-26` issues correctly labeled; the 4 deferrals needed correction):

| Issue | Before | After |
|---|---|---|
| #1357 | `sprint-26` | `sprint-27` (created label; `sprint-26` removed) |
| #1356 | `sprint-26` | `sprint-27` (created label; `sprint-26` removed) |
| #1374 | (no sprint label) | `sprint-27` added |
| #1224 | `sprint-26` | `sprint-27` (created label; `sprint-26` removed) |

New `sprint-27` label created on the repo (color `0E8A16`, matching `sprint-25` / `sprint-26` convention). Final verification confirmed all 4 deferrals carry `sprint-27` only.

#### Prep-task briefing summary

All 7 prep-task outputs read as Sprint 26 briefing material (each drives one or more day-level prompts):

| Document | Drives | Key finding |
|---|---|---|
| `PATTERN_C_HYPOTHESIS_VALIDATION.md` (Task 3) | Day 1, Days 3–4 | **REPLAN**: Priority 1 split into Phase A (Day 1 — restore #1306 launch fix via consolidated zero-offset builder rewrite, removes #1351 rollback) + Phase B (Days 3–4 — generalize gate to camcge + cesam2). fawley + otpop reclassified out of Priority 1. |
| `PATTERN_A_RECLASSIFICATION_PLAN.md` (Task 4) | Day 6 | 6 cohort issues = 4 mechanical closures + 1 close-and-refile + 1 forward-link to Priority 1 PR. ~1.5h GitHub-only work. |
| `PATTERN_E_STATUS.md` (Task 5) | Day 6 | Scope reduced 3 → 1 model (kand alias-AD). catmix and camshape closures are mechanical. |
| `DESIGN_OPTION_1_SHORT_CIRCUIT.md` (Task 6) | Day 8 | Patch sites confirmed in `src/ad/index_mapping.py::enumerate_equation_instances`; ~4–6h implementation budget; projected +1–2 Translate from srpchase. |
| `AD_RESIDUALS_RECAP.md` (Task 7) | Days 8–10 | #1334 fix-site corrected to `_add_indexed_jacobian_terms:4228` (not scalar-only `_add_jacobian_transpose_terms_scalar:5421`). #1357 explicitly NOT subsumed; deferred to Sprint 27. |
| `DESIGN_PR19_SOLVE_TIME_CI.md` (Task 8) | Day 11 | `.github/workflows/pr19-emit-solve-validation.yml` design; PATH solver under 30s budget on 11 Tier 0/1 canaries; GAMS demo install in CI. |
| `BASELINE_METRICS.md` (Task 9) | Day 13 | Day 0 baseline frozen + bucket-provenance column (PR17) for Day 13 retest comparison. 3 Day-0 machine-variance churn-outs (clearlak / ganges / turkpow) tracked separately. |

Sprint 25 carryforward KUs (KU-33 through KU-36) referenced in `PLAN.md`:

- KU-33 (Pattern C generalization) → Days 1–5 (Task 3 drives)
- KU-34 (bucket churn dominates `path_syntax_error`) → Day 13 retest comparison (PR17 evaluation)
- KU-35 (Sprint 25 PR #1351 launch rollback) → Day 1 Phase A
- KU-36 (otpop `$171` vs `$141`) → Days 8–10 Priority 5 + Sprint 27 #1357 deferral

#### Notes

- All 11 Sprint 26 prep tasks ✅ COMPLETE (PRs #1365, #1366–#1373, #1375, #1376). Final Prep-Task Status table in `PREP_PLAN.md` §"Final Prep-Task Status".
- All 26 Sprint 26 Known Unknowns (KUs 1.1–6.5) ✅ VERIFIED in `KNOWN_UNKNOWNS.md`.
- Day 0 commit + PR ships this `SPRINT_LOG.md` initialization only; no `src/` changes.

---

### Day 1 — Priority 1 Phase A: Restore Launch Fix (Consolidated Zero-Offset Builder Rewrite)

**Status:** COMPLETE (2026-05-11)
**Branch:** `sprint26-day1-pattern-c-phase-a`

| Task | Status |
|---|---|
| Diff #1306 vs #1351 to identify consolidator code path | ✅ Identified: `_add_indexed_jacobian_terms` gate site (`src/kkt/stationarity.py:4318–4346`) + downstream offset-group consolidation. #1351 hardcoded `allow_nonzero_offsets = True`; #1306 had the predicate-based gate. |
| Implement the rewrite per Sprint 25 SPRINT_LOG.md Day 11 follow-up | ✅ New helpers `_find_eq_domain_index_in_expr`, `_find_pattern_c_alias_sum`, `_apply_pattern_c_swap_to_term`, `_expr_references_var`. The transform applies an alias↔eq-domain swap to the auto Sum-wrapped term so the consolidated emit shape is the GAMS-equivalent of the target `sum(ss$ge(s,ss), -nu_dweight(ss))`. |
| Re-enable Pattern C gate; capture `pattern_c_info` for transform | ✅ Removed `allow_nonzero_offsets = True` hardcode and the no-op `if eq_def_for_gate is not None: pass` branch. Restored the original #1306 gate logic with the additional `_expr_references_var(sum.body, var_name)` check (prevents spurious firing on variables outside the alias sum — discovered during initial impl when `stat_weight(s)` regressed to `nu_dweight(ss)`). |
| Tier 0 dispatch canary byte-identical | ✅ Byte-identical to `data/gamslib/mcp/dispatch_mcp.gms`. |
| Tier 1 canary (10 models) byte-identical | ✅ 10/10 byte-identical to golden artifacts (quocge, partssupply, prolog, sparta, gussrisk, ps2_f, ps3_f, ship, splcge, paklive). The `$cond`-required predicate stays narrow — does NOT fire on plain-alias enumeration shapes like quocge's `sum(i, ax(i,j)*pq(i))`. |
| Re-enable xfail test + strengthen assertions | ✅ `tests/unit/kkt/test_pattern_c_alias_offset_gate.py::test_alias_only_conditional_sum_emits_no_phantom_offsets` xfail decorator removed; assertions extended to check `nu_dweight(ss)` present, `nu_dweight(s)` absent, `ge(s,ss)` present. Both Pattern C unit tests pass. |
| Translate launch fresh; verify stat_iweight body shape | ✅ Emit: `sum(ss, ((-1) * 1$(ge(s,ss))) * nu_dweight(ss))` (single consolidated term, alias-indexed mult, swapped condition). All 5 phantom-offset `nu_dweight(s±k)` terms eliminated. Same fix applies to `stat_pweight`. |
| PR14 obligation: regenerate `data/gamslib/mcp/launch_mcp.gms` | ✅ Regenerated; included in PR diff. |
| `make typecheck && make lint && make format && make test` | ✅ 4,737 passed, 10 skipped, 1 xfailed (above ≥ 4,750 Sprint 26 target — counts updated upward by the strengthened Pattern C test + new shape-recovery test). |

#### Launch PATH solve regression (deferred to Sprint 27 #1378)

Phase A's mathematically correct KKT emit produces a different KKT system from the Sprint 25 #1351 over-counted form. PATH converged on the over-counted system (MODEL STATUS 1 Optimal, obj=2731.711) but stalls on the correct system (MODEL STATUS 5 Locally Infeasible, 6194 iterations, `defvt` complementarity residual ~3.2e+04).

- **Mathematical verification:** Resolved Phase A `stat_iweight(stage-3)..  ... - nu_dweight(1) - nu_dweight(2) - nu_dweight(3) ... =E= 0` matches the hand-derived `-sum_{k<=s} nu_dweight(k)` from the Lagrangian.
- **Root cause:** Sprint 25 #1351 emitted `stat_iweight(stage-s)..  ... - card({ss:ss>=s})*sum_k nu_dweight(k) + ...` (per-row weighted; same primal but DIFFERENT multiplier system). PATH found a numerical fix for the wrong system that doesn't transfer to the right one.
- **Filed:** Sprint 27 issue #1378 ("launch PATH solve regresses to MODEL STATUS 5 with mathematically correct Phase A KKT") with `sprint-27` label, investigation paths: PATH initial-point / preprocessing tuning, NLP-warm-start, sign/scaling refinement in `_apply_pattern_c_swap_to_term`.
- **Day 5 Checkpoint 1 impact:** `PLAN.md` updated — "launch PATH solve to MODEL STATUS 1" is now a stretch row (does not count toward GO/CONDITIONAL GO/NO-GO routing); the gating criteria are camcge + cesam2 + Phase A landing + canaries (5 rows, ≥ 4 of 5 to GO).

#### Notes

- The Pattern C gate predicate (`_body_has_index_offset_on_sets` + the new variable-scope check) is conservative — requires the source body to have an aliased conditional sum referencing the equation's domain (launch shape only). Phase B (Days 3–4) broadens the gate to plain-alias (camcge) and `sameas`-decomposed (cesam2) variants.
- Day 1 builds on `_rewrite_subset_to_superset` for the alias↔eq-domain swap — a single rename map `{alias: eq_dom, eq_dom: alias}` works because the helper does single-pass per-node lookups (no chained re-application).

---

### Day 2 — Priority 1 Phase A Validation + Phase B Scoping (camcge / cesam2)

**Status:** COMPLETE (2026-05-11)
**Branch:** `sprint26-day2-pattern-c-phase-a-validation`

Validation + scoping pass (no `src/` changes). Confirms Day 1 Phase A is byte-stable across the 54-model golden corpus and identifies the gate-predicate + builder-transform changes needed for Day 3 (camcge) and Day 4 (cesam2).

| Task | Status |
|---|---|
| Full 54-model Tier 0/1/2 golden-file regression | ✅ 54/54 byte-identical (11 Tier 0/1: dispatch, quocge, partssupply, prolog, sparta, gussrisk, ps2_f, ps3_f, ship, splcge, paklive; 43 Tier 2: ajax, alkyl, ampl, ... whouse — full list in Sprint 25 SPRINT_LOG.md Day 0). |
| Translate launch fresh + verify byte-identical to Day 1 commit | ✅ Byte-identical to `data/gamslib/mcp/launch_mcp.gms` from PR #1379. |
| launch PATH solve outcome | ⚠ MODEL STATUS 5 (Locally Infeasible) — consistent with Sprint 27 #1378 deferral. PATH-numerics work is out of scope for Days 2–10; rel_diff vs NLP baseline (Sprint 25 final 0.17) cannot be computed (MCP didn't solve). |
| Phase B scoping for camcge (#1354) | ✅ Documented below. |
| Phase B scoping for cesam2 (#1355) | ✅ Documented below. |
| `make typecheck && make lint && make format && make test` | ✅ See PR test plan. |

#### Phase B scoping — camcge (#1354)

**Phantom-offset emit (current main, Day 1 Phase A patch applied):** 120 phantom-offset terms across 5 multipliers:

| Multiplier | Phantom-offset count | Source equation |
|---|---|---|
| `nu_prodinv` | 40 | `prodinv(i)..  pk(i)*dk(i) =e= kio(i)*savings - kio(i)*sum(j, dst(j)*p(j));` |
| `nu_pkdef` | 20 | `pkdef(i)..    pk(i) =e= sum(j, p(j)*imat(j,i));` |
| `nu_inteq` | 20 | `inteq(j)..    int(j) =e= sum(i, io(j,i)*xd(i));` |
| `nu_ieq` | 20 | `ieq(i)..      id(i) =e= sum(j, imat(i,j)*dk(j));` |
| `nu_actp` | 20 | `actp(i)..     px(i)*(1-itax(i)) =e= pva(i) + sum(j, io(j,i)*p(j));` |

Each source body has the same shape: `sum(<alias>, <coeff>*<var>(...))` where the alias canonical-resolves to the eq-domain set. **No `$cond` filter** linking the alias to the eq-domain index.

**Why Phase A doesn't fire on camcge:** `_find_pattern_c_alias_sum` at `src/kkt/stationarity.py:362` requires `expr.condition is not None` for the matching Sum. Camcge's sources have `expr.condition is None` → gate doesn't fire → phantom offsets emit.

**Gate predicate change needed (Day 3):**

1. **Relax `expr.condition is not None` requirement** in `_find_pattern_c_alias_sum`. The condition check was originally there as a tighter scope marker for the launch fingerprint; the variable-scope guard (`_expr_references_var(expr.body, var_name)`) plus the equation-domain reference check already constrain the predicate to alias-sums that produce phantom offsets.
2. **Handle missing `condition` in `_apply_pattern_c_swap_to_term`** / `pattern_c_info`. When `pattern_c_info["condition"] is None`, the swap-applied condition is also None — no outer `DollarConditional` wrap on the consolidated Sum.

**Expected target shape (after Phase B camcge fix):**

```gams
# Before (current, 21 phantom-offset terms):
stat_dk(i).. pk(i) * nu_prodinv(i)
           + ((-1) * imat(i,i)) * nu_ieq(i)
           + (((-1) * imat(i-1,i)) * nu_ieq(i-1))$(ord(i) > 1)
           + (((-1) * imat(i+1,i)) * nu_ieq(i+1))$(ord(i) <= card(i) - 1)
           + ... 19 more
           =E= 0;

# After (Phase B camcge, single consolidated Sum):
stat_dk(i).. pk(i) * nu_prodinv(i)
           + sum(j, ((-1) * imat(j,i)) * nu_ieq(j))
           =E= 0;
```

The coefficient swap (`imat(i,j) → imat(j,i)`) plus multiplier reindex (`nu_ieq(i) → nu_ieq(j)`) is the same transform Phase A applies — just without the `condition` swap (since there's no condition). The existing `_apply_pattern_c_swap_to_term` already handles `term.condition is None` correctly (single-pass per-node).

**Effort estimate (Day 3):** ~2–4h (predicate relaxation + new test fixture for camcge plain-alias shape).

#### Phase B scoping — cesam2 (#1355)

**Phantom-offset emit (current main, Day 1 Phase A patch applied):** 18 phantom-offset terms, all `nu_COLSUM(i±N)` within `stat_tsam(i,j)`. Source equation:

```gams
COLSUM(jj)..   sum(ii, TSAM(ii,jj)) =e= Y(jj);
```

- `jj` and `ii` are both aliases of canonical set `i`.
- COLSUM has 1D domain `(jj,)`; TSAM (the variable being differentiated) has 2D domain `(i, j)` — both canonical `i`.
- **Dim-mismatch case:** eq domain 1D vs var domain 2D.

**Current buggy emit shape:**

```gams
stat_tsam(i,j).. (nu_ROWSUM(i)$(ii(i))
               + (nu_COLSUM(i)$(jj(i)))$(<huge sameas-block guard>)     # WRONG: nu_COLSUM(i), should be nu_COLSUM(j)
               + (((nu_COLSUM(i+7)$(jj(i+7)))$(ord(i) <= card(i) - 7))$(ord(j) = 7))$(...)
               + ... 17 more phantom-offset terms with sameas-block guards
               =E= 0;
```

The `sameas`-block guards (`sameas(i, 'ACT')` / `sameas(j, 'COM')` / etc.) are emit-formatting artifacts from element-to-set mapping firing on the dim-mismatch — they disappear once the consolidation is correct (the correct emit has no per-offset enumeration).

**Why Phase A doesn't fire on cesam2:** same as camcge — `expr.condition is None` on `sum(ii, TSAM(ii, jj))`. Predicate relaxation fixes the gate-firing problem.

**Gate predicate + transform change needed (Day 4):**

1. **Relax `expr.condition is not None`** (same change as camcge — sharing the gate-relaxation work from Day 3).
2. **Handle dim-mismatch in `_apply_pattern_c_swap_to_term`**: when the eq's domain is a strict prefix/subset of the var's domain (cesam2: `(jj,)` ↔ `(i, j)`), the multiplier reindex must produce `nu_COLSUM(var_dom[position_of_eq_idx])` — for cesam2 that's `nu_COLSUM(j)` (since `jj` binds to the var's second position). The current `_apply_pattern_c_swap_to_term` uses `(alias_name,) * len(mult_domain)` — correct for same-dim Phase A but wrong for dim-mismatch.

**Expected target shape (after Phase B cesam2 fix):**

```gams
# Before (current, 18 phantom-offset terms with sameas blocks):
stat_tsam(i,j).. (nu_ROWSUM(i)$(ii(i)) + (nu_COLSUM(i)$(jj(i)))$(<sameas mess>) + 18 phantom-offsets ...)$(...) =E= 0;

# After (Phase B cesam2, single zero-offset COLSUM term, no phantom offsets):
stat_tsam(i,j).. (nu_ROWSUM(i)$(ii(i)) + nu_COLSUM(j)$(jj(j)) + nu_SAMCOEF(...) + nu_TSAMEQ(...) + nu_GDPDEF + ...)$(ii(i) and ii(j)) =E= 0;
```

Note: the source body has NO Sum-wrap in the result — because cesam2's alias-sum binds `ii` to the var's first position (already controlled by `stat_tsam(i,j)`), so the consolidation produces a single multiplier reference, not a Sum.

This is a NEW Phase A→B distinction: when the alias is "shared" with a free var-domain index (dim-mismatch case), the consolidated form is a single zero-offset term rather than a Sum-wrapped term. The `_apply_pattern_c_swap_to_term` helper needs a dim-mismatch branch that emits this shape.

**Effort estimate (Day 4):** ~4–6h (predicate relaxation already from Day 3; dim-mismatch handling in the swap helper is the new work, plus 2 new test fixtures: dim-mismatch + sameas-block-cleanup verification).

#### Notes

- Phase B scope confirmed at 2 targets (camcge + cesam2). fawley and otpop remain reclassified out of Pattern C scope per Task 3 REPLAN (deferred to Sprint 27 #1356 / #1357 for the comp_up subset/superset shape).
- Day 3 lands camcge (simpler, ~2–4h). Day 4 lands cesam2 (dim-mismatch, ~4–6h). Day 5 Checkpoint 1 evaluates both.
- The Phase B gate-relaxation is conservative: even with `expr.condition is None` accepted, the predicate still requires (a) no `IndexOffset` on var's domain in body, (b) an aliased Sum over var's domain canonical, (c) the differentiated variable referenced inside the Sum's body. Plain alias-sums where the variable is NOT inside the Sum (e.g. quocge's `eqXp` body where `rt` is outside the alias sum) won't fire — the per-`_var_inside_alias_sum`-style scope check is unchanged.
- No PR14 artifact regeneration this PR (no `src/` changes).

---

### Day 3 — RECLASSIFIED to Sprint 27 #1381 (Pattern C Phase B redesign)

**Status:** COMPLETE (2026-05-11) — docs-only PR; `src/` rollback.
**Branch:** `sprint26-day3-pattern-c-phase-b-camcge`

| Task | Status |
|---|---|
| Implement gate-predicate relaxation (Day 2 scoping) | ❌ Rolled back — produced mathematically wrong emits on plain-alias bodies. See design discovery below. |
| File Sprint 27 carryforward issue | ✅ #1381 ("Pattern C Phase B redesign — camcge (#1354) + cesam2 (#1355) plain-alias + dim-mismatch consolidation") |
| Update `PLAN.md` Day 3 + Day 4 + Day 5 Checkpoint 1 + Sprint 26 Targets table | ✅ Day 3/4 marked RECLASSIFIED; Checkpoint 1 camcge/cesam2 rows → "n/a — deferred to Sprint 27 #1381"; Sprint 26 Solve / Match / path_syntax_error targets relaxed to maintain baseline |
| Update `PLAN_PROMPTS.md` Day 3 + Day 4 + Day 5 prompts | ✅ Same reclassification |
| SPRINT_LOG Day 3 entry (this section) | ✅ This entry |

#### Day 3 design discovery — why the Day 2 scoping was wrong

The Day 2 scoping concluded that Phase B for camcge needed only:
1. Relax `expr.condition is not None` requirement in `_find_pattern_c_alias_sum`
2. Find eq-domain index in body when no condition (camcge's `imat(i,j)` reference)
3. Re-use Phase A's `_apply_pattern_c_swap_to_term` (already handles `condition=None`)

Day 3 implemented the relaxation (~15 LOC) and ran it on camcge + the 54-model corpus. Result: **11 byte-shifted canaries, all producing mathematically wrong emits.**

**Concrete failures:**

| Model | Equation | Correct (hand-derived) consolidated form | Day 3 attempt produced |
|---|---|---|---|
| camcge | `stat_dk` | `sum(j, (-imat(j,i)) * nu_ieq(j))` | `((-1) * imat(j,j)) * nu_ieq(j)` — `j` free unbound; both coords wrong (should be `imat(j,i)`); no Sum wrap |
| camcge | `stat_xd` | `sum(j, (-io(j,i)) * nu_inteq(j))` | `((-1) * io(j,j)) * nu_inteq(j)` — same shape failure |
| quocge | `stat_pq` | `sum(j, (-ax(j,i)) * nu_eqpzs(j))` | `((-1) * ax(j,j)) * nu_eqpzs(j)` — same |
| prolog | `stat_q` | `sum(j, (-a(j,i)) * lam_cb(j))` (with `t` guard) | `a(i+1,i) * lam_cb(i) - lam_cb(i) + ...` — even more mangled |

**Root cause: element-to-set substitution collapses alias and eq-domain names BEFORE the swap can run.**

Phase A's launch case worked because the source body's condition was `ge(ss,s)` — the alias `ss` and eq-domain `s` are **textually distinct** symbols. The swap `ss ↔ s` correctly transforms each independently.

Plain-alias bodies have `imat(i,j)` (camcge) or `ax(i,j)` (quocge) where `j` is an alias of canonical set `i`. Element-to-set substitution (which runs BEFORE the auto Sum-wrap in `_add_indexed_jacobian_terms`) maps both `i` and `j` to canonical `i`, producing `imat(i,i)` in the indexed derivative. The Day 3 swap `i ↔ j` then transforms both `i`s to `j`s, producing `imat(j,j)` — wrong (position information lost when the names collapsed).

Additionally, the auto Sum-wrap doesn't fire because there's no free index after the collapse — leaving `j` as a dangling unbound reference in the swapped term.

**Phase A's swap-based approach is fundamentally launch-shape-specific.** Generalizing to plain-alias requires intercepting BEFORE element-to-set substitution and building the consolidated term explicitly from the source Sum's body structure (positions preserved). This is a builder redesign, not a predicate relaxation.

#### Sprint 27 #1381 — Phase B redesign scope

Sprint 27 carryforward issue #1381 documents the full Phase B redesign requirements:

- **Phase B-1 (~3–5h):** Source-body-driven builder for camcge's 4-of-5 simple variants (actp, pkdef, inteq, ieq). Read the source Sum's body AST, identify the alias position and eq-domain index in the coefficient, build the consolidated `Sum((alias,), coeff_swapped * mult(alias))` term explicitly.
- **Phase B-2 (~3–5h):** camcge's prodinv-style — eq-domain factor OUTSIDE the inner Sum (`prodinv(i)..  pk(i)*dk(i) =e= ... - kio(i)*sum(j, dst(j)*p(j))`). Target consolidated form: `dst(i) * sum(j, kio(j) * nu_prodinv(j))` — eq-side factor `kio` reindexed inside the new Sum, var-side factor `dst` left outside.
- **Phase B-3 (~4–6h):** cesam2's dim-mismatch (eq 1D, var 2D) + sameas-block element-to-set artifacts. Multiplier reindex must use the var-domain position bound to the eq-domain index.

Total: 10–16h, plus per-phase test coverage.

#### Sprint 26 schedule impact

- **Day 3 + Day 4 freed.** Available for forward-pulling Priority 4 (Option 1 short-circuit, originally Day 8–9) or Priority 5 (#1334 investigation, originally Day 8–10).
- **Day 5 Checkpoint 1 criteria updated** — camcge / cesam2 rows reclassified `n/a — deferred to Sprint 27 #1381`. GO routing now requires only Phase A landing + canary rows green (already true since Day 1 + Day 2).
- **Sprint 26 Targets relaxed:**
  - Solve: was ≥ 108 → now maintain ≥ 104 (no Phase A/B Solve gain this sprint; Priority 5 #1334/#1335 still potential +1–2 stretch)
  - Match: was ≥ 64 → now maintain ≥ 60 (same rationale)
  - path_syntax_error: was ≤ 6 → now maintain ≤ 9 (camcge + cesam2 stay in path_syntax_error)
  - Translate: was ≥ 135 → now ≥ 132 (Priority 4 still in scope for +2 from srpchase / iswnm)

#### Notes

- Phase A (launch) landed cleanly Day 1 + validated byte-stable across 54 canaries Day 2 — that work remains shipped via PR #1379 + PR #1380.
- Sprint 25 SPRINT_LOG.md Day 11 §"Open follow-ups (revised)" was explicit about launch-only scope ("proper fix for the launch Pattern C consolidation (#1306 test xfail)"). Sprint 26 Task 3 REPLAN added camcge + cesam2 as hypothesis-validation targets ("verify the gate predicate generalizes"). The Day 3 discovery is the empirical answer: it doesn't generalize via predicate relaxation alone; needs a builder redesign.
- No `src/` changes in this PR — Day 3 `src/` work rolled back. No PR14 obligation. Quality checks (`make format && make lint && make test`) verified clean against the docs-only diff per CONTRIBUTING.md / docs/development/AGENTS.md; no CI-gating change expected since no Python files were modified.

---

### Day 4 — RECLASSIFIED Priority 4 to Sprint 27 #1385; Priority 5 #1334 re-investigation completed

**Status:** COMPLETE (2026-05-12) — Priority 4 src/ rolled back; Priority 5 #1334 re-investigation shipped (separate docs-only PR).
**Branches:**
- Priority 4 reclassification: `sprint26-day4-priority-4-option-1-short-circuit` (this PR — docs-only after rollback)
- Priority 5 #1334: `sprint26-day4-priority-5-1334-investigation-on-p4` (separate docs-only PR; #1334 re-opened)

**Reschedule note (Day 3):** Day 4 originally scoped for Pattern C cesam2 Phase B work. Phase B reclassified to Sprint 27 #1381; Day 8's Priority 4 + Priority 5 #1334 work pulled forward. Day 8 is now buffer.

#### Priority 4 — RECLASSIFIED to Sprint 27 #1385 (Option 1 short-circuit redesign)

| Task | Status |
|---|---|
| Implement Option 1 short-circuit at `src/ad/index_mapping.py::enumerate_equation_instances` per Task 6 design | ❌ Rolled back — placeholder approach broken downstream. See "Day 4 Priority 4 design discovery" below. |
| Add unit + integration tests | ❌ Rolled back. Tests pass in isolation (positive predicate firing + negative cases) but the integration test only verified "translation completes" + "stat_ appears" — NOT emit correctness. Stronger test coverage required for Sprint 27 redesign (hand-derived KKT shape verification + GAMS compile-clean). |
| Re-profile srpchase / iswnm / sarf / mexls / nebrazil | ✅ Profile data captured BEFORE rollback (informative for Sprint 27 #1385 redesign): srpchase 846s → 5.7s (recovers translate but emit broken); iswnm 61.1s (recovers; emit not hand-verified); sarf/mexls/nebrazil still timeout >180s (per design doc §4.1, LOW-MEDIUM confidence — independent of the placeholder bug). |
| Tier 0 + Tier 1 canary byte-identical | ✅ 11/11 byte-identical was true of the BROKEN impl (the predicate is conservative — doesn't fire on Tier 0/1 canaries). After rollback: trivially still 11/11 byte-identical. |
| File Sprint 27 carryforward issue | ✅ #1385 ("Translation timeout Option 1 short-circuit redesign — placeholder approach broken downstream") with full design discovery + Phase 1/2/3 sub-scope breakdown. Issue doc at `docs/issues/ISSUE_1385_*.md`. |
| Update PLAN.md / PLAN_PROMPTS.md / Sprint 26 Targets table | ✅ Day 4 marked RECLASSIFIED in both docs; Translate target relaxed `≥ 132 → maintain ≥ 130`. |

##### Day 4 Priority 4 design discovery — why the Task 6 design was incomplete

Day 4 implemented the Task 6 design verbatim:

```python
def _build_symbolic_instance_placeholder(eq_domain):
    return [tuple(eq_domain)]  # e.g., [("srn",)] for srpchase's slack(srn)$..
```

**Translate-time savings worked** (srpchase 846s → 5.7s). **Emit-side correctness FAILED.** Concrete failures observed in srpchase emit (the Copilot reviewer caught all three on PR #1383):

```gams
stat_y(n).. ((((-1) * 1$(ancestor(srn,srn))) * nu_slack("srn"))$(srn(srn)))$((not leaf(srn))) + ((((-1) * 1$(ancestor(srn,srn))) * lam_demand("srn"))$(srn(srn)))$(leaf(srn)) - piL_y(n) =E= 0;

stat_x(n).. (prob(n) * price(n) - piL_x(n))$(srn(n)) =E= 0;
```

1. **`nu_slack("srn")` / `lam_demand("srn")`** — quoted literal "srn" where `srn` is the SET name (subset of `n`), not a valid element of `n` (which has elements `n0..n1000`). GAMS would emit UEL/domain errors at runtime.
2. **`1$(ancestor(srn,srn))`** — using "srn" as both arguments of `ancestor` SetMembershipTest.
3. **`stat_x(n)` missing the `comp_demand` cross-term** — Jacobian entries involving `x(srn)` got dropped during AD differentiation because `_diff_varref` requires exact index matches; with the symbolic placeholder the entries become 0.

**Root cause:** the design doc §2.3 asserted "the downstream emit path already handles symbolic-index instances per Sprint 25 #1306 / #1308 prior art." That assertion was wrong. The Sprint 25 prior art is for INDEXED stationarity equations where the equation HEADER `stat_<eq>(i)..` BINDS the symbolic index `i`. The Day 4 placeholder is different: it tries to use the SET NAME (`"srn"`) as an instance/element value, but the AD pipeline (`src/ad/constraint_jacobian.py::_diff_varref` etc.) treats the placeholder tuple `("srn",)` as a CONCRETE element string per the existing Cartesian-enumeration contract — NOT as a bound symbol.

**This is the same root-cause class as Sprint 26 Day 3 Phase B reclassification (Sprint 27 #1381).** Both shared the diagnostic gap: prep-task validation at the design stage (read code; identify patch sites; verify nothing obvious blocks the change) is necessary but insufficient. Empirical end-to-end verification — actually running the pipeline AND verifying emit correctness against hand-derived expected output — must be part of the design-validation phase, not deferred to implementation day. Sprint 27 prep should add a Phase 0 sub-task to both #1381 and #1385: "translate one concrete target model with a prototype patch + verify GAMS compile-clean + KKT body shape against hand-derived Lagrangian" BEFORE committing the implementation budget.

##### Sprint 27 #1385 — Option 1 redesign scope

Sprint 27 carryforward issue #1385 documents the full Option 1 redesign requirements (`docs/issues/ISSUE_1385_*.md` for the full issue doc):

- **Phase 1 (~3–4h):** Inventory AD/emit consumer sites + Option A (symbolic-instance handling end-to-end) vs Option B (alternative shape — emit-time guard rather than translate-time collapse) design choice.
- **Phase 2 (~4–6h):** Implement chosen option.
- **Phase 3 (~3–6h):** Integration tests verifying emit CORRECTNESS (hand-derived KKT shape + GAMS compile-clean) on srpchase + iswnm — NOT just "translation completes".

Total: 10–16h, plus Tier 0/1 byte-stable regression + PR14 obligation.

##### Sprint 26 schedule impact

- **Sprint 26 Translate target relaxed:** `≥ 132/142` (was `+2 from Priority 4`) → `maintain ≥ 130/142`. The +2 Translate from srpchase + iswnm carries forward to Sprint 27.
- **Day 5 Checkpoint 1 criteria** to be updated similarly when Day 5 is executed: "Priority 4 Option 1 short-circuit: srpchase translates" reclassifies to `n/a — deferred to Sprint 27 #1385`.
- **Day 8 buffer** (already free per Day 3 reschedule) absorbs whatever forward-pull alternatives the user chooses; Day 9 Priority 5 work remains as planned.

#### Priority 5 — #1334 re-investigation (separate docs-only PR; #1334 re-opened)

Detailed status + Approach 1 sketch in the Priority 5 PR. Highlights:

| Task | Status |
|---|---|
| Verify otpop bug pattern still visible in current main emit (per Task 7 §2.2 grep) | ✅ **Bug present.** `grep -cE "sum\(t__," /tmp/otpop_mcp.gms` returns 2 (matches §2.2 finding); spurious `sum(t__, ((-1) * (del(t__) * x(tt) * 0.365 * (1 - c))) * nu_kdef)$(t(tt))` wraps in `stat_p(tt)` line 207 + `stat_x(tt)` line 209. |
| Read GitHub issue #1334 close-comment + linked PR | ✅ #1334 closed 2026-05-05 by PR #1359 (docs-only; the body explicitly listed #1334 as supposed-to-stay-OPEN — closure was UNINTENDED). |
| Routing decision | ✅ **Re-opened #1334.** Posted re-open comment with bug-pattern reproduction, closure context, and Sprint 26 routing (Day 4 scoping → Day 9 implementation). |
| Scope and sketch the Approach 1 fix per `ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md` | ✅ See the §"Approach 1 sketch" section immediately below. Patch site `_replace_indices_in_expr` (def at `src/kkt/stationarity.py:2534`; `case ParamRef` branch at `:2652+`); align ParamRef substitution with parallel VarRef substitution when param_domain is strict subset of equation_domain. Day 9 picks up implementation alongside #1335. |

**Sprint 26 Day 4 Priority 5 deliverable:** investigation + scoping only. **NO `src/` changes** — Day 9 picks up implementation alongside #1335.

##### Approach 1 sketch (per `ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md` §Approach 1, refined per Task 7 §3.1)

**Patch site (verified Day 4 via `grep -nE`):** `_replace_indices_in_expr` in `src/kkt/stationarity.py` (def at line ~2534; the `case ParamRef` branch at ~2652+; grep anchor `def _replace_indices_in_expr(` to avoid line drift).

**Bug shape recap.** otpop's source body for `kdef` (NLP source at `data/gamslib/raw/otpop.gms:99`; the emit at `data/gamslib/mcp/otpop_mcp.gms:224` is the byte-identical body with `=e=` → `=E=` capitalization):

```gams
kdef.. k =e= sum(t, del(t) * (0.365 * (1 - c) * p(t) * x(t) - rd(t)));
```

Source declarations (`data/gamslib/raw/otpop.gms:27`): `del(t)` is declared on subset `t` (where `t ⊂ tt` per the set declaration in lines 12–13 of the source). The MCP emit at `data/gamslib/mcp/otpop_mcp.gms:30` widens this to `del(tt)` via the Issue #1164/#1175 `KKTSystem.param_domain_widenings` machinery (computed in `src/kkt/stationarity.py:1628+` and consumed in `src/emit/original_symbols.py:1069+` when emitting the Parameters block) — but the bug is that the ParamRef substitution machinery used inside AD's stationarity-body construction does NOT apply the same widening to source-body call-site references like `del(t)` inside the Sum. (For variables, the analogous in-body subset-preservation logic is Issue #666's `_preserve_subset_var_indices` at `src/kkt/stationarity.py:2943+`; the parameter-side analog called out by ISSUE_1334 §Approach 1 is the inverse — a `_promote_subset_param_indices` companion that aligns ParamRef substitution with parallel VarRef substitution under the eq-domain guard.)

When AD differentiates with respect to `x(tt)` for the indexed-stationarity path (`stat_x(tt)`):
- The Sum's iteration index is `t` (the subset; `t ⊂ tt`).
- `del` is declared on subset `t` in the source; the call-site `del(t)` uses that declared domain.
- Substitution `x(t) → x(tt)` should propagate to a parallel `del(t) → del(tt)` so the Jacobian entry's coefficient becomes `del(tt) * 0.365 * (1 - c) * p(tt)` — a per-`tt` scalar (the `p(tt)` factor is the other variable in the product `p(t) * x(t)`; differentiating w.r.t. `x` leaves `p` as the coefficient). The symmetric `stat_p(tt)` case gets `del(tt) * 0.365 * (1 - c) * x(tt)`.

What actually happens (current main):
- The Sum-internal `t` doesn't get substituted to `tt` consistently across `del(t)`, `p(t)`, and `x(t)`.
- `x(t)` (for `stat_x`) and `p(t)` (for `stat_p`) become `x(tt)` / `p(tt)` (correctly, via the indexed-stationarity rewrite).
- `del(t)` gets WRAPPED in a residual `Sum(("t__",), ...)` — the offset-resolution machinery treats the leftover unbound `t` as a free index requiring an aggregating Sum. The `t__` is a fresh alias minted to bind it.
- The `nu_kdef` cross-terms then emit as `sum(t__, ((-1) * (del(t__) * x(tt) * 0.365 * (1 - c))) * nu_kdef)` in `stat_p(tt)` and `sum(t__, ((-1) * (del(t__) * 0.365 * (1 - c) * p(tt))) * nu_kdef)` in `stat_x(tt)` — over-counting `del` by `|t|` in both.

**Approach 1 fix (Day 9 scope):**

1. In `_replace_indices_in_expr`, identify the ParamRef branch where `param.indices` includes a name that's been substituted in a parallel VarRef in the same expression context.
2. When `param_domain` (the parameter's declared domain) is a strict subset of `equation_domain` (the stationarity equation's domain) AND a parallel VarRef has been substituted to use the eq-domain variable, align the parameter substitution with the variable substitution: rewrite `del(t)` → `del(tt)` (using the eq-domain index) the same way `x(t)` was rewritten to `x(tt)`.
3. Result: the Jacobian entry for `(kdef, x(tt))` becomes a clean scalar `del(tt) * 0.365 * (1 - c) * p(tt)` (and `(kdef, p(tt))` becomes `del(tt) * 0.365 * (1 - c) * x(tt)`) — no Sum wrap, no `t__`.

**Alternative (Approach 2 — fallback if Approach 1 has unexpected side-effects):** targeted suppression in `_add_indexed_jacobian_terms` (per Task 7 §3.1 fix-site correction; was incorrectly attributed to `_add_jacobian_transpose_terms_scalar` in earlier `ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md` drafts — that function only handles SCALAR stationarity; otpop's `stat_p(tt)` and `stat_x(tt)` are INDEXED). Check whether unconstrained indices in the Jacobian-entry derivative match the equation-domain guard restriction (`$(t(tt))`); if they do, substitute and skip the `Sum` wrap.

**Day 9 acceptance gate** (per Task 7 §3.1):
- otpop emit `grep -cE "sum\(t__," data/gamslib/mcp/otpop_mcp.gms` returns 0 (currently 2).
- otpop NLP-warm-started MCP residual on `stat_x('1990')` shrinks toward 0 (Day 10 acceptance — full reproducer per `ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md` §Diagnostic).
- Tier 0 + Tier 1 (11 models) byte-stable across the regression.
- Combined PR with #1335 narrow AD fix (same target model otpop, same verification recipe).

**Estimated effort (Day 9):** 4–8h #1334 (Approach 1 implementation + investigation contingency) + 4–8h #1335 (per Task 7 §3.2 scalar-equation `if eq_domain:` gate fix at `src/ad/constraint_jacobian.py:986`/`:1107`) = 8–18h total Priority 5 (Day 9 + Day 10 wrap).

##### Notes (Priority 5)

- #1334 doesn't subsume #1357 (per Task 7 §2.4 — different code paths: `src/kkt/stationarity.py` for #1334 vs `src/kkt/complementarity.py` + `src/emit/emit_gams.py` for #1357). #1357 stays in Sprint 27 deferral.
- #1335 (`nu_zdef` missing from `stat_p`) is a separate but related bug — same target model otpop, different fix-site (`src/ad/constraint_jacobian.py:986`/`:1107` `if eq_domain:` gate). Day 9 lands both fixes in one PR per Task 7 §"Combined PR" framing.
- This Priority 5 sub-PR is docs-only — no `src/` changes per Day 4 scoping. Day 9 picks up the implementation.

#### Notes

- The Day 4 src/ commit (`243fe578` on the Day 4 PR branch) was reverted via `git reset --hard main` on the branch. The PR title is updated to reflect reclassification.
- Per Sprint 26 Day 3 reclassification PR #1382, this is the **second** Sprint 26 day where a prep-task design was empirically disproved. The pattern is consistent: design-doc inspection of patch sites + downstream-handling assertions is insufficient without empirical end-to-end correctness verification.
- No `src/` changes in either Day 4 PR (Priority 4 reclassification + Priority 5 investigation). No PR14 obligation. Quality checks (`make format && make lint && make test`) verified clean against the docs-only diff per CONTRIBUTING.md / docs/development/AGENTS.md; no CI-gating change expected since no Python files were modified.

---
