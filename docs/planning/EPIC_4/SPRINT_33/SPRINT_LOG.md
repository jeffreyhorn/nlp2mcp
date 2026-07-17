# Sprint 33 — Progress Log

**Sprint:** 33 (S32 carryforward — mine cross-term · sarf symbolic-emit · fawley 2nd-index · camcge Walras [Epic 5] · rocket/Case-c) · **Weeks 31–32**
**Code anchor:** S32 close `ee51ed9e` · **DB byte-anchor:** `4cbf8bff` (S31 close)

## Headline KPIs (142 convex-candidate corpus)

| Metric | Day-0 | Close | Δ |
|---|---|---|---|
| Parse | 142 | 142 | — |
| Translate | 135 | 135 | — |
| **Solve** | 107 | **108** | **+1** (sample cold match; cold 63→64 + presolve 44) |
| **Match** (as-measured) | 92 | **93** | **+1** (sample) |
| **genuine floor** | 74 | **75** | **+1** (sample genuine cold-emit — meets the ≥ 75 target) |
| model_infeasible | 7 | 7 | — |
| path_syntax_error | 8 | **7** | **−1** (sample) |
| all-219 Match | 95 | **96** | +1 |
| Determinism | — | ✅ ×3 `{0,1,42}` | byte-identical (blast radius = `sample_mcp.gms` only) |

**One genuine bucket move (P6 sample); the three deep tracks (P1/P2/P3) all REPLAN'd/deferred — control-refuted before any bad ship. Zero broken code shipped.**

---

## Day 0 — Kickoff + Day-0 traces + control probes → GO (2026-07-16)
GO/NO-GO GREEN (`git diff ee51ed9e..HEAD -- src/ scripts/` empty). Baseline confirmed vs the DB (Solve 107 / Match 92 / floor 74 / mi 7 / all-219 95). Three deep-track/Case-c fingerprints re-confirmed **exactly** on the live tree: mine CASE_B `stat_x(3,1,1)` 2.37, fawley CASE_B `stat_bq(*,fuel-oil)` 473, rocket CASE_C_OBJDEF boundary. `DAY0_TRACE_NOTES.md`.

## Day 1 — P1 mine Phase-0 control + residual decomposition (2026-07-16)
Cleared the standalone-presolve blocker (the emit `$include` is repo-relative → run from the repo root); reproduced MS-5 @ 22058 exactly. The §5 residual decomposition reproduces the harness residuals row-for-row. `DAY1_PROGRESS_NOTES.md`.

## Day 2 — P1 mine H1 control → **REPLAN (H3)** (2026-07-17)
The pre-`src/` control **refuted H1** (head-label multiplier re-keying): it is **value-invariant** (22→22 nonzero rows, `d_N` = `d_Nh1` row-for-row) — the `l+1`-shifted transfer already stores the head-label value at the body label. No emit-consistent change closes the `c`-boundary (`x.m=0` degeneracy). → Sprint-34 head-offset dual subsystem. Task-9 P1-High-prior REPLAN realized. `DAY2_MINE_REPLAN.md`.

## Day 4 — P3 fawley sameas control → **H-b** (2026-07-17)
The sameas over-sum is real (473→18.468, genuine fix), but the 18.468 is an untransferred bound multiplier (a max-convention transfer-sign gap). sameas + all-bound-transfers-fixed → warm residual ~0 **but the MCP still solves MS-5 @ 4399.557** (LP opt 2899.25) → non-emit divergence. NEW cross-cutting finding: the max-convention bound-transfer gap (shared with mine). `DAY4_FAWLEY_CONTROL.md`.

## Day 5 — P3 fawley CLOSE (H-b) + Checkpoint 1 GO (2026-07-17)
The genuine sameas correction is a constraint-index-diagonal change in the ~1400-line general emit function (`_add_indexed_jacobian_terms`) — high blast radius for **zero in-sprint bucket** (fawley stays `model_infeasible`, H-b). Deliberately **deferred to Sprint 34** (risk/reward), not a correctness REPLAN. Checkpoint 1: `--resolve-changed --since-commit ee51ed9e` GO. `DAY5_FAWLEY_CLOSE.md`.

## Day 6 — P2 sarf REPLAN (Option B) → Sprint 34 (2026-07-17)
Tractability assessment: the blow-up is per-column diff of `task`'s 369K columns (S1 acost3 / S2 enumeration / S3 stationarity); the active subset (398) is not statically enumerable → a from-scratch symbolic/parametric emit mode is required — a 20–28h high-risk atomic rebuild for the lowest-leverage bucket (+1 Translate). **Sprint-owner decision: Option B** — defer to Sprint 34, pivot to P6. `DAY6_SARF_ASSESSMENT.md`.

