# Sprint 27 PR19 Target-List Widening Design

**Status:** ✅ COMPLETE (Day 0 design) — ⚠️ **CORRECTED 2026-06-01 (Day 0 CI evidence): `launch` is `tier=pattern-c`, NOT `tier=1`** (see banner below)
**Date:** 2026-05-28 (design) / 2026-06-01 (Day 0 launch-tier correction)

> ⚠️ **DAY 0 CORRECTION (2026-06-01).** This design's §3.2 premise that *"launch PATH-solves cleanly today (model_optimal)"* is **empirically false** — the PR19 CI on PR #1413 ran PATH on `launch` and got **MODEL STATUS 5 (Locally Infeasible)**. That is exactly the **Priority 4 #1378** numerics target. A Tier 0/1 hard-fail on `launch` would therefore red every emit PR's CI until #1378 lands (~Day 9). **Resolution:** `launch` is added as **`tier=pattern-c` (soft-fail)**, to be promoted to `tier=1` after #1378 fixes its numerics (per §6.4 tier-promotion). **Corrected counts: the final union is 30 unique models = 11 Tier 0/1 hard-fail + 19 Pattern C soft-fail.** Any "12 Tier 0/1 + 18 Pattern C" figures in the analysis sections below predate this correction and are superseded by 11 + 19.
**Owner:** Prep Task 5
**Inputs:** `.github/path-solve-ci-targets.txt` (current Sprint 26 PR #1396 target list); `.github/workflows/pr19-emit-solve-validation.yml` (current CI workflow + budgeted timeout); Sprint 26 PR #1396 CI run timings (from `gh run view 25862102598`); `PRIORITY_1_ANCHOR_MAPPING.md` (Task 4 — 8 anchor identification); `PROJECT_PLAN.md` §Sprint 27 Priority 1 + §"PR19 target-list widening" rationale.

---

## 1. Purpose

This document is the Sprint 27 Day 0 design for **widening the PR19 CI target list** to cover all 15 #1398-affected models + launch (the byte-stability anchor). PR19 is the structural mitigation against Sprint 26's #1398 gate-overreach incident (KU-37 per Sprint 26 retrospective):

- **Why widening matters:** Sprint 26 Day 1 PR #1379 ("Phase A consolidated zero-offset builder") shipped GREEN through PR19's existing 15-model target list because launch (the Phase A fix target) and the 14 affected non-target models (qdemo7 + 13 others) were NOT in the target set. The emit changes on launch AND the gate-overreach surface on the 15 affected non-target models (per PR #1399 review surface) were invisible until PR #1399 reviewer-driven retest discovered the regressions days later. **PR19 widening is the structural mitigation against this class of regression for the entire Sprint 27 emit-pipeline work** (Priorities 1, 2, 3 all touch emit-affecting code paths).
- **Budget constraint:** PR19's existing CI extension (per Sprint 26 PR #1396) runs PATH-solve on each target model, the most expensive pipeline stage. Per the workflow's budget comment (`pr19-emit-solve-validation.yml` L21-32), worst-case (regression scenario, all timeouts) is ~17 min; happy-path Tier 0/1 sum is ~4.6s. Per-model max is 60s (reslim=30 + 30s subprocess buffer). Per-job timeout set to 20 minutes. Under the assumption that widening adds 15 net new models, projected total runtime must stay well under the 5-min developer-friction threshold for Sprint 27 to land Option A (full widening).

This document records: (1) the current PR19 state inventory with per-model timing data from PR #1396 CI logs, (2) the runtime impact calculation for the 16-candidate widening cohort, (3) evaluation of 3 widening options (A full / B anchor-only / C tiered split) with explicit recommendation, (4) the concrete implementation steps (`.github/path-solve-ci-targets.txt` line-level edits), and (5) the validation plan (dummy PR to confirm CI behavior).

---

## 2. Current State Inventory (PR19 list per `.github/path-solve-ci-targets.txt`)

### 2.1 Tier 0/1 canaries (hard-fail surface) — 11 models, all PASS

Per Sprint 26 PR #1396 CI run timings (latest 2026-05-14T13:15:47Z run, sourced from `gh run view 25862102598`):

| Model | Tier | Sprint 26 PR #1396 timing | Notes |
|---|---|---|---|
| `dispatch` | 0 | 0.05s | MODEL STATUS 1 Optimal |
| `quocge` | 1 | 0.12–0.17s | MODEL STATUS 1 Optimal (slowest of Tier 0/1) |
| `partssupply` | 1 | 0.03–0.04s | MODEL STATUS 1 Optimal |
| `prolog` | 1 | 0.04s | MODEL STATUS 1 Optimal |
| `sparta` | 1 | 0.03s | MODEL STATUS 1 Optimal |
| `gussrisk` | 1 | 0.02–0.03s | MODEL STATUS 1 Optimal |
| `ps2_f` | 1 | 0.03s | MODEL STATUS 1 Optimal |
| `ps3_f` | 1 | 0.03–0.04s | MODEL STATUS 1 Optimal |
| `ship` | 1 | 0.03–0.04s | MODEL STATUS 1 Optimal |
| `splcge` | 1 | 0.03–0.04s | MODEL STATUS 1 Optimal |
| `paklive` | 1 | 0.03s | MODEL STATUS 1 Optimal |

**Tier 0/1 sum:** ~0.47–0.61s (median 0.04s per model) — matches workflow budget comment's "happy-path Tier 0/1 is 4.6s sum" claim (the budget figure is a worst-case ceiling; actual PR #1396 run was 10× faster).

### 2.2 Pattern C target models (soft-fail / informational) — 4 models, all currently FAIL

| Model | Tier | Sprint 26 PR #1396 timing | Notes |
|---|---|---|---|
| `camcge` | pattern-c | 0.02s | rc=2 (compile-fail) — expected pre-fix; awaits Sprint 27 #1381 |
| `cesam2` | pattern-c | 0.02s | rc=2 (compile-fail) — expected pre-fix; awaits Sprint 27 #1381 |
| `fawley` | pattern-c | 0.01s | rc=2 (compile-fail) — expected pre-fix; awaits Sprint 27 #1356 |
| `otpop` | pattern-c | 0.01s | rc=2 (compile-fail) — expected pre-fix; awaits Sprint 27 #1357 |

**Pattern C sum:** ~0.06s (rc=2 compile-fail exits fast at ~0.01–0.02s each — far below the 60s per-model timeout budget).

### 2.3 Whole-workflow timing

Per `gh run view 25862102598` step timings:

| Step | Duration |
|---|---|
| Set up job + check label | ~1s |
| Checkout | ~2s |
| Set up Python 3.12 | ~4s |
| Install GAMS demo | ~14s (download 648MB + verify SHA256 + extract) |
| Verify GAMS on PATH | ~0s |
| Read target list | ~0s |
| Run PATH solves (Tier 0/1) | ~1s (11 models in 1 second total — happy path) |
| Run PATH solves (Pattern C) | ~0s (4 models compile-fail in ~0s wall-clock combined) |
| Post PR comment | ~1s |
| Upload artifacts | ~1s |
| Post-job cleanup | ~0s |
| **Total** | **~24–27s** (run ID 25862102598: 13:15:47 → 13:16:14 = 27s) |

**Setup overhead** (everything except the two solve steps) ≈ **~22s**, dominated by GAMS install (~14s). **Per-model solve cost** ≈ **0.04s median** (happy path) or **~0.02s** (compile-fail).

---

## 3. 16-Candidate Widening Cohort

Per PROJECT_PLAN.md L1034 + PRIORITY_1_ANCHOR_MAPPING.md §2 (Sprint 27 Priority 1 #1398 cohort):

**16 candidates** = **15 #1398-affected models** (`qdemo7`, `egypt`, `ferts`, `shale`, `sambal`, `qsambal`, `harker`, `tfordy`, `dinam`, `ganges`, `gangesx`, `fawley`, `srpchase`, `sroute`, `turkpow`) **+ `launch`** (byte-stability anchor; not in the 15-affected list).

### 3.1 Overlap with current PR19 list

**1 overlap:** `fawley` is already in the Pattern C tier (per §2.2 — currently fails as "expected pre-fix" awaiting Sprint 27 #1356). The other 15 candidates are net new.

**Net additions:** 16 candidates − 1 (`fawley`) = **15 net new models**.

**Final widened union:** 15 (current) + 15 (net new) = **30 unique models**.

### 3.2 Per-candidate tier assignment (proposed)

Based on each model's Sprint 27 Day 0 bucket (from `PRIORITY_1_ANCHOR_MAPPING.md` §2):

| Candidate | Day 0 Bucket | Proposed Tier | Reasoning |
|---|---|---|---|
| `launch` | **model_infeasible (MODEL STATUS 5 Locally Infeasible — corrected Day 0 from the erroneous "solves model_optimal")** | **`tier=pattern-c` soft-fail** (corrected Day 0 from `tier=1`) | Sprint 26 PR #1379 fix target AND Priority 4 #1378 numerics target. PATH returns MODEL STATUS 5 today (PR #1413 CI), so it CANNOT be a hard-fail canary; promote to `tier=1` once #1378 fixes its numerics (§6.4). |
| `qdemo7` | path_syntax_error | `tier=pattern-c` soft-fail | Expected to fail compile-fast until Sprint 27 #1398 lands; promote to tier=1 once recovery confirmed |
| `egypt` | path_syntax_error | `tier=pattern-c` soft-fail | Same as qdemo7 |
| `ferts` | path_syntax_error | `tier=pattern-c` soft-fail | Same as qdemo7 |
| `shale` | path_syntax_error | `tier=pattern-c` soft-fail | Same as qdemo7 |
| `dinam` | path_syntax_error | `tier=pattern-c` soft-fail | Same as qdemo7; Phase 0 anchor for 2 distinct shapes |
| `gangesx` | path_syntax_error | `tier=pattern-c` soft-fail | Same as qdemo7 |
| `turkpow` | path_syntax_error | `tier=pattern-c` soft-fail | Same as qdemo7 |
| `ganges` | translate_timeout (machine-variance — was path_syntax_error at Sprint 26 Day 13 final) | `tier=pattern-c` soft-fail | PR19 runs PATH on the pre-generated `_mcp.gms` (not translate), so the translate_timeout flake doesn't block PR19 — same compile-fast behavior as qdemo7 expected |
| `srpchase` | translate_timeout (same caveat as ganges) | `tier=pattern-c` soft-fail | Same as ganges |
| `tfordy` | path_solve_license | `tier=pattern-c` soft-fail | PATH-compile succeeds; fails at solve with license error (fast — ~0.5s expected); promote to tier=1 once #1398 surface verified |
| `sroute` | path_solve_license | `tier=pattern-c` soft-fail | Same as tfordy |
| `sambal` | compare_mismatch (PATH-solves model_optimal) | `tier=pattern-c` soft-fail | PATH-solves cleanly today; conservative as pattern-c until Sprint 27 #1398 verification — could be tier=1 if Day 0 expects no emit drift |
| `qsambal` | compare_mismatch (PATH-solves model_optimal) | `tier=pattern-c` soft-fail | Same as sambal |
| `harker` | compare_mismatch (PATH-solves model_optimal) | `tier=pattern-c` soft-fail | Same as sambal |

**Tier counts (post-widening):**

- **Tier 0/1 hard-fail:** 11 (current) + 0 (`launch` → pattern-c per the Day 0 correction) = **11 models**
- **Pattern C soft-fail:** 4 (current including `fawley`) + 15 (net new incl. `launch`) = **19 models**
- **Total widened union:** 30 models

---

## 4. Runtime Impact Calculation

### 4.1 Per-model time projections for the 15 net new models

Based on each model's Sprint 27 Day 0 PATH behavior (extrapolated from `gamslib_status.json` + PR #1396 evidence on similar-shape models):

| Model | Expected PATH behavior | Time estimate | Rationale |
|---|---|---|---|
| `launch` | **MODEL STATUS 5 Locally Infeasible** (corrected Day 0 from "solves model_optimal" — per PR #1413 CI) | ~0.22s | Fails fast at solve; soft-fail (pattern-c) until #1378 fixes numerics |
| `qdemo7`, `egypt`, `ferts`, `shale`, `dinam`, `gangesx`, `turkpow`, `ganges`, `srpchase` (9 models) | Compile-fail rc=2 (path_syntax_error) | ~0.02s each | Matches camcge/cesam2/fawley/otpop's PR #1396 timing |
| `tfordy`, `sroute` (2 models) | License-fail (compile succeeds, solve license-rejects) | ~0.5–1s each | License rejection typically fast |
| `sambal`, `qsambal`, `harker` (3 models) | Solve model_optimal | ~0.5–2s each | Real solves; medium-size NLPs |

**Sum of 15 net new (estimated max happy-path):** 1.5s + 9×0.02s + 2×1.0s + 3×2.0s ≈ **9.7s** (worst case under estimation; median ~3–5s).

**Sum of 15 net new (worst case if any models hit 30s reslim):** Cap at 60s per timed-out model × possible 0–2 timeouts = 0–120s extra. Conservative upper bound assuming 0 timeouts in steady state: ~10s.

### 4.2 Total widened CI runtime projection

| Component | Current (15 models) | Option A widened (30 models) | Delta |
|---|---|---|---|
| Setup overhead (checkout + Python + GAMS install + verify + parse) | ~22s | ~22s | 0s |
| Tier 0/1 solves (11 → 12) | ~0.5s | ~2s (+launch) | +1.5s |
| Pattern C solves (4 → 18) | ~0.06s | ~10s (estimated) | +~10s |
| Comment + artifact upload | ~3s | ~3s | 0s |
| **Total wall-clock** | **~27s** | **~37s** | **+~10s** |

**Worst case (one Pattern C timeout):** ~37s + 60s = ~97s.
**Worst case (assume all 19 Pattern C models timeout):** ~22s + 2s + 19×60s + 3s ≈ 1167s = 19.5 min — within the 20-min job timeout but tight. **BUT** this scenario only occurs when every #1398-affected model hits PATH timeout simultaneously, which doesn't match observed behavior (path_syntax_error → fail-fast rc=2 in <0.05s; launch → MODEL STATUS 5 in ~0.2s).

### 4.3 Threshold check against budgets

- **5-min developer-friction threshold** (per Unknown 1.4 framing): Option A projected ~37s, well under 5 min ✅
- **20-min per-job hard ceiling** (workflow `timeout-minutes: 20`): Option A worst-case ~18.5 min if all Pattern C hit timeout (unlikely but theoretically possible) — within budget but tight ⚠️ (see §5.3 Option C as defensive option if Pattern C cohort grows beyond Sprint 27)
- **GitHub Actions per-job runtime limit** (6 hours default): not a constraint ✅
- **GAMS demo daily quota** (no documented limit but installer fetches 648MB per run): not affected by widening ✅

---

## 5. Three Widening Options + Recommendation

### 5.1 Option A — Full widening (RECOMMENDED)

**Description:** Add all 15 net new models to `.github/path-solve-ci-targets.txt`. Final widened union: 30 unique models (**11 Tier 0/1 + 19 Pattern C** per the Day 0 launch-tier correction).

**Pros:**
- Full coverage of KU-37 mitigation surface — all 15 #1398-affected models + launch byte-stability anchor are in PR19.
- Matches PROJECT_PLAN.md L1034 widening intent.
- Runtime projection (~37s steady state) is well under the 5-min friction threshold.
- No CI workflow YAML changes needed — only `.github/path-solve-ci-targets.txt` edits.
- No tier-promotion script required — pattern-c models become tier=1 incrementally as each Sprint 27 priority lands and recovers the model.

**Cons:**
- Worst-case all-timeout scenario (~18.5 min) is tight under the 20-min workflow ceiling. Mitigation: per-model reslim=30s + 30s buffer caps timeouts; failure mode is `time` field in PR comment, observable.
- Pattern C cohort grows from 4 to 18 models (4.5× expansion) — PR comment table doubles in length.

**Implementation effort:** ~10 min (file edit only). Implementation lands at Sprint 27 Day 0.

### 5.2 Option B — Anchor-only widening (NOT RECOMMENDED)

**Description:** Add only the 8 Phase 0 anchor models (per `PRIORITY_1_ANCHOR_MAPPING.md` §3-§4): launch + qdemo7 + ferts + sambal + ganges + sroute + turkpow + dinam. None currently in PR19 list, so 8 net new. Final widened union: 15 + 8 = 23 unique models.

**Pros:**
- Smallest runtime delta (~5s vs current ~27s baseline).
- Minimal Pattern C table growth (4 + 7 = 11 models — only the 7 in-cohort anchors as pattern-c; launch as tier=1).

**Cons:**
- **Defeats KU-37 mitigation rationale.** The 7 non-anchor #1398-affected models (egypt, shale, qsambal, harker, tfordy, gangesx, srpchase) remain UNCOVERED by PR19. If Sprint 27's #1398 fix introduces a non-anchor-only regression (e.g., shale's sameas-Cartesian sub-shape per Open Question 2; harker/tfordy/srpchase mappings per Open Question 3 — all flagged in `PRIORITY_1_ANCHOR_MAPPING.md` §6), PR19 doesn't catch it. Sprint 26's #1398 incident is exactly this failure mode at the launch level.
- Misses the structural-mitigation intent. PR19's purpose is to make the affected-models cohort observable at PR-review time, not just the anchors.

**Rejected** because the cost saving (~5s) is negligible relative to the loss of coverage on 7 non-anchor models.

### 5.3 Option C — Tiered widening (split into 2 parallel CI jobs) (RESERVE)

**Description:** Same final widened union as Option A (30 unique models), but split into 2 parallel CI jobs. E.g., Job 1: 11 Tier 0/1 hard-fail. Job 2: 19 Pattern C soft-fail (current 4 + 15 net new incl. `launch`, which is pattern-c per the Day 0 correction). Each job has its own GAMS install + setup overhead.

**Pros:**
- Same coverage as Option A.
- Parallelization shrinks wall-clock to max(Job1, Job2) instead of sum. Job 1 (Tier 0/1, ~22s setup + ~2s solves + ~3s overhead = ~27s) and Job 2 (Pattern C, ~22s setup + ~10s solves + ~3s overhead = ~35s) → wall-clock ~35s (matches Option A roughly).
- Defensive headroom if Pattern C cohort grows beyond Sprint 27 (e.g., Sprint 28 or 29 widening).

**Cons:**
- 2× GAMS install cost (22s × 2 = 44s combined CPU time, even though wall-clock is reduced) — wastes runner minutes.
- Workflow YAML changes required: matrix strategy or duplicate job definition, 2× artifact-upload paths, 2× PR-comment upsert with distinct markers. ~1–2h of implementation work.
- Worth the complexity only when Option A's worst-case timeout scenario actually materializes — which Sprint 26 PR #1396 evidence suggests is unlikely with current cohort size.

**Reserve for Sprint 28+ if Pattern C cohort grows past ~25 models.** Not selected for Sprint 27 Day 0.

### 5.4 Recommendation

**Selected: Option A (full widening).**

**Rationale:**

1. **KU-37 mitigation fully satisfied:** All 15 #1398-affected models + launch byte-stability anchor in PR19.
2. **Runtime projection well within budget:** ~37s steady state vs 5-min friction threshold (8× headroom); worst-case ~18.5 min vs 20-min hard ceiling (tight but within bounds; mitigated by per-model reslim=30s caps).
3. **Minimal implementation effort:** `.github/path-solve-ci-targets.txt` line edits only. No CI workflow YAML changes. No tier-promotion script needed.
4. **Option B's cost saving (~5s) does not justify losing coverage on 7 non-anchor models** — these are exactly the surface Sprint 26's #1398 incident demonstrated PR19 must cover.
5. **Option C's complexity (workflow YAML rewrite + 2× artifact + 2× PR-comment) is unwarranted at current cohort size** — defer until Pattern C grows past ~25 models.

---

## 6. Implementation Steps (Sprint 27 Day 0)

### 6.1 Edit `.github/path-solve-ci-targets.txt`

Append the following block to the end of `.github/path-solve-ci-targets.txt` (after the existing Pattern C section):

```
# Sprint 27 PR19 widening (per PR19_WIDENING_DESIGN.md Task 5): cover all 15
# #1398-affected models + launch (byte-stability anchor for Sprint 26 PR #1379
# Phase A fix). launch joins Pattern C soft-fail (CORRECTED Day 0: it is MODEL
# STATUS 5 Locally Infeasible today — the Priority 4 #1378 target — so it cannot
# be a Tier 0/1 hard-fail; promote to tier=1 after #1378 lands). The 14 net-new
# #1398-affected models (fawley already in Pattern C above) join Pattern C
# soft-fail; once each model's Sprint 27 priority fix lands and the model
# returns to its Sprint 26 Day 0 baseline bucket, promote to tier=1.
launch           # tier=pattern-c
qdemo7           # tier=pattern-c
egypt            # tier=pattern-c
ferts            # tier=pattern-c
shale            # tier=pattern-c
sambal           # tier=pattern-c
qsambal          # tier=pattern-c
harker           # tier=pattern-c
tfordy           # tier=pattern-c
dinam            # tier=pattern-c
ganges           # tier=pattern-c
gangesx          # tier=pattern-c
srpchase         # tier=pattern-c
sroute           # tier=pattern-c
turkpow          # tier=pattern-c
```

**Net additions:** 15 lines. **NOT added:** `fawley` (already present in Pattern C — would duplicate).

**Final widened union:** 30 unique models (**11 Tier 0/1 hard-fail + 19 Pattern C soft-fail** — corrected Day 0: `launch` is pattern-c, not tier=1).

### 6.2 NO changes to CI workflow YAML

`.github/workflows/pr19-emit-solve-validation.yml` is unchanged. The workflow already:

- Reads the target list via `scripts/ci/parse_pr19_targets.py` (handles arbitrary list size).
- Runs Tier 0/1 hard-fail and Pattern C soft-fail in separate steps (handles arbitrary tier sizes).
- Posts PR comment with both tier tables (handles arbitrary row counts).
- Uploads results JSON + scratch `.lst` artifacts (handles arbitrary model count).

The existing `timeout-minutes: 20` per-job budget is preserved. Per the worst-case analysis in §4.2/§4.3, Option A widening stays within this budget.

### 6.3 NO changes to helper scripts

`scripts/ci/parse_pr19_targets.py` and `scripts/ci/run_pr19_solves.py` accept arbitrary target lists — no code changes needed.

### 6.4 Tier-promotion follow-up (post each Sprint 27 priority fix)

When each Sprint 27 priority fix lands and a Pattern C model returns to a passing state (per `gamslib_status.json` retest), promote the model from `tier=pattern-c` to `tier=1` in the target list. This is a separate per-priority follow-up PR (not part of this Task 5 design):

- Sprint 27 Priority 1 (#1398 lands) → promote qdemo7 + the other Phase A-affected models that recover (per PRIORITY_1_ANCHOR_MAPPING.md §2 cohort table) to tier=1.
- Sprint 27 Priority 5 (#1356 lands) → promote fawley to tier=1.
- Sprint 27 Priority 5 (#1357 lands) → promote otpop to tier=1.
- Sprint 27 Priority 2 (#1381 lands) → promote camcge + cesam2 to tier=1.
- **Sprint 27 Priority 4 (#1378 lands) → promote `launch` to tier=1** (added Day 0: `launch` starts as pattern-c because it is MODEL STATUS 5 Locally Infeasible today; once #1378 restores MODEL STATUS 1 it becomes a valid hard-fail canary).

---

## 7. Validation Plan

### 7.1 Pre-merge validation (Sprint 27 Day 0 implementation PR)

1. **Local dry-run of parse_pr19_targets.py against the widened target list:**

   ```bash
   python3 scripts/ci/parse_pr19_targets.py .github/path-solve-ci-targets.txt > /tmp/pr19-targets.json
   jq '.tier_0_1 | length' /tmp/pr19-targets.json
   # Expect: 11 (current 11; launch is pattern-c per the Day 0 correction)
   jq '.pattern_c | length' /tmp/pr19-targets.json
   # Expect: 19 (current 4 + 15 net new incl. launch)
   ```

2. **Open the Sprint 27 Day 0 implementation PR** with a no-op edit to a path under `.github/path-solve-ci-targets.txt` (which is in the workflow's `paths:` trigger list per `pr19-emit-solve-validation.yml` L15). This triggers PR19 CI on the actual widened target list with the actual current `data/gamslib/mcp/*.gms` artifacts.

3. **Verify the PR19 CI workflow:**
   - Workflow completes within budget (target: <60s, hard ceiling 20 min)
   - Tier 0/1 hard-fail surface: 11/11 PASS (`launch` is now Pattern C, not a hard-fail canary — it is MODEL STATUS 5 today)
   - Pattern C soft-fail surface: ~3/19 PASS (sambal/qsambal/harker should solve; `launch` + the other 15 expected pre-fix). The actual PASS count depends on which Sprint 27 priorities have already landed when validation runs.
   - PR comment renders correctly (table layout, no Markdown indentation regressions from the larger Pattern C table).
   - Artifacts upload successfully (`pr19-solve-results` artifact contains both JSON results files + scratch `.lst` files for each widened model).

### 7.2 Post-merge regression check

After the widening PR merges to main, ensure subsequent emit-affecting PRs (any file under the `paths:` filter at `pr19-emit-solve-validation.yml` L6-L15) re-trigger PR19 with the widened list. Verify on the first follow-up PR:

- New Tier 0/1 model `launch` continues to PASS (no Sprint 27 work has altered launch emit if Priority 1 hasn't merged yet).
- Pattern C `qdemo7` continues to FAIL with rc=2 (expected pre-#1398 state).
- No false-positive failures from runner-load variance on the 18-model Pattern C tier (each model is independent — variance is bounded by per-model reslim=30s).

### 7.3 Acceptance criteria for the Sprint 27 Day 0 implementation PR

- [ ] `.github/path-solve-ci-targets.txt` final union = 30 unique models (no duplicates, including `fawley` not duplicated).
- [ ] PR19 CI workflow runs end-to-end on the implementation PR within the 20-min budget.
- [ ] Tier 0/1 hard-fail (11 models) all PASS — workflow exits 0.
- [ ] Pattern C soft-fail count matches projection (≥3 PASS, ≤19 PASS, depending on which priorities have landed).
- [ ] PR comment renders correctly with the widened tables.

---

## 8. Open Questions / Deferred Items

### 8.1 Open Question: Tier promotion automation

Pattern C → Tier 0/1 promotion is currently a manual per-PR follow-up step. Sprint 27 PR23 (CI-workflow PR self-review checklist, per `PROJECT_PLAN.md` L1084) does NOT cover tier promotion — that's a separate workstream candidate for Sprint 28.

**Question:** Should Sprint 27 author a `scripts/ci/promote_pr19_tier.py` helper that detects PASS-state Pattern C models from CI logs and proposes target-list promotions in a follow-up PR?

**Deferred to Sprint 28** (low-priority; manual promotion is workable for the Sprint 27 cohort of ~4 fixes).

### 8.2 Open Question: PR19 trigger path expansion

Sprint 27 Priority 6 (#1224 mine `IndexOffset(ParamRef)`) touches `src/ad/index_mapping.py` — NOT in the current PR19 `paths:` filter (per `pr19-emit-solve-validation.yml` L6-L15). If Sprint 27 lands #1224 without expanding the trigger paths, PR19 won't fire on that PR.

**Question:** Should the Sprint 27 Day 0 widening PR also add `src/ad/index_mapping.py` to the trigger paths?

**Recommended action:** YES. Add `src/ad/index_mapping.py` to the trigger paths in the same Sprint 27 Day 0 PR that widens the target list. This is a 1-line YAML edit and avoids forgetting it before #1224 lands. (This is a small scope creep beyond Task 5's strict charter but is too cheap to defer.)

### 8.3 Open Question: launch byte-stability check

PR19's current Tier 0/1 hard-fail only asserts MODEL STATUS 1 + SOLVER STATUS 1 — it does NOT byte-compare the regenerated `launch_mcp.gms` against a golden artifact. The Sprint 27 #1398 Phase 0 acceptance gate requires byte-stability on launch (per `PRIORITY_1_ANCHOR_MAPPING.md` §3 + Unknown 4.2). PR19 won't catch a launch emit change unless PATH-solve also breaks.

**Question:** Should PR19 widening also add a `git diff --exit-code data/gamslib/mcp/launch_mcp.gms` byte-stability check?

**Deferred to PR23 codification** (CI-workflow PR self-review checklist) — byte-stability assertion is a separate workstream from runtime widening; #1378 launch-numerics work in Sprint 27 may shift launch emit anyway. Tracked as a Sprint 27 retrospective candidate.

---

## 9. Verification Summary

| Verification Target | Result |
|---|---|
| Current PR19 target list inventoried with per-model timing data | ✅ §2 (PR #1396 run 25862102598 cited; Tier 0/1 sum ~0.5s; Pattern C sum ~0.06s) |
| 16-candidate cohort overlap calculated | ✅ §3.1 (1 overlap on `fawley`; 15 net new) |
| Final widened union calculated | ✅ §3.1 (30 unique models = **11 Tier 0/1 + 19 Pattern C** per Day 0 launch-tier correction) |
| 3 options evaluated with explicit pros/cons | ✅ §5.1–§5.3 |
| Runtime impact calculated for the recommended option | ✅ §4.2 (Option A projected ~37s steady state, ~18.5min worst case) |
| Threshold check against 5-min developer-friction budget | ✅ §4.3 (~37s vs 5min — 8× headroom) |
| Threshold check against 20-min per-job hard ceiling | ⚠️ §4.3 (worst-case ~18.5min within budget but tight — mitigated by per-model reslim=30s) |
| Recommendation made with rationale | ✅ §5.4 (Option A) |
| Implementation steps documented (file edits, no YAML/script changes) | ✅ §6 |
| Validation plan documented (local dry-run + dummy PR + post-merge check) | ✅ §7 |

**Decision: Sprint 27 Day 0 implements Option A (full widening).** Implementation effort: ~10 min file edit. Risk: low (well within budget at current cohort size).

---

## 10. Related Documents

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 5 — this task's specification.
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Unknown 1.4 — research question this task verifies.
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md` (Task 4) — anchor identification + non-anchor mappings input to the tier-assignment logic in §3.2.
- `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md` §6.2 (Task 3) — per-model Sprint 27 Day 0 bucket data referenced in §3.2 tier-assignment table.
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §Sprint 27 §"Priority 1: Phase A Gate Predicate Tightening (#1398)" L1030–L1035 — widening intent source.
- `docs/planning/EPIC_4/SPRINT_26/DESIGN_PR19_SOLVE_TIME_CI.md` §"Target Model List" — Sprint 26 PR #1396 design source for current PR19 list semantics.
- `.github/path-solve-ci-targets.txt` — file edited by §6.1.
- `.github/workflows/pr19-emit-solve-validation.yml` — workflow that consumes the target list; unchanged by Task 5.
- Sprint 26 PR #1396 CI run `25862102598` — per-model timing source (`gh run view 25862102598`).
