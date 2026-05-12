# Sprint 26 Day-by-Day Execution Prompts

Step-by-step execution prompts for Sprint 26 Days 0–13.

**Usage:** Copy the relevant day's prompt into a new conversation to execute that day's work. Each prompt is self-contained; the contributor does not need prior context beyond the prerequisites section.

**Branch naming convention:** `sprint26-dayN-<slug>` (one branch per day; rebase/merge to main at PR merge).

**Pipeline retest command:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` (~3h based on Task 9 Day 0 baseline timing; use for Day 13 final retest. Day 5 + Day 10 use targeted multi-model retests instead).

**Day 0 baseline reference:** Parse 142/142, Translate 130/142, Solve 104, Match 60. See `docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md` for full per-bucket composition + per-model bucket-provenance.

---

## Day 0 Prompt: Setup & Kickoff

**Branch:** `sprint26-day0-kickoff` (matches `PLAN.md` Day 0). Day 0 is verification + log-initialization (no `src/` changes), but per CONTRIBUTING.md and branch protection on `main`, the `SPRINT_LOG.md` Day 0 entry still ships via a docs-only PR — see §"Commit + PR" below.

**Objective:** Verify Day 0 baseline; initialize SPRINT_LOG; brief on all prep-task outputs.

**Prerequisites:**
- All 11 Sprint 26 prep tasks COMPLETE on `main` (verify via `git log --oneline -25 docs/planning/EPIC_4/SPRINT_26/`).
- Baseline freeze on `main`: `data/gamslib/gamslib_status.json` matches `BASELINE_METRICS.md` Day 0.

**Tasks to Complete (~2 hours):**

1. Verify Day 0 baseline matches `docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md` §2 — the snippet below classifies each in-scope model into its current pipeline bucket and prints per-bucket counts that you can directly compare against §2.1 / §2.2 / §2.3:
   ```bash
   .venv/bin/python -c "
   import json
   from collections import Counter
   data = json.load(open('data/gamslib/gamslib_status.json'))
   in_scope = [m for m in data['models'] if m['convexity']['status'] in ('likely_convex', 'verified_convex')]
   print('In-scope:', len(in_scope))

   def bucket(m):
       parse = m.get('nlp2mcp_parse', {}).get('status', 'unknown')
       if parse != 'success':
           return f'parse_{parse}'
       trans = m.get('nlp2mcp_translate', {})
       if trans.get('status') != 'success':
           cat = (trans.get('error') or {}).get('category', 'unknown')
           return f'translate_{cat}'
       solve = m.get('mcp_solve', {})
       oc = solve.get('outcome_category', 'unknown')
       if solve.get('status') != 'success' or oc not in ('model_optimal', 'model_optimal_presolve'):
           return f'solve_{oc}'
       return f'compare_{m.get(\"solution_comparison\", {}).get(\"comparison_status\", \"unknown\")}'

   counts = Counter(bucket(m) for m in in_scope)
   for b, c in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
       print(f'  {c:>3}  {b}')

   # Headline checks (must match BASELINE_METRICS.md §2):
   parse = sum(c for b, c in counts.items() if not b.startswith('parse_'))  # all reach parse_success
   translate = sum(c for b, c in counts.items() if not b.startswith(('parse_', 'translate_')))
   solve = sum(c for b, c in counts.items() if b.startswith('compare_'))
   match = counts.get('compare_match', 0)
   print()
   print(f'Parse:     {parse}/142   (BASELINE: 142)')
   print(f'Translate: {translate}/142   (BASELINE: 130)')
   print(f'Solve:     {solve}     (BASELINE: 104)')
   print(f'Match:     {match}     (BASELINE: 60)')
   "
   ```
   Expected: 142 in-scope; per-bucket and headline counts match BASELINE_METRICS.md (Parse 142, Translate 130, Solve 104, Match 60). If any count diverges, do NOT proceed — investigate via an explicit revision-range diff against the Day 0 baseline commit (`f1cdb91f` — the PR #1373 merge that froze the baseline):
   ```bash
   # 1. What changed on main since the baseline freeze (any file)?
   git diff f1cdb91f..HEAD --stat
   # 2. Did the status JSON or BASELINE_METRICS itself drift?
   git diff f1cdb91f..HEAD -- data/gamslib/gamslib_status.json \
                             docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md
   ```
2. Initialize `docs/planning/EPIC_4/SPRINT_26/SPRINT_LOG.md` Day 0 entry (mirror Sprint 25 SPRINT_LOG.md format — header, baseline-matches-metrics check, day-task list).
3. Confirm GitHub issue labels (split across two label sets):
   - **`sprint-26` label** (Sprint 26 Day 1–13 in-scope work):
     - Priority 1: #1306, #1307, #1354, #1355
     - Priority 2: #1138, #1139, #1140, #1142, #1145, #1150 (closing this sprint per Task 4)
     - Priority 3: #1141, #1144, #1147 (closing or fixing per Task 5)
     - Priority 4: #885, #931, #932, #1185, #1228
     - Priority 5: #1334, #1335
   - **`sprint-27` label** (deferred work — must NOT carry `sprint-26`):
     - #1357 (otpop `comp_up` subset/superset, deferred per Task 7)
     - #1356 (fawley `comp_up`, deferred per Task 4)
     - #1374 (emit duplicate-init bugs, surfaced during Task 9 PR review)
     - #1224 (mine `ParamRef` IndexOffset, deferred per Task 6)
4. Read all Task 3–10 prep-task outputs as Sprint 26 briefing material (the "in-conversation context" for downstream day-prompts):
   - `PATTERN_C_HYPOTHESIS_VALIDATION.md` — drives Day 1
   - `PATTERN_A_RECLASSIFICATION_PLAN.md` — drives Day 6
   - `PATTERN_E_STATUS.md` — drives Day 6
   - `DESIGN_OPTION_1_SHORT_CIRCUIT.md` — drives Day 4 (pulled forward from Day 8 per Day 3 reschedule)
   - `AD_RESIDUALS_RECAP.md` — drives Day 4 + Days 9–10 (#1334 investigation pulled forward to Day 4 per Day 3 reschedule)
   - `DESIGN_PR19_SOLVE_TIME_CI.md` — drives Day 11
   - `BASELINE_METRICS.md` — Day 13 retest comparison basis

**Quality Checks:** None (no code changes).

**Commit + PR:** Day 0 is verification + log initialization (no code changes). Per CONTRIBUTING.md §"Development Workflow", create a branch (`sprint26-day0-kickoff`) and open a docs-only PR for the `SPRINT_LOG.md` Day 0 entry — direct pushes to `main` are blocked by branch protection on this repo. The PR should be small (single-commit `SPRINT_LOG.md` initialization) and merge fast; the "no PR" framing in earlier sprint plan docs is a stale convention from before branch protection was enabled.

---

## Day 1 Prompt: Priority 1 Phase A — Restore Launch Fix (Consolidated Zero-Offset Builder Rewrite)

**Branch:** `sprint26-day1-pattern-c-phase-a`.

**Objective:** Per Task 3 REPLAN finding, fix the consolidated zero-offset builder in `src/kkt/stationarity.py:4318–4346`. Currently disabled by Sprint 25 #1351 (`allow_nonzero_offsets = True` hardcoded at line 4339); Task 3's prototype patch confirmed flipping the gate without fixing the builder reproduces #1351's launch failure on 3 of 12 canary outputs.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md` §"Recommendation: REPLAN Sprint 26 Priority 1 as TWO-PHASE workstream".
- Read Sprint 25 SPRINT_LOG.md Day 11 §"Open follow-ups (revised)" — the proper fix shape: `sum(ss$ge(s,ss), -nu_dweight(ss))` instead of the over-counting `sum(ss, -1$ge(ss,s) * nu_dweight(s))` per-offset enumeration.
- Read PR #1306 (Sprint 25 launch fix) and PR #1351 (Sprint 25 rollback) diffs for the consolidator code path.
- Key source file: `src/kkt/stationarity.py`. Likely fix sites: the consolidated zero-offset builder around line 4318–4346 (Task 3 prototype patch site) + the `if eq_def_for_gate is not None:` no-op branch.

