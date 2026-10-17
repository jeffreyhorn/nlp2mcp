# Sprint 40 Plan (Weeks 45–46): Day-by-Day Schedule

**Sprint 40 Prep Task 12** · **Planned at:** `d43091ae` · **2026-10-17**

**Baseline at `d43091ae`** (derived by `kpi_block.py` / `floor_tracker.py`, unchanged since the S39 close `bd2af6e9`):

- Solve **111** · Match **95** (65 cold + 30 presolve) · Translate **135**
- `path_solve_terminated` **0** · `path_solve_license` **11**
- genuine floor **75**

**Checkpoint anchor:** `bd2af6e9` (the Sprint-39 close). `git diff bd2af6e9 HEAD -- src/ data/gamslib/mcp/` is empty at planning time.

**Owner answers (fixed inputs, committed at `b44344a2`, 2026-10-14, before Task 7 measured anything):**

- **Floor: B.** A separate, non-counting `license_unlocked` ledger in `data/floor_provenance.json`, with the fail-before sub-rule.
- **Corpus: A.** Admit by rule: a model enters the corpus iff the licensed verifier classifies it convex. Both denominators go in one sentence.
- **CI: B.** Hosted CI, gated on GAMS. That gate was met by the owner's 2026-10-14 statement that **the access code can be activated on every CI run** (`OWNER_DECISION_BRIEF.md` §4). **There is no Day-0 decision and no Day-0 fallback.** This supersedes `PROJECT_PLAN.md`'s "owner decision on Day 0" timing.

> **"Weeks 45–46" are project-relative sprint weeks, not ISO weeks** (see `../SPRINT_39/PLAN.md`). **Read the dates.** Day 0 is the day after prep completes. If this PR merges later than 2026-10-17, shift every date by the same amount; the validator checks only that the dates are consecutive.

---

## 1. The schedule

| Day | date | h | allocation |
|---|---|---|---|
| **0** | 2026-10-18 | 10 | **baseline** 2h · **P1** 8h |
| **1** | 2026-10-19 | 12 | **P1** 10h · **P10** 2h |
| **2** | 2026-10-20 | 10 | **RT** 3h · **P2** 5h · **P3** 2h |
| **3** | 2026-10-21 | 10 | **P2** 6h · **P3** 4h |
| **4** | 2026-10-22 | 10 | **P2** 5h · **P3** 5h |
| **5** | 2026-10-23 | 10 | **P3** 1h · **P7** 7h · **CK** 2h |
| **6** | 2026-10-24 | 10 | **P7** 3h · **P4** 7h |
| **7** | 2026-10-25 | 10 | **P4** 5h · **P8** 5h |
| **8** | 2026-10-26 | 10 | **P4** 4h · **P8** 1h · **P5** 5h |
| **9** | 2026-10-27 | 10 | **P6** 8h · **P5** 2h |
| **10** | 2026-10-28 | 9 | **CK** 2h · **P6** 6h · **P5** 1h |
| **11** | 2026-10-29 | 10 | **P9** 6h · **P10** 4h |
| **12** | 2026-10-30 | 4 | **P10** 4h |
| **13** | 2026-10-31 | 6 | **close** 6h |

TOTAL **131 h** against a **168 h** cap; heaviest day **12 h**.

**Labels:**
- **RT** is the license-neutrality gate on the first licensed full run (§4).
- **CK** is a checkpoint.
- **baseline** and **close** are the two non-priority blocks: Day-0 re-derivation, and the Day-13 retest plus close documents.

**Unattended GAMS time is not booked as hours.** It runs on the nightly slots below and is analysed in the next day's hours:
- the RT full run (night of Day 1);
- the P2 batch (night of Day 2);
- the checkpoint licensed re-runs.

**Days are consecutive calendar days**, matching how prep ran (Tasks 1–12 spanned 2026-10-12 → 10-17, weekends included).

### Budget against the PROJECT_PLAN estimates and the prep re-estimates

