# Sprint 25 Day-by-Day Execution Prompts (Revised Post-Day-5)

Step-by-step execution prompts for Sprint 25 Days 0–15. **Revised 2026-04-24** after the Day 5 evidence-driven investigation disproved the Phase 2 Pattern A hypothesis. See `../DAY5_PATTERN_A_INVESTIGATION.md` and `../PLAN.md` §"Day 5 Pivot" for context.

**Usage:** Copy the relevant day's prompt into a new conversation to execute that day's work. Each prompt is self-contained; the contributor does not need prior context beyond the prerequisites section.

**Branch naming convention:** `sprint25-dayN-<slug>` (one branch per day; rebase/merge to main at PR merge).

**Pipeline retest command:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` (~2h15m under doubled timeouts; use for Day 11 Checkpoint 2 + Day 14 final retest).

---

## Days 0–5: COMPLETED — Historical Reference

Days 0–5 have been executed. PR links:

- **Day 0** — Setup & Kickoff (baseline verification, golden-file generation, SPRINT_LOG initialization).
- **Day 1** — WS3 Determinism Landing (Option D + PR12) → **PR #1301 (merged)**.
- **Day 2** — WS1 Phase 1 Start + WS2 Batch 1 Start (#1275 presolve paths; trace instrumentation) → **PR #1302 (merged)**.
- **Day 3** — WS1 Phase 1 Prototype + #1280 (unquoted UEL dots; `_partial_collapse_sum` multi-index mechanical port) → **PR #1303 (merged)**.
- **Day 4** — WS1 Phase 1 Complete + WS2 Batch 2.5 (#1289 ganges calibration stripping) → **PR #1304 (merged)**.
- **Day 5** — **Pattern A Investigation (pivot day)** — evidence-driven examination of qabel/abel/launch concluded none exhibit Pattern A. Launch has Pattern C phantom offsets in KKT stationarity; qabel/abel AD is byte-correct. → **PR #1305**; deliverable `DAY5_PATTERN_A_INVESTIGATION.md`.

The Day 5 pivot DROPS the originally-planned Phase 2 broader Pattern A rollout and replaces it with Pattern C work (Days 6–7) plus a cohort sanity sweep and qabel/abel PATH-solve reassessment (Days 7–8). See `../PLAN.md` §"Day 5 Pivot" for full rationale.

Original Day 0–5 prompts are preserved in the file history of `docs/planning/EPIC_4/SPRINT_25/prompts/PLAN_PROMPTS.md` on `main`; the merged PRs listed above (PR #1301–#1305) mark the relevant points in that history for locating the pre-revision version (`git log --follow -- docs/planning/EPIC_4/SPRINT_25/prompts/PLAN_PROMPTS.md`).

---

## Day 6 Prompt: Pattern C Prototype (NEW — replaces original Day 6 Checkpoint 1)

**Branch:** `sprint25-day6-pattern-c-prototype`.

**Objective:** Locate the phantom-offset enumeration code in KKT stationarity, reproduce launch's `stat_iweight` bug minimally, prototype a conservative gate that only enumerates ±N offsets when the source has a real IndexOffset.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_25/DAY5_PATTERN_A_INVESTIGATION.md` — findings + §"Key code pointers for Day 6".
- Read `docs/planning/EPIC_4/SPRINT_25/PLAN.md` §"Day 6 — Pattern C Prototype".
- Key source files: `src/kkt/stationarity.py` (candidate functions `_compute_lead_lag_conditions`, `_collect_lead_lag_offsets`; also any site that iterates equation bodies and enumerates alias bindings).
- Reference emission from Day 5 trace (`/tmp/sprint25-day5/launch_mcp.gms`):
  ```gams
  stat_iweight body contains phantom offsets:
    sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s+1))$(ord(s) <= card(s) - 1)
    sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s+2))$(ord(s) <= card(s) - 2)
    sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s-1))$(ord(s) > 1)
    sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s-2))$(ord(s) > 2)
  ```
  Source `dweight(s)..` has NO IndexOffset — just a conditional alias sum.

**Tasks to Complete (~4–6 hours):**

