# Sprint 25 Day-by-Day Execution Prompts

Step-by-step execution prompts for Sprint 25 Days 0–14.

**Usage:** Copy the relevant day's prompt into a new conversation to execute that day's work. Each prompt is self-contained; the contributor does not need prior context beyond the prerequisites section.

**Branch naming convention:** `sprint25-dayN-<slug>` (one branch per day; rebase/merge to main at PR merge).

**Pipeline retest command:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` (~2h15m under doubled timeouts; use for Day 6 Checkpoint 1 + Day 10 Checkpoint 2 + Day 13 final retest).

---

## Day 0 Prompt: Setup & Kickoff

**Branch:** Create a new branch named `sprint25-day0-setup` from `main`.

**Objective:** Verify baseline, generate golden files for Tier 0/1/2 canaries, initialize sprint log.

**Prerequisites:**
- `data/gamslib/raw/` populated (gitignored; `python scripts/gamslib/download_models.py` if missing).
- Read `docs/planning/EPIC_4/SPRINT_25/PLAN.md` end-to-end.
- Read `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` — baseline numbers are LOCKED per PR15.

**Tasks to Complete (~2–3 hours):**

1. **Verify baseline matches `BASELINE_METRICS.md`:** Parse 143/143, Translate 135/143, Solve 99, Match 54. If any number drifts, STOP and investigate — baseline freeze was the whole point of Task 9.
2. **Generate Tier 0/1 canary golden files** (11 models): `mkdir -p /tmp/sprint25-golden && for m in dispatch quocge partssupply prolog sparta gussrisk ps2_f ps3_f ship splcge paklive; do python -m src.cli data/gamslib/raw/$m.gms -o /tmp/sprint25-golden/${m}_mcp.gms --skip-convexity-check; done`.
3. **Generate Tier 2 (44 non-alias matching) golden files** — extract the list from Task 9 baseline + filter out Tier 1 models + alias-using models per `AUDIT_ALIAS_AD_CARRYFORWARD.md` §regression canary tiers.
4. **Initialize `SPRINT_25/SPRINT_LOG.md`** with a Day 0 entry (mirror `SPRINT_24/SPRINT_LOG.md` format).

**Quality Checks:** Skip unless `.py` touched.

---

## Day 1 Prompt: WS3 Determinism Landing (Option D + PR12)

**Branch:** `sprint25-day1-determinism`.

**Objective:** Land the #1283 Option D grammar fix and the PR12 byte-stability test harness. These MUST land together so CI stays green going forward.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_25/INVESTIGATION_PARSER_NON_DETERMINISM.md` — Option D design at §Proposed Fix.
- Read `docs/planning/EPIC_4/SPRINT_25/DESIGN_DETERMINISM_TESTS.md` — §7 CI Integration Plan for the test harness.
- Key source files: `src/ir/parser.py::_resolve_ambiguities` (lines 166–225), `src/gams/gams_grammar.lark` (`table_row` / `simple_label` rules), `pyproject.toml` (marker registration).

**Tasks to Complete (~4–6 hours):**

1. **Option D fix:** Extend `_resolve_ambiguities()` with a greediest-value `table_row` heuristic — prefer the `_ambig` alternative that packs the most `table_value` children into the fewest `table_row` nodes. Unit test at `tests/unit/ir/test_resolve_ambiguities.py` covering a minimal `(low,medium,high).ynot` reproducer.
2. **Verify fix via 20-seed sweep on chenery:** `for s in $(seq 0 19); do PYTHONHASHSEED=$s python -m src.cli data/gamslib/raw/chenery.gms -o /tmp/chenery_s${s}.gms --skip-convexity-check; done; md5sum /tmp/chenery_s*.gms` — expect 20/20 identical.
3. **Register `determinism` pytest marker** in `pyproject.toml` under `[tool.pytest.ini_options] markers = [...]`.
4. **Create `tests/integration/test_pipeline_determinism.py`** with `TestDeterminismFast` (5 fixtures × 5 seeds, `@pytest.mark.integration @pytest.mark.determinism`) and `TestDeterminismFull` (`@pytest.mark.slow @pytest.mark.determinism`). Use the subprocess pattern from `DESIGN_DETERMINISM_TESTS.md` §7 (`-o <path>` + `Path.read_bytes()`).
5. **Create `.github/workflows/nightly.yml`** per `DESIGN_DETERMINISM_TESTS.md` §7 — mirrors ci.yml's dependency install sequence + adds `pip install -r requirements.txt`.
6. **Verify CI budget:** `pytest -m "integration and determinism" --tb=short` locally should complete in ~60s.