| priority | scheduled | PROJECT_PLAN | prep re-estimate | |
|---|---|---|---|---|
| P1 licensed toolchain + CI + schema 3.1.0 | 18 h | 14–18 h | Tasks 3/4/5: local half proven in prep; CI half unblocked (§2); plus the corpus-aware `check_doc_figures.py` that Decision 2 requires before any admission (`OWNER_DECISION_BRIEF.md` §Decision 2) | ✅ at the top of the band |
| P2 MCP-gated cohort | 16 h | 16–22 h | Task 7: batch is **2,162 s** wall; 0 unrouted fingerprints | ✅ |
| P3 NLP-gated set | 12 h | 10–14 h | Task 7: all 9 classify convex, so all are admitted by rule | ✅ |
| P4 two-class triage | 16 h | 14–20 h | Task 10: turkpow's layer traced; egypt/shale necessary but not sufficient | ✅ |
| P5 lnts → the `stat_step` class | 8 h | 6–10 h | Task 8: **verdict C, +1 Solve removed**; budget redirected | ⚠ **re-scoped** |
| P6 sarf Jacobian | 14 h | 20–28 h | Task 9: **14–24 h**; E1–E4 + E7/E8 ≈ 8–12 h, E5/E6 bounded | ⚠ **under**, by re-estimate |
| P7 #1755 diagonal defect | 10 h | 8–12 h | Task 10: layer AD, `_sum_should_collapse` | ✅ |
| P8 structural sites | 6 h | 6–8 h | Task 10: both guards live; discriminating inputs exist | ✅ |
| P9 smaller items | 6 h | 6–10 h | Task 11 + owner answers: 4.5–5.5 h, plus the danwolfe/decomp check moved to P1 | ✅ |
| P10 process mechanisms | 10 h | 10–14 h | Task 11: 9.0 h | ✅ |
| pipeline retest (RT + close) | 9 h | 4–6 h | the RT gate is new in this sprint | ⚠ over by 3 h |
| checkpoints | 4 h | — | each includes a licensed cohort re-run (§4) | |
| **baseline** (Day 0) | 2 h | — | | |

**Two departures, both from prep measurements:**

- **P6 is under its plan band.** Task 9 found sarf's non-termination is **one unfiltered loop**, and re-estimated the whole track at 14–24 h. The plan schedules the low end:
  - E1–E4 + E7/E8, which are byte-identical and corpus-safe;
  - E5/E6, the `simplify` recursion, **as a bounded diagnosis**.

  **+1 Translate is not projected** (close rule **C7**).
- **P5 keeps its band but changes its object.** Task 8's verdict C removed lnts's +1 Solve. It redirected the budget to the `stat_step` emit class, which has 2 confirmed models (lnts, robot) and 2 candidates (glider, rocket).

**The total, 131 h, sits 37 h under the cap deliberately.** The cohort tracks (P2, P3) are first measurements of 20 never-solved emits. The plan's dominant risk is a cascade of first-time fingerprints, and slack is what absorbs it without breaking the measure-and-route rule.

## 2. Fixed points

| constraint | why | where it lands |
|---|---|---|
| **P1 on Days 0–1, before any license-dependent measurement** | the schema 3.1.0 writers must exist before any licensed row is written, so every row is written once, with its `license_edition` | Days 0–1. **No P2, P3 or RT hours before Day 2** |
| **the three owner decisions are fixed inputs** | answered blind at `b44344a2`, before Task 7 measured anything. Task 7 descends from that commit, and this plan from both | consumed in P1 (ledger, `corpus_admissions`), P2 (floor booking), P3 (admission) — **never re-opened** |
| **RT before any cohort KPI** | the license should affect only size-refused solves. Any other row that moves is a toolchain finding, and must be explained before a figure is reported | Day 2, first block |
| **the P2 batch on a nightly slot** | Task 7 measured the whole two-population pipeline at **2,162 s** (~36 min), or ~16 min without the two translate timeouts. It fits a nightly slot with room for the retention of every listing | night of Day 2; analysed Days 3–4 |
| **P4 after P2** | egypt and shale need their licensed solves to verify a Class-A fix against | P2 ends Day 4; P4 starts Day 6 |
| **P9a after Checkpoint 2** | P9a moves every qualifying row `not_tested` → `mismatch`, and `--resolve-changed` reads each one as a `forward` move (Task 11), which would confound a checkpoint. **The set is derived when P9a starts, not taken from prep** (§5 C9) | Day 11 |
| **checkpoints** | Day 5 and Day 10 | both `--resolve-changed --since-commit bd2af6e9` |
| **final retest** | ≥ 3 `PYTHONHASHSEED`, byte-identical | Day 13 |

