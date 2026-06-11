# Sprint 28 Day-0 Baseline Metrics + Bucket Provenance

**Task:** Sprint 28 Prep Task 2 (PR15 bucket provenance + PR17 scope freeze + PR25 projection discipline)
**Date:** 2026-06-10
**Baseline source:** The committed Sprint 27 final pipeline DB (`data/gamslib/gamslib_status.json`, last written by the Day-13 closeout commit `c6199d66`). Reused per the Task 2 "reuse the committed Sprint 27 final DB if `main` is unchanged since the Day-13 retest" guidance — **verified applicable**: `git diff 68be9cca..HEAD -- src/ scripts/` is empty (only Sprint 28 planning docs landed since the Sprint 27 close, PR #1428), so no pipeline-affecting change has occurred. **Sprint 28 Day 0 = Sprint 27 final**; no fresh ~4h retest was required.

---

## 1. Day-0 Headline Counts (142-model GAMSlib corpus)

Authoritative figures from the Sprint 27 Day-13 deterministic retest (`SPRINT_27/SPRINT_LOG.md` §"Final headline metrics" + §"Final pipeline retest under 3 `PYTHONHASHSEED` values" + `SPRINT_27/SPRINT_RETROSPECTIVE.md` header). Byte-identical across `PYTHONHASHSEED` 0/1/42.

| Metric | Sprint 28 Day 0 | Sprint 28 Target | Gap |
|---|---|---|---|
| Parse | **142** / 142 | ≥ 142 | met |
| Translate | **135** / 142 | ≥ 135 | met (maintain) |
| Solve (`model_optimal`) | **105** / 142 | ≥ 110 (stretch) | -5 to stretch |
| Match | **62** / 142 | ≥ 65 | -3 |
| Mismatch | **37** | — | (solved-but-diverging) |
| path_syntax_error | **8** | maintain ≤ 8 | met |
| path_solve_terminated | **5** | maintain ≤ 5 | met |
| model_infeasible | **8** | ≤ 5 | -3 |
| Tests | **4,779** | ≥ 4,800 | -21 |

Of the 105 solved models, 62 match their NLP reference, 37 mismatch, and 6 are uncompared (`compare_multi_solve_skip` — no single-solve NLP reference).

### Failure-bucket membership (frozen Day-0 reference)

From `SPRINT_27/SPRINT_LOG.md` §"Named non-success buckets (final)", cross-checked against the committed DB:

- **Translate failures (7)** — parse-success, translate-fail: `danwolfe`, `decomp`, `iswnm`, `mexls`, `nebrazil`, `saras`, `sarf`.
- **model_infeasible (8):** `agreste`, `camcge`, `camshape`, `cesam`, `fawley`, `lnts`, `mine`, `otpop`.
- **path_syntax_error (8):** `clearlak`, `dinam`, `ganges`, `gangesx`, `indus`, `sample`, `turkey`, `turkpow`.
- **path_solve_license (9):** `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`.
- **path_solve_terminated (5):** `dyncge`, `elec`, `maxmin`, `tricp`, `twocge`.

Translated 135 = solved 105 + (8 + 8 + 9 + 5 = 30) solve-stage failures. ✓

> **Scope note.** A naive recompute over every parse-success row in the raw DB returns 150 parse / 107 solve / 57 match — it includes 8 out-of-scope models (non-NLP/QCP corpus) and applies a looser scope than the canonical 142-model pipeline. The authoritative figures above are the committed Day-13 retest summary; the raw DB is used below only to confirm the six carryforward models' per-model buckets (which match the committed bucket lists exactly).

---

## 2. Bucket-Provenance Table — Six Sprint 28 Carryforward Targets

Per-model trajectory: Sprint 27 Day-0 → Sprint 27 final (= Sprint 28 Day-0), with the gating issue. Day-0 buckets from `SPRINT_27/BASELINE_METRICS.md`; final buckets confirmed live from the committed DB.

| Model | S27 Day-0 bucket | S28 Day-0 bucket (= S27 final) | Movement across Sprint 27 | Gating issue (Sprint 28) |
|---|---|---|---|---|
| **mine** | `translate_internal_error` | `model_infeasible` | translate-fail → infeasible (**S27 +1 Translate** via #1224 `IndexOffset(ParamRef)` render, Day 12) | **#1224** — Solve: `stat_x` must invert the parameter-valued offset (`sum(k, lam_pr(k,l,i-li(k),j-lj(k)))` - the `l-1` term) |
| **camshape** | `model_infeasible` | `model_infeasible` | unchanged (#1424 subset-corruption landed Day 11 but MCP stays MS5) | **#1388** — Case-(b) `stat_r` per-term divergence (`stationarity.py:1835`) |
| **otpop** | `path_syntax_error` | `model_infeasible` | **moved forward** (P5 #1356/#1357 comp_up subset/superset cleared `$171` → Locally Infeasible) | **#1393 + #1335** — scalar-eq Sum-collapse (`stationarity.py`) + `_try_eval_offset` `card(t)-ord(t)` |
| **cclinpts** | `model_optimal` / mismatch | `model_optimal` / mismatch | unchanged (solves; obj -9.975 vs NLP -3.0011, rel 0.70) | **#1387** — three coupled AD changes (offset-enum + re-symbolization anchor + non-convex warm-start) |
| **kand** | `model_optimal` / mismatch | `model_optimal` / mismatch | unchanged (solves; obj 195.0 vs NLP 2613.0, rel 0.93) | **#1390** — re-diagnose the true mismatch source (tree-predicate collapse proven inert) |
| **camcge** | `path_syntax_error` | `model_infeasible` | **moved forward** (#1381 Pattern C Phase B cleared the syntax error → Locally Infeasible / singular Jacobian) | **camcge** singular-Jacobian CGE degeneracy (`docs/issues/ISSUE_1330_camcge-model-infeasible-after-1245.md`) |

**Provenance reading:** two of the six (otpop, camcge) are already *forward bucket moves* banked in Sprint 27 — they advanced from `path_syntax_error` to `model_infeasible` without yet yielding a Solve. This is precisely the over-counting trap the Sprint 27 retro flagged (§"What We'd Do Differently #2"): a bucket-forward move is progress, not target credit. The PR25 table below tallies only genuine bucket-to-success transitions.

---

## 3. PR25 Projection Table — Genuine Gain vs Bucket-Forward

For each Sprint 28 priority, the projected delta and whether it is a **genuine gain** (failure → solve, or solve → match) or a **bucket-forward** move (within the failure set). Only genuine gains are tallied toward Solve ≥ 110 / Match ≥ 65. Firmness mirrors the `PROJECT_PLAN.md` Sprint 28 Acceptance Criteria (as reconciled in PR #1428).

| Priority | Target | Projected transition | Classification | Counts toward target |
|---|---|---|---|---|
| **P1 #1224** | mine | `model_infeasible` → solve | **Genuine** (Solve, firm) | **+1 Solve** |
| | mine | solve → match | Genuine, **conditional** on solving first | Match stretch (not tallied) |
| **P2 #1388** | camshape | `model_infeasible` → solve | **Genuine** (Solve, firm) | **+1 Solve** |
| | camshape | solve → match | Genuine, **conditional** on solving first | Match stretch (not tallied) |
| **P3 #1393+#1335** | otpop | `model_infeasible` → solve → match | **Genuine** (Solve firm + Match firm) | **+1 Solve, +1 Match** |
| **P4 #1387** | cclinpts | mismatch → match (already solves) | **Genuine** (Match, firm) | **+1 Match** |
| **P5 #1390** | kand | mismatch → match (already solves) | **Genuine** (Match, firm) | **+1 Match** |
| **P6 camcge** | camcge | `model_infeasible` → solve | **Conditional** (may be inherent CGE degeneracy) | +1 Solve *if* it lands; else **bucket-forward** (progress, not credit) |
| **P7** | #1374 / #1400 / #1385 | cleanup (no bucket transition) | Neither (hygiene / no metric move) | — |

### Tally (genuine gains only)

- **Solve:** mine +1, camshape +1, otpop +1 (firm) = **+3 → 108**; camcge +1 (conditional) = **109**. The **≥ 110 target is an explicit stretch** — reaching it needs a 5th recovery not present in the carryforward set (consistent with the `PROJECT_PLAN.md` Solve criterion). cclinpts and kand already solve and contribute **no** Solve credit.
- **Match:** otpop +1, cclinpts +1, kand +1 (firm) = **+3 → 65** (meets ≥ 65). mine and camshape Match gains are conditional on their Solve landing first → **stretch beyond 65**, not tallied.

**Bucket-forward / progress-not-credit:** camcge if it remains `model_infeasible` (the singular-Jacobian degeneracy may be inherent → an Epic 5 observation rather than a Sprint 28 fix); the #1374/#1400/#1385 cleanups (no bucket transition by construction).

This projection is deliberately conservative versus the Sprint 27 Day-0 "+6 firm Match" that over-counted fawley/otpop/camcge: here otpop's and camcge's already-banked `path_syntax_error → model_infeasible` moves are **not** re-counted, and the two conditional Match gains (mine/camshape) are held out of the headline tally.

---

## 4. Scope Freeze (PR17)

### In-target for Sprint 28

- **Solve/Match carryforwards:** mine (#1224), camshape (#1388), otpop (#1393+#1335), cclinpts (#1387), kand (#1390), camcge (Priority 6).
- **Lower-priority cleanups:** #1374 `.l` denominator/override dedup (robot), #1400 `message`-field captured-warning path leak, #1385 runtime-guard cross-terms.
- **Infrastructure (no model targets):** golden-staleness CI check (P8), KKT-residual harness (P9), divergence detector + AD cross-term property tests (P10).

### Sprint-29 REPLAN exits (the diagnosis-heavy three)

Each carries an explicit Sprint 29 deferral if its Day-0 trace / Task-6 hypothesis-validation fails to confirm an emit-bug fix surface:

- **#1387 cclinpts** — three coupled architectural changes; if the re-symbolization-anchor fix proves architectural (touches all re-symbolization callers), defer to Sprint 29 with a re-scoped Phase-0 filing.
- **#1390 kand** — the phantom-term collapse is proven inert; if the 195-vs-2613 gap localizes to LP first-stage/recourse coupling rather than a single stationarity/complementarity row, defer to Sprint 29.
- **camcge** — if the singular Jacobian is inherent CGE degeneracy (no redundant-row / numéraire / PATH-option fix), reclassify as an Epic 5 observation task, not a Sprint 28 Solve.

### Committed regression-guard sets (PR15)

The frozen reference is the committed Day-13 `gamslib_status.json` (Solve/Match sets byte-identical across the 3-seed retest). The guard, enforced at every Day-N checkpoint (Sprint 27's "measure, don't sweep" discipline):

- **Solve set — 105 models** must not shrink. Any model leaving `model_optimal` is a regression.
- **Match set — 62 models** must not shrink. Any model leaving the match set is a regression.
- **Frozen failure buckets** (the sets a regression would *grow*) are enumerated in §1: translate-fail (7), model_infeasible (8), path_syntax_error (8), path_solve_license (9), path_solve_terminated (5).

A genuine Sprint 28 gain moves a model *out* of a failure bucket into Solve/Match; any *other* membership change is investigated as a regression before goldens are swept (mechanized in Sprint 28 by the Priority 8 golden-staleness check).

---

## 5. Verification

```bash
# Headline counts present
grep -E 'Parse|Translate|Solve|Match' docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md

# Projection labels each delta genuine-gain vs bucket-forward
grep -Ei 'genuine|bucket-forward' docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md | wc -l

# Each carryforward target model has a provenance row
for m in mine camshape otpop cclinpts kand camcge; do
  grep -q "$m" docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md && echo "$m: present" || echo "$m: MISSING"
done
```