**Quality Checks:** `make typecheck && make lint && make format && make test`.

**Commit + PR:** One PR for this day. Title: `Sprint 25 Day 1: Land #1283 Option D grammar fix + PR12 determinism test harness`.

---

## Day 2 Prompt: WS1 Phase 1 Start + WS2 Batch 1 #1275

**Branch:** `sprint25-day2-alias-phase1-start`.

**Objective:** Begin Pattern A debugging for `_partial_collapse_sum` multi-index gap (qabel). Land #1275 presolve-path fix in parallel.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_25/DESIGN_ALIAS_AD_ROLLOUT.md` §Phase 1.
- Read `docs/planning/EPIC_4/SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md` §Pattern A.
- Key source files: `src/ad/derivative_rules.py::_partial_collapse_sum` (lines ~2173+), `src/ad/derivative_rules.py::_alias_match` (lines 258–312), `src/emit/emit_gams.py::_emit_nlp_presolve` (line 889 for #1275).

**Tasks to Complete (~4–5 hours):**

1. **WS1:** Add debug logging to `_diff_varref` and `_partial_collapse_sum` (tag with `SPRINT25_DAY2`).
2. **WS1:** Translate qabel: `python -m src.cli data/gamslib/raw/qabel.gms -o /tmp/qabel_mcp.gms --skip-convexity-check -vvv`. Trace the `sum(np, a(n,np)*x(np,k))` derivative w.r.t. `x(consumpt,q1)`.
3. **WS1:** Identify the multi-index concrete→symbolic gap. Document findings in a scratch file under `/tmp/sprint25-phase1-findings.md` for tomorrow's prototype.
4. **WS2:** Fix #1275 presolve absolute `$include` paths at the emit site in `src/emit/emit_gams.py:933` (the `Path(source_file).resolve().as_posix()` call per `CATALOG_EMITTER_BACKLOG.md` Batch 1). Per the issue writeup and `CATALOG_EMITTER_BACKLOG.md`, emit a repo-relative path when the source is inside the repo (e.g., `$include data/gamslib/raw/<model>.gms`), or use a configurable macro such as `%NLP2MCP_SRC%` with a default like `data/gamslib/raw` so the presolve wrapper is portable across workstations and CI. Unit test under `tmp_path`.
5. **Tier 0 dispatch canary:** `diff /tmp/sprint25-golden/dispatch_mcp.gms <(python -m src.cli data/gamslib/raw/dispatch.gms -o /dev/stdout --skip-convexity-check)` — MUST be empty.

**Quality Checks:** `make typecheck && make lint && make format && make test`.

---

## Day 3 Prompt: WS1 Phase 1 Prototype + WS2 Batch 1 #1280

**Branch:** `sprint25-day3-alias-prototype`.

**Objective:** Prototype `_partial_collapse_sum` multi-index extension; land #1280 unquoted-UEL-dots fix.

**Tasks to Complete (~4–5 hours):**

1. **WS1:** Implement multi-index concrete→symbolic recovery in `_partial_collapse_sum` (guard with `_find_var_indices_in_body` and `bound_indices`). Target: qabel `stat_x` now includes the correct cross-term `sum(n', a(n',n)*x(n',k))`.
2. **WS1:** Validate qabel: translate → diff stationarity against Day 2 baseline → GAMS compile via `gams qabel_mcp.gms action=c` → PATH solve.
3. **WS1:** Tier 0 dispatch canary + Tier 1 canary (quocge, partssupply, prolog) MUST still match.
4. **WS2:** Fix #1280 (mathopt4 unquoted UEL dots) — quote synthetic element labels containing `.` in emitter.
5. **Run golden-file regression** on all 54 matching models. Enumerate them from the frozen baseline status JSON, then diff each:

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

   No diffs expected.

**Quality Checks:** `make typecheck && make lint && make format && make test`.

---

## Day 4 Prompt: WS1 Phase 1 Complete + WS2 Batch 2.5 (#1289 high-leverage)

**Branch:** `sprint25-day4-phase1-complete-plus-ganges`.

**Objective:** Complete Phase 1 validation (qabel, abel, launch). Land the highest-leverage single fix of the sprint: #1289 ganges/gangesx calibration stripping (unblocks 2 of 5 Task 5 models).

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_25/ANALYSIS_RECOVERED_TRANSLATES.md` §#1289.

**Tasks to Complete (~5–7 hours):**

1. **WS1:** Validate Phase 1 fix on abel, launch. Measure `stat_x` / `stat_u` line count change vs Day 0 golden. Document any Pattern A model that now matches.
2. **WS1:** Run Tier 0 + Tier 1 canary. Run `make test`. Quality gate.
3. **WS1:** **Gate 1 (Day 3 deferred into Day 4):** dispatch identical + ≤1 Tier 1 regression + ≥1 of 3 targets improves ≥50% → GO to Phase 2 Day 5.
4. **WS2 #1289:** Fix ganges calibration-from-`.l` stripping in `src/emit/emit_gams.py`. Per `ANALYSIS_RECOVERED_TRANSLATES.md` §1.2, the emitter currently strips calibration assignments like `deltas(i)$ls.l(i) = (k(i)/ls.l(i))**(1/sigmas(i))*...` because they reference `.l` values. For ganges/gangesx the pattern is "declare + initial-solve + calibrate + final-solve": the calibration must run **after** an initial NLP solve (typically supplied via `--nlp-presolve` `$include`). Update the stripping logic to retain post-initial-solve calibration assignments when the presolve flow will supply their `.l` values; preserve any pre-solve calibration assignments too if present. Verify ganges + gangesx translate → PATH compile → PATH solve → Match.
5. **WS2:** Check whether the #1289 post-solve calibration-preservation change causes any regression on the 54 matching set (it should not — the fix is additive for calibration-stripped models).

**Quality Checks:** `make typecheck && make lint && make format && make test`.

---

## Day 5 Prompt: WS1 Phase 2 Start + WS2 Batch 2 Start

**Branch:** `sprint25-day5-phase2-start`.

**Objective:** Apply Pattern A fix across all 6 issues (#1138, #1139, #1140, #1142, #1145, #1150). Begin Batch 2 with #1279 robustlp scalar widening.

**Tasks to Complete (~4–5 hours):**

1. **WS1:** Validate Pattern A fix on model set: {quocge (already matching), irscge, lrgcge, moncge, stdcge, cesam, korcge, chenery, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps5_s_mn, ps10_s_mn, cclinpts}. Record per-model outcome:
   - mismatch → match
   - mismatch → mismatch (value improved)
   - mismatch → path_syntax_error (count as INFLUX — charged against 30% alias-AD budget)
   - no change
2. **WS2 #1279:** Fix robustlp `defobj(i)` scalar-equation widening in `src/ir/normalize.py`. The emitter currently emits `defobj(i)` as a domain-indexed equation when the AD treats it as scalar — fix the normalize pass to either consistently widen or consistently narrow.
3. **Tier 0 + Tier 1 canary + full 54-set golden-file regression.**

**Quality Checks:** `make typecheck && make lint && make format && make test`.

---

## Day 6 Prompt: Checkpoint 1 + WS2 Batch 2 Continue (#1276, #1281)

**Branch:** `sprint25-day6-checkpoint1`.

**Objective:** **Checkpoint 1** — evaluate Phase 2 GO/CONDITIONAL/NO-GO. Continue Batch 2 with #1276 and #1281 using shared `_DeclaredSymbolTracker` helper.

**Tasks to Complete (~5–7 hours):**

1. **Run full pipeline retest:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` (~2h15m). Record Translate / Solve / Match / error-category counts.
2. **Evaluate Checkpoint 1 criteria** (see `PLAN.md` §Checkpoint 1 table):

| Criterion | Day 6 value | GO threshold | Status |
|---|---|---|---|
| Tier 0 (dispatch) | | Identical | |
| Tier 1 regressions | | 0 (GO) / ≤1 (COND) / >1 (NO-GO) | |
| Pattern A ≥50% improved | | ≥3 of 6 (GO) / ≥1 (COND) / 0 (NO-GO) | |
| Cumulative Match Δ | | ≥+3 (GO) / ≥+1 (COND) / <0 (NO-GO) | |
| Tests | | All pass | |
| path_syntax_error | | ≤10 (GO) / ≤11 (COND) / >11 (NO-GO) | |

3. **Document decision** in `SPRINT_LOG.md` Day 6 entry. If NO-GO: revert Phase 2 PRs; plan Day 7 as root-cause investigation.
4. **WS2 Batch 2:** Implement shared `_DeclaredSymbolTracker` helper. Fix #1276 (fawley duplicate `.fx`) + #1281 (lmp2 duplicate Parameter).

**Quality Checks:** `make typecheck && make lint && make format && make test`.

---

## Day 7 Prompt: WS1 Phase 3 Start (Pattern C) + WS2 #1292

**Branch:** `sprint25-day7-pattern-c`.

**Objective:** Extend `_alias_match` for `IndexOffset.base` (Pattern C). Land short WS2 fix #1292 turkpow line-wrap.

**Prerequisites:**
- Read `DESIGN_ALIAS_AD_ROLLOUT.md` §Phase 3.
- Key source: `src/ad/derivative_rules.py:304–307` (`_alias_match`).

**Tasks to Complete (~4–5 hours):**

1. **WS1 Phase 3:** Extend `_alias_match` to handle `IndexOffset` vs plain-string cases via `_same_root_set(expr_idx.base, wrt_idx, aliases)`. Target models: polygon, himmel16 (#1143, #1146).
2. **WS1:** Validate polygon, himmel16 translate → compile → solve. Measure Solve/Match delta.
3. **WS2 #1292:** Fix turkpow `stat_zt` 144k-char single-line emission — add line-wrapping in the emitter for `sameas()` Cartesian-product expansions when line length exceeds ~1000 chars.
4. **Tier 0 + Tier 1 canary.**

**Quality Checks:** `make typecheck && make lint && make format && make test`.

---

## Day 8 Prompt: WS1 Phase 3 Continue + WS2 #1278 (twocge tautology)

**Branch:** `sprint25-day8-pattern-c-plus-1278`.

**Objective:** Re-validate #1277 (partially subsumed by Pattern C). Fix #1278 (twocge `ord(r) <> ord(r)` tautology).

**Tasks to Complete (~4–5 hours):**

1. **WS1:** Re-translate twocge after Pattern C landing. Verify #1277 `stat_tz` offset-alias correctness; if still broken, file a narrow follow-up issue.
2. **WS2 #1278:** Fix tautology substitution bug in `src/kkt/stationarity.py`. The stationarity emitter substitutes `ord(r) <> ord(r)` (always false) instead of `ord(r) <> ord(rp)` (the alias-correct form). Identify the substitution site; fix + unit test.
3. **Tier 0 + Tier 1 canary + 54-set golden-file regression.**

**Quality Checks:** `make typecheck && make lint && make format && make test`.

---

## Day 9 Prompt: Gate 3 + WS2 Batch 3 Completion (#1290, #1291)

**Branch:** `sprint25-day9-batch3-complete`.

**Objective:** Evaluate Gate 3; complete Batch 3 with #1290 (ferts identifier length) + #1291 (clearlak statement ordering).

**Tasks to Complete (~4–5 hours):**

1. **Gate 3 evaluation:** Pattern C target (polygon, himmel16) improves ≥50% OR Pattern A not regressed AND #1277 resolved → GO to Phase 4.
2. **WS2 #1290:** Fix ferts multiplier-name 67-char length violation. Add a synthetic-hash-shortening pass in the emitter.
3. **WS2 #1291:** Fix clearlak statement ordering — hoist `sum(leaf, ...)` AFTER `leaf(n) = yes$(...)` initialization, not before. Deterministic per 3-seed verification per Task 5.
4. **Run full 54-set golden-file regression.**

**Quality Checks:** `make typecheck && make lint && make format && make test`.

---

## Day 10 Prompt: Checkpoint 2 + WS1 Phase 4 Start

**Branch:** `sprint25-day10-checkpoint2`.

**Objective:** **Checkpoint 2** — evaluate Phase 4 scope. Begin Pattern E routing if GO (#1141, #1144, #1147).

**Tasks to Complete (~5–7 hours):**

1. **Full pipeline retest** (~2h15m).
2. **Evaluate Checkpoint 2 criteria** (see `PLAN.md` §Checkpoint 2 table):

| Criterion | Day 10 value | GO threshold | Status |
|---|---|---|---|
| Match | | ≥60 (GO) / ≥58 (COND) / <55 (NO-GO) | |
| Solve | | ≥102 (GO) / ≥100 (COND) / <99 (NO-GO) | |
| path_syntax_error | | ≤7 (GO) / ≤9 (COND) / >11 (NO-GO) | |
| model_infeasible | | ≤7 (GO) / ≤8 (COND) / >8 (NO-GO) | |
| Canaries (Tier 0+1) | | All match (GO) / ≤1 regression (COND) | |
| Tests | | All pass | |

3. **GO → Phase 4:** Route #1141 (kand: multi-solve driver? re-verify after Sprint 24 gate extension), #1144 (launch rechecked), #1147 (camshape — re-verify post-Pattern-A).
4. **CONDITIONAL → Phase 4 cleanup-only.**
5. **NO-GO → lock main; Day 11 reverts.**

**Quality Checks:** `make typecheck && make lint && make format && make test`.

---

## Day 11 Prompt: WS4 Small Priorities (#1270 + #1271)

**Branch:** `sprint25-day11-small-priorities`.

**Objective:** Land the #1270 multi-solve gate extension and the #1271 dispatcher refactor.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_25/DESIGN_SMALL_PRIORITIES.md`.
- Key sources: `src/validation/driver.py:151–225` (#1270), `src/emit/original_symbols.py::emit_pre_solve_param_assignments` (line ~3271, nested `_loop_tree_to_gams_subst_dispatch`).

**Tasks to Complete (~7.5–9.5 hours — may spill to Day 12 buffer):**

1. **#1270 (3.5–4.5h):** Implement Approach A cross-reference in `_collect_top_level_marginals_with_param_feedback`. Fixture matrix (per `DESIGN_SMALL_PRIORITIES.md` fixture table — only F1 should flag):
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

---

## Day 12 Prompt: Buffer / Overflow / Sprint-Close Prep

**Branch:** `sprint25-day12-buffer`.

**Objective:** Absorb slippage; optional Priority 5 contingency; file Sprint 26 issues.

**Tasks to Complete (~3–6 hours):**

1. **Buffer:** Close any Phase 4 / Batch 3 / Day 11 tail.
2. **Stretch (optional, only if slack):** Per Task 8 contingency, implement Option 1 short-circuit in `src/ad/index_mapping.py::enumerate_equation_instances` (with supporting behavior in `resolve_set_members` + static `SetMembershipTest` failure path in `src/ir/condition_eval.py`). Target: unblock srpchase (+1 Solve) and possibly iswnm (+1 Solve). Effort 4–6h; do NOT land unless schedule has ≥4h clear headroom.
3. **File Sprint 26 carryforward issues** (label `sprint-26`):
   - Translation timeouts: 4 of 5 hard timeouts (iswnm, sarf, mexls, nebrazil) unless Option 1 landed today.
   - `mine` `internal_error`.
   - Any Pattern E issue not resolved (#1141, #1144, #1147 if Phase 4 didn't land).
4. **Update `KNOWN_UNKNOWNS.md`** with end-of-sprint discoveries.

**Quality Checks:** Skip unless `.py` touched.

---

## Day 13 Prompt: Final Pipeline Retest

**Branch:** `sprint25-day13-retest`.

**Objective:** Definitive pipeline metrics per PR6.

**Tasks to Complete (~3–4 hours):**

1. **Full pipeline:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` (~2h15m).
2. **Record final metrics:** Parse / Translate / Solve / Match + 4 `outcome_category` counts.
3. **Cross-check against `PLAN.md` §Sprint 25 Targets.**
4. **Error-influx accounting (per PR7 + PR10 re-calibrated):**
   - Alias-AD gross fixes vs new errors. Check against 30% budget.
   - Emitter-recovered gross fixes vs new errors. Check against 80–100% budget.
5. **Commit updated `data/gamslib/gamslib_status.json`** (and note that `.gms` emitted artifacts remain advisory-only until PR12 fully stabilizes per BASELINE_METRICS.md §6).

**Quality Checks:** Skip unless `.py` touched.

---

## Day 14 Prompt: Sprint Close + Retrospective

**Branch:** `sprint25-day14-retro`.

**Objective:** Write retrospective, update CHANGELOG + PROJECT_PLAN, file Sprint 26 recommendations.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_24/SPRINT_RETROSPECTIVE.md` as template.

**Tasks to Complete (~3–4 hours):**

1. **Write `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md`** using Sprint 24 template:
   - Metrics delta against Sprint 25 Targets.
   - Acceptance criteria pass/fail (X of 8).
   - Went well / what could be improved.
   - PR10 re-calibration outcome (did the 30% / 80–100% split hold?).
   - New recommendations (PR16+) for Sprint 26.
2. **Update `CHANGELOG.md`** Sprint 25 Summary (mirror Sprint 24's format).
3. **Update `PROJECT_PLAN.md` Rolling KPIs.**
4. **File Sprint 26 recommendations** — translation timeouts, Pattern E remainders, any new discoveries.

**Quality Checks:** Skip unless `.py` touched.

---

## Reference: Tier 1 Canary Command

```bash
# Run before any WS1 PR merges — expect zero diffs from golden files
for m in dispatch quocge partssupply prolog sparta gussrisk ps2_f ps3_f ship splcge paklive; do
  diff /tmp/sprint25-golden/${m}_mcp.gms \
    <(python -m src.cli data/gamslib/raw/$m.gms -o /dev/stdout --skip-convexity-check 2>/dev/null) \
    && echo "✅ $m" || echo "❌ $m REGRESSED"
done
```
