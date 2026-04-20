# Design — Alias-AD Rollout Plan (Sprint 25 Priority 1)

**Created:** 2026-04-20
**Sprint:** 25 (Prep Task 6)
**Predecessors:** [`AUDIT_ALIAS_AD_CARRYFORWARD.md`](AUDIT_ALIAS_AD_CARRYFORWARD.md) (Task 2), [`../SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md`](../SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md), [`../SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md`](../SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md)
**Sprint 24 reference:** [`../SPRINT_24/PLAN.md`](../SPRINT_24/PLAN.md) §Day 5 Checkpoint 1 (template)

---

## Executive Summary

Sprint 25 Priority 1's 12-day alias-AD block is structured as **4 sequential phases** with explicit per-phase gates and **5 stop-the-sprint triggers**. The default rollout is **all-or-nothing per PR** (no feature flag) — Task 2's audit confirms a feature flag would double the test matrix for zero operational benefit. Rollback is **per-PR git revert**, codified per checkpoint.

**Phase summary:**

| Phase | Days | Target | Gate | Outcome on fail |
|---|---|---|---|---|
| 1 | 1–3 | Pattern A — single-index path validation (qabel, abel, launch) + `_partial_collapse_sum` multi-index recovery prototype | Tier 0 + Tier 1 canaries pass; ≥ 1 of {qabel, abel, launch} improves rel_diff by ≥ 50% | Stop, narrow scope, file investigation |
| 2 | 4–6 | Pattern A across all 6 issues (#1138 CGE, #1140 PS-family, #1145 cclinpts, #1150) | Checkpoint 1 (Day 6): ≤ 1 regression on 54 matching models; ≥ 3 of 6 Pattern A issues show rel_diff improvement; net Match delta ≥ +3 | Stop, revert Phase 2 PRs, return to Phase 1 |
| 3 | 7–9 | Pattern C — extend `_alias_match()` with `IndexOffset.base`; revalidate polygon, himmel16; verify #1277 | Pattern C target rel_diff drops by ≥ 50% on at least one of polygon/himmel16; no Phase-1/2 regressions reintroduced | Stop, isolate Pattern C, leave A in-place |
| 4 | 10–12 | Final regression sweep + Pattern E routing decisions (camshape post-fix re-eval; #1141, #1144 routed to other workstreams) + Checkpoint 2 | Match net ≥ +6 over baseline; path_syntax_error not regressed; full pipeline retest passes | Stop, scope down to landed work |

**Cumulative target:** Match 54 → ≥ 62 (+8) per Sprint 25 PROJECT_PLAN. Conservative-case (Phase 3 only): +5–6.

**Stop triggers (5 defined):**

1. ≥ 2 golden-file regressions on the 54 matching set that can't be root-caused within 1 working day.
2. dispatch canary fails (any non-trivial diff) at any point.
3. Checkpoint 1 (Day 6) returns NO-GO on regression count (> 1 regression).
4. New `path_syntax_error` or `model_infeasible` appears on any currently-matching model after a Phase 1–3 PR lands.
5. Tests `make test` regresses (any failure that wasn't pre-existing per Sprint 24 Day 14 baseline of 4,522 passed).

**Parallel-work allocation:** Priority 2 (emitter backlog) Batches 1–2 from `CATALOG_EMITTER_BACKLOG.md` run on Days 1–4 while alias-AD is in Phase 1–2 wait states. Batch 3 (post-Pattern-C work) runs on Days 7–9 alongside Phase 3.

**`sameas` guard regression-test matrix** (Unknown 1.5): 5 element types × 4 test scenarios = **20 unit tests** under `tests/unit/ad/test_sameas_guards.py`, executed in CI as part of `make test`.

**Rollout strategy** (Unknown 1.8): **all-or-nothing per PR**, with per-checkpoint git-revert rollback. No feature flag.

---

## Section 1 — Phase Definitions

### Phase 1: Days 1–3 — Pattern A single-index validation + multi-index prototype

**Goal:** Re-verify Sprint 24's single-index sum-collapse fix still works on qabel/abel/launch under Sprint 25's parser/emitter state, then prototype the multi-index `_partial_collapse_sum` extension (the primary stubbed Pattern A item from Task 2 §Section 1).

**Day-by-day:**

- **Day 1**
  - Re-run dispatch canary to baseline.
  - Generate golden-file snapshots for the 54 currently-matching models (script: `scripts/gamslib/generate_golden.py` — to be written if it doesn't exist; see §Section 3.2).
  - Re-verify qabel, abel, launch reproductions; confirm rel_diff baseline (8.2%, 29.8%, 17.3% respectively per Task 2 §Section 2).
  - Spawn Priority 2 Batch 1 (#1275 + #1280) on a separate branch.

- **Day 2**
  - Implement `_partial_collapse_sum` multi-index concrete→symbolic recovery (port the Day 3 single-index fix's `_find_var_indices_in_body` + bound-index guard logic to the multi-index path).
  - Land first targeted PR: just the `_partial_collapse_sum` extension. Run dispatch + Tier 1 canaries (10 alias users) immediately.

- **Day 3**
  - Validate qabel/abel/launch under the new fix.
  - Run Tier 2 golden-file diff across the 44 non-alias matching models (expect zero changes).
  - **Phase 1 gate evaluation** (see §Gate 1).

**Target models for measurable improvement:** `qabel`, `abel`, `launch` — single-alias models where the fix can produce a clean rel_diff signal.

### Phase 2: Days 4–6 — Pattern A across all 6 issues + Checkpoint 1

**Goal:** Extend Pattern A coverage to the CGE family, PS-family, cclinpts, and #1150. Land the bulk of the architectural change.

**Day-by-day:**

- **Day 4**
  - Validate Pattern A on CGE family (#1138 — irscge, lrgcge, moncge, stdcge); expect rel_diff drops from 1.0–2.2% baseline.
  - Validate Pattern A on PS-family (#1140 — ps2_f_s, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, ps10_s; rel_diff baseline 0.5–27.4%).
  - Spawn Priority 2 Batch 2 (#1279 + #1276 + #1281) on a separate branch.

- **Day 5**
  - Validate Pattern A on cclinpts (#1145; rel_diff baseline 100%) and #1150 (qabel/abel; rel_diff 8.2%/29.8%).
  - Extend `_apply_alias_offset_to_deriv` for multi-position offset handling (currently skipped at `src/kkt/stationarity.py:4389`).
  - Land second targeted PR with the multi-position offset extension.

- **Day 6** — **Checkpoint 1**
  - Full regression run: dispatch + Tier 1 + Tier 2 + Tier 3 (Pattern A targets).
  - **Checkpoint 1 evaluation** (see §Gate 2).
  - On GO: proceed to Phase 3.
  - On CONDITIONAL GO: address regression(s) on Day 6, re-evaluate end-of-day before proceeding.
  - On NO-GO: invoke stop-trigger #3.

**Target models for measurable improvement:** CGE (4 models), PS-family (7 authoritative + 2 multi-solve-skip ANALYSIS-only), cclinpts, #1150 reproducer.

**Match delta target by end of Phase 2:** ≥ +3 (out of the 16-model Pattern A pool).

### Phase 3: Days 7–9 — Pattern C offset-alias extension

**Goal:** Land the `IndexOffset.base` extraction in `_alias_match()` (Task 2 §Section 1 row 2 stubbed item), validate against polygon/himmel16/cclinpts, and verify #1277 (twocge `stat_tz` mixed offsets).

**Day-by-day:**

- **Day 7**
  - Implement `_alias_match()` extension at `src/ad/derivative_rules.py:304–307` — handle `IndexOffset` / plain-string mixed cases by extracting `expr_idx.base` and calling `_same_root_set`, then emitting an offset-aware guard.
  - Unit-test the new code path on a synthetic example before integration tests.
  - Spawn Priority 2 Batch 3 (#1277, #1278) on a separate branch (only if Phase 2 has concluded).

- **Day 8**
  - Validate Pattern C on polygon (#1143; rel_diff baseline 33.8%) and himmel16 (#1146; rel_diff baseline 43.0%).
  - Validate #1277 twocge `stat_tz` after Pattern C lands; if mixed-offset persists, extend `_apply_alias_offset_to_deriv` to cover VarRef operands per Task 4 catalog §Section 2.3.

- **Day 9**
  - Run regression sweep (Tier 1 + Tier 2) — verify Pattern C didn't reintroduce Phase 1/2 regressions.
  - Re-evaluate camshape (#1147) and the alias-related infeasibility set (cesam, korcge) — Task 2 Tier 5 informational targets.
  - **Phase 3 gate evaluation** (see §Gate 3).

**Target models for measurable improvement:** polygon, himmel16, cclinpts, twocge (`stat_tz`).

### Phase 4: Days 10–12 — Final sweep + Pattern E routing + Checkpoint 2

**Goal:** Final regression sweep, route Pattern E issues to other workstreams, and land any remaining Pattern A/C cleanup.

**Day-by-day:**

- **Day 10** — **Checkpoint 2**
  - Run full pipeline retest (`scripts/gamslib/run_full_test.py --quiet`).
  - **Checkpoint 2 evaluation** (see §Gate 4).
  - On GO: address only minor cleanup; freeze main branch for Day 12 prep.
  - On CONDITIONAL GO: prioritize the highest-leverage remaining issue.
  - On NO-GO: invoke stop-trigger #5; freeze and document residual scope for Sprint 26.

- **Day 11**
  - Pattern E routing decisions:
    - **#1141 kand** → close as "not an alias-AD bug; multi-solve comparison semantics" (Task 2 §Section 3 Pattern E subsection); route to Priority 3 / pipeline comparator.
    - **#1144 catmix** → IR-level domain inference bug; not in Sprint 25 alias-AD scope; close out of Priority 1.
    - **#1147 camshape** → re-evaluate post-fix; if still `model_infeasible`, route to PATH-convergence (Category B) bucket alongside agreste/chain/fawley/lnts/robustlp.
  - Address any residual Pattern A/C work that didn't make Phases 1–3.

- **Day 12** — Sprint Close Prep for alias-AD
  - File any newly-discovered alias-AD issues with `sprint-26` label.
  - Update `SPRINT_LOG.md` (sibling file in this directory) Priority 1 section with final Match delta and per-pattern outcome.
  - Run `make test` final pass.

**Match delta target by end of Phase 4:** ≥ +5 (Phase 2's +3 + Phase 3's +2 from polygon/himmel16). Stretch: ≥ +8 (full Sprint 25 PROJECT_PLAN target).

---

## Section 2 — Per-Phase Gate Definitions

Each gate uses Sprint 24's GO / CONDITIONAL GO / NO-GO scoring template (`SPRINT_24/PLAN.md` §Day 5 Checkpoint 1), adapted with Sprint 25's quantitative thresholds.

### Gate 1 — Phase 1 evaluation (Day 3)

| Criterion | GO | CONDITIONAL GO | NO-GO |
|---|---|---|---|
| dispatch canary | identical (or trivial newline diff) | trivial diff | non-trivial diff |
| Tier 1 alias-user canaries (9 + paklive) | 0 regressions | ≤ 1 regression | > 1 regression |
| Tier 2 golden files (44 non-alias matching) | identical | identical | any difference |
| qabel rel_diff | drops ≤ 4% (≥ 50% improvement) | drops ≤ 6% | unchanged or worse |
| Tests `make test` | all pass | all pass | any failure |

**On GO:** proceed to Phase 2.
**On CONDITIONAL GO:** address the regression on the same day; re-run gate at end of day; only proceed to Phase 2 if upgraded to GO.
**On NO-GO:** stop, revert the Phase 1 PR, file investigation issue with `sprint-25` label.

### Gate 2 — Checkpoint 1 / Phase 2 evaluation (Day 6)

| Criterion | GO | CONDITIONAL GO | NO-GO |
|---|---|---|---|
| Tier 1 + Tier 2 canaries | 0 regressions | ≤ 1 regression | ≥ 2 regressions |
| Pattern A target improvement | ≥ 3 of 6 issues show rel_diff drop ≥ 50% | ≥ 1 of 6 shows drop | 0 of 6 improved |
| Match net delta | ≥ +3 over Sprint 24 baseline (54) | ≥ +1 | unchanged or negative |
| New `path_syntax_error` / `model_infeasible` | 0 new on the 54-set | ≤ 1 new | ≥ 2 new |
| Tests `make test` | all pass | all pass | any failure |

**On GO:** proceed to Phase 3.
**On CONDITIONAL GO:** address regression(s) on Day 6; re-evaluate end-of-day; if not upgraded to GO, defer Phase 3 and continue investigation Day 7.
**On NO-GO:** invoke **stop-trigger #3**. Revert all Phase 2 PRs; main reverts to end-of-Phase-1 state; spend Day 7 on root-cause; resume only if root-cause fixable in Day 7–8.

### Gate 3 — Phase 3 evaluation (Day 9)

| Criterion | GO | CONDITIONAL GO | NO-GO |
|---|---|---|---|
| Phase 1/2 canaries (Tier 1 + Tier 2) | still 0 regressions | ≤ 1 regression | regression vs Phase 2 baseline |
| Pattern C target improvement | polygon OR himmel16 rel_diff drops ≥ 50% | one improves, other unchanged | both unchanged |
| #1277 twocge stat_tz | mixed offsets resolved | partial fix (some offset operands corrected) | unchanged |
| Tests `make test` | all pass | all pass | any failure |

**On GO:** proceed to Phase 4.
**On CONDITIONAL GO:** Pattern C may carry over to Day 10; reassess at Checkpoint 2.
**On NO-GO:** revert Phase 3 PR; Phase 4 runs with Phase 2's Pattern A landing only; Pattern C issues defer to Sprint 26.

### Gate 4 — Checkpoint 2 / Phase 4 evaluation (Day 10)

| Criterion | GO | CONDITIONAL GO | NO-GO |
|---|---|---|---|
| Match net delta | ≥ +6 over baseline | ≥ +3 | unchanged or negative |
| Solve net delta | ≥ +1 over baseline (99 → ≥ 100) | unchanged | regression |
| `path_syntax_error` count | ≤ 11 (Sprint 24 Day 13 Addendum baseline) | ≤ 13 | ≥ 14 |
| `model_infeasible` count | ≤ 8 (Sprint 24 Day 13 baseline) | ≤ 9 | ≥ 10 |
| Tests `make test` | all pass | all pass | any failure |

**On GO:** lock main; Day 11–12 is Sprint Close Prep only (no functional changes).
**On CONDITIONAL GO:** Day 11 is dedicated to addressing the lowest-pass criterion.
**On NO-GO:** invoke **stop-trigger #5**; freeze main; document residual scope for Sprint 26 carryforward.

---

## Section 3 — Regression-Guard Infrastructure

### Section 3.1 — Canary Ladder

Imported from [Task 2 audit §Section 5](AUDIT_ALIAS_AD_CARRYFORWARD.md):

- **Tier 0** (non-negotiable): `dispatch` — must produce identical stationarity to pre-fix baseline (trivial newline diff OK).
- **Tier 1** (run all 10 after Tier 0): `quocge`, `paklive`, `partssupply`, `prolog`, `sparta`, `gussrisk`, `ps2_f`, `ps3_f`, `ship`, `splcge` — 9 alias-using matching models + paklive (non-alias-using, included defensively per S24 Day 5).
- **Tier 2**: 44 non-alias matching models — golden-file diff (expect identical output).
- **Tier 3** (Pattern A targets): `qabel`, `abel`, `launch`, `irscge`, `cclinpts`.
- **Tier 4** (Pattern C targets, Phase 3 onward): `polygon`, `himmel16`.
- **Tier 5** (informational): `cesam`, `korcge`, `camshape` — alias-related infeasibility candidates.

### Section 3.2 — Golden-File Set

**Set definition:** the 54 currently-matching models per `data/gamslib/gamslib_status.json` snapshot at start of Sprint 25 Day 1.

**Generation script** (sketch, to be added at `scripts/gamslib/generate_golden.py` if not already present):

```python
import json, subprocess, os, hashlib
from pathlib import Path

SEED = "0"  # PYTHONHASHSEED=0 to pin parser determinism (workaround for #1283 until Task 3's fix lands)
OUT = Path("/tmp/sprint25-golden")
OUT.mkdir(exist_ok=True)

with open("data/gamslib/gamslib_status.json") as f:
    data = json.load(f)
matching = [
    m["model_id"] for m in data["models"]
    if (m.get("solution_comparison") or {}).get("comparison_status") == "match"
]

env = os.environ.copy()
env["PYTHONHASHSEED"] = SEED
failed: list[tuple[str, int]] = []
for mid in sorted(matching):
    result = subprocess.run(
        [".venv/bin/python", "-m", "src.cli",
         f"data/gamslib/raw/{mid}.gms",
         "-o", str(OUT / f"{mid}_mcp.gms"),
         "--quiet"],
        env=env,
    )
    if result.returncode != 0:
        failed.append((mid, result.returncode))

if failed:
    print(f"FAILED: {len(failed)} of {len(matching)} models did not translate:")
    for mid, rc in failed:
        print(f"  {mid}: rc={rc}")
    raise SystemExit(1)  # Fail fast — golden set is incomplete; do not mark as "usable"
print(f"Generated {len(matching)} golden files at {OUT}")
```

**Diff script** (post-PR): same script + post-PR regen + `shasum -a 256` comparison.

### Section 3.3 — Per-Model Verification

Each Pattern target gets a smoke-test under `tests/unit/ad/test_alias_pattern_<X>.py` that asserts:

- Differentiation produces the expected term shape (with mocked-IR inputs).
- `_alias_match()` returns the expected guard / `Const(1)` / `None`.

Sprint 25 PRs land with their unit tests; CI runs them on every push.

### Section 3.4 — `PYTHONHASHSEED` pinning

Until Task 3's #1283 fix lands (Sprint 25 Day 1–2 per Task 3's recommendation), all canary scripts and CI runs in this sprint use `PYTHONHASHSEED=0` to suppress parser non-determinism. Once #1283 is fixed, the pinning can be removed (Sprint 26).

---

## Section 4 — Stop-the-Sprint Triggers

Five explicit triggers. Each requires the sprint lead's acknowledgement; on trigger, the sprint freezes the alias-AD work for at least one day to investigate.

### Stop Trigger 1 — Golden-file regression budget exceeded

**Condition:** ≥ 2 of the 54 matching models produce a non-trivial diff against their pre-fix golden file, AND the regression cannot be root-caused within 1 working day.

**Action:** Revert the most-recent PR; resume Phase work from prior state. If the regression appeared in Phase 2, regression budget is consumed (only 1 regression tolerable per Task 2 §Section 4 budget).

### Stop Trigger 2 — dispatch canary fails

**Condition:** `dispatch` produces any non-trivial output diff at any point in any phase.

**Action:** Immediate revert of the offending PR; this is a non-negotiable canary.

### Stop Trigger 3 — Checkpoint 1 NO-GO

**Condition:** Day 6 Checkpoint 1 evaluation returns NO-GO on regression count (> 1 regression) or `make test` failure.

**Action:** Revert all Phase 2 PRs; main returns to end-of-Phase-1 state; Day 7 is dedicated to root-cause; resume Phase 2 only if fix lands by end of Day 8 (otherwise scope down to Phase 1 + Phase 4 sweep).

### Stop Trigger 4 — New `path_syntax_error` or `model_infeasible` on a matching model

**Condition:** Any model that was `model_optimal` + `match` at Sprint 25 Day 0 baseline transitions to `path_syntax_error` or `model_infeasible` after a Phase 1–3 PR lands.

**Action:** Revert the offending PR; investigate the specific model; resume only after fix.

### Stop Trigger 5 — `make test` regression

**Condition:** Any test that was passing at Sprint 24 Day 14 baseline (`4,522 passed, 10 skipped, 2 xfailed`) now fails after a Phase 1–4 PR lands. Pre-existing failures don't count (Sprint 24 had `test_markov_stationarity_has_correction_term` as an unrelated pre-existing failure noted in Day-12 entries).

**Action:** Revert the offending PR; fix the test; re-land. If the failing test reveals a new bug, file with `sprint-25` label and assess severity.

---

## Section 5 — Parallel-Work Allocation

Map Priority 2 (emitter backlog) batches from [`CATALOG_EMITTER_BACKLOG.md`](CATALOG_EMITTER_BACKLOG.md) §Section 3 to days where alias-AD is in Phase-transition wait states.

| Day | Alias-AD Phase | Priority 2 Batch | Notes |
|---|---|---|---|
| 1 | Phase 1 setup | Batch 1 (#1275 + #1280) — start | Zero coupling; can ship same day |
| 2 | Phase 1 implementation | Batch 1 land | Day-2 PR for #1275 + #1280 |
| 3 | Phase 1 gate | (idle Priority 2) | Phase 1 gate evaluation absorbs the day |
| 4 | Phase 2 implementation | Batch 2 (#1279 + #1276 + #1281) — start | Different files, no merge conflict |
| 5 | Phase 2 implementation | Batch 2 land | Day-5 PR for emitter dedup pair |
| 6 | Phase 2 gate (Checkpoint 1) | (idle Priority 2) | Checkpoint 1 absorbs the day |
| 7 | Phase 3 implementation | Batch 3 prep (#1277, #1278) — start; **Task 5 new issues #1289–#1292 prep** | Pattern C land enables #1277 validation |
| 8 | Phase 3 implementation | Batch 3 + #1289–#1292 land in parallel | Highest-leverage day for Solve target — #1289 unblocks 2 of 5 ganges-family models |
| 9 | Phase 3 gate | (Priority 2 verification only) | Phase 3 gate + Priority 2 retest |
| 10 | Phase 4 (Checkpoint 2) | (idle) | Checkpoint 2 absorbs the day |
| 11 | Phase 4 cleanup | (idle) | Pattern E routing + cleanup |
| 12 | Sprint Close Prep | (idle) | Issue filing + log update |

**Critical observation:** the highest-leverage parallel-work day is **Day 8** — Phase 3 (Pattern C) on the alias-AD side, AND Batch 3 + new issues #1289–#1292 from Task 5 on the emitter side. #1289 (ganges calibration stripping) alone is worth 2 of 5 Solve recoveries; if Day 8 lands cleanly, Sprint 25 is on track for both Match and Solve targets.

---

## Section 6 — `sameas()` Guard Regression-Test Matrix (Unknown 1.5)

A 5 × 4 = **20-test matrix** under `tests/unit/ad/test_sameas_guards.py` (new file in Sprint 25). Each cell asserts: (a) the emitted MCP compiles under GAMS, (b) the `sameas()` guard evaluates to the expected boolean at the listed concrete pair, (c) the guard text matches the expected exact string.

### Section 6.1 — Element types (rows)

| ID | Element form | Example values |
|---|---|---|
| **A** | Numeric | `/1*5/` (elements `1`, `2`, `3`, `4`, `5`) |
| **B** | String (alphanumeric) | `/'alpha', 'beta', 'gamma'/` |
| **C** | Hyphenated (must be quoted in GAMS) | `/'light-ind', 'food-agr', 'heavy-ind'/` |
| **D** | Plus-signed (must be quoted) | `/'food+agr', 'energy+water'/` |
| **E** | Dotted (potentially attribute-form, must be quoted) | `/'x1.l', 'x2.l', 'x3.l'/` |

### Section 6.2 — Test scenarios (columns)

| ID | Scenario | Assertion |
|---|---|---|
| **1** | Equal pair: `sameas(elem, elem)` | Evaluates to TRUE |
| **2** | Unequal pair: `sameas(elem_i, elem_j)` where `i ≠ j` | Evaluates to FALSE |
| **3** | Cross-alias pair: `sameas(np, n)` where `Alias(n, np)` and both bound to same set | Evaluates to TRUE on diagonal, FALSE off-diagonal |
| **4** | Combined with dollar condition: `body$(sameas(np, n) and other_cond)` | Both conditions evaluated correctly; no scope conflict |

### Section 6.3 — Compile-time benchmark

Additional benchmark test: emit a `sameas()`-guarded MCP for `twocge` (large CGE model with many sameas guards) and measure compile-step duration via `time gams data/gamslib/mcp/twocge_mcp.gms action=c` (invoked from the repo root). Acceptance: total compile time ≤ 60s on the standard development machine; flag for investigation if > 90s.

### Section 6.4 — Coverage matrix

| | Test 1 | Test 2 | Test 3 | Test 4 |
|---|---|---|---|---|
| **A Numeric** | ✓ | ✓ | ✓ | ✓ |
| **B String** | ✓ | ✓ | ✓ | ✓ |
| **C Hyphenated** | ✓ | ✓ | ✓ | ✓ |
| **D Plus-signed** | ✓ | ✓ | ✓ | ✓ |
| **E Dotted** | ✓ | ✓ | ✓ | ✓ |

20 unit tests. Land alongside the Phase 1 PR (Day 2).

### Section 6.5 — Emitter quoting policy

To pass scenarios C/D/E, the emitter must wrap element names in single quotes when they contain non-identifier characters. Verify in `src/emit/emit_gams.py` (and ISSUE_1280 — UEL quoting fix from Task 4 Batch 1 — which lands on Day 1–2 and is a prerequisite for these tests).

---

## Section 7 — Rollout Strategy + Rollback Procedure (Unknown 1.8)

### Section 7.1 — Decision: All-or-nothing per PR (no feature flag)

Per Task 2's audit verification of Unknown 1.8: a feature flag would double the test matrix and provide zero operational benefit (no "some users want the old behavior" case). The Sprint 23/24 base layer (`bound_indices`, `_alias_match`, `_same_root_set`, etc.) is already in production; Sprint 25's additions sit on top of that.

**Per-PR rollout gates:**

1. PR contains a single Pattern's worth of changes (one of: Pattern A `_partial_collapse_sum` extension, Pattern A multi-position offset extension, Pattern C `_alias_match` `IndexOffset.base`).
2. Local `make test` passes.
3. Tier 0 (dispatch) canary passes.
4. Tier 1 (10 alias users) canary passes.
5. Tier 2 (44 non-alias matching) golden-file diff is empty.
6. PR description includes the canary results.
7. Reviewer approves; CI green.

### Section 7.2 — Rollback procedure (per checkpoint)

**Phase 1 PR fails Phase 1 Gate (Day 3):**

```bash
git revert <phase-1-PR-merge-commit-sha>
git push origin main
# Investigation continues on a feature branch off main; no Sprint 25 work
# on Phase 2 until Phase 1 lands cleanly.
```

**Phase 2 PR(s) fail Checkpoint 1 (Day 6):**

```bash
# Identify all Phase 2 merge commits on main (filter to Day 4-Day 6 PR titles)
git log --oneline --merges main | grep "Phase 2"
# Revert each in reverse order
git revert <phase-2-pr-3-sha> <phase-2-pr-2-sha> <phase-2-pr-1-sha>
git push origin main
# Main is now at end-of-Phase-1 state; Day 7 is dedicated investigation.
```

**Phase 3 PR fails Phase 3 Gate (Day 9):**

```bash
git revert <phase-3-pr-merge-commit-sha>
git push origin main
# Phase 4 runs with Phase 2's Pattern A only; Pattern C issues defer to
# Sprint 26 (file with `sprint-26` label on Day 12).
```

**Checkpoint 2 NO-GO (Day 10):**

```bash
# Selective revert based on which Phase regressed; use canary diff to
# identify the offending PR. Do NOT cascade-revert all phases;
# preserve as much landed work as is canary-clean.
# Document residual scope for Sprint 26 in `SPRINT_LOG.md`
# Day 10 entry.
```

### Section 7.3 — What does NOT roll back

- Sprint 23/24 base layer (`bound_indices`, `_alias_match`, `_same_root_set`, `_collect_bound_indices`, `_apply_alias_offset_to_deriv`, `_var_inside_alias_sum`, `_replace_indices_in_expr` IndexOffset.base canonicalization). These are pre-Sprint 25 commits and remain intact through any Sprint 25 rollback.
- Priority 2 (emitter backlog) PRs — different code paths; rollback decisions are independent.
- Priority 3 (multi-solve gate extension), Priority 4 (dispatcher refactor), Priority 5 (translation timeout) — all unaffected by alias-AD rollback.

### Section 7.4 — Communication procedure

On any rollback:

1. Sprint lead posts the rollback commit SHA, reason, and residual scope to the Day-N entry in the sibling `SPRINT_LOG.md` file for Sprint 25.
2. File a `sprint-25-rollback` GitHub issue with the canary diff that triggered the rollback.
3. If rollback exceeds 1 PR's worth of work, also update `KNOWN_UNKNOWNS.md` (sibling file in this directory) with a new "Newly Discovered" KU entry per the §How to Use This Document protocol.

---

## Section 8 — Cross-Reference

| Source | Used For |
|---|---|
| [Task 2 §Section 1 "Stubbed / Not Landed"](AUDIT_ALIAS_AD_CARRYFORWARD.md) | Phase 1's `_partial_collapse_sum` target, Phase 2's `_apply_alias_offset_to_deriv` extension, Phase 3's `IndexOffset.base` extraction |
| [Task 2 §Section 2 Pattern table](AUDIT_ALIAS_AD_CARRYFORWARD.md) | Phase target-model lists |
| [Task 2 §Section 5 Canary ladder](AUDIT_ALIAS_AD_CARRYFORWARD.md) | §Section 3.1 of this doc |
| [Task 4 §Section 3 Batch order](CATALOG_EMITTER_BACKLOG.md) | §Section 5 parallel-work allocation |
| [Task 5 leverage matrix](ANALYSIS_RECOVERED_TRANSLATES.md) | Day 8 highest-leverage planning |
| [Sprint 24 Day 5 Checkpoint 1](../SPRINT_24/PLAN.md) | Gate template (GO / CONDITIONAL GO / NO-GO format) |
| Sprint 24 KU-03 (49 → 54 matching), KU-17 (infeasibility influx) | Risk inputs to gates and stop triggers |

---

## Appendix A — Phase Execution Checklist

For each phase, the on-call sprint contributor runs:

```bash
# Phase setup
git checkout -b sprint25-phase<N>-<workitem>
PYTHONHASHSEED=0 .venv/bin/python -m src.cli data/gamslib/raw/dispatch.gms -o /tmp/dispatch-pre.gms --quiet > /dev/null 2>&1

# ... implement the phase's code change ...

# Phase verification (pre-PR)
make typecheck && make lint && make format && make test

# Tier 0 canary
PYTHONHASHSEED=0 .venv/bin/python -m src.cli data/gamslib/raw/dispatch.gms -o /tmp/dispatch-post.gms --quiet > /dev/null 2>&1
diff /tmp/dispatch-pre.gms /tmp/dispatch-post.gms

# Tier 1 alias-user canary
for m in quocge paklive partssupply prolog sparta gussrisk ps2_f ps3_f ship splcge; do
  PYTHONHASHSEED=0 .venv/bin/python -m src.cli data/gamslib/raw/${m}.gms -o /tmp/post-${m}.gms --quiet > /dev/null 2>&1
  diff /tmp/sprint25-golden/${m}_mcp.gms /tmp/post-${m}.gms || echo "REGRESSION: ${m}"
done

# Tier 2 golden-file diff (44 non-alias matching) — script TBD per §Section 3.2

# Tier 3 target-model improvement
# (Per phase: list specific reproducers and expected rel_diff drop)
```

## Appendix B — Pre-Sprint Checklist

Before Sprint 25 Day 1 begins:

- [ ] Generate the 54-model golden-file set (`/tmp/sprint25-golden/`) — Task 6 deliverable
- [ ] Verify `dispatch` baseline with `PYTHONHASHSEED=0` and `PYTHONHASHSEED=42` — both should produce identical output (if not, file an additional Sprint 25 issue under #1283)
- [ ] Confirm Sprint 24 base layer code is intact: `grep -n "_alias_match\|_apply_alias_offset_to_deriv\|_var_inside_alias_sum" src/ad/derivative_rules.py src/kkt/stationarity.py` → all 3 helpers present
- [ ] Sprint 25 PROJECT_PLAN target reaffirmed: Match 54 → ≥ 62, Solve 99 → ≥ 105
- [ ] Sprint lead acknowledges the 5 stop-triggers and the per-PR gate criteria