**CI is unblocked, not REPLAN'd.** Task 4's local-only recommendation predates the owner's 2026-10-14 statement that the access code can be activated per run. Each hosted job activates its own license with `gamsgetkey`, so the embedded node ID is the runner's own. **P1's CI half proceeds** in the order `CI_LICENSE_DESIGN.md` gives:
1. create `gams-licensed`. This is an **owner action** in GitHub settings: `main`-only, no required reviewers;
2. store `GAMS_ACCESS_CODE` in that environment only;
3. land `licensed-solve.yml` together with the PR-side skip-by-notice change.

## 3. REPLAN exits: the specific evidence, and where the budget goes

**A REPLAN is not a failure.** Every exit below is pre-registered with its evidence, so a track that stops is read against its own rule, not against a hoped-for outcome.

### P1: the licensed toolchain (Days 0–1)

| trigger | evidence | budget goes to |
|---|---|---|
| `gamsgetkey` activation fails on a hosted runner | the `licensed-solve.yml` job's activation step exits non-zero (`CI_LICENSE_DESIGN.md` §3, `… \|\| exit 1`) | **CI half → local-only** (Decision 3's own fallback, A). The local half and every later track proceed unchanged. Record it and ask GAMS whether activations are counted |
| the edition discriminator misreads a stage | any stage's licensed listing classified `demo` or `None` (Task 3's 20/20 control) | stop P1's writers; it is a parser defect, and no licensed row is written until it is fixed |
| the schema migration fails its positive control | the new fields do not **fail** 3.0.0 or do not **pass** 3.1.0, or 3.1.0 stops rejecting an unknown key | fix before Day 2; **P2/P3 cannot start** on an unmigrated DB |

### P2: the MCP-gated cohort (Days 2–4)

| trigger | evidence | budget goes to |
|---|---|---|
| a cohort re-emit is **not** byte-identical | `cmp` against the committed golden. Task 7 found 11/11 identical at `79eeccff` | a **staleness finding**, not a solve result. Route it to the change that drifted the golden, and do not book that model |
| a result has no attribution | `check_mcp_solve_attribution.py` is not `MCP-SOLVED` for a claimed match | **not booked** (the `weapons` trap) |
| a non-match fingerprint needs diagnosis | anything other than the 2 P10-rule qualifiers (`egypt`, `shale`) | **route, do not fix in place.** Open the routing-note issue (R-PRE-140, R-EXEC, R-JB-171, R-B-*); the budget stays in P2's band |
| `turkey`'s pre-fix golden **matches** under the license | the fail-before sub-rule (Decision 1) | turkey is **not** credited fix-driven genuine. It is reported license-unlocked, and the floor does not move for it |

### P3: the NLP-gated set (Days 2–5)

| trigger | evidence | budget goes to |
|---|---|---|
| a multi-solve model's last solve is the wrong reference | `airsp2` classifies from a `DECISM` solve, not the requested CPLEX LP (Task 7). Four models are multi-solve | admit by rule anyway (Decision 2 is on classification), but **record the reference question** and keep that model's comparison out of the headline until it is settled |
| a parse failure or translate timeout (`emfl`, `indus89`, `phosdis`; `airsp`, `msm`) | Task 2/7, unchanged | **route** to grammar / translate-performance issues. They are admitted (convex), but reach no MCP this sprint and are reported as such |

### P4: the two-class triage (Days 6–8)

