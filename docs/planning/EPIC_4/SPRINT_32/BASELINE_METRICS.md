# Sprint 32 Baseline Metrics (Day-0)

**Created:** 2026-07-13
**Prep Task:** 2 (Sprint 31 → Sprint 32 Day-0 Baseline + Genuine-Floor Re-Baseline — PR15 + PR17 + PR25)
**Purpose:** Establish the authoritative Sprint 32 Day-0 baseline (per-model bucket provenance) + reproduce the PR25 genuine-vs-methodology partition, so every Sprint-32 KPI delta is measured against a clean starting line.

**Day-0 = Sprint 31 final.** The Sprint-31-final commit is **`4cbf8bff`** (`Sprint 31 Day 13: final retest + closeout — SPRINT 31 CLOSED`). `git diff --quiet 4cbf8bff..HEAD -- src/ scripts/` is **empty** — no `src/`/`scripts/` drift since the S31 close (the intervening PRs #1538 review-fix / #1539 PROJECT_PLAN / #1540 prep-docs are all docs-only), so **no fresh ~4 h retest is needed**: the committed DB (`data/gamslib/gamslib_status.json`, unchanged since the S31 Day-13 DB persist) is the Day-0 source and the recompute below reproduces the Sprint 31 final headline exactly.

---

## 1. Day-0 KPI Baseline (142-corpus)

| Metric | Sprint 31 Final = Sprint 32 Day-0 | Sprint 32 Target |
|---|---|---|
| Parse | **142** / 142 | ≥ 142 (maintain) |
| Translate | **135** / 142 | ≥ 135 (stretch +1 via #1385 sarf) |
| Solve | **107** (63 `model_optimal` + 44 `model_optimal_presolve`) | ≥ 109 (+2 firm via mine [P1] + camcge [P3]) |
| Match (142-corpus) | **92** / 142 | maintain ≥ 92 |
| genuine floor | **74** | ≥ 75 (mine [P1] + camcge [P3] cold-matches) |
| model_infeasible | **7** | ≤ 5 (−2 via mine + camcge) |
| path_syntax_error | 8 | maintain ≤ 8 |
| path_solve_terminated | 4 | maintain ≤ 5 |
| Tests | **5,074** | ≥ 5,080 |
| Determinism | ✅ ×3 `{0,1,42}` | ✅ |
| all-219 Match tally | **95** (92 candidates + 3 non-candidate ps2/ps3) | — (see §4) |

**Corpus definition:** the 142-model candidate corpus = `get_candidate_models` = `convexity.status ∈ {verified_convex, likely_convex}` (`scripts/gamslib/run_full_test.py`). All headline KPIs are over these 142; the +3 ps2/ps3 gains land on non-candidate `non_convex` models (see §4).

---

## 2. Canonical Bucket Recompute (142 candidates)

`mcp_solve.outcome_category` distribution over the 142 candidates:

| outcome_category | count |
|---|---|
| `model_optimal` (cold match/solve) | 63 |
| `model_optimal_presolve` (presolve match/solve) | 44 |
| `path_solve_license` | 9 |
| `path_syntax_error` | 8 |
| (translate-failure — no `mcp_solve`) | 7 |
| `model_infeasible` | 7 |
| `path_solve_terminated` | 4 |

Solve = 63 + 44 = **107**. Translate = 142 − 7 translate-failures = **135**.

**Failure-bucket members (by name):**

- **model_infeasible (7):** `agreste`, `camcge`, `cesam`, `fawley`, `lnts`, `mine`, `rocket`
- **translate-failure (7):** `danwolfe`, `decomp`, `iswnm`, `mexls`, `nebrazil`, `saras`, `sarf`
- **path_syntax_error (8):** `clearlak`, `dinam`, `ganges`, `gangesx`, `indus`, `sample`, `turkey`, `turkpow`
- **path_solve_terminated (4):** `dyncge`, `elec`, `tricp`, `twocge`
- **path_solve_license (9):** `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`

---

## 3. Genuine-vs-Methodology Partition (PR25) — genuine floor 74

**Operational definition** (unchanged from PR25): the **methodology** set = `mcp_solve.outcome_category = model_optimal_presolve` **AND** `comparison_status = match` whose **cold** MCP failed/mismatched (the warm-start was *required*), with the cold emit **byte-identical to its pre-fix state** — these are *already emit-correct* models the broadened presolve-retry warm-start-*validates*, not repeatable cross-term gains. The **genuine floor** = every other match: a cold match, OR a match whose cold emit a real fix *changed* (a genuine cross-term contribution, even if PATH still needs the presolve warm-start to converge on a non-convex model).

**Partition of the all-219 matched set (95 total):**

| Class | Count | Provenance |
|---|---|---|
| **Genuine, stable (floor)** | **74** | S28 genuine 68 (otpop/chakra/chenery/kand/srkandw + the 6 non-methodology presolve matches) **+1** S29 (maxmin `-1` + catmix) **+1** S30 (robert cold obj-grad) **+4** S31 (P2 #1111/#1112: polygon methodology→genuine + ps2_f_s/ps2_s/ps3_s_gic mismatch→genuine) |
| **Methodology-recovered** | **21** | `model_optimal_presolve` matches whose cold emit is byte-identical to pre-fix (incl. the CGE cluster irscge/lrgcge/moncge, cpack, himmel16, …) |
| **As-measured (all-219) Match** | **95** | 74 genuine + 21 methodology |

**Genuine floor = 74** is the Day-0 anchor (S30 70 + P2's +4). Note the genuine floor spans candidates **and** non-candidates (the P2 +4 = polygon [candidate] + ps2×3 [non-candidate]); it is not a 142-corpus-only count.

**Genuine-floor → ≥ 75 conversion map (Sprint 32 tracks that convert a `model_infeasible` bucket into a genuine cold match, +1 genuine floor each):**

| Track | Day-0 bucket | Converts to | genuine-floor Δ |
|---|---|---|---|
| **mine** (P1 #1443) | `model_infeasible` | genuine cold match (if the 4th-site bound-multiplier lands + it cold-matches) | +1 (conditional) |
| **camcge** (P3 #1330) | `model_infeasible` | genuine cold match (if the `stat_mps` + dual-consistent Walras lands) | +1 (conditional) |
| **sarf** (P2 #1385) | translate-failure | +Translate (not a floor delta unless it also solves+matches) | 0 (Translate track) |
| **rocket** (P4 #1462) | `model_infeasible` | deferred → Sprint-33 PATH consultation | 0 (hand-off) |
| **hhfair + CGE cluster** (P5 #1236) | mismatch / presolve-match | **documented genuine Case-c** (no emit fix; the ν_objective reduction was control-refuted) | 0 |

**Footnote-⁸ ramp alignment:** the genuine-floor ramp is **S30 70 → S31 74 → S32 ≥ 75 → S33 maintain ≥ 75 → S34 ≥ 77 → S35 ≥ 78** (`PROJECT_PLAN.md` footnote ⁸, as renumbered when Sprint 32 was inserted). Day-0 genuine floor **74** is the ramp's S31 anchor; Sprint 32 targets the **≥ 75** step, conditional on mine [P1] + camcge [P3] cold-matching (the Sprint-30-retro §3 warning: the ramp is NOT independent +1s — S31's +4 was carried entirely by P2).

---

## 4. 142-corpus vs all-219 scope (the Sprint-31 closeout finding)

The headline Match KPI and the genuine floor measure **different populations** — state which one you mean:

| Match scope | Day-0 value | Note |
|---|---|---|
| **142-corpus (headline KPI)** | **92** | matches among the 142 convex candidates (`verified_convex + likely_convex`) |
| **all-219 tally** | **95** | +3 non-candidate `non_convex` matches: `ps2_f_s`, `ps2_s`, `ps3_s_gic` (persisted S31 Day 13) |
| **genuine cold-robustness floor** | **74** | spans candidates + non-candidates (S30 70 + P2's +4) |

The Sprint-31 P2 gains land **outside** the 142 corpus (`ps2_f_s`/`ps2_s`/`ps3_s_gic` are `non_convex` → non-candidates), so they lift the all-219 tally + the genuine floor but **not** the headline 142-corpus KPI (which was "maintain ≥ 92", met at 92). **Sprint 32's Solve movers (mine, camcge) ARE candidates**, so their gains lift all three (142-corpus Match, all-219 tally, genuine floor).

---

## 5. Per-Sprint-32-Target Day-0 Bucket Provenance

| Model / Track | Day-0 bucket | Corpus scope | Sprint-32 projected delta | PR25 label |
|---|---|---|---|---|
| **mine** (P1 #1443) | `model_infeasible` | candidate | +1 Solve (+1 genuine floor if cold-matches); model_infeasible −1 | **genuine** (infeasible → optimal) |
| **sarf** (P2 #1385) | translate-failure | candidate | +1 Translate | **genuine** (translate-failure → translate) |
| **camcge** (P3 #1330 → Epic 5) | `model_infeasible` | candidate | +1 Solve (+1 genuine floor if cold-matches); model_infeasible −1 | **genuine** (infeasible → optimal), Epic-5 |
| **rocket** (P4 #1462) | `model_infeasible` | candidate | conditional +1 Solve OR the Sprint-33 PATH-consultation hand-off | **genuine** (infeasible → match), conditional |
| **hhfair** (P5 #1236) | `model_optimal` + **mismatch** (72.147 vs NLP 87.159) | candidate | 0 (documented genuine Case-c; the sign flip is BANNED, refuted 4×) | **non-convert** (Case-c) |
| **irscge / lrgcge / moncge** (P5 CGE cluster) | `model_optimal_presolve` + **match** (26.09 / 25.77 / 25.98) | candidate | 0 (documented genuine Case-c; stays methodology) | **non-convert** (Case-c) |

**Solve ≥ 109 rests on mine [P1] + camcge [P3]** (both `model_infeasible` candidates, both REPLAN-prone — see `REPLAN_RISK_ASSESSMENT.md` when Task 9 lands); rocket [P4] is deferred to the PATH consultation. **model_infeasible ≤ 5** needs both mine + camcge to recover (7 → 5). The P5 cluster is documented Case-c (no emit fix → 0 delta).

---

## 6. Checkpoint Anchor (`--resolve-changed`)

The Sprint-32 mid-sprint checkpoints (Day 5 / Day 10) re-solve only the emit-touched models via:

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --resolve-changed --since-commit 4cbf8bff
```

At **Day 0** this selects **0 models** — `git diff --name-only 4cbf8bff..HEAD -- 'data/gamslib/mcp/*_mcp.gms' 'data/gamslib/mcp/*_mcp_presolve.gms'` is empty (no emit golden has changed since the S31 close), confirming the clean baseline:

```
GO: no emit goldens changed since 4cbf8bff
```
(`run_full_test.py` logs the `--since-commit` value verbatim, so the output echoes the same short SHA the command was invoked with; the full 40-char form `4cbf8bffa0b2481d4bb324f449a6ed23223f1f4b` resolves to the same commit.)

During Sprint 32, as the emit sites change (the mine bound-multiplier, the sarf `stat_task` sparsification, the camcge `stat_mps` + Walras redefinition), the anchor selects exactly the emit-touched models for a bounded re-solve rather than a full ~4 h pipeline run; GO iff no changed golden moves backward.

---

**Document Created:** 2026-07-13
**Owner:** Sprint 32 Planning Team
**Day-0 anchor:** `4cbf8bff` (Sprint 31 close) · genuine floor 74 · 142-corpus Match 92 · all-219 Match 95
