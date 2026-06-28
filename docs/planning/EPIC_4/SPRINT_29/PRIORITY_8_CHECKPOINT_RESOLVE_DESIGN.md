# Sprint 29 Priority 8 — Checkpoint Re-Solve + Post-Methodology Re-Baseline (Design)

**Task:** Sprint 29 Prep Task 8 (design-only — the tooling is built in-sprint as Priority 8). Zero `src/` here.
**Date:** 2026-06-27
**Implements the two Sprint-28 Day-13 lessons** (`docs/planning/EPIC_4/SPRINT_28/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently"):
- **#4 — re-solve the changed-golden set.** The Day-13 full retest was the *only* thing that caught the rocket stale baseline (#1462): a golden can stay byte-identical (passes the golden-staleness gate) while its *solve* is broken. → wire a "re-solve the changed-golden set" step into the Day-5/Day-10 checkpoints so a stale/broken match surfaces mid-sprint, not at the final retest.
- **#5 — re-baseline after any pipeline-methodology change.** The Day-9 presolve-retry broadening lifted Match 62→92 — far beyond the genuine gains — and the headline conflated genuine cross-term fixes with a methodology lift. → re-baseline immediately after any methodology change so the headline delta stays attributable.

---

## Part A — the `--resolve-changed` checkpoint re-solve

### A.1 The gap it closes

The golden-staleness gate (`check_golden_staleness.py`) re-emits each model and byte-diffs against the committed golden — it catches an **emit drift**, but **not a broken solve**: rocket's golden was byte-stable yet PATH aborted/MS-5'd. The presolve-divergence detector checks the *embedded NLP*, not the *MCP solve bucket*. So nothing between Day-0 and the Day-13 full retest re-runs the actual MCP solve + objective comparison on changed models. `--resolve-changed` fills exactly that gap.

### A.2 Interface

A new mode on the pipeline test driver (built in-sprint; `scripts/gamslib/run_full_test.py` already has the per-model `--model` path it reuses):

```bash
# Re-solve every model whose emitted golden changed since the Day-0 SHA, and
# diff each one's solve/compare bucket against the committed DB.
python scripts/gamslib/run_full_test.py --resolve-changed --since-commit <Day-0 SHA>

# Derive the at-risk model list (the `--resolve-changed` mode consumes exactly this):
# changed_emit_artifacts --format json emits {commits:[{files:[<path>...]}...]};
# map each changed `*_mcp[_presolve].gms` path to its model id.
python scripts/sprint_audit/changed_emit_artifacts.py --since-commit <Day-0 SHA> --format json \
  | jq -r '.commits[].files[]' \
  | sed -E 's|.*/||; s/_mcp_presolve\.gms$//; s/_mcp\.gms$//' | sort -u
# -> the new --resolve-changed mode (built in-sprint) re-solves each of these and
#    bucket-diffs vs the committed DB. (run_full_test's existing --model path is the
#    per-model executor it reuses; there is no `--compare-only` flag yet — the
#    bucket-diff-vs-committed-DB comparison is part of the new --resolve-changed mode.)
```

- **At-risk-list source (confirmed Task 6):** `changed_emit_artifacts.py --since-commit <Day-0 SHA> --format json` — it groups every changed `*_mcp.gms` / `*_mcp_presolve.gms` by triggering commit. That golden diff **is** the at-risk list (the exact set whose solve could have silently changed).
- **What it does per model:** re-run the GAMS PATH solve on the model + the embedded NLP comparison, classify the `outcome_category` + `comparison_status`, and **diff against the committed `gamslib_status.json`** for that model. A model whose bucket moved *backward* (e.g. `match → mismatch`, `model_optimal → model_infeasible`, `*_presolve match → abort`) is a **regression**.
- **Solve-only vs re-translate:** the primary path re-solves the **committed golden** (no re-translate) — that is precisely what catches the rocket class (byte-stable emit, broken solve) and is the cheapest. A `--retranslate` variant (re-emit then solve) is available when the PR changed `src/` emit logic and the golden itself is the thing under test; it costs the extra translate time (see A.3) but the changed-golden set is small.

### A.3 Wall-clock budget (Unknown 8.1 — measured)

From the committed DB's `mcp_solve.solve_time_seconds` over the 115 solved models (Sprint-28 Day-13 retest):

| Metric | Value |
|---|---|
| Median MCP solve | **0.71 s** |
| Mean MCP solve | 1.88 s |
| **Full re-solve, all 115 solved models** | **216 s (3.6 min)** |
| Slowest in-scope models | lmp2 14.2 s, prodsp2 6.5 s, apl1p 5.6 s, harker 4.3 s, bearing 4.1 s |
| MCP solves > 30 s | 2 (both out-of-scope `ps*`) — **0 in-scope model exceeds ~14 s** |

**A typical emit-change PR touches a handful of goldens** (Sprint-28 blast radii: usually 1–16 models — e.g. #1388 camshape = 16, #1335 = 1). So the re-solve cost is:
- typical changed set (≤ 16 models, median-ish): **~10–20 s**;
- a worst-case 16 *slowest* in-scope models: **~140 s (2.3 min)**;
- even re-solving the **entire** solved corpus: **3.6 min**.

**Verdict: the changed-golden re-solve is minutes, not hours — it fits the Day-5/Day-10 checkpoint budget with no backgrounding.** The "ganges ~8 min / clearlak slow" concern in the unknown is about **translate/parse** time (the full pipeline), **not** the MCP solve; `--resolve-changed` (solve-only on the committed golden) sidesteps it. Only the `--retranslate` variant pays translate cost, and only for the small changed set.

### A.4 GO / NO-GO criterion

- **GO (checkpoint passes):** every changed-golden model's re-solved bucket **matches** its committed-DB bucket (no backward move).
- **NO-GO (investigate):** **any** changed-golden model regressed — `match → mismatch/abort`, `model_optimal → model_infeasible`, a `*_presolve` match that no longer solves, or a new `path_*` error. A NO-GO is not an automatic sprint-stop; it is a **mid-sprint surface** (the thing Day-13 caught too late) — investigate the regressing model before the next priority lands. A *forward* move (e.g. `model_infeasible → match` from a landed fix) is expected and not a regression.

---

## Part B — the PR25 post-methodology re-baseline step

### B.1 What it codifies (Unknown 8.2 — verified by Task 2)

The current Match 92 decomposes (Task 2 / BASELINE_METRICS §2) as **genuine 68** (62 cold matches + 6 non-methodology presolve) **+ ~24 methodology** (the Day-9 `_cold_objective_mismatches_nlp` presolve-retry-on-cold-mismatch broadening; these models were always emit-correct — the broadened retry merely *validates* them). The re-baseline step makes this split a **standing discipline**, not a one-off Task-2 analysis.

### B.2 The trigger

Run the re-baseline **whenever a pipeline-methodology change lands** — i.e. any change to:
- a **retry trigger** (`run_full_test.py` `_cold_objective_mismatches_nlp` or the presolve-retry condition), or
- the **comparison logic** (objective-match tolerance, the `comparison_status` decision), or
- the **scope** (which models count toward the canonical 142).

These are the changes that can move the headline Match without a genuine cross-term fix — exactly the Day-9 class.

### B.3 The minimal PR25 template addition

Add to the PR25 projection-discipline template (`CONTRIBUTING.md` §"Projection Discipline") a labeled split + a trigger note:

| Match component | Count | Definition |
|---|---|---|
| **Genuine** (the re-baseline floor) | _N_ | cold matches + non-methodology presolve matches — repeatable cross-term-fix transitions |
| **Methodology** | _M_ | `model_optimal_presolve` + match whose cold MCP failed/mismatched **and** whose cold emit is byte-identical to its pre-change state (always-correct, now validated) |
| **As-measured total** | _N+M_ | the headline number |

> **Re-baseline trigger:** after any retry-trigger / comparison-logic / scope change, recompute (genuine, methodology) and record the **new genuine floor**. Report the headline Match delta as **genuine** (cross-term transitions) separately from **methodology** (validation of already-correct emits). The methodology lift is *not* a repeatable gain and must not be projected as one.

**Operational recompute:** genuine = (`comparison_status = match` AND `outcome_category = model_optimal`) ∪ (presolve matches whose cold emit is byte-identical to pre-change); methodology = the remaining `model_optimal_presolve` + match. Sprint 29's genuine floor = **68**, as-measured maintain target = **92**.

---

## Part C — cadence wiring

The Day-5 / Day-10 checkpoints (`docs/planning/EPIC_4/SPRINT_28/PLAN.md` §"Pipeline Retest Cadence" pattern, carried to Sprint 29) currently run: `changed_emit_artifacts.py --since-commit <Day-0 SHA>` + golden-staleness + the PR25 tally. **Add two steps:**

1. **`--resolve-changed`** (Part A) — immediately after the golden-staleness check, re-solve the changed-golden set and apply the GO/NO-GO criterion. The at-risk list is the same `changed_emit_artifacts.py` output the checkpoint already computes, so it adds only the solve time (minutes).
2. **Re-baseline check** (Part B) — in the PR25 tally, if any methodology-affecting change landed since the last checkpoint, recompute the genuine/methodology split and record the new floor; otherwise carry the prior split.

**Day-13 final retest** keeps the full 142-model pipeline run (the authoritative measurement) — `--resolve-changed` is the *mid-sprint* early-warning, not a replacement for the final retest.

## Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_29/PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md && echo present
grep -Ei 'resolve-changed|re-baseline|GO ?/ ?NO-GO|changed_emit_artifacts' docs/planning/EPIC_4/SPRINT_29/PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md | head
# Reproduce the re-solve budget (per-model MCP solve times from the committed DB):
.venv/bin/python - <<'PY'
import json, statistics
db=json.load(open("data/gamslib/gamslib_status.json"))
v=[ (m.get("mcp_solve") or {}).get("solve_time_seconds")
    for m in db["models"]
    if (m.get("mcp_solve") or {}).get("outcome_category") in ("model_optimal","model_optimal_presolve") ]
v=[t for t in v if isinstance(t,(int,float))]
print(f"{len(v)} solved | median {statistics.median(v):.2f}s | full re-solve {sum(v):.0f}s ({sum(v)/60:.1f}min)")
PY
```