1. **Locate the emission site.** Grep `src/kkt/` for `card(` and `ord(` adjacent to alias-iteration patterns; inspect `_compute_lead_lag_conditions` and `_collect_lead_lag_offsets`. Document the call path that produces the launch `stat_iweight` ±N terms. If neither candidate is the culprit, broaden search to `src/kkt/assemble.py` and `src/emit/emit_gams.py`.
2. **Reproduce minimally.** Add a new test in `tests/unit/kkt/test_pattern_c_alias_offset_gate.py`:
   - Build a synthetic IR mirroring `dweight(s).. weight(s) =e= sum(ss$ge(ss,s), iweight(ss) + pweight(ss)) + ...` — alias `ss` over `s`, conditional sum, no IndexOffset on `s`.
   - Assemble KKT stationarity for the equation.
   - Assert the emitted `stat_iweight` body has NO `s+N`/`s-N` terms. After the prototype lands, a single identity-offset `sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s))` term will remain; that term still exhibits the Day-5 Bug #2 (`mis-scoped $(ge(ss, s))` condition inside a `sum(ss, ...)` whose multiplier doesn't depend on `ss`) and is deliberately OUT OF SCOPE for Day 6 — see task 9 below.
   - Verify the test FAILS against current main (documents Bug #1 — the phantom offsets) and will PASS against the prototype. The test should NOT over-specify the residual `sum(ss, ...)` multiplier argument, since Bug #2's fix may later change it.
3. **Prototype the gate.** Two-sided approach:
   - Check the equation IR for actual `IndexOffset` nodes on the alias's base set before enumerating ±N offsets. If the body contains no IndexOffset on `s` (or whatever the alias base set is), skip ±N enumeration entirely.
   - If IndexOffsets do exist, preserve the current enumeration logic (so models like twocge #1277 aren't broken — see Day 10 for post-Pattern-C twocge re-validation).
4. **Verify launch translates correctly.** Translate launch (`python -m src.cli data/gamslib/raw/launch.gms -o /tmp/launch_mcp.gms --skip-convexity-check`) and inspect `stat_iweight`:
   - **Must hold post-prototype:** `iwf(s) * nu_diweight(s)` remains intact; ALL four phantom-offset `nu_dweight(s±N)` terms are gone; a single identity-offset alias-sum term remains.
   - **Still-present Day-5 Bug #2 (expected and out of scope today):** the residual alias-sum term is `sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s))` — note the multiplier `nu_dweight(s)` does NOT depend on the summed index `ss`, so the `sum` degenerates into a spurious `card(ss-satisfying-ge)` factor. This mis-scoped condition is a separate defect from phantom-offset enumeration and is tracked via task 9.
5. **Tier 0 dispatch canary:** `diff /tmp/sprint25-golden/dispatch_mcp.gms <(python -m src.cli data/gamslib/raw/dispatch.gms -o /dev/stdout --skip-convexity-check)` — MUST be empty.
6. **Tier 1 canary:** run the Reference command at the bottom of this file on quocge, partssupply, prolog, sparta, gussrisk, ps2_f, ps3_f, ship, splcge, paklive. MUST match golden.
7. **Do NOT run full 54-set regression today** — defer to Day 7 to isolate the prototype failure surface. A mid-prototype regression on a Tier 2 model is easier to triage on Day 7 when we also have the cohort-sweep data.
8. **File a new GH issue** `pattern_c_phantom_offset_stat_iweight` — title "Pattern C: KKT stationarity emits phantom ±N offsets on alias-only conditional sums (launch)"; body references `DAY5_PATTERN_A_INVESTIGATION.md` §Bug #1.
9. **File a separate GH issue** `pattern_c_mis_scoped_alias_condition` — title "Pattern C Bug #2: KKT stationarity mis-scopes `$(ge(ss, s))` condition inside `sum(ss, ...)` where the multiplier is not indexed by `ss`"; body references `DAY5_PATTERN_A_INVESTIGATION.md` §Bug #2 and links to the Day 6 PR as the landing point for Bug #1. Target Sprint 25 Day 13 buffer or Sprint 26 carryforward depending on schedule.

**Quality Checks:** `make typecheck && make lint && make format && make test`.

**Commit + PR:** One PR for this day. Title: `Sprint 25 Day 6: Pattern C prototype — gate phantom-offset enumeration on real IndexOffset presence`.

---

## Day 7 Prompt: Pattern C Validation + Pattern A Cohort Sanity Sweep (NEW)

**Branch:** `sprint25-day7-pattern-c-validation-plus-cohort-sweep`.

**Objective:** Validate the Day 6 prototype on the full 54-set golden-file regression. Run a short evidence-gathering sweep on the six Pattern A candidate models to confirm they are not AD-blocked (establishing that dropping the original Phase 2 was correct) and classify each.

**Prerequisites:**
- Day 6 PR merged or cherry-picked onto this branch.
- `DAY5_PATTERN_A_INVESTIGATION.md` for the investigation methodology (trace capture + emission inspection).
- `AUDIT_ALIAS_AD_CARRYFORWARD.md` for the original Pattern A cohort list: #1138, #1139, #1140, #1142, #1145, #1150.

**Tasks to Complete (~5–7 hours):**

1. **Full 54-set golden-file regression with Day 6 prototype.** Enumerate matching models from the frozen baseline status JSON, then diff each (see `../PLAN.md` and the Sprint 24 prompts for the standard incantation). Expected 0 regressions; if regressions appear, classify by whether they involve alias-of-IndexOffset patterns — that tells you whether to narrow the Pattern C gate or widen it.
2. **Full launch re-validation.** Translate launch fresh. Then run two separate GAMS invocations:
   - First, a compile-only check: `gams /tmp/launch_mcp.gms action=c` — this verifies the emitted MCP parses and symbols resolve, but does NOT attempt a solve.
   - Second, a full PATH solve: invoke GAMS without `action=c` (or with `action=ce` for compile+execute) so PATH actually runs and produces a solution. Measure rel_diff against the baseline NLP solution.

   Document both steps in `DAY7_COHORT_SWEEP.md`. If rel_diff materially improves (e.g., 0.17 → <0.01), mark launch as a Match candidate for Day 14 pipeline retest.
3. **Pattern A cohort sanity sweep** — for each of the 6 models in #1138, #1139, #1140, #1142, #1145, #1150:
   - Map the GH issue to the concrete model name (check `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Pattern A rows).
   - Run `SPRINT25_DAY2_DEBUG=1 .venv/bin/python -m src.cli data/gamslib/raw/<model>.gms -o /tmp/sprint25-day7/<model>_mcp.gms --skip-convexity-check --quiet 2> /tmp/sprint25-day7/<model>_trace.stderr`.
   - Inspect the model's primary stationarity equation(s) in the emitted MCP. Classify as:
     - **Pattern A shape (AD-blocked):** `_partial_collapse_sum` gap → emits `0` where a known-nonzero derivative belongs.
     - **Pattern C shape (phantom offsets):** stationarity emission has ±N offsets not present in the source.
     - **Other:** nonconvex-solver noise, scalar/domain mismatch, or latent KKT bug.
   - Record the classification in `DAY7_COHORT_SWEEP.md` (one row per model with: model name, issue ID, symptom shape, evidence reference [trace file path or specific line in emitted MCP], proposed Sprint 26 follow-up issue title).
4. **If any cohort model is classified as Pattern-C-shaped,** extend the Day 6 prototype gate to cover it; re-run the 54-set regression after the extension.
5. **If any cohort model is classified as genuinely Pattern-A-shaped** (the Day 5 investigation missed it), document in `DAY7_COHORT_SWEEP.md` + flag for potential Day 13 buffer-day work; file a Sprint 26 carryforward.
6. **Create `docs/planning/EPIC_4/SPRINT_25/DAY7_COHORT_SWEEP.md`** — structure mirrors DAY5_PATTERN_A_INVESTIGATION.md with a "Classification Table" section + one short evidence subsection per model.
7. **Tier 0 + Tier 1 canary** — same commands as Day 6.

**Quality Checks:** `make typecheck && make lint && make format && make test`.

**Commit + PR:** One PR for this day. Title: `Sprint 25 Day 7: Pattern C full-regression validation + Pattern A cohort classification sweep`. Body references `DAY5_PATTERN_A_INVESTIGATION.md` + the new `DAY7_COHORT_SWEEP.md`.

---

## Day 8 Prompt: qabel/abel PATH-Solve Reassessment + WS2 Batch 2 Start (#1279)

**Branch:** `sprint25-day8-qabel-abel-reassess-plus-1279`.

**Objective:** Determine whether qabel/abel rel_diff (0.08, 0.30) reflects a real emission bug or nonconvex-solver noise. Start WS2 Batch 2 with #1279 robustlp scalar-widening.

**Prerequisites:**
- `DAY5_PATTERN_A_INVESTIGATION.md` §"Evidence — KKT stateq term on qabel/abel" — specifically the `nu_stateq(n, k-1)$(ord(k) > 1)` shift and its compatibility with the declared `nu_stateq(n, k)` domain.
- GAMS + PATH solver installed locally. (If not — run the PATH solve on a CI runner; this day's results can be captured asynchronously.)

**Tasks to Complete (~5–7 hours):**

1. **Translate qabel + abel fresh** (they should be unchanged from Day 5 since neither is Pattern-C-shaped):
   ```bash
   for m in qabel abel; do
     python -m src.cli data/gamslib/raw/$m.gms -o /tmp/sprint25-day8/${m}_mcp.gms --skip-convexity-check
   done
   ```
2. **Full PATH solve** (NOT `action=c` — action=c hits pre-existing Error 141 cascades per Day 5). Capture solve output + rel_diff measurement.
3. **Classify the result:**
   - **If rel_diff < ~1e-4 (acceptable numerical noise on nonconvex problem):** mark #1138 (qabel) and/or #1139 (abel) as "non-bug; nonconvex-solver noise" in `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Pattern A rows. Close the corresponding GH issues with resolution note linking to this Day 8 PR.
   - **If rel_diff remains material (systematic bias):** bisect the `stat_x` emission against the expected symbolic form. Prime suspects per Day 5 evidence: the `nu_stateq(n, k-1)$(ord(k) > 1)` domain-shift term (check emitter's handling of equations declared over `(n, k+1)`). File a narrow follow-up issue with the specific emission bug localized; add to Day 13 buffer if a same-day fix is feasible, otherwise Sprint 26 carryforward.
4. **#1279 robustlp scalar-widening:** Fix in `src/ir/normalize.py`. The emitter currently emits `defobj(i)` as a domain-indexed equation when the AD treats it as scalar. Fix the normalize pass to consistently widen OR consistently narrow. Add unit test in `tests/unit/ir/test_normalize_scalar_widening.py`.
5. **Tier 0 + Tier 1 + full 54-set golden-file regression.** Expected 0 regressions from the #1279 fix (it only affects robustlp-shaped models).

**Quality Checks:** `make typecheck && make lint && make format && make test`.

**Commit + PR:** One PR for this day. Title: `Sprint 25 Day 8: qabel/abel PATH-solve reassessment + #1279 robustlp scalar-widening`.

---

## Day 9 Prompt: WS2 Batch 2 Continue (#1276, #1281, #1292)

**Branch:** `sprint25-day9-batch2-complete`.

**Objective:** Land Batch 2 remainder: #1276 fawley duplicate `.fx`, #1281 lmp2 duplicate Parameter declaration, #1292 turkpow line wrap.

**Prerequisites:**
- Read `CATALOG_EMITTER_BACKLOG.md` §Batch 2.
- Key source files: `src/emit/emit_gams.py` (assignment-emit + declaration-emit sites for `.fx` and Parameter); new `_DeclaredSymbolTracker` helper.

**Tasks to Complete (~5–7 hours):**

1. **Implement `_DeclaredSymbolTracker` helper.** Module-local in `src/emit/emit_gams.py` (or a small new file). Tracks `(symbol_name, scope_tuple)` pairs that have already been emitted so subsequent duplicate declarations/assignments can be skipped. Unit test under `tests/unit/emit/`.
2. **#1276 fawley:** Use the tracker to detect already-emitted `.fx` assignments on `(var_name, indices)` pairs and skip duplicates. Confirm fawley translates + compiles.
3. **#1281 lmp2:** Same helper, applied to Parameter declarations. Confirm lmp2 translates + compiles.
4. **#1292 turkpow:** Add line-wrapping in the emitter for `sameas()` Cartesian-product expansions when the emitted line length exceeds ~1000 chars. Wrap at natural boundaries (after `+`/`-` operators in top-level sums). Add synthetic test with a known-large expansion asserting max line length.
5. **Tier 0 + Tier 1 + full 54-set golden-file regression.**

**Quality Checks:** `make typecheck && make lint && make format && make test`.

**Commit + PR:** One PR for this day. Title: `Sprint 25 Day 9: WS2 Batch 2 complete (#1276 fawley .fx dedup, #1281 lmp2 Parameter dedup, #1292 turkpow line wrap)`.

---

## Day 10 Prompt: WS2 Batch 3 Core (#1277 post-Pattern-C + #1278 tautology)

**Branch:** `sprint25-day10-batch3-core`.

**Objective:** Re-validate #1277 twocge mixed offsets now that Pattern C is live; fix #1278 `ord(r) <> ord(r)` tautology.

**Prerequisites:**
- Day 6 Pattern C prototype merged.
- `CATALOG_EMITTER_BACKLOG.md` §#1277, §#1278.

**Tasks to Complete (~5–7 hours):**

1. **#1277 twocge re-validation:** Re-translate twocge. Inspect `stat_tz` for offset-alias correctness. If still broken, file a narrow follow-up issue with the specific mis-emission localized and move on (Batch 3 is not a single-fix blocker).
2. **#1278 `ord(r) <> ord(r)` tautology:** Locate the substitution site in `src/kkt/stationarity.py`. The stationarity emitter produces `ord(r) <> ord(r)` (always false) where `ord(r) <> ord(rp)` is intended (the alias-correct form). Fix + unit test in `tests/unit/kkt/`.
3. **Tier 0 + Tier 1 + full 54-set golden-file regression.**

**Quality Checks:** `make typecheck && make lint && make format && make test`.

**Commit + PR:** One PR for this day. Title: `Sprint 25 Day 10: WS2 Batch 3 core — #1277 twocge post-Pattern-C + #1278 tautology fix`.

---

## Day 11 Prompt: WS2 Batch 3 Finish (#1290, #1291) + Checkpoint 2

**Branch:** `sprint25-day11-batch3-complete-plus-checkpoint2`.

**Objective:** Close Batch 3 with #1290 ferts identifier length + #1291 clearlak statement ordering. Evaluate Checkpoint 2 (GO/CONDITIONAL/NO-GO) via full pipeline retest.

**Prerequisites:**
- `CATALOG_EMITTER_BACKLOG.md` §#1290, §#1291.
- `../PLAN.md` §"Day 11 — WS2 Batch 3 Finish ... + Checkpoint 2" for the Checkpoint 2 criteria table.

**Tasks to Complete (~6–8 hours):**

1. **#1290 ferts identifier length:** Fix the 67-char multiplier-name violation. Add a synthetic-hash-shortening pass in the emitter: when an emitted identifier would exceed the GAMS 63-char identifier limit, replace the tail with a short deterministic hash of the full name. Record the mapping in a comment banner near the declaration so a human reader can trace back.
2. **#1291 clearlak statement ordering:** Hoist `sum(leaf, ...)` AFTER `leaf(n) = yes$(...)` initialization, not before. Verify determinism via 3-seed run (`for s in 0 1 42; do PYTHONHASHSEED=$s python -m src.cli data/gamslib/raw/clearlak.gms -o /tmp/clearlak_s${s}.gms --skip-convexity-check; done; shasum -a 256 /tmp/clearlak_s*.gms`).
3. **Run full pipeline retest:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` (~2h15m).
4. **Evaluate Checkpoint 2 criteria** (see `../PLAN.md` §"Day 11"):

   | Criterion | Day 11 value | GO threshold | Status |
   |---|---|---|---|
   | Match | | ≥56 (GO) / ≥55 (COND) / <54 (NO-GO) | |
   | Solve | | ≥100 (GO) / ≥99 (COND) / <99 (NO-GO) | |
   | path_syntax_error | | ≤7 (GO) / ≤9 (COND) / >11 (NO-GO) | |
   | model_infeasible | | ≤7 (GO) / ≤8 (COND) / >8 (NO-GO) | |
   | Canaries (Tier 0+1) | | All match (GO) / ≤1 regression (COND) | |
   | Tests | | All pass | |

5. **Document decision in `SPRINT_LOG.md`** Day 11 entry. If NO-GO: Day 12 reverts offending PRs; Phase E cancelled; Day 13 buffer used for revert stabilization.

**Quality Checks:** `make typecheck && make lint && make format && make test`.

**Commit + PR:** One PR for this day. Title: `Sprint 25 Day 11: WS2 Batch 3 complete (#1290 ferts, #1291 clearlak) + Checkpoint 2`.

---

## Day 12 Prompt: WS4 Small Priorities (#1270 + #1271)

**Branch:** `sprint25-day12-small-priorities`.

**Objective:** Land the #1270 multi-solve gate extension and the #1271 dispatcher refactor.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_25/DESIGN_SMALL_PRIORITIES.md`.
- Key sources: `src/validation/driver.py:151–225` (#1270), `src/emit/original_symbols.py::emit_pre_solve_param_assignments` (nested `_loop_tree_to_gams_subst_dispatch`).

**Tasks to Complete (~7.5–9.5 hours):**

1. **#1270 (3.5–4.5h):** Implement Approach A cross-reference in `_collect_top_level_marginals_with_param_feedback`. 4-fixture test matrix (per `DESIGN_SMALL_PRIORITIES.md` fixture table — only F1 should flag):
   - F1 saras-style feedback (MUST flag).
   - F2 post-solve reporting (MUST NOT flag).
   - F3 multi-stage display (MUST NOT flag).
   - F4 partssupply-style `var.l` (MUST NOT flag).
   - Canaries: gussrisk / sparta (MUST NOT flag — currently matching).
2. **#1271 (4–5h):** Unify signature `_loop_tree_to_gams(node, *, token_subst=None)`. Remove nested `_loop_tree_to_gams_subst_dispatch`. Byte-diff regression — enumerate the 135 currently-translating models from the frozen baseline status JSON:

   ```bash
   TRANSLATING=$(python - <<'PY'
   import json
   from pathlib import Path
   data = json.loads(Path('data/gamslib/gamslib_status.json').read_text())
   print(' '.join(e['model_id'] for e in data['models']
                  if (e.get('nlp2mcp_translate') or {}).get('status') == 'success'))
   PY
   )
   mkdir -p /tmp/pre /tmp/post
   for m in $TRANSLATING; do
     PYTHONHASHSEED=0 python -m src.cli data/gamslib/raw/$m.gms -o /tmp/pre/${m}.gms --skip-convexity-check
   done
   # apply refactor
   for m in $TRANSLATING; do
     PYTHONHASHSEED=0 python -m src.cli data/gamslib/raw/$m.gms -o /tmp/post/${m}.gms --skip-convexity-check
   done
   diff -r /tmp/pre /tmp/post  # MUST be empty
   ```

**Quality Checks:** `make typecheck && make lint && make format && make test`.

**Commit + PR:** One PR for this day. Title: `Sprint 25 Day 12: WS4 small priorities — #1270 multi-solve gate extension + #1271 dispatcher refactor`.

---

## Day 13 Prompt: Buffer / Optional Phase E / Sprint-Close Prep

**Branch:** `sprint25-day13-buffer`.

**Objective:** Absorb slippage; optional Phase E routing if Checkpoint 2 was GO; file Sprint 26 carryforward issues.

**Tasks to Complete (~3–6 hours):**

1. **Buffer:** Close any Batch 3 / WS4 tail.
2. **OPTIONAL (Checkpoint 2 GO + ≥3h slack):** Phase E routing — re-inspect:
   - **#1141 (kand):** re-verify after Sprint 24 multi-solve gate extension. If still broken, classify as Pattern E via `DESIGN_ALIAS_AD_ROLLOUT.md` §Phase 4.
   - **#1144 (launch post-Pattern-C):** Day 6 Pattern C fix may have already resolved this. Re-check.
   - **#1147 (camshape):** Re-verify.
3. **OPTIONAL stretch (≥4h clear headroom):** Per Task 8 contingency, implement Option 1 short-circuit in `src/ad/index_mapping.py::enumerate_equation_instances` (with supporting behavior in `resolve_set_members` + static `SetMembershipTest` failure path in `src/ir/condition_eval.py`). Target: unblock srpchase (+1 Solve) and possibly iswnm (+1 Solve).
4. **OPTIONAL (if Day 8 flagged qabel/abel as real emission bug with a localized fix):** Land the narrow qabel/abel `nu_stateq` domain-shift fix here; otherwise carry forward to Sprint 26.
5. **File Sprint 26 carryforward issues (label `sprint-26`):**
   - Translation timeouts: 4 of 5 hard timeouts (iswnm, sarf, mexls, nebrazil) unless Option 1 landed today.
   - `mine` `internal_error` / `SetMembershipTest`.
   - Any Phase E issue not resolved (#1141, #1144, #1147 if not landed today).
   - **Original Pattern A Phase 2 cohort models reclassified per Day 7 cohort sweep** — close original issues with resolution note "reclassified via Day 7 sweep as <shape>; see `DAY7_COHORT_SWEEP.md`"; file new Sprint 26 issues under the correct bug category.
6. **Update `KNOWN_UNKNOWNS.md`** with end-of-sprint discoveries.

**Quality Checks:** Skip unless `.py` touched.

**Commit + PR:** One PR for this day (if any code changes) + `SPRINT_LOG.md` entry for Sprint 26 issue-filing. Title: `Sprint 25 Day 13: buffer + Sprint 26 carryforward issue filing`.

---

## Day 14 Prompt: Final Pipeline Retest

**Branch:** `sprint25-day14-retest`.

**Objective:** Definitive pipeline metrics per PR6.

**Tasks to Complete (~3–4 hours):**

1. **Full pipeline:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` (~2h15m).
2. **Record final metrics:** Parse / Translate / Solve / Match + 4 `outcome_category` counts.
3. **Cross-check against `../PLAN.md` §Sprint 25 Targets (Revised).**
4. **Error-influx accounting (per PR7 + PR10 re-calibrated):**
   - Alias-AD / Pattern C gross fixes vs new errors. Check against 30% budget.
   - Emitter-recovered gross fixes vs new errors. Check against 80–100% budget.
5. **Commit updated `data/gamslib/gamslib_status.json`** (and note that `.gms` emitted artifacts remain advisory-only until PR12 fully stabilizes per `BASELINE_METRICS.md` §6).

**Quality Checks:** Skip unless `.py` touched.

**Commit + PR:** One PR for this day. Title: `Sprint 25 Day 14: final pipeline retest`.

---

## Day 15 Prompt: Sprint Close + Retrospective

**Branch:** `sprint25-day15-retro`.

**Objective:** Write retrospective (with special focus on the Day 5 pivot lessons), update CHANGELOG + PROJECT_PLAN, file Sprint 26 recommendations.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_24/SPRINT_RETROSPECTIVE.md` as template.
- Day 14 final metrics recorded in `SPRINT_LOG.md`.

**Tasks to Complete (~3–4 hours):**

1. **Write `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md`** using Sprint 24 template:
   - Metrics delta against `../PLAN.md` §Sprint 25 Targets (Revised).
   - Acceptance criteria pass/fail.
   - Went well / what could be improved.
   - **Special section: Day 5 pivot retrospective.** What the original Phase 2 Pattern A hypothesis got wrong. The evidence methodology that disproved it — trace capture under `SPRINT25_DAY2_DEBUG=1`, reading the emitted GAMS, comparing to the formal symbolic derivative — is reusable. Recommend: in future sprints where a multi-issue workstream shares a single hypothesized root cause, run the Day 5 investigation Pre-Sprint-0 rather than post-hoc mid-sprint.
   - PR10 re-calibration outcome — did the 30% / 80–100% split hold against Pattern C's narrower scope?
   - New recommendations (PR16+) for Sprint 26.
2. **Update `CHANGELOG.md`** Sprint 25 Summary (mirror Sprint 24's format). Include the Day 5 pivot as a key narrative beat, not just a metrics delta.
3. **Update `PROJECT_PLAN.md` Rolling KPIs.**
4. **File Sprint 26 recommendations** — Pattern A cohort reclassification, Pattern C remainder, translation timeouts, Phase E remainders, any new discoveries.

**Quality Checks:** Skip unless `.py` touched.

**Commit + PR:** One PR for this day. Title: `Sprint 25 Day 15: retrospective + sprint close`.

---

## Reference: Tier 1 Canary Command (unchanged)

```bash
# Run before any WS1 / Pattern C / WS2 PR merges — expect zero diffs from golden files
for m in dispatch quocge partssupply prolog sparta gussrisk ps2_f ps3_f ship splcge paklive; do
  diff /tmp/sprint25-golden/${m}_mcp.gms \
    <(python -m src.cli data/gamslib/raw/$m.gms -o /dev/stdout --skip-convexity-check 2>/dev/null) \
    && echo "✅ $m" || echo "❌ $m REGRESSED"
done
```

---

## Reference: 54-Set Golden-File Regression Command (unchanged)

```bash
MATCHING=$(python - <<'PY'
import json
from pathlib import Path
data = json.loads(Path('data/gamslib/gamslib_status.json').read_text())
print(' '.join(e['model_id'] for e in data['models']
               if (e.get('solution_comparison') or {}).get('comparison_status') == 'match'))
PY
)
for m in $MATCHING; do
  diff /tmp/sprint25-golden/${m}_mcp.gms \
    <(python -m src.cli data/gamslib/raw/$m.gms -o /dev/stdout --skip-convexity-check 2>/dev/null) \
    && echo "✅ $m" || echo "❌ $m REGRESSED"
done
```