**Tasks to Complete (~6–8 hours):**

1. **Diff #1306 vs #1351** to identify the consolidator code path:
   ```bash
   git log --oneline --grep="#1306\|#1351" src/kkt/stationarity.py
   git diff <pre-#1351-sha>..<post-#1351-sha> src/kkt/stationarity.py
   ```
2. **Implement the rewrite** per the Sprint 25 SPRINT_LOG.md follow-up: consolidated builder must emit `sum(ss$(domain_filter), <body>)` iterating over the equation domain with the body's condition, NOT the per-offset enumeration `sum(ss, -1$ge(ss,s) * nu_dweight(s))`.
3. **Re-enable the Pattern C gate for the launch case.** Remove the hardcoded `allow_nonzero_offsets = True` at line 4339. Restore the original Sprint 25 #1306 gate logic.
4. **Tier 0 dispatch canary:** must remain byte-identical to `data/gamslib/mcp/dispatch_mcp.gms`.
5. **Tier 1 canary** (10 models): must match committed golden artifacts.
6. **Re-enable the xfail test:** `tests/unit/kkt/test_pattern_c_alias_offset_gate.py::test_alias_only_conditional_sum_emits_no_phantom_offsets` was `xfail (strict=True)` in Sprint 25 — should now PASS with the proper builder fix.
7. **Translate launch fresh** (`.venv/bin/python -m src.cli data/gamslib/raw/launch.gms -o /tmp/sprint26-day1/launch_mcp.gms --skip-convexity-check --quiet`); verify `stat_iweight` body contains the consolidated `sum(ss$ge(s,ss), -nu_dweight(ss))` form.

**PR14 obligation (per CONTRIBUTING.md §"Emit-Affecting PRs"):** Include the regenerated `data/gamslib/mcp/launch_mcp.gms` in the PR diff. Reviewers must read the `stat_iweight` block.

**Quality Checks:** `make typecheck && make lint && make format && make test`.

**Commit + PR:** One PR titled `Sprint 26 Day 1: Priority 1 Phase A — restore launch fix via consolidated zero-offset builder rewrite`.

---

## Day 2 Prompt: Priority 1 Phase A Validation + Phase B Scoping (camcge / cesam2)

**Branch:** `sprint26-day2-pattern-c-phase-a-validation`.

**Objective:** Validate Day 1's Phase A patch on the Tier 2 corpus; scope Phase B fixes for camcge + cesam2.

**Prerequisites:**
- Day 1 PR merged or cherry-picked onto this branch.
- Read `PATTERN_C_HYPOTHESIS_VALIDATION.md` §2 (per-model evidence for camcge + cesam2) — buggy emit shapes documented with specific phantom-offset patterns.

**Tasks to Complete (~5–7 hours):**

1. **Full 54-model Tier 0/1/2 golden-file regression** with Day 1's Phase A patch (combined set: 11 Tier 0/1 canaries — `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` Day 0 §"Tier 0/1 canaries generated (11 models)" — plus 43 Tier 2 canaries — Sprint 25 SPRINT_LOG.md Day 0 §"Tier 2 canaries generated (43 models)" — totaling 54). Document any regressions; expected 0.
2. **Translate launch + run full PATH solve.** Compare rel_diff against the baseline NLP solution. If rel_diff improves materially (Sprint 25 final was 0.17 — target < 0.01), note as +1 Match candidate for Day 13 pipeline retest.
3. **Phase B scoping (camcge):**
   - Translate camcge fresh (`.venv/bin/python -m src.cli data/gamslib/raw/camcge.gms -o /tmp/sprint26-day2/camcge_mcp.gms --skip-convexity-check --quiet`).
   - Read the emit; identify the 21 phantom-offset terms per `PATTERN_C_HYPOTHESIS_VALIDATION.md` §"camcge ✅ CONFIRMED Pattern C plain-alias variant".
   - Identify the gate-predicate change needed: per Task 3, camcge needs the launch-shape predicate (which checks for a specific `$cond` filter) broadened to detect plain-alias enumeration where there's no `$cond` at all.