| trigger | evidence | budget goes to |
|---|---|---|
| the turkpow fix leaves the P2 ratchet at 9 | `make check-index-repeats` | the layer is wrong. Re-trace from `_replace_indices_in_expr`, and **do not** patch the `t__kkt1` mint (Task 10: it is downstream and correct) |
| egypt / shale stay MS 5 after the Class-A fix | the licensed solve | **expected** (Task 10: necessary, not sufficient). Land the fix on property + golden evidence, and route the underlying defect; do not widen the track |
| a Class-A fix newly references a multiplier on a repeated-domain equation | #1737's refusal fires (Task 10 §6) | that is #1737 working. Record which equation; **never narrow #1737** |

### P5: the `stat_step` class (Days 8–10)

| trigger | evidence | budget goes to |
|---|---|---|
| the lnts / robot `stat_step` rows do not share a mechanism | per-row `kkt_residual.py` trace | split them. Bank the one that does not reproduce, and land nothing on a guessed shared cause |
| the traced fix perturbs a live match | the leak gate | stop. Bank behind its Phase-0 doc. lnts's banked diff (verdict C) is **not** re-applied |

### P6: sarf (Days 9–10)

Task 9's three exits, unchanged (`SARF_JACOBIAN_DESIGN.md` §8):
1. **Timeout re-trigger:** after E1–E4, sarf still exceeds the cap **before** `assemble_kkt_system` → stop and re-attribute.
2. **Atomicity:** **any** golden or fixture-hash change from E1–E4 → a `_referenced_index_tuples` false negative. Stop.
3. **E5/E6 balloons:** a change to `simplify`'s algorithm (rather than to the expression's shape) → its own issue, and **C7 becomes VOID**.

### P8: the structural pins (Days 7–8)

