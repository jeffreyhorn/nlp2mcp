# Sprint 35 Detailed Schedule (Day 0 + Days 1–13)

**Prep Task:** 12 (Critical — final integration; on the critical path) · **Date:** 2026-07-24 · **Owner:** Sprint 35 planning (schedule + GO/NO-GO)
**Day-0 code anchor:** `78ceaead` (S34 close — the `--resolve-changed` baseline for every emit-touching day; advanced from S33's `750803b2`, which is now historical because `src/` changed at S34 Day 4 via P4)
**Budget:** 92–134 h nominal work-items over 14 days (Day 0 + Days 1–13) at ≤ 12 h/day (168 h cap); **real in-sprint footprint ~34–70 h** (P1/P2 design budgets were spent in prep — Task 11's retrospective-budget finding). Risk **LOW-to-flat / bimodal on P4**.
**Scope:** docs-only — the 14-day schedule + the pasteable per-day prompts (`prompts/PLAN_PROMPTS.md`). The fixes the designs specify are *built in-sprint*, not here.

---

## 1. Sprint 35 Goal

Land the six Sprint-34 REPLAN'd/deferred/banked carryforwards — but with a **structural difference from its three predecessors: four of the five deep tracks REPLAN'd/DEFER'd/Epic-5-deferred IN PREP** (Tasks 6/7/8/9), so their in-sprint REPLAN risk is **already resolved** rather than a prospective probability gambled on at Day 1/5/6. **P1 mine head-offset dual subsystem** (#1443 — REPLAN'd in prep, the whole keying/pairing space value-invariant → Sprint-36 consultation), **P2 sarf symbolic `stat_task` emit** (#1385 — DEFER'd in prep, measured > 303 s, +1 Translate is the lowest-leverage KPI → dedicated effort), **P3 fawley constraint-index-diagonal correction** (#1111/#1112 — PROCEED correctness-only but **0 bucket**, H-b), the **NEW P4 ganges/gangesx multi-root recovery** (the sole live bucket gate — `$141`→`$145`→`$149`, target +2), and **P5 camcge dual-consistent Walras** (#1330 → Epic 5, expected MS-4) + **rocket PATH** (#1462 → Sprint 36). So the schedule **front-loads P4 (Days 1–5)** — the exact inversion of the prior three sprints' "deep tracks front-loaded, failure-cohort in the back half" that produced three flat closes — because the three-sprint record is unambiguous: **mine ×4, sarf ×3, fawley ×3 have consumed ~half of three sprints' budget and moved zero buckets, while the failure-cohort track produced the only genuine move in that window (S33 sample)**. P4 *is* the failure-cohort class, promoted to first-class, and it carries the sprint's **only live REPLAN gate** (its `$149` `_diff_prod` surgical fix). Front-loading surfaces that REPLAN by the **Day-5 checkpoint** and frees budget to P6 (the second bucket source) early if it exits.

## 2. Acceptance Criteria (from `PROJECT_PLAN.md` §"Sprint 35" + `BASELINE_METRICS.md` + Task 11's honest projection)

The projection is **BIMODAL on P4, not "modal-flat"** (Task 11) — either P4 lands +2 or the sprint is flat:

| KPI | Day-0 (S34 close) | P4 lands (all 3 roots + both cold-match) | P4 REPLANs / not cold-match |
|---|---|---|---|
| Parse | 142 | 142 | 142 |
| Translate | 135 | **135** (P2 DEFER'd — the PROJECT_PLAN "+1 → 136 via sarf" is **off**) | 135 |
| Solve | 108 | **110** (+2 ganges + gangesx) | 108 |
| Match (142 corpus) | 93 | **95** | 93 |
| genuine floor (PR25) | 75 | **77** *only if ganges/gangesx **cold**-match* (presolve-only = methodology = 0 floor) | 75 |
| model_infeasible | 7 | ≤ 7 (no in-sprint recovery of the mi cohort) | 7 |
| path_syntax_error | 7 | **5** (−2) | 7 |
| all-219 Match | 96 | 98 | 96 |

- **The stretch ≥ 112 is a-priori REFUTED** (Task 11): the PROJECT_PLAN's ">≥ 112 if the ganges pair + one deep track land" required a deep track, and all three REPLAN'd/deferred in prep — the max reachable is **110** (P4's +2), or +1 more only if a P6 residual-cohort model recovers a whole root-set. **Do not promise ≥ 112 or a floor > 77.**
- **The entire in-sprint bucket hope is P4 (+ the P6 residual cohort).** P1/P2/P3/P5 are all **0-bucket** (prep-resolved).

## 3. Sequencing Constraints (from the prep-task outputs)

- **Front-load P4 (Days 1–5), not the back half** (Task 11 §Front-load, argued from the three-sprint record): P4 is the designated best shot *and* carries the sprint's only live REPLAN gate, so it gets the prime slot and its `$149` `/tmp` control surfaces the REPLAN by the **Day-5 checkpoint**. **The golden-regeneration window does not constrain P4's start** — Task 3 **measured** the slow-emit regen at ~8.2 min scoped (worst case ~25–50 min; fits a normal ≤ 12 h day, **no overnight slot needed**), so P4 runs Days 1–5 without reserving a nightly window (the operational blocker that banked S34's verified `$141` fix is removed).
- **P4 is a PER-ROOT sequence with a hard invariant: no bucket moves until all three roots land** (Task 5, empirically proven — the `$141`-only re-emit leaves `$145×3 + $149×9`). Steps 1–2 (`$141`/`$145`) are Low-risk banked roots; **step 3 (`$149`) is the live REPLAN gate**. A mid-sequence flat KPI is the **expected** state, not a failure.
- **Per-model verification is mandatory, never inferred** (the exact assumption S34 got wrong at Day 11): ganges AND gangesx each independently emit → compile → count residual `$NNN` (assert 0) → solve (cold AND presolve, `modelstat` asserted) → bucket → match. **Compile-clean-but-not-solving is NOT a recovery** (`path_syntax_error → model_infeasible`, a different bucket) — report it as such.
- **P1/P2 need NO in-sprint execution slot** — REPLAN'd/DEFER'd in prep; their in-sprint footprint is a documentation line + the Sprint-36 hand-off bundle (folded into Day 8's P5 slot). **P3 is optional** (correctness-only, 0 bucket) and must not displace P4 or P6.
- **P6 (the residual failure cohort) is the second bucket source** (Task 4's per-model catalog: turkey `$161`, dinam/indus `$140`+`$149`, turkpow/clearlak `$149`+`$171`) — placed Days 6–7, right after P4, so the freed P4/P1/P2 budget concentrates on the two bucket sources.
- **Checkpoints:** Day 5 (P4 PROCEED/REPLAN + freed-budget reallocation), Day 10 (Checkpoint 2), Day 13 (final retest under ≥ 3 `PYTHONHASHSEED`).

## 4. Day 0 — Kickoff + Day-0 Traces + Control Probes (≤ 6 h)

- Confirm Day-0 = S34 close (`BASELINE_METRICS.md`: Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7 / path_syntax_error 7 / Translate 135 / Parse 142 / all-219 Match 96). Verify `git diff 78ceaead..HEAD -- src/ scripts/` is empty before skipping the retest; if non-empty, run a fresh retest.
- **Re-confirm each Phase-0 gate's Day-0 fingerprint (PR24)** (`PHASE_0_ACCEPTANCE_GATES.md` §1) — the banked `file:line` is a *hypothesis*, wrong ~half the time:
  - **P4 ganges/gangesx (the live gate — run FIRST):** re-confirm the per-model compile counts (`$141×15` corpus-wide, `$145×3`, `$149×9` on ganges) and that `$141` at `src/emit/original_symbols.py:152` still removes all 15 (Task 5 scratch re-emit); re-confirm the Task-4 hand-derived `stat_pc` cross-term `prod(j,(pc(j)/pc00(j))**ac(j,r)) * ac(i,r)/pc(i)` and the 18-model prod-in-stationarity regression set (lmp2 most sensitive).
  - **P1 mine:** re-confirm the boundary is `x.m=0`-degenerate (CASE_B, dual CONSISTENT) — the gate is **pre-refuted** (no candidate reaches cold-MS-1 @ 17500); **no `/tmp` control warranted**, the exit (Sprint-36 consultation) is taken.
  - **P2 sarf:** the O(active = 398)-not-369,024 count + the measured > 303 s baseline — DEFER'd; no build.
  - **P3 fawley:** CASE_B `stat_bq` raw 473 → 18.468 control; H-b re-confirm (MS-5 @ 4399.557, the emit-correct `stat_trans(tr-2)` residual is the harness max).
  - **P5 camcge:** the S1∧S2∧S3 detector fires only on camcge; expected MS-4. **rocket:** clean at the NLP point (CASE_C_OBJDEF, dual CONSISTENT 1.53e-10).
- **Restate the PR25 tally** (genuine 75; the → +2 conversion map is entirely P4-contingent and specifically on a **cold** match). **`modelstat` asserted before every objective read; `x.up=inf` BANNED (mine); the Case-c sign flip BANNED.**
- **GO/NO-GO for Day 1** (§17). Docs/trace-only (no `src/`). **No PR** (or a docs-only trace-notes PR).

## 5. Day 1 — Priority 4: ganges/gangesx `$141` + `$145` banked-root re-apply (~7 h)

- Re-apply the banked-and-verified `$141` fix (`_param_assignment_references_varref_attr` skip in `emit_post_assignment_na_cleanup`, `src/emit/original_symbols.py:152`, mirroring `_param_assignment_has_division:137`) + the `$145` universal-set (`*`-domain) skip in the same cleanup loop. **Verified this sprint** to remove all 15 `$141` + the `$145×3` (Task 5). Regenerate the ~9 `.l`-calibration collateral goldens with the **scoped** `check_golden_staleness.py --models …` `--fix` (Task 3; **never** the unscoped `make regen-goldens`) + determinism ×3.
- **⚠ No bucket moves yet** (Task 5, proven: the `$141`-only re-emit leaves `$145×3 + $149×9`; even `$141`+`$145` leaves `$149×9`). This is the **expected** mid-sequence flat state — steps 1–2 **do not ship on their own** (the "no bucket → no `src/`" rule); they land only as part of the all-three-roots P4 landing.
- **Phase-0 gate:** `PHASE_0_ACCEPTANCE_GATES.md` §1 P4 (roots 1–2). **Emit-touching WIP (not yet shipped). Est ~7 h.**

## 6. Day 2 — Priority 4: `$149` `/tmp` control BEFORE `src/` (the sole live REPLAN gate) (~8 h)

- **PR27 `/tmp` control BEFORE any `src/` change:** prototype the AD-layer product-rule fix (`src/ad/derivative_rules.py:_diff_prod:3276` + the emit-alias contract, Task 4 — **NOT** the prior's `stationarity.py:_add_indexed_jacobian_terms` surface, refuted). The control must (a) reproduce Task 4's hand-derived `stat_pc` cross-term (`i` controlled, no free `j`), (b) drive ganges's 9 `$149` → 0, and (c) leave the **18-model prod-in-stationarity regression set byte-identical** (lmp2 most sensitive — the name-match case the collapsed `_diff_prod` branch relies on).
- **This is the sprint's only live REPLAN gate.** **REPLAN exit:** if the `_diff_prod` correction cannot be made surgical against the 18-model set → **bank all three roots** (steps 1–2 alone = 0 bucket + golden churn, exactly the S34-banked outcome — no `src/` ships) and reallocate P4's budget to P6/P7. `modelstat` asserted; no `x.up=inf`.
- **Phase-0 gate:** `PHASE_0_ACCEPTANCE_GATES.md` §1 P4 (`$149`). **`/tmp`-only (no `src/`). Est ~8 h.**

## 7. Day 3 — Priority 4: `$149` `src/` land + per-model residual-count (~8 h)

- If the Day-2 control passed: apply the `_diff_prod` correction to `src/`, then for **ganges and gangesx independently** emit → compile (`gams a=c`) → **count residual `$NNN` by code (assert 0)**. Regenerate goldens (scoped `--fix`) + determinism ×3.
- **Phase-0 gate:** the per-model protocol (encoded so it can't be skipped under time pressure). **Emit-touching. Est ~8 h.**

## 8. Day 4 — Priority 4: per-model solve + match verification (~8 h)

- For **ganges and gangesx independently** (never inferred from one another): translate → solve **cold AND presolve** (`modelstat` asserted) → bucket → match classification (**cold-match = genuine floor; presolve-only = methodology = 0 floor**). Answer **Unknown 4.4** (DESIGN-SPECIFIED — the recovery verdict, the one aspect not executed in prep): do ganges AND gangesx each actually solve-and-match, and cold or presolve? A fourth per-model root could surface at the compile step (the S34 lesson).
- **Emit-touching (the all-three-roots landing). Est ~8 h.** *(P4 total ~14–20 h across Days 1–5.)*

## 9. Day 5 — Priority 4: close-or-REPLAN + Checkpoint 1 (~7 h)

- **Checkpoint 1 (Day 5):** `--resolve-changed --since-commit 78ceaead` re-solve of the changed-golden set (bucket-diff vs the committed DB) + golden-staleness (PR26) + the presolve-divergence detector + the PR25 re-baseline. **NO-GO** if any *unchanged* golden moved backward (`match→mismatch`, `model_optimal→model_infeasible`, presolve-match→abort). **The sprint's only live REPLAN gate has now fired** (P4 PROCEED or REPLAN).
- **Freed-budget reallocation:** if P4 REPLAN'd, its 14–20 h joins P6/P7 (already the plan — the sprint still has enormous slack). If P4 landed, record the bucket move + the cold-vs-presolve floor verdict.
- **Verifies (in-sprint):** the P4 gate + no-regression. **REPLAN exit explicit. PR (emit-touching, or docs-only if banked). Est ~7 h.**

## 10. Days 6–7 — Priority 6: residual failure-cohort re-triage (the second bucket source) (~16 h)

- Work Task 4's per-model catalog — the residual `path_syntax_error` cohort that `$149` does **not** unblock (only ganges/gangesx are product-rule beneficiaries): **turkey `$161`** (the dotted-tuple set — a-priori hard), **dinam/indus** (`$140`+`$149`), **turkpow/clearlak** (`$149`+`$171`). **Multi-root discipline (Unknown 6.2):** verify per-model, never infer one model's roots from another's; **no model recovers until its whole root-set clears.** Each candidate passes the `--resolve-changed --since-commit 78ceaead` GO gate before landing.
- **Bucket at stake:** up to +1 more Solve/Match if a whole root-set clears (a-priori hard per Task 4). **Est ~16 h across two days.**

## 11. Day 8 — Priority 5: camcge Epic-5 gate + rocket/mine/fawley Sprint-36 bundle (~6 h)

- **camcge (Epic-5 `/tmp` gate, expected MS-4):** prototype the full dual-consistent Walras redefinition → MS-1 @ omega 191.7346 (dual side, `modelstat` asserted). **Expected MS-4** (the price-pin variant + 3+ sprints of variants all stayed MS-4 at the correct primal) → the per-model-numéraire declaration is the documented **Epic-5** fallback. **camcge is excluded from the in-sprint Solve target.**
- **Sprint-36 hand-off bundle (Task 9):** submit the FINALIZED rocket PATH-consultation input to **Sprint 36** with the renumbering fixes (11 "Sprint 33" refs + the "Sprint 35" refs → Sprint 36 — technical content current, only sprint-number labels stale); bundle mine (the primal-degenerate-LP consultation question, P1's exit) + fawley (the H-b `--force` survey, P3's +Solve) into the same package. **0 in-sprint bucket. No `src/`. Est ~6 h.**

## 12. Day 9 — Priority 3: fawley constraint-index-diagonal correction (optional, correctness-only) (~8 h)

- **Optional / low-priority (0 bucket, H-b) — must not have displaced P4 or P6.** **PR27 `/tmp` control BEFORE `src/`:** the constraint-index-diagonal `$(sameas(cfq__,cf))` guard on the `qsb`/`pbal` terms (the predicate in `_add_indexed_jacobian_terms`, `src/kkt/stationarity.py:5861`, distinct from #1049 `:7176` and the variable-index diagonal — a **hypothesis** to re-trace) must drive **`max|stat_bq| → 0`** (scoped to `stat_bq`, not the harness global max, which retains the emit-correct `stat_trans(tr-2)` non-emit residual — Task 8's finding). **Leak-free:** no mbal-term change, the 1-D core + 2-D cohort (cesam2/camcge/ps2_f_s/ps2_s/ps3_s_gic/polygon) byte-identical; `--resolve-changed --since-commit 78ceaead` GO with fawley the only changed golden.
- **REPLAN exit (gate leak):** any mbal/cohort/1-D-core change or `max|stat_bq|` not reaching 0 → DEFER again (a dedicated effort + the 2-D-cohort harness); budget → P6/P7. **The +Solve is out of P3 scope** (H-b → the Sprint-36 `--force` survey). **Emit-touching IF it lands. Est ~8 h.**

## 13. Day 10 — Priority 7: infrastructure (fixtures + floor tracking) + Checkpoint 2 (~8 h)

- P7 property fixtures, **each gated on its track's landing, fail-before/pass-after** (Unknown 7.1, the S33 `test_sample_pruned_var_l_init.py` skip-if-absent + S34 `test_p4_maximize_bound_transfer_sense_aware` patterns): a **ganges-recovery** raw-emit fixture (if P4 landed); shape12 head-offset / shape13 sarf / a fawley 2-D second-index fixture are **not applicable** (P1/P2 no-`src/`; P3 optional). Recompute the PR25 genuine-floor tracking against the anchor (**75 → 75 or 77**); refresh the `--resolve-changed` checkpoint targets; continue the Epic-4 `SUMMARY.md` row-35 groundwork (Unknown 7.3 — larger than a row fill).
- **Checkpoint 2 (Day 10):** `--resolve-changed --since-commit 78ceaead` re-solve + golden-staleness + the PR25 tally. **Est ~8 h.**

## 14. Day 11 — REPLAN-slack + P6/P7 continuation (~8 h)

- Absorb any Day-5 REPLAN reallocation (P4 → P6/P7); continue the residual-cohort push or the P7 fixtures. With the retrospective-budget slack (~34–70 h real work vs 168 h cap), this day is genuine buffer for a **thorough P4 + P6** push rather than spreading budget thin. **Est ~8 h.**

## 15. Day 12 — Sprint-36 carryforward drafting + pre-retest staging (~8 h)

- Draft `SPRINT_36_CARRYFORWARDS.md` (mine primal-degenerate-LP consultation + sarf dedicated symbolic-emit effort + fawley `--force` survey + rocket PATH consultation + any P4/P6 REPLAN); stage the Day-13 retest. **Est ~8 h.**

## 16. Day 13 — Final Retest + Closeout (~8 h)

- Full retest; **determinism ×3 `PYTHONHASHSEED ∈ {0,1,42}`**; `--resolve-changed --since-commit 78ceaead` GO; the PR25 genuine-vs-methodology final tally; `SPRINT_LOG.md` + `SPRINT_RETROSPECTIVE.md`; the honest close (bimodal — Solve 108 or 110; floor 75 or 77; **not** ≥ 112). **Est ~8 h.**

## 17. Budget Summary

| Days | Priority / work | Nominal h | In-sprint footprint |
|---|---|---|---|
| 0 | Kickoff + Day-0 traces + control probes | — | ~6 |
| 1–5 | **P4 ganges/gangesx multi-root recovery** (`$141`/`$145` Days 1; `$149` `/tmp` control Day 2 — the sole live REPLAN gate; `src/` + per-model verify Days 3–4; close + Checkpoint 1 Day 5) | 14–20 | ~38 |
| 6–7 | P6 residual failure-cohort (the second bucket source) | 8–14 | ~16 |
| 8 | P5 camcge Epic-5 gate + Sprint-36 bundle (rocket + mine + fawley) | 10–16 → ~2–4 | ~6 |
| 9 | P3 fawley correctness-only (optional, 0 bucket) | 12–18 | ~8 |
| 10 | P7 infrastructure + Checkpoint 2 | 6–10 | ~8 |
| 11–12 | REPLAN-slack + Sprint-36 carryforwards + staging | — | ~16 |
| 13 | Final retest + closeout | 4 | ~8 |

**The per-priority work-item sizings** (`PROJECT_PLAN.md` §"Sprint 35"): P1 [18–24 h] + P2 [20–28 h] + P3 [12–18 h] + P4 [14–20 h] + P5 [10–16 h] + P6 [8–14 h] + P7 [6–10 h] + retest [4 h] = **92–134 h** — **fits the 168 h cap**; **no day > 12 h** (heaviest ~8 h — well under the PROJECT_PLAN's ~11 h ceiling, because **P1's 18–24 h + P2's 20–28 h design budgets were spent in prep**, Task 11's retrospective finding). The **real in-sprint footprint is ~34–70 h** (P4 + P6 + P7 + retest + the small P5/P3 slots), less than half the cap — ample slack for a thorough P4 + P6 push. The nominal 92–134 h is retained for the PROJECT_PLAN reconciliation, but it is now **mostly retrospective**.

## 18. Phase 0 Coverage Audit (PR20 + PR24 + PR27)

Only **P4** (and **P3** if it lands leak-free) touch `src/`; **P1/P2/P5 ship no `src/`**. Each emit-touching gate cites `kkt_residual.py` (PR27) + a control-before-`src/` rule: **P4** the `$149` `/tmp` control (the hand-derived `stat_pc` cross-term + the 18-model regression set — Day 2, BEFORE `src/`), plus the per-model emit→compile→count→solve→match protocol encoded so it can't be skipped; **P3** the constraint-index-diagonal localize-by-column `/tmp` (473 → 18.468 → 0, scoped to `stat_bq`). P1's gate is **pre-refuted** (no candidate reaches cold-MS-1 @ 17500 — the whole keying/pairing space is value-invariant); P2's is a **timing** gate (O(active = 398) seconds vs the measured > 303 s) — both exits taken in prep. P5 camcge is an Epic-5 `/tmp` gate (expected MS-4); rocket is a docs hand-off (no solve gate). **`modelstat` asserted before every objective read; `x.up=inf` BANNED (mine); the objective-gradient sign flip BANNED (Case-c, refuted 4×).** Every emit-touching PR passes determinism ×3 (PR12) + golden-staleness (PR26, scoped `--models` for P4) + presolve-divergence + `--resolve-changed --since-commit 78ceaead`. **"No bucket → no `src/`"** with the S34-P4 exception (fast, regenerable goldens + `--resolve-changed` GO) — P4 is *expected* to invoke it (steps 1–2 bank if `$149` REPLANs).

## 19. Known Unknowns Status Snapshot + GO/NO-GO

**All 29 Known Unknowns are accounted for** (`KNOWN_UNKNOWNS.md`). Of the **19 Critical/High** (7 Critical + 12 High), **none remain a genuine Day-0 blocker**:

| Disposition | Count | Unknowns |
|---|---|---|
| ✅ VERIFIED (resolved in prep) | 24 | 1.1, 1.3, 1.4, 1.5, 2.1, 2.3, 2.4, 2.5, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.5, 4.6, 5.2, 5.3, 6.1, 6.2, 6.3, 7.1, 7.2, 7.3 |
| ❌ WRONG / REFUTED → REPLAN (resolved as an exit) | 1 | 1.2 (mine H_dual — REPLAN'd; the exit is Sprint-36 consultation) |
| 🔍 DESIGN-SPECIFIED (an in-sprint execution gate **by design**, not a blocker) | 4 | **4.4** (P4 per-model recovery verdict — *the* live in-sprint gate, executed Day 4), 2.2 (post-change sarf timing — moot, P2 DEFER'd), 3.1 (fawley `stat_bq → 0` closure — P3 optional), 5.1 (camcge MS-1 — Epic-5-deferred, expected MS-4) |

**No Critical/High unknown is `🔍 INCOMPLETE` as a genuine Day-0 blocker.** The four DESIGN-SPECIFIED items are in-sprint execution gates by design — the correct disposition (a `/tmp`/solve control that can only run against the in-sprint `src/` change), not unresolved risk. The one refuted unknown (1.2) is resolved as a *taken exit* (mine → Sprint-36), not an open question.

**⇒ GO for Day 0.** Every Critical/High unknown is resolved, taken as an exit, or a DESIGN-SPECIFIED in-sprint gate; the sole live bucket lever (P4) is front-loaded with its REPLAN gate surfacing by the Day-5 checkpoint; the golden-regen ship-blocker that banked S34's fix is measured away (fits a normal day); the budget fits with enormous slack; and the honest bimodal projection (Solve 108 or 110; floor 75 or 77; **not ≥ 112**) binds the acceptance criteria.

## 20. Risk Register + Mitigations

| Risk | Mitigation |
|---|---|
| P4's `$149` `_diff_prod` correction cannot be made surgical against the 18-model regression set (Med-High — the sole live REPLAN) | The `/tmp` control (Day 2, BEFORE `src/`) surfaces it by the Day-5 checkpoint; REPLAN → bank all three roots (no `src/` ships, the S34 outcome — now with goldens *measured* regenerable) + reallocate 14–20 h to P6/P7. `modelstat` asserted; `x.up=inf` BANNED. |
| P4 lands clean but ganges/gangesx solve only under presolve, not cold (Unknown 4.4) | Report honestly: presolve-only = methodology = **0 genuine floor** (Match still +2, floor stays 75). The floor gain is *contingent* on a cold match — do not promise floor 77. |
| A fourth per-model root surfaces at the compile step (the S34 Day-11 lesson) | Per-model protocol encoded (emit→compile→count→solve→match, ganges AND gangesx independently, never inferred); compile-clean-but-not-solving reported as `path_syntax_error → model_infeasible`, a different bucket. |
| P3 fawley's constraint-index-diagonal guard leaks onto mbal / the 2-D cohort (Medium; bucket 0 either way) | The `/tmp` control + the cohort byte-diff, both pre-`src/`; leak → DEFER again (P3 is optional and must not displace P4/P6). |
| P6 residual cohort a-priori hard (whole root-sets, turkey `$161` dotted-tuple) | P6 is the *second* bucket source, not the first; a flat P6 is acceptable — the sprint's headline is P4. |
| The sprint closes flat (P4 REPLANs) | Expected under the bimodal projection; the firm product is de-risking + the banked roots + the Sprint-36 bundle — zero broken code, the S32/S33/S34 pattern. |

## 21. Related Documents

- **This sprint's prep:** `PREP_PLAN.md` · `KNOWN_UNKNOWNS.md` · `BASELINE_METRICS.md` (Task 2) · `TOOLING_AND_BACKLOG_ANALYSIS.md` (Task 3) · `GANGES_149_PRODUCT_RULE_ANALYSIS.md` (Task 4) · `GANGES_RECOVERY_DESIGN.md` (Task 5) · `MINE_DUAL_ARCHITECTURE_DESIGN.md` (Task 6) · `SARF_SYMBOLIC_EMIT_DESIGN.md` (Task 7) · `FAWLEY_DIAGONAL_DESIGN.md` (Task 8) · `CAMCGE_ROCKET_PLAN.md` (Task 9) · `PHASE_0_ACCEPTANCE_GATES.md` (Task 10) · `REPLAN_RISK_ASSESSMENT.md` (Task 11)
- **The per-day prompts:** `prompts/PLAN_PROMPTS.md` (this task's companion deliverable)
- **Format precedents:** `SPRINT_34/PLAN.md` + `SPRINT_34/prompts/PLAN_PROMPTS.md`
- **Sprint 35 scope:** `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 35 (Weeks 35–36)"
- **The carryforwards:** `SPRINT_34/SPRINT_35_CARRYFORWARDS.md`

---

**Status:** Sprint 35 is **GO for Day 0** — all 12 prep tasks complete; the schedule front-loads P4 (Days 1–5, the sole live bucket gate) so its `$149` REPLAN surfaces by the Day-5 checkpoint, with P6 (the second bucket source) Days 6–7, the small P5 Epic-5/Sprint-36 slot Day 8, P3 optional Day 9, P7 + Checkpoint 2 Day 10, REPLAN-slack + Sprint-36 carryforwards Days 11–12, and the final retest Day 13. The honest **bimodal** projection binds: **Solve 108 or 110; genuine floor 75 or 77 (cold-match-contingent); Translate 135; ≥ 112 REFUTED.** P1/P2 REPLAN'd/DEFER'd in prep (no in-sprint slot); P5 camcge Epic-5-deferred + rocket → Sprint-36; P4 is the designated best shot and the sprint's outcome is decided by its single `$149` fix.

**Document Status:** ✅ Complete — Sprint 35 Prep Task 12
**Last Updated:** 2026-07-24
**Owner:** Sprint 35 Planning Team