4. **Phase B scoping (cesam2):**
   - Translate cesam2 fresh.
   - Read the emit; identify the 18 phantom-offset terms per `PATTERN_C_HYPOTHESIS_VALIDATION.md` §"cesam2 ✅ CONFIRMED Pattern C `sameas`-decomposed variant".
   - Identify the additional gate-predicate condition needed: per Task 3, cesam2 needs the gate to also recognize `sameas`-block guards as Pattern C triggers.
5. **Tier 0 + Tier 1 canary.**

**PR14 obligation:** No regenerated `_mcp.gms` artifacts needed (Day 2 is validation + scoping only — no `src/` changes).

**Quality Checks:** `make typecheck && make lint && make format && make test`.

**Commit + PR:** One PR titled `Sprint 26 Day 2: Priority 1 Phase A validation + Phase B scoping notes (camcge + cesam2)`. Include the scoping notes either as commit message detail or as a `SPRINT_LOG.md` Day 2 entry.

---

## Day 3 — RECLASSIFIED to Sprint 27 #1381 (Phase B redesign)

**Original objective:** Pattern C gate generalization for camcge (#1354).

**Reclassification reason (Day 3 design discovery):** Phase A's swap-based transform (Sprint 25 SPRINT_LOG.md Day 11 §"Open follow-ups (revised)") doesn't generalize to plain-alias bodies. Element-to-set substitution collapses the alias name to its canonical (same as the eq-domain index) BEFORE the swap can run, breaking the swap's assumption that alias and eq-domain are textually distinct. The Day 3 attempt to extend the gate via `expr.condition is not None` relaxation produced mathematically wrong emits on camcge + 11 other byte-shifted canaries (quocge, prolog, paklive, blend, chem, demo1, fdesign, ibm1, pollut, prodmix, trussm — all plain-alias variants).

**Deferred to Sprint 27 #1381:** Pattern C Phase B redesign (camcge + cesam2 + likely other plain-alias variants in path_syntax_error). Estimated 10–16h across Phase B-1 / B-2 / B-3 sub-scopes (see #1381 for breakdown). Requires intercepting BEFORE element-to-set substitution and building the consolidated term explicitly from the source Sum's body structure.

**Day 3 deliverable (this PR):** Docs-only — `SPRINT_LOG.md` Day 3 entry with the design discovery + rollback rationale; `PLAN.md` + `PLAN_PROMPTS.md` Day 3/4/5 updates; CHANGELOG entry. No `src/` changes.

---

## Day 4 — RECLASSIFIED Priority 4 to Sprint 27 #1385; Priority 5 #1334 re-investigation completed (2026-05-12)

**Branches:**
- Priority 4: `sprint26-day4-priority-4-option-1-short-circuit` (Day 4 docs-only PR after rollback — Priority 4 reclassification + Sprint 27 #1385 carryforward).
- Priority 5: `sprint26-day4-priority-5-1334-investigation-on-p4` (separate docs-only PR; #1334 re-opened).

**Reschedule note:** Day 4's original Pattern C cesam2 Phase B work reclassified to Sprint 27 #1381 (per Day 3 discovery). Day 8's Priority 4 + Priority 5 #1334 work pulled forward to fill Day 4. Day 8 is now buffer.

**Day 4 outcome (revised 2026-05-12):**

### Priority 4 — RECLASSIFIED to Sprint 27 #1385 (Option 1 short-circuit redesign)

Day 4 attempted to implement the Option 1 short-circuit per Task 6 design. **Translate-time savings worked** (srpchase 846s → 5.7s; iswnm 61.1s recovered) **BUT the resulting MCP emit was structurally wrong** — the `_build_symbolic_instance_placeholder` returned `[("srn",)]` (the SET NAME as the index) which the downstream AD/emit pipeline treated as the literal element string `"srn"`, producing broken multiplier references like `nu_slack("srn")` and `lam_demand("srn")` (invalid — `srn` is a subset of `n`, not an element). Same root-cause class as Day 3 Pattern C Phase B reclassification (Sprint 27 #1381): design doc validated against an assumption ("downstream emit handles symbolic-index instances per Sprint 25 #1306 / #1308 prior art") that doesn't hold — the prior art is for indexed-equation HEADERS that bind symbolic indices, but the AD pipeline's per-instance enumeration treats the placeholder as a concrete element.

**Day 4 src/ rolled back** (commit `243fe578` reverted on the Day 4 PR branch). **Sprint 27 #1385** captures the redesign scope (10–16h: AD/emit pipeline changes for symbolic-instance handling OR alternative short-circuit shape that works with concrete indices). The 5 translate-timeout candidate issues (#885, #931, #932, #1185, #1228) carry forward to Sprint 27.

**Sprint 26 Translate target relaxed:** `≥ 132/142` (was `+2 from Priority 4`) → `maintain ≥ 130/142` (per PLAN.md §"Sprint 26 Targets" revised Day 4).

### Priority 5 #1334 — COMPLETED Day 4 (separate docs-only PR)

Re-investigation per Task 7 §2.2 + §3.1 completed:

1. **Bug present on current main:** `grep -cE "sum\(t__," /tmp/otpop_mcp.gms` returns 2; spurious `sum(t__, ((-1) * (del(t__) * x(tt) * 0.365 * (1 - c))) * nu_kdef)$(t(tt))` wraps in `stat_p(tt)` + `stat_x(tt)`.
2. **#1334 closure traced to PR #1359** ("Sprint 25 Day 13: buffer + Sprint 26 carryforward issue filing" — docs-only). PR #1359's body explicitly listed #1334 under supposed-to-stay-OPEN "carryforward issues with rel_diff data attached"; the auto-closure was UNINTENDED.
3. **Re-opened #1334** with full re-investigation context.
4. **Approach 1 sketched** in SPRINT_LOG.md Day 4 §Priority 5 §"Approach 1 sketch" — Day 9 picks up `_replace_indices_in_expr` ParamRef-branch implementation alongside #1335.

### Day 4 deliverables (revised)

Two docs-only PRs:
- **Priority 4 reclassification PR** (this branch): src/ rollback + Sprint 27 #1385 carryforward + PLAN.md / PLAN_PROMPTS.md / SPRINT_LOG.md / CHANGELOG updates.
- **Priority 5 #1334 PR** (separate branch, stacked): re-investigation findings + Approach 1 sketch + #1334 re-opened on GitHub.

No src/ changes shipped Day 4. No PR14 obligation. Quality checks not required.

---

## Day 5 Prompt: Checkpoint 1 + Buffer

**Branch:** `sprint26-day5-checkpoint1`.

**Objective:** Evaluate Checkpoint 1 (Priority 1 landed); buffer for Phase A/B slippage.

**Prerequisites:**
- Days 1–4 PRs merged (or evaluating the partial set if any slipped).

**Tasks to Complete (~4–6 hours):**

1. **Targeted pipeline retest** (NOT full pipeline — see PLAN.md Day 5 rationale). The loop **regenerates each MCP from the current branch's `src/` code** (via `python -m src.cli`) BEFORE running gams — running gams on the committed `data/gamslib/mcp/<model>_mcp.gms` would only test pre-merge artifacts, missing any translation-side regression introduced by Days 1–4 PRs. All paths anchor on `$REPO_ROOT` so the recipe is cwd-agnostic. **Model list updated Day 3:** dropped camcge / cesam2 / fawley (Phase B deferred to Sprint 27 #1381); added launch (Phase A landed Day 1 — smoke-check) + srpchase (Priority 4 Day 4 target):
   ```bash
   REPO_ROOT="$(git rev-parse --show-toplevel)"
   for m in launch srpchase otpop dispatch quocge partssupply prolog sparta gussrisk ps2_f ps3_f ship splcge paklive; do
     rm -rf /tmp/sprint26-day5/$m
     mkdir -p /tmp/sprint26-day5/$m
     # 1. Regenerate the MCP on the current branch.
     .venv/bin/python -m src.cli "$REPO_ROOT/data/gamslib/raw/${m}.gms" \
       -o /tmp/sprint26-day5/$m/${m}_mcp.gms \
       --skip-convexity-check --quiet \
       2> /tmp/sprint26-day5/$m.translate.stderr
     translate_rc=$?
     if [ $translate_rc -ne 0 ]; then
       printf "%-13s translate=FAIL (rc=%d)\n" "$m" "$translate_rc"
       continue
     fi
     # 2. Run gams on the freshly-regenerated MCP. Set cwd=$REPO_ROOT so
     #    any presolve-variant `$include` lines resolve correctly (per
     #    Sprint 25 #1345/#1346/#1347; same pattern as scripts/gamslib/test_solve.py).
     (cd "$REPO_ROOT" && gams "/tmp/sprint26-day5/$m/${m}_mcp.gms" lo=0 reslim=30 \
       ScrDir=/tmp/sprint26-day5/$m \
       o=/tmp/sprint26-day5/$m/${m}_mcp.lst) &> /tmp/sprint26-day5/$m.gams.stdout
     gams_rc=$?  # capture GAMS exit code BEFORE the next command overwrites $?
     status=$(grep -hE "MODEL STATUS|SOLVER STATUS" /tmp/sprint26-day5/$m/${m}_mcp.lst 2>/dev/null | head -2 | tr '\n' '|')
     printf "%-13s translate=OK  gams_rc=%d  %s\n" "$m" "$gams_rc" "$status"
   done
   ```
2. **Evaluate Checkpoint 1 criteria** per `PLAN.md` §"Checkpoint 1 criteria (Day 5 evaluation)" (UPDATED Day 3 per Phase B reclassification to Sprint 27 #1381 + Priority 4/5 #1334 forward-pull to Day 4):
   - **Phase A landed**: gate restored + correct emit shape + xfail removed (test passes) — gating
   - **launch PATH solve to MODEL STATUS 1** — stretch (Phase A re-landed the correct KKT but PATH stalls; PATH-numerics investigation deferred to Sprint 27 issue #1378) — stretch, does NOT count toward routing
   - **camcge solves to MODEL STATUS 1** — n/a — deferred to Sprint 27 #1381 (Phase B builder redesign required) — does NOT count toward routing
   - **cesam2 solves to MODEL STATUS 1** — n/a — deferred to Sprint 27 #1381 (dim-mismatch case requires same redesign) — does NOT count toward routing
   - **Priority 4 Option 1 short-circuit: srpchase translates** (Day 4 PR landed) — gating
   - **Priority 4 stretch: ≥ 1 of {iswnm, sarf, mexls, nebrazil} also recovers** — stretch, does NOT count toward routing
   - **Priority 5 #1334 routing decision documented** (Day 4 #1334 re-investigation produced re-open OR successor filed) — gating
   - **Tier 0 + Tier 1 canaries (11 models) all match golden** — gating
   - **Tier 0/1/2 (54 models combined) golden-file regression: 0 (or ≤ 1 documented)** — gating

   **GO** (≥ 5 of 5 gating rows): continue Days 6+. **CONDITIONAL GO** (partial Priority 4 OR Priority 5 routing is "successor filed" not yet re-opened): proceed; Day 8 buffer absorbs follow-up. **NO-GO** (Phase A regression OR srpchase fails to translate OR canary regression > 1): Days 6+ buffer for revert + scope-back.
3. **Document Checkpoint 1 decision** in `SPRINT_LOG.md` Day 5 entry: GO / CONDITIONAL GO / NO-GO + per-criterion table + routing decision.
4. **Buffer** (if Checkpoint passes): absorb any Days 1–4 slippage. If Checkpoint fails: revert + scope-back per the NO-GO routing in `PLAN.md`.

**Quality Checks:** Re-verify `make test` is green on the merged set.

**Commit + PR:** PR (or revert) per checkpoint outcome + `SPRINT_LOG.md` Day 5 entry documenting decision.

---

## Day 6 Prompt: Priority 2 (Mechanical Closures) + Priority 3 kand Scoping (Parallel)

**Branch:** `sprint26-day6-priority-2-and-3`.

**Objective:** Mechanical close-and-refile per Task 4; scope kand fix work per Task 5.

**Prerequisites:**
- Day 5 Checkpoint 1 outcome documented.
- Read `PATTERN_A_RECLASSIFICATION_PLAN.md` §"TL;DR" table — per-issue actions.
- Read `PATTERN_E_STATUS.md` §"TL;DR" table — per-issue actions.

**Tasks to Complete (~4–6 hours):**

**Priority 2 — Pattern A cohort closures (~1.5h):**

1. **#1138** (irscge family): close-and-forward-link to Sprint 27 #1381 (Phase B redesign — camcge / cesam2 plain-alias generalization). Per Day 3 reclassification, the Phase B builder redesign that would close #1138 is deferred to Sprint 27 (Day 3 prototype produced wrong emits on irscge-family canaries — see Sprint 27 #1381 design discovery). Forward-link to #1381 in the close comment so the cohort-issue tracking stays accurate.
2. **#1139** (meanvar): close as `not-a-bug`. Note: meanvar is `legacy_excluded`.
3. **#1140** (PS-family): close as informational-mismatch. Note: all 7 ps*_s* models are `non_convex` runtime-filter per Prep Task 2.
4. **#1142** (launch): close as duplicate of Sprint 26 Priority 1 Phase A. Forward-link to Day 1 PR.
5. **#1145** (cclinpts): close-and-refile as new Sprint 27 issue per Task 4 §"Issue #1145" draft title + body.
6. **#1150** (qabel + abel): close as resolved (#1311 + #1312 already CLOSED in Sprint 25; abel reclassified `non_convex` per Prep Task 2).

**Priority 3 — Pattern E carryforward (~3–4h):**

1. **#1144** (catmix): close as bucket-shifted-resolved. Note: Sprint 25 #1338 SetMembershipTest fix recovered it; rel_diff 0.21% within tolerance.
2. **#1147** (camshape): close-and-refile as Sprint 27 issue per Task 5 §"Issue #1147" draft title + body.
3. **#1141** (kand): begin scoping the alias-AD fix:
   - Capture `SPRINT25_DAY2_DEBUG=1` trace per Sprint 25 Day 5 methodology.
   - Identify the gradient-mismatch source (per Task 5, kand still has 92.5% rel_diff that didn't bucket-shift in Sprint 25).
   - Document scoping in branch commit message; continue Day 7.

**Quality Checks:** `make test` (no `src/` changes today, but verify nothing accidentally broke).

**Commit + PR:** One commit per issue closure (8 GitHub-only operations) + 1 commit for branch metadata. PR titled `Sprint 26 Day 6: Priority 2 + Priority 3 mechanical closures + kand scoping`.

---

## Day 7 Prompt: Priority 3 kand Fix + Test xfail Cleanup

**Branch:** `sprint26-day7-priority-3-kand`.

**Objective:** Land kand alias-AD fix (or carryforward to Sprint 27); un-xfail the 1 affected test per Task 4 finding.

**Prerequisites:**
- Day 6 PR merged.
- Day 6 kand scoping notes.

**Tasks to Complete (~4–6 hours):**

1. **Implement kand alias-AD fix** per Day 6 scoping. Likely fix surface: AD partial in `src/ad/derivative_rules.py` or upstream in `src/ad/constraint_jacobian.py`.
2. **Un-xfail test:** `tests/unit/kkt/test_pattern_c_alias_offset_gate.py::test_alias_only_conditional_sum_emits_no_phantom_offsets` was xfail with reason referencing #1142 (per Task 4 §"Test xfail impact"). #1142 closed Day 6, so the xfail reason is stale; remove the xfail decorator.
3. **Update source-comment ref:** `src/kkt/stationarity.py:4336` (per Task 4 §"Source ref scan") references #1142; update or remove the reference now that #1142 is closed.
4. **If kand fix is intractable in 4–6h** (per Task 5 contingency): close-and-refile as Sprint 27 issue with the trace evidence + the design hypothesis from Day 6 scoping.
5. **Tier 0 + Tier 1 + Tier 2** golden-file regression.

**PR14 obligation:** If kand fix lands, include regenerated `data/gamslib/mcp/kand_mcp.gms` in PR diff.

**Quality Checks:** `make typecheck && make lint && make format && make test`.

**Commit + PR:** One PR titled `Sprint 26 Day 7: Priority 3 kand fix + xfail cleanup` (or `... kand carryforward to Sprint 27 + xfail cleanup` if the fix slips).

---

## Day 8 Prompt: Buffer (Priority 4 + Priority 5 #1334 investigation moved to Day 4)

**Branch:** as needed for buffer work (e.g. `sprint26-day8-buffer` if any commits ship from this day).

**Reschedule note:** Day 8's original Priority 4 Option 1 short-circuit + Priority 5 #1334 re-investigation pulled forward to Day 4 when Phase B reclassification freed Day 4 (per Day 3 discovery). Day 8 is now buffer.

**Objective:** Absorb any slippage from Days 4 / 6 / 7. If nothing slipped, choose one of the buffer-use options below.

**Buffer uses (in priority order):**

1. **Absorb slippage** — if Day 4 (Priority 4 + #1334 start), Day 6 (Priority 2/3), or Day 7 (kand + xfail cleanup) didn't fully land, catch up here.
2. **Forward-pull Priority 5 #1335 start** — originally Day 9. If Day 4's #1334 investigation already produced enough lead time that Day 9 can absorb #1334 fix completion + #1335 start without crowding, leave #1335 on Day 9. Otherwise, scope #1335 onto Day 8 to give Day 9 more time for #1334 fix completion.
3. **Forward-pull Day 12's PR14 emit-artifact review pass** — if Days 4 + 9 produced multiple regenerated `.gms` artifacts (srpchase, otpop, and possibly others), do the mid-sprint PR14 read-through here instead of deferring to Day 12.
4. **Sprint 27 #1381 (Pattern C Phase B redesign) — design notes only.** If other buffer uses are exhausted, sketch out Phase B-1 (source-body-driven builder) design notes in advance of Sprint 27. **Do NOT begin `src/` implementation in Sprint 26** — Phase B is explicitly deferred per Day 3.

**Quality Checks:** Re-verify `make test` green at end-of-day if any `src/` changes shipped from buffer work.

**Commit + PR:** Per buffer-use option chosen (zero or more PRs).

---

## Day 9 Prompt: Priority 5 #1334 Fix + #1335 Start

**Branch:** `sprint26-day9-priority-5-1334-and-1335`.

**Objective:** Land Priority 5 #1334 fix per Day 4 scoping. Begin #1335 fix.

**Prerequisites:**
- Day 4 PRs merged (Priority 4 Option 1 short-circuit + Priority 5 #1334 investigation).
- Day 4 #1334 routing decision documented (re-opened or successor filed).

**Tasks to Complete (~5–8 hours):**

**Priority 5 #1334 fix (~3–5h):**

1. Complete Approach 1 implementation per ISSUE_1334.md §Approach 1: ParamRef-branch alignment when `param_domain` is a strict subset of `equation_domain` AND a parallel VarRef has been substituted to use the eq domain variable.
2. Add unit test in `tests/unit/kkt/`:
   - Minimal `ModelIR` with scalar `kdef.. k = sum(t, p(t)*x(t))` over `t ⊂ tt`, with `x` and `p` declared on `tt`.
   - Assert `stat_x(tt)` body has no `sum(t__, ...)` and uses `p(tt)` directly.
3. Translate otpop fresh:
   ```bash
   .venv/bin/python -m src.cli data/gamslib/raw/otpop.gms -o /tmp/sprint26-day9/otpop_mcp.gms --skip-convexity-check --quiet
   grep -nE "sum\(t__, .* \* nu_kdef" /tmp/sprint26-day9/otpop_mcp.gms
   # Expected: 0 lines (was 2 pre-fix per Task 7 §2.2)
   ```

**Priority 5 #1335 fix (~2–3h):**

1. Implement scalar-equation gating fix per AD_RESIDUALS_RECAP.md §3.2: extend the offset-resolution / sum-expansion pipeline to scalar equations. The `if eq_domain:` gate at `src/ad/constraint_jacobian.py:986` + `:1107` currently skips `_resolve_index_offsets` + `_expand_sums_with_unresolved_offsets` for scalar equations like `zdef`.
2. Add unit test asserting `nu_zdef` cross-term emission in `stat_p` body for the otpop time-reversal-on-`p` shape.
3. Translate otpop fresh; verify per Task 7 §What-needs-to-be-done verification recipe:
   ```bash
   awk '/^stat_p\(.*\)\.\./, /=E= 0;/' /tmp/sprint26-day9/otpop_mcp.gms | grep -c nu_zdef
   # Expected: ≥ 1 (was 0 pre-fix per Task 7 §2.3)
   ```

**Tier 0 + Tier 1 + Tier 2** golden-file regression for both fixes (single full sweep for the combined PR).

**PR14 obligation:** Include regenerated `data/gamslib/mcp/otpop_mcp.gms` in PR diff. Reviewers must read the `stat_x(tt)` and `stat_p(tt)` blocks.

**Quality Checks:** `make typecheck && make lint && make format && make test`.

**Commit + PR:** One PR (combined #1334 + #1335 — same target model, same verification recipe) titled `Sprint 26 Day 9: Priority 5 — AD residuals #1334 + #1335 (otpop)`.

---

## Day 10 Prompt: Priority 5 Wrap (Full NLP-Warm-Started Reproducer) + Checkpoint 2

**Branch:** `sprint26-day10-checkpoint2`.

**Objective:** Run the full NLP-warm-started reproducer per ISSUE_1334.md §Diagnostic (deferred from Task 7 to Sprint 26 Priority 5 fix work — it's the acceptance gate). Evaluate Checkpoint 2.

**Prerequisites:**
- Days 1–9 PRs merged.

**Tasks to Complete (~4–6 hours):**

1. **Run the full otpop NLP-warm-started reproducer** per ISSUE_1334.md §Diagnostic:
   - NLP solve via baseline GAMS (e.g., `data/gamslib/raw/otpop.gms` via CONOPT).
   - Dual-multiplier transfer (per the per-issue scaffold).
   - MCP run with `iterlim=0` against the otpop_mcp.gms emitted by the Day 9 fix.
   - Capture `Inf-Norm` residual on `stat_x('1990')`. Pre-fix value: ≈ 760. Post-fix target: ≈ 0.
2. Confirm otpop's NLP-warm-started MCP converges to `pi ≈ 4217.80` (matches NLP per ISSUE_1334.md §Diagnostic).
3. **Targeted pipeline retest** on the 3 Priority-affected models in scope (srpchase, kand, otpop) + the 11 Tier 0/1 canaries. Use the same regenerate-from-current-branch loop pattern as Day 5 / §"Reference: Targeted Multi-Model Retest" (regenerate the MCP via `python -m src.cli` THEN run gams on the freshly-regenerated artifact, otherwise the retest only validates the pre-merge committed `_mcp.gms` files). **Model list updated Day 3:** dropped camcge / cesam2 (Phase B deferred to Sprint 27 #1381):
   ```bash
   REPO_ROOT="$(git rev-parse --show-toplevel)"
   for m in srpchase kand otpop dispatch quocge partssupply prolog sparta gussrisk ps2_f ps3_f ship splcge paklive; do
     # See §"Reference: Targeted Multi-Model Retest (Days 5 + 10)" at the bottom
     # of this file for the full per-iteration body — regenerates the MCP from
     # the current branch's src/, then runs gams with cwd=$REPO_ROOT and
     # captures gams_rc + MODEL STATUS.
     :
   done
   ```
4. **Evaluate Checkpoint 2 criteria** per PLAN.md §"Checkpoint 2 criteria (Day 10 evaluation)" (UPDATED Day 3 per Phase B reclassification):
   - Match Δ vs Day 0 ≥ +1 (was ≥ +3; relaxed because Phase B's +2 deferred to Sprint 27 #1381)
   - Solve Δ vs Day 0 ≥ +1 (same shape)
   - Priority 1 Phase A landed (already true — PR #1379; sanity check)
   - Priority 4 srpchase translates (Day 4 PR landed)
   - Priority 5 otpop NLP-warm-started MCP residual ≈ 0
   - Tier 0 + Tier 1 canaries all match golden

   **GO** (≥ 5 of 6 rows green). **CONDITIONAL GO** (3–4 of 6 green). **NO-GO** (≤ 2 of 6 green, OR any regression in Match / Solve / canaries).
5. **Document Checkpoint 2 decision** in `SPRINT_LOG.md` Day 10 entry.

**Quality Checks:** `make test` after Day 10 work merges.

**Commit + PR:** PR titled `Sprint 26 Day 10: Priority 5 wrap + Checkpoint 2` containing the otpop full-reproducer evidence + targeted retest results + `SPRINT_LOG.md` Day 10.

---

## Day 11 Prompt: PR19 CI Extension Implementation

**Branch:** `sprint26-day11-pr19-ci-extension`.

**Objective:** Implement PR19 per Task 8 design. The design doc specifies the workflow YAML, target list, helper scripts, and SHA256-pinned GAMS demo install.

**Prerequisites:**
- Read `DESIGN_PR19_SOLVE_TIME_CI.md` end-to-end. Implementation steps map to the design doc's sections.

**Tasks to Complete (~4–8 hours):**

1. **Land workflow YAML:** `.github/workflows/pr19-emit-solve-validation.yml` per DESIGN_PR19_SOLVE_TIME_CI.md §"Draft Workflow YAML".
2. **Land target-list file:** `.github/path-solve-ci-targets.txt` per DESIGN_PR19_SOLVE_TIME_CI.md §"Target Model List" (15 models = 11 Tier 0/1 hard-fail + 4 Pattern C soft-fail).
3. **Land helper scripts:**
   - `scripts/ci/parse_pr19_targets.py` (~30 LOC per Task 8 §"Helper scripts referenced").
   - `scripts/ci/run_pr19_solves.py` (~80 LOC per Task 8). Use `cwd=PROJECT_ROOT` + `ScrDir=<tmpdir>` per Sprint 25 #1345/#1346/#1347 pattern.
4. **Capture the GAMS installer SHA256** per Task 8 §"Open Questions" Q1:
   ```bash
   curl -fSL -o /tmp/gams-installer.exe "https://d37drm4t2jghv5.cloudfront.net/distributions/53.1.0/linux/linux_x64_64_sfx.exe"
   sha256sum /tmp/gams-installer.exe
   # Replace the `<TO BE FILLED IN BY SPRINT 26 IMPLEMENTATION>` placeholder in the workflow YAML.
   ```
5. **Smoke-test PR19 on this branch** per Task 8 §"Test Plan":
   - Open this PR (touches `.github/workflows/`, so the workflow self-fires).
   - Verify the bypass path: add `skip-emit-solve-ci` label, observe the workflow short-circuits with the bypass-comment notice.
   - Remove the label, observe the workflow runs the 11 Tier 0/1 canaries to MODEL STATUS 1.
6. **Promotion check:** Phase B (camcge / cesam2) deferred to Sprint 27 #1381 per Day 3 — leave `tier=pattern-c` on those rows in `.github/path-solve-ci-targets.txt` (soft-fail). Promotion to `tier=1` is a Sprint 27 task after the Phase B redesign lands.

**Quality Checks:** workflow YAML lint per existing `.github/workflows/lint.yml` patterns; verify `actionlint` passes locally if available.

**Commit + PR:** One PR titled `Sprint 26 Day 11: Implement PR19 pre-merge solve-time validation CI extension`.

---

## Day 12 Prompt: Buffer / PR14 Emit-Artifact Review Pass

**Branch:** `sprint26-day12-buffer`.

**Objective:** Mid-sprint "read the regenerated `.gms`" pass on the models with emit changes this sprint per CONTRIBUTING.md §"Emit-Affecting PRs" reviewer obligations. Buffer for any Days 1–11 slippage. **Updated Day 3:** dropped camcge / cesam2 / fawley (Pattern C Phase B deferred to Sprint 27 #1381) — those artifacts didn't change this sprint.

**Prerequisites:**
- Days 1–11 PRs merged.

**Tasks to Complete (~4–6 hours):**

1. **Read end-to-end:**
   - `data/gamslib/mcp/launch_mcp.gms` (post Day 1 Phase A fix — PR #1379)
   - `data/gamslib/mcp/srpchase_mcp.gms` (post Day 4 Priority 4 Option 1 short-circuit)
   - `data/gamslib/mcp/otpop_mcp.gms` (post Day 9 Priority 5 #1334 + #1335 fixes)
   - Plus any other artifacts that regenerated this sprint (e.g. iswnm / sarf / mexls / nebrazil if Day 4 Priority 4 stretch recoveries landed).
2. Per CONTRIBUTING.md §"What reviewers must do" — look for:
   - **Clobber patterns** (duplicate assignments where one silently overrides the other; see #1374).
   - **Ordering bugs** (clamps applied AFTER explicit overrides; see #1374 rocket case).
   - **Spurious Sum-wraps** (#1334 pattern; should be FIXED post Day 9).
   - **Missing cross-terms** (#1335 pattern; should be FIXED post Day 9).
3. **If new bugs surface:**
   - Trivially fixable in 1–2h: file as branch fix on this branch.
   - Larger: file as Sprint 27 carryforward issue (label `sprint-27`); document in `SPRINT_LOG.md`.
4. **Buffer:** absorb any Days 1–11 slippage. Examples:
   - PR19 implementation slipped to Day 12 → finish here.
   - Priority 5 otpop full reproducer didn't pass Day 10 → Day 12 deep-dive.
   - Priority 4 stretch recoveries (iswnm / sarf / mexls / nebrazil) need additional re-profiling → finalize.
5. **NO new architectural work** — this is buffer, not slip-prevention. Pattern C Phase B (camcge + cesam2) is explicitly deferred to Sprint 27 #1381 per Day 3; do NOT begin Phase B `src/` work here.

**Quality Checks:** If any `src/` changes land, `make typecheck && make lint && make format && make test`.

**Commit + PR:** PR (if any work landed) titled `Sprint 26 Day 12: Buffer + PR14 emit-artifact review pass`. Sprint 27 carryforward issues filed (if any).

---

## Day 13 Prompt: Final Pipeline Retest + Sprint Close

**Branch:** `sprint26-day13-final-retest`.

**Objective:** Full pipeline retest (per PR6); compare against Day 0 baseline (Task 9 BASELINE_METRICS.md) with explicit bucket-provenance evaluation (per PR17). File Sprint 26 retrospective scaffold.

**Prerequisites:**
- All Sprint 26 fix-work PRs merged (Days 1–12).
- Baseline reference: `docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md`.

**Tasks to Complete (~3–6 hours):**

1. **Run full pipeline retest:**
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet 2>&1 | tee /tmp/sprint26-day13-retest.log
   ```
   Expected runtime: ~3h based on Task 9 Day 0 baseline timing.
2. **Compare per-bucket counts vs Day 0 baseline:**
   - Headline metrics: Parse / Translate / Solve / Match.
   - Failure-bucket counts: path_syntax_error / path_solve_terminated / model_infeasible / path_solve_license / translate_timeout / translate_internal_error.
3. **Build per-model bucket-provenance table** per PR17 (Task 9 §4 format):
   - Sprint 25 Day 14 → Sprint 26 Day 0 → Sprint 26 Day 13 transitions.
   - Distinguish bucket churn (e.g., `clearlak path_syntax_error → translate_timeout → path_syntax_error`) from real recoveries (e.g., `camcge path_syntax_error → path_syntax_error → match`).
4. **Update `data/gamslib/gamslib_status.json`** (commit per Sprint 25 Day 14 convention).
5. **Compose Sprint 26 final-headline-metrics block** in `SPRINT_LOG.md` Day 13:
   - Headline metrics table (Day 0 / Day 13 / Δ / target / verdict per criterion).
   - Per-bucket transitions table.
   - Error-influx accounting per PR7 + PR10 calibration.
6. **Compose Sprint 26 retrospective scaffold** at `docs/planning/EPIC_4/SPRINT_26/SPRINT_RETROSPECTIVE.md`:
   - What went well (target hits, process recommendations applied successfully).
   - What didn't (Sprint 27 carryforward items, missed targets).
   - Process recommendations for Sprint 27 (PR-XX numbering continues from Sprint 25's PR19).
   - End-of-sprint Known Unknowns (KU-37+).
7. **Update `CHANGELOG.md`** — Sprint 26 Summary entry per Sprint 25 Summary precedent.
8. **Update `PROJECT_PLAN.md`** Sprint 26 footnote (per Sprint 25 footnote ⁶ precedent).
9. **File Sprint 27 carryforward issues** (label `sprint-27`):
   - Any unaddressed Priority 1–5 work from Days 1–10 Checkpoint outcomes.
   - **#1357** (otpop comp_up subset/superset, deferred per Task 7).
   - **#1356** (fawley comp_up subset/superset, deferred per Task 4).
   - **#1374** (emit duplicate-init bugs, surfaced during Task 9 PR review).
   - **#1224** (mine ParamRef IndexOffset, deferred per Task 6).

**Quality Checks:** `make test` (final green).

**Commit + PR:** One PR titled `Sprint 26 Day 13: Final pipeline retest + Sprint 26 close (retrospective + CHANGELOG + Sprint 27 carryforward)`. Includes:
- `data/gamslib/gamslib_status.json` update.
- `SPRINT_LOG.md` Day 13 entry.
- `SPRINT_RETROSPECTIVE.md` (new).
- `CHANGELOG.md` Sprint 26 Summary.
- `PROJECT_PLAN.md` Sprint 26 footnote.

---

## Reference: Pipeline Retest Command

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --quiet 2>&1 | tee /tmp/sprint26-retest.log
```

Expected runtime ~3h on the Sprint 26 reference machine (per Task 9 Day 0 timing).

## Reference: Targeted Multi-Model Retest (Days 5 + 10)

The loop **regenerates each MCP from the current branch's `src/` code** via `python -m src.cli` BEFORE running gams. Running gams on the committed `data/gamslib/mcp/<model>_mcp.gms` would only re-validate pre-merge artifacts, missing any translation-side regression introduced by the PRs being checkpointed. All paths anchor on `$REPO_ROOT` so the recipe is cwd-agnostic.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
mkdir -p /tmp/sprint26-retest
for m in <model_list>; do
  rm -rf /tmp/sprint26-retest/$m
  mkdir -p /tmp/sprint26-retest/$m
  # 1. Regenerate the MCP on the current branch (catches translate-side regressions).
  .venv/bin/python -m src.cli "$REPO_ROOT/data/gamslib/raw/${m}.gms" \
    -o /tmp/sprint26-retest/$m/${m}_mcp.gms \
    --skip-convexity-check --quiet \
    2> /tmp/sprint26-retest/$m.translate.stderr
  translate_rc=$?
  if [ $translate_rc -ne 0 ]; then
    printf "%-13s translate=FAIL (rc=%d)\n" "$m" "$translate_rc"
    continue
  fi
  # 2. Run gams on the freshly-regenerated MCP. cwd=$REPO_ROOT so any
  #    presolve-variant `$include` lines resolve correctly (per Sprint 25
  #    #1345/#1346/#1347; same pattern as scripts/gamslib/test_solve.py).
  (cd "$REPO_ROOT" && gams "/tmp/sprint26-retest/$m/${m}_mcp.gms" lo=0 reslim=30 \
    ScrDir=/tmp/sprint26-retest/$m \
    o=/tmp/sprint26-retest/$m/${m}_mcp.lst) &> /tmp/sprint26-retest/$m.gams.stdout
  gams_rc=$?  # capture GAMS exit code BEFORE the next command overwrites $?
  status=$(grep -hE "MODEL STATUS|SOLVER STATUS" /tmp/sprint26-retest/$m/${m}_mcp.lst 2>/dev/null | head -2 | tr '\n' '|')
  printf "%-13s translate=OK  gams_rc=%d  %s\n" "$m" "$gams_rc" "$status"
done
```

Where `<model_list>` is the per-day list (revised Day 3 per Phase B reclassification to Sprint 27 #1381):
- **Day 5:** 3 in-scope models (launch, srpchase, otpop) + 11 Tier 0/1 canaries = 14 models.
- **Day 10:** 3 Priority-affected models (srpchase, kand, otpop) + 11 Tier 0/1 canaries = 14 models.

(camcge / cesam2 / fawley dropped from both lists — Phase B builder redesign deferred to Sprint 27 #1381.)