| trigger | evidence | budget goes to |
|---|---|---|
| a 3-D aliased fixture does **not** discriminate when re-run on `main` | the assertion passes with the consume-once guard neutralised (Task 10's mutation result does not reproduce) | stop. Record the guard as dead **at the probed shapes**, with the proof scope, as `PROJECT_PLAN.md` P8 allows. Remaining hours → slack |
| promoting a pin needs an `src/` change | anything beyond a test is required | out of scope. P8 is tests only; route the change to its own issue |

### P9: the smaller items (Day 11)

| trigger | evidence | budget goes to |
|---|---|---|
| P9a's derived set differs from what its Phase-0 doc predicted | the Day-11 identity pin (§5 C9) | **re-pin and re-state before landing.** Never assert prep's 7 |
| P9a's change moves any `kpi_block` figure | `kpi_block.py --json` before/after | stop: it is no longer a relabel. Bank it behind its Phase-0 doc |
| P9b finds a reader of `integration_health_check.py` | `grep -rn integration_health_check` outside `docs/` | do not delete. Re-carry with the reader named |
| P9c's rename breaks `check_doc_figures` | `make check-doc-figures` | fix in the same commit; the fact's `source` string names the key |

### P10: the process mechanisms (Days 1, 11–12)

| trigger | evidence | budget goes to |
|---|---|---|
| a mechanism's fail-before test passes **before** the change | the test run against `main` | the test is vacuous. Rewrite it before landing the mechanism (§7.5) |
| 10c's `--fail-on-unverified` makes the local gate fail on an uncontended run | a timeout with nothing else running | the 600 s budget is too tight for that model. Record it; do not loosen the flag. Run that model alone |
| 10a's extraction changes a resolved anchor | the 16-site before/after comparison | stop. It is not a pure refactor (Unknown 10.1). Keep the resolver where it is, and re-carry |
| a mechanism overruns its estimate | hours against `PROCESS_AND_SMALL_ITEMS.md` | land the finished mechanisms, re-carry the rest by name. **10e (rules recorded) is the last to drop**, because it costs 1 h and the prompts already carry the rules |

### P7: #1755 (Days 5–6)

| trigger | evidence | budget goes to |
|---|---|---|
| the fix changes a golden | the full leak gate, **complete** | each changed golden is a **candidate corpus instance** to examine, not to blindly refresh (Task 10) |
| #1737 refuses a newly referenced equation | emit exits 1, "domain … repeats" | expected for repeated-domain shapes. Record it; do not narrow #1737 |
| the layer is not `_sum_should_collapse` | the off-diagonal positive control (`tsam('i1','i2')` → 0) breaks | re-trace; bound the mechanism and stop |

## 4. Checkpoints, the license-neutrality gate and the final retest

| when | what | verdict rule |
|---|---|---|
| **Day 2 (RT)**, first block | the **first licensed full run**: `run_full_test.py` over the full corpus on a **scratch DB copy** (night of Day 1), diffed against the committed DB on outcome, objective (rel 1e-6) and verdict | **every row outside the two populations keeps its outcome** (Unknown 1.5's universal claim). Any other moved row is a toolchain finding, to be explained **before any KPI is reported**. Never persisted |
| **Day 5 (CK1)** | `run_full_test.py --resolve-changed --since-commit bd2af6e9 --min-scope <N>`, plus a licensed re-run of the 11 cohort models | **NO-GO on any `backward` or `missing` row.** `<N>` is **discovered** first by a dry run and then asserted, as Sprint 39 did. An empty selection is an error without `--allow-empty`, and that run certifies nothing |
| **Day 10 (CK2)** | same, **before P6 lands and before P9a** | same |
| **Day 13** | full retest + determinism **×3** `PYTHONHASHSEED`, byte-identical over the full golden scope; `make check-goldens` **alone**, with the derived `--min-scope` **and** `--fail-on-unverified` (P10c) | any drift is a landing failure. **Any unverified timeout is a FAIL**, not a soft pass |

**Why each checkpoint includes a licensed cohort re-run.** PR workflows stay demo-only, so a large-model regression shows up only on the next licensed run (Task 4's stated trade-off). Until `licensed-solve.yml` runs on `main`, the checkpoints are that run.

**Three gate properties not to rediscover:**
- `make leak-check MODEL=sarf` reports `NO-OP`, because sarf has no golden. The real gate is the full sweep plus sarf newly producing one (186 → 187).
- The leak gate is **load-dependent** (`MAX_WORKERS = 3`), so it **runs alone**.
- **Contention shows up as timeouts, not as a smaller scope** (Task 11). `--min-scope` alone passes it.

## 5. Pre-registered close rules, each with its PRECONDITION

**A precondition references only a track's start state, never its outcome.** It is fixed here and cannot be edited at close. A rule whose precondition fails is **VOID, not unmet**, and the closeout says which one failed.

| # | rule | precondition | if the precondition fails |
|---|---|---|---|
| **C1** | **`path_solve_terminated` maintains 0 over every row outside the two populations.** A non-cohort model reaching it is a **REGRESSION**. Cohort rows that land there are a **first-measurement influx**, reported **by identity**, never folded into the 0. Task 7 measured `ferts` and `tabora` (in-corpus) and `minsurf` (NLP-gated) there | **none** | cannot be voided |
| **C2** | **Three-gate firm landing:** a per-model Phase-0 doc (layer named, **positive control** named) **and** an *unqualified*, uncontended leak-gate pass **and** in `main`. Two of three is not a landing | **none** | cannot be voided |
| **C3** | **Cohort moves are reported as LICENSE-UNLOCKED, never as recovered,** stated **once**, pinned to the batch commit, and kept separate from fix-driven moves | **P2's batch started** | no cohort movement exists to report; the closeout says so |
| **C4** | **The headline is on the 142-candidate corpus**, with the expanded scope (142 + *k* admitted by rule) **in the same sentence**, plus a Rolling-KPIs footnote. A scope addition is never booked as a recovery | **P3's admission (W10 `--admit`) started** | report on 142 only, and say no model was admitted |
| **C5** | **The floor is read from `data/floor_provenance.json` under Decision 1 (B):** license-unlocked matches go in the non-counting `license_unlocked` ledger, reported as 75 + *k*. A previously-fixed model counts as fix-driven genuine only if its pre-fix golden, run licensed, **does not** match | **none**. Decision 1 is a committed fixed input (`b44344a2`) | cannot be voided |
| **C6** | **Every figure is derived at execution time** and carries the commit it was measured at. The PR body is a pointer; a figure is stated once | **none** | cannot be voided |
| **C7** | **+1 Translate → 136** is reported only if sarf newly produces a byte-stable golden at **≤ 300 s** | **P6's E5/E6 item started** | **VOID.** Translate reports 135 flat, naming P6 as E1–E4 only |
| **C8** | **License neutrality:** every row outside the two populations keeps its outcome on the first licensed full run. **No KPI is reported before this passes** | **none** | cannot be voided |
| **C9** | **P9a's `forward` moves are RELABELS, not fixes.** The affected set is **derived and pinned by identity when P9a starts**, in two parts: the remainder of prep's 7 (any that P5 or another landing moved first is dropped, by name), and the **cohort additions** (rows that P2 persisted as an own-infeasible MCP against an optimal NLP). Report the **measured** `mismatch` +*k* / `not_tested` −*k*, with no change to any `kpi_block` figure, in the same sentence as their reason | **P9a started** | the rows stay `not_tested`; the closeout says P9a did not start |

**Five of nine take no precondition** (C1, C2, C5, C6, C8). That shows preconditions aren't being used as an escape hatch: the rules that guard correctness and reporting discipline can't be voided at all.

**C1's wording is a prep finding, not a softening.** Task 7 measured two in-corpus cohort models at `path_solve_terminated`. Read literally, "`path_solve_terminated` maintains 0" would report a first measurement as a regression. The rule now names its population, and the influx is pinned by identity.

**C9's set is not prep's 7, and that is a consequence of the schedule.** Prep's 7 (agreste, camcge, cesam, fawley, lnts, mine, rocket) describe the prep DB. By Day 11:
- P2 has persisted the cohort, and Task 7 measured five own-infeasible MCPs there (`egypt`, `robot`, `shale`, `sroute`, `tricp`). P4 expects egypt and shale to **stay** infeasible, so they qualify too.
- P5 may have moved lnts.

A fixed "+7, these seven" assertion would then fail a correct relabel, or report it wrongly. Derive the set from the DB at P9a's start, using the widened condition itself, and pin it.

**Reporting rule for C3, pre-written** (to be used verbatim, with the realized figures filled in from the batch commit):

> **Cohort result — license-unlocked, not recovered** (batch at `<sha>`): of the 11 MCP-gated models, `<k>` solve and `<m>` match; `path_solve_license` → `<p>`. None of these is a fix: the emits are byte-identical to their committed goldens; only the ability to run them changed.

## 6. Acceptance criteria, with each figure's source

| criterion | baseline → target | source |
|---|---|---|
| Solve, continuity (142) | ≥ 111, **excluding** the cohort | `kpi_block.py`; the cohort movement is reported per **C3** (Task 7's dry run measured +4 at `79eeccff`, never persisted) |
| Match, continuity (142) | ≥ 95, **excluding** the cohort | `kpi_block.py`; cohort matches per **C3** (dry run: +2, both presolve) |
| Translate | 135 → **135**; 136 only under **C7** | `kpi_block.py` |
| expanded scope | reported per **C4** | `kpi_block.py --corpus` (P1) over `corpus_admissions.json` |
| genuine floor | ≥ 75, plus the `license_unlocked` ledger count | `floor_tracker.py`, per **C5**; never the mechanical DB count (65) |
| `path_solve_license` | 11 → **0**, every cohort row `license_edition: "licensed"` | `kpi_block.py` + the DB rows |
| `path_solve_terminated` | **0** outside the populations | **C1**; the influx is listed by identity |
| model_infeasible / path_syntax_error | ≤ 7 / ≤ 6 **excluding the influx** | `kpi_block.py`. The lnts −1 is **removed** (Task 8, verdict C) |
| schema | 3.0.0 → **3.1.0** | `data/gamslib/schema.json`; both result types accept `license_edition` and still reject an unknown key |
| license neutrality | — | **C8**, Day 2 |
| P2 ratchet | 9 → ≤ **6** (turkpow's 3), with `--update-baseline` in the same commit | `make check-index-repeats`. nonsharp's 2 cannot move by regeneration (Task 10) |
| CI | no `pull_request` job receives the license; a > 1,000-row probe fails on the demo and passes licensed | P1's Phase-0 gate (`PROJECT_PLAN.md` P1) |
| leak gate | full scope, **alone**, 0 timeouts, `--fail-on-unverified` | `make check-goldens` after P10c |
| determinism | — | Day 13, ×3 `PYTHONHASHSEED` |
| correctness | every claim and every cohort non-match carries a `kkt_residual.py` verdict; **`CASE_B` is a refusal** | `scripts/diagnostics/kkt_residual.py`, or the recorded harness failure (Task 7: 6 models) |

**Tool paths**, given once: `scripts/sprint_audit/kpi_block.py` · `scripts/sprint_audit/floor_tracker.py`. Both run at execution time (**C6**).

**Superseded from `PROJECT_PLAN.md`:**
- "+1 Solve via lnts" and "model_infeasible 7 → 6": removed by Task 8's verdict C.
- "+1 Translate via sarf" as a target: conditional under **C7**.
- "the owner decides floor classification on Day 0": decided in prep (`b44344a2`).

## 7. Risk register

| risk | likelihood | mitigation |
|---|---|---|
| **a cascade of first-time fingerprints** pulls P2/P3 into open-ended diagnosis | **high**: Task 7 found 9 of 11 non-matches, 6 of them with no residual verdict because the presolve emit itself fails | measure and route by rule (P10's rule: a reproduced fingerprint **and** a named fix surface). Only egypt/shale qualify today. 37 h of slack |
| hosted activation fails or is rate-limited | low–medium: activations may be counted (unknown) | P1 exit → local-only (Decision 3's A). The checkpoints' licensed re-runs carry the large-model coverage; reduce the nightly `schedule` first |
| **license text leaks** into a log, artifact or commit | low, but irreversible | **isolation, not detection:** the secret is only in the `main`-only environment. Masking and the in-job scan are defence in depth. Scan every diff before commit; never commit `USER:`/licensee lines |
| the neutrality run moves a non-cohort row | low (Task 3: 0/13 on the sample) | **C8** blocks KPI reporting until it is explained |
| the corpus grows silently | **confirmed possible** (Task 6: 142 → 143 on a scratch DB) | W10 refuses un-`--admit`ted models; `kpi_block --corpus` reports both. The danwolfe/decomp disagreement (142 vs 140) is checked in P1 |
| sarf's recursion fix touches every emit | high, if attempted | E5/E6 is a bounded diagnosis; **C7** voids rather than stretching the track |
| the leak gate passes on unverified timeouts | **measured** (Task 11: rc 0 with `--min-scope 193`) | P10c lands on Day 1, before any `src/` landing relies on the gate |
| a figure is quoted stale | **high**: it recurred in every prep PR review round | **C6**; `make check-doc-figures` before every push, and on the PR body once P10d lands |

## 8. Known-Unknown routing

**28 of 29 unknowns were resolved in prep: 14 ✅ · 2 ❌ · 12 🔶, plus 1 🔍 routed.** That one, 1.5, is routed **by design**: a sample cannot verify a universal claim, so only the first licensed full run can close it. Each resolution is routed to the day that **consumes** it:

| unknowns | resolved as | consumed by |
|---|---|---|
| 1.1, 1.2 | effective license proven; discriminator 20/20 | **Days 0–1** (P1 writers) |
| 1.3 | isolation holds; hosted CI unblocked by the owner statement | **Days 0–1** (P1 CI half) |
| 1.4 | writer list closed at 11 sites (W1–W11) | **Days 0–1** (P1 schema) |
| 1.5 | 🔍 sample-neutral; universal claim open | **Day 2** (RT, **C8**) |
| 2.1–2.4 | cohort measured; 0 unrouted; attribution works; `ISSUE_933` re-scoped | **Days 2–4** (P2) |
| 3.1–3.3 | all 9 convex; the corpus can grow silently, and can be held | **Days 2–5** (P3); 3.3's hold → P1 |
| 4.1–4.3 | turkpow layer traced; egypt/shale insufficient; Class B in the IR | **Days 6–8** (P4) |
| 5.1–5.3 | verdict C; the `stat_step` class | **Days 8–10** (P5) |
| 6.1–6.3 | one unfiltered loop; E1–E4 byte-identical; recursion behind | **Days 9–10** (P6) |
| 7.1, 7.2 | #1755 filed; layer AD | **Days 5–6** (P7) |
| 8.1 | both guards live | **Days 7–8** (P8) |
| 8.2 | #1737 reached indirectly by P7/P4 | **Days 5–8** (P7, P4 exits) |
| 9.1, 9.2 | P9a two sites; owner answers; #1758 filed; #1668 closed | **Day 11** (P9) |
| 10.1, 10.2 | 10a–10e specified with fail-befores | **Days 1, 11–12** (P10) |

## 9. What prep found wrong, and what each change did

**14 of 29 assumptions were refuted or partially refuted** (2 ❌ + 12 🔶), a **48 %** refutation rate. Sprint 39's was 63 % and Sprint 38's 32 %.

The ones that **changed the sprint**, not just a figure:

| # | the assumption | what prep found | what it changed |
|---|---|---|---|
| **5.1** | lnts's Day-5 failure was procedural; a gate makes the banked diff landable | the diff reproduces Day 5 byte for byte, and a gate changes neither REPLAN condition | **+1 Solve removed**; P5 redirected to the `stat_step` class |
| **6.1 / 6.3** | sarf's cost is the "70.9 %" Jacobian share, and one commit finishes it | **one unfiltered loop** (292.3 M differentiations); fixing it reaches a dense validation and then a `RecursionError` | P6 scheduled at the low end; **+1 Translate conditional (C7)** |
| **4.1** | turkpow's defect is the `t__kkt1` mint | the mint is downstream and correct; the layer is `_replace_indices_in_expr`'s alias map | P4 opens on the right function |
| **4.2** | egypt/shale's mismatch is their Class-A reference | the references are live, but both stay MS 5 | P4 lands on property evidence; no Solve projected from it |
| **2.2** | every cohort non-match gets a residual verdict | **5 of 11**; the harness fails on 6 presolve emits | non-matches are routed by fingerprint, and **CASE_B is a refusal** |
| **1.3** | the license can reach hosted CI | very unlikely for a node-bound local license, **then** unblocked by per-run activation (owner, 2026-10-14) | P1's CI half proceeds; the fallback is pre-registered |
| **1.4** | the plan's writer list is complete | **3 more sites**, two of them fixed-key-list writers (the `mcp_attribution`-loss mechanism) | P1's schema work covers 11 sites |
| **9.1** | P9a is "only Case 6's label" | the DB holds `not_tested`, so Case 6 alone is **inert**; two sites; 7 checkpoint `forward` moves | **P9a after CK2**, with **C9** |
| **10.2** | `--min-scope` catches a contention-narrowed leak gate | **contention causes timeouts**, which pass at rc 0 | P10c adds `--fail-on-unverified`; the Day-13 gate requires it |
| **7.2** | the diagonal term is dropped through misaligned indices | dropped **even when aligned**; the whole constraint vanishes | P7's Phase-0 targets `_sum_should_collapse` |

**Two findings that are not unknowns but change the close:**
- Task 7 put `ferts` and `tabora` at `path_solve_terminated`, so **C1 had to name its population**.
- Task 6 found `danwolfe` and `decomp` counted by `kpi_block` (142) but skipped by `batch_parse` (140), so the corpus has **two readers that disagree**. P1 checks this.

---

**Document Status:** ✅ Complete (Sprint 40 Prep Task 12). **GO for Day 0.** No owner decision is outstanding. The one owner *action* is creating the `gams-licensed` environment on Day 1.
**Last Updated:** 2026-10-17
