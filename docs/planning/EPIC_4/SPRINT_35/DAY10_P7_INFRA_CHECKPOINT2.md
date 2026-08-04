# Sprint 35 — Day 10 (P7): infrastructure (fixtures + floor tracking) + Checkpoint 2

**Day:** 10 (Priority 7 — infrastructure) · **Date:** 2026-08-04 · **Owner:** Sprint 35 execution
**Branch:** `planning/sprint35-day10-p7-infra-checkpoint` · **Scope:** docs-only (no `src/` — see §1). **0 bucket, tally == Day-0 baseline.**
**Outcome: Checkpoint 2 GO — DB byte-unchanged since the anchor, the only golden drift is the expected turkey landing (testbed-only), PR25 genuine floor holds at 75. P7 fixture deliverable is satisfied by the sole `src/` landing's own tests (no net-new fixture warranted — see §1).**

---

## 1. P7 property fixtures — disposition (no net-new fixture warranted)

The P7 deliverable is "property fixtures, each **gated on its track's landing**, fail-before/pass-after." Walking every candidate against what actually landed in Sprint 35:

| Candidate fixture (prompt) | Track | Landed `src/`? | Fixture disposition |
|---|---|---|---|
| ganges-recovery raw-emit | P4 | **No — BANKED** (≥5-blocker cascade, Day 3) | **N/A** — the prompt gated it on "if P4 landed"; it didn't |
| shape12 head-offset | P1 mine | No — REPLAN'd, ships no `src/` | **N/A** |
| shape13 sarf | P2 sarf | No — REPLAN'd, ships no `src/` | **N/A** |
| fawley-2D second-index | P3 fawley | **No — DEFER** (Day 9: control verified, general src/ predicate leaks onto markov #1110) | **N/A** — lands *with* the deferred fix, not now |
| turkey `$161` recovery | P6 turkey (Day 6) | **Yes — the sprint's sole `src/` landing** | **Already covered — shipped with PR #1620** (see below) |

**The turkey landing already carries its fail-before/pass-after fixtures** — three unit tests added in PR #1620 (`tests/unit/emit/test_original_symbols.py`):
- `test_infer_domainless_tuple_arity` (L1005) — the helper: `grains.wheat, oil-crops.sunflower → 2`; ambiguous/numeric/1-D/pre-quoted stay `1`.
- `test_domainless_2d_set_quotes_per_part` (L1021) — **the fail-before/pass-after guard**: asserts per-part `'oil-crops'.sunflower` / `vegetables.'gr-pepper'` present and the whole-quoted `'oil-crops.sunflower'` (the `$161` bug) **absent**. On pre-fix code the emit whole-quotes → this fails; post-fix → passes.
- `test_domainless_inference_does_not_touch_1d_subset` (L1034) — the PR-review gate: a 1-D subset with `domain=(…)` must **not** split (verifies the fix is gated on `not set_def.domain`, not `domain_arity == 1`).

Confirmed green on the Day-10 tree (`5 passed in 1.34s`).

**Why no net-new (emit-from-raw) turkey fixture:** an integration test emitting turkey from `data/gamslib/raw/turkey.gms` would be a distinct layer, but (a) it is **impractical** — a fresh turkey emit is minutes-scale (measured: the CLI emit did not complete within a 2-minute cap; turkey's MCP is 3,866 rows, the same >1000-row / testbed constraint that blocks its local solve), so it would be a multi-minute `slow` subprocess test; and (b) it is **redundant** — the three unit tests already assert the exact `ao` per-part-quoting property at the function level (fast, deterministic), and the **golden-staleness gate** already regression-checks the committed `turkey_mcp.gms` end-to-end at checkpoint/CI time. Adding a slow subprocess duplicate is not proportionate. The disciplined P7 outcome is: **the gate is the landing; only turkey landed `src/`, and it is covered.**

## 2. Checkpoint 2 — `--resolve-changed --since-commit 78ceaead`

**At-risk set (golden diff since the anchor).** `git diff --name-only 78ceaead..HEAD -- data/gamslib/mcp/` = exactly **one** golden: `turkey_mcp.gms` (the Day-6 compile-recovery). The only emit-affecting `src/` change since the anchor is `src/emit/original_symbols.py` (the turkey `_infer_domainless_tuple_arity` fix, +52 lines); the other diffs (`scripts/diagnostics/kkt_residual.py`, `presolve_divergence_allowlist.txt`, `scripts/gamslib/test_solve.py`) are the GAMS-path / v54-transition changes and touch **no** emit golden.

**Re-solve result — GO, with a positive signal.** The tool re-solved the one changed-golden model and reported:

```
[resolve-changed] re-solving 1 changed-golden model(s) since 78ceaead: turkey
  turkey  {'outcome_category': 'path_syntax_error', 'comparison_status': 'not_tested'}
       -> {'outcome_category': 'path_solve_license', 'comparison_status': 'not_tested'}  ~ shift
GO: all 1 changed-golden model(s) held their bucket
```

**GO — bucket held** (both `path_syntax_error` and `path_solve_license` are non-bucket / non-match states, so no Solve or Match regression). The `~ shift` is a **positive** confirmation of the Day-6 landing: freshly emitted, turkey **no longer hits `path_syntax_error`** — it now compiles clean and **reaches the PATH solver**, where the *only* remaining blocker is `path_solve_license`, i.e. the **1000-row GAMS demo limit** (turkey's MCP is 3,866 rows). This is exactly the "+1 pending a v54 testbed re-solve" state: the compile-recovery is real and complete; the solve is gated solely by the local demo license, not by any emit defect. (The re-solve **never persists** the DB — the committed DB still records `path_syntax_error`, which is why §2's DB-integrity check shows byte-unchanged while the live re-emit reaches the license gate.)

**The at-risk model is testbed-only.** turkey is `translate=success` but `mcp_solve.outcome_category = path_syntax_error`, `solution_comparison = not_tested` in the committed DB — the Day-6 landing made turkey **compile-clean** (golden changed) but recorded **no** solve/bucket move, because turkey's 3,866-row MCP exceeds the **1000-row GAMS demo limit** (both v53 and v54). Its re-solve + match is a **testbed/CI step**, not locally runnable. The CI validation path (`pr19-emit-solve-validation.yml` + `presolve-divergence.yml`, bumped to GAMS 54.2.1 in PR #1620) is where turkey is exercised end-to-end. The "+1 pending v54 testbed" remains the sprint's only live upside (Day-13 retest).

**Golden-staleness.** Clean by construction for the Day-10 branch — it adds **no** `src/`, so every committed golden is byte-identical to what the current `src/` emits (unchanged from main). The one golden that drifted vs the anchor (turkey) was regenerated and golden-staleness-validated **with** its landing in PR #1620's CI; a local re-emit to re-confirm is the same >2-minute / testbed constraint as its solve.

**DB integrity.** `data/gamslib/gamslib_status.json` is **byte-unchanged since 78ceaead** (`git diff` empty) → **0 bucket move**, tally identical to the Day-0 baseline.

## 3. PR25 genuine-floor tally (recomputed against the anchor)

Recomputed over the **142 convex-candidate corpus** (`convexity.status ∈ {verified_convex, likely_convex}`, `get_candidate_models`):

| KPI | Value | Note |
|---|---|---|
| convex candidates | 142 | scope unchanged |
| **Solve** (model_optimal ∪ model_optimal_presolve) | **108** | = Day-0 baseline |
| **Match** | **93** | = Day-0 baseline |
| — cold-optimal + match (definitely genuine) | 63 | |
| — model_optimal_presolve + match (methodology-candidate) | 30 | of which 18 methodology / 12 genuine (S34 hand-partition) |
| **genuine floor** | **75** | unchanged — the DB is byte-identical to the anchor, so the S34 partition (`BASELINE_METRICS.md`) carries forward verbatim |

**Floor 75 — flat.** No genuine cold-emit match landed in Sprint 35 (P4 banked, P3 deferred, P1/P2 no `src/`; turkey is compile-only, not a match). The S32→S35 aspirational ramp (≥78) did **not** realize — actuals are flat at 75 since S33, exactly the Sprint-30/31 §3 conditionality lesson (the floor advances only via emit-changing cold-matches).

## 4. `--resolve-changed` checkpoint targets — refreshed

The at-risk target set is regenerated from git each checkpoint (`_changed_golden_model_ids(since_commit)` = `git diff --name-only <SHA>..HEAD -- data/gamslib/mcp/`), not a static list. For the Sprint-35 anchor `78ceaead` the current target set is **{turkey}** (was **∅** at Day-5 Checkpoint-1 — turkey's golden landed on Day 6). The Day-13 retest inherits this set plus the GAMS-version axis (v53 vs v54 baseline; [FOLLOWUPS_GAMS54_TRANSITION.md](FOLLOWUPS_GAMS54_TRANSITION.md)).

## 5. Epic-4 SUMMARY.md — row-35 groundwork

Filled `docs/planning/EPIC_4/SUMMARY.md` row 35 (was `(planned)`) with the through-Day-10 provisional result (**Solve 108 / Match 93 / floor 75 — FLAT, 0 bucket move; turkey +1 pending v54 testbed**), the firm landing (P6 turkey `$161` compile-recovery + the v53→v54.2.1 transition), and the REPLAN/carryforward column (P4 banked, P3 deferred, camcge→Epic 5, rocket+mine+fawley→S36 bundle, multi-root defers, v53→v54 baseline review). Marked _provisional, closes Day 13_. Extended the stale genuine-floor-ramp cross-epic bullet through S33–S35 (75/75/75; the aspirational ≥78 ramp did not realize).

## Outcome

**Checkpoint 2 = GO.** DB byte-unchanged (0 bucket), the sole golden drift (turkey) is the expected Day-6 landing and is testbed-only, genuine floor holds at 75, and the P7 fixture deliverable is satisfied by the turkey landing's own three fail-before/pass-after unit tests (no net-new fixture proportionate). Docs-only — no `src/`, no `*.py`, quality gate N/A.

**Next (Days 11–12):** slack / carryforwards. **Day 13:** retest (GAMS-version axis — decide v53 vs v54 baseline; turkey's +1 needs a v54 testbed re-solve; markov `slow`-test triage, [FOLLOWUPS_GAMS54_TRANSITION.md](FOLLOWUPS_GAMS54_TRANSITION.md) Follow-up 3).

---

**Document Status:** ✅ Complete — Sprint 35 Day 10 (P7 infra + Checkpoint 2 GO)
**Last Updated:** 2026-08-04
**Owner:** Sprint 35 Execution Team