## Day 11 — P6 sample RECOVERED — +1 Solve / +1 Match / +1 genuine floor (2026-07-17)
Fixed a `path_syntax_error` emit bug: the variable-init pass passed through an expression `.l` init referencing a variable **pruned** from the MCP. `sample.gms` has two models (`sample` uses `n`, `sampler` uses `nr`); the last solve translates `sampler`, pruning `n`, but the emit carried `c.l = sum(h, data(h,"cost")*n.l(h))` → `$140 Unknown symbol`. **Fix** (`src/emit/emit_gams.py`): skip an expression `.l` init whose `.l`-refs aren't a subset of `_declared_mcp_vars` (from `kkt.stationarity`; narrower than `kkt.referenced_variables`). sample → MS-1 @ 726.679 = NLP optimum (match). Blast radius = sample only; det ×3; `make test` 5,034 passed. `DAY11_P6_COHORT.md`.

## Day 12 — P7 infrastructure (2026-07-17)
Regression fixture for the P6 fix (`test_sample_pruned_var_l_init.py`, fail-before/pass-after verified). Genuine-floor tracking 74→75. Epic-4 `SUMMARY.md` row-33 reconciled (was Sprint-34's theme) + filled. shape12/13/fawley fixtures correctly deferred (P1/P2/P3 didn't land). `DAY12_P7_INFRA.md`.

## Day 13 — Final Retest + Closeout — **SPRINT 33 CLOSED** (2026-07-17)
Final KPIs confirmed from the DB (above). Determinism ✅ ×3 (blast radius `sample_mcp.gms` only; all other goldens byte-unchanged since `ee51ed9e`). PR25 re-baseline: genuine floor **75** / methodology 21 / all-219 Match 96. `SPRINT_RETROSPECTIVE.md` authored; Sprint-34 carryforwards filed (`SPRINT_34_CARRYFORWARDS.md`).

---

### Per-priority summary

| P | Track | Disposition |
|---|---|---|
| **P1** | mine head-offset bound-active cross-term | **REPLAN (H3)** — H1 value-invariant (control-refuted) → Sprint-34 head-offset dual subsystem |
| **P2** | sarf three-site symbolic `stat_task` emit | **REPLAN (Option B)** — from-scratch symbolic-emit mode, 20–28h/high-risk for +1 Translate → Sprint 34 |
| **P3** | fawley second-index `sameas` generalization | **H-b** — sameas genuine but non-emit MS-5 divergence; the correction (constraint-index diagonal) deferred → Sprint 34 |
| **P4** | camcge dual-consistent Walras | Epic-5-deferred (step 1 on `main` since S32) |
| **P5** | rocket + hhfair/CGE Case-c forcing | hand-off + survey (0 floor); rocket → Sprint-34 PATH consultation |
| **P6** | failure-cohort re-triage | **✅ sample +1 Solve / +1 Match / +1 genuine floor** (pruned-var `.l`-init fix). agreste (scenario driver), ganges/gangesx (`$141/$145/$149` root) banked. |
| **P7** | infrastructure | sample regression fixture + floor 74→75 recompute + SUMMARY row-33 |

### Targets vs actual (`PROJECT_PLAN.md` §"Sprint 33")

| Target | Result |
|---|---|
| Solve 107 → +1 (conditional P1/P3) | ✅ **108** — via **P6 sample** (P1/P3 REPLAN'd; the mover the honest projection didn't count) |
| genuine floor 74 → ≥ 75 | ✅ **75** (sample genuine cold-emit) |
| Match maintain ≥ 92 | ✅ **93** |
| Translate 135 → +1 (P2) | ✗ maintained **135** (sarf REPLAN, Option B — lowest-leverage) |
| model_infeasible ≤ 7 | ✅ **7** |
| Determinism ×3 | ✅ |
| Tests | ✅ 5,034 passed (+ the P7 fixture) |

**Net:** the Task-9 **modal flat-KPI** projection held for the three deep tracks (all control-refuted), **but P6 — the designated best-remaining-shot — delivered the +1 Solve / +1 Match / +1 genuine floor**, meeting the floor ≥ 75 target. Zero broken code; six precisely-characterized Sprint-34 hand-offs.
