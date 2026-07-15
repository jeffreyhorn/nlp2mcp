# EPIC 4 — Sprint-by-Sprint Summary (SKELETON)

**Status:** 🚧 Groundwork skeleton (begun Sprint 32 Day 12, 2026-07-15 — S30-retro §5 front-loading recommendation). One row per Sprint 18–35; the KPI columns are filled from the closed-sprint record (SPRINT_RETROSPECTIVE.md / SPRINT_LOG.md per sprint) and completed at Epic-4 close. Cells marked "—" are historical rows to backfill.

**Headline KPI convention:** Solve / Match / genuine floor are over the **142 convex-candidate corpus** (`reference_match_kpi_corpus_scope`); "genuine floor" = cold-emit-correct genuine matches (vs presolve-recovered methodology). Anchors: S32 close DB byte-unchanged since S31 close `4cbf8bff`.

---

## Sprint-by-sprint

| Sprint | Weeks | Theme | Headline (Solve / Match / genuine floor) | Firm landing(s) | REPLAN'd → carryforward |
|---|---|---|---|---|---|
| 18 | 1–3 | Syntactic validation, emit solve fixes, parse quick wins | — | — | — |
| 19 | 3–4 | Major parse push (lexer/internal errors) | — | — | — |
| 20 | 5–6 | IndexOffset + translation | Parse 127/160 · Solve 29+ (PR #815) | IndexOffset | — |
| 21 | 7–8 | Macro expansion, error triage, solve quality | — | — | — |
| 22 | 9–10 | Solve improvements & solution matching | — | — | — |
| 23 | 11–12 | Solve-rate push & error-category reduction | — | — | — |
| 24 | 13–14 | Alias differentiation & error reduction | — | — | — |
| 25 | 15–16 | Alias-differentiation carryforward & emitter backlog | — | — | — |
| 26 | 17–18 | Pattern-C generalization, Pattern-A reclassification | — | — | sarf `nu_slack("srn")` symbolic-emit (failed) |
| 27 | 19–20 | S26 carryforward — Pattern-C Phase B + AD redesigns | Translate +4 / Solve +2 / Match +3 | cesam2 objgrad-collapse fix | — |
| 28 | 21–22 | S27 carryforward — KKT cross-term correctness + diagnostic/CI tooling | **Match 62 → 92** (+30; ~+7 genuine cross-term, ~+24 presolve-retry broadening) | KKT-residual harness · golden-staleness gate · divergence detector · AD property catalog | — |
| 29 | 23–24 | S28 carryforward — presolve/warm-start robustness, cold-convex convergence | Solve 107 / Match 92 / floor 69 | `_fx_` warm-start (#1462) · maxmin objvar · catmix | all headline movers REPLAN'd; DB byte-unchanged |
| 30 | 25–26 | S29 carryforward — head-offset emit arch + non-convex forcing | Solve 107 / Match 92 / floor 70 | robert obj-grad fix (+1 floor) · `--force` scaffold | mine / rocket / polygon / hhfair / camcge |
| 31 | 27–28 | S30 carryforward — head-offset IR plumbing, #1111/#1112, dual-consistent CGE | Solve 107 / Match 92 / **floor 74 (+4)** | head-offset IR foundation · P2 offset-alias #1111/#1112 (polygon +4 floor) | mine [4th site] · camcge [Epic 5] · sarf [369K] · hhfair [Case-c] · rocket [PATH] |
| 32 | 29–30 | S31 carryforward — mine 4th site, sarf 4-D, camcge Walras, rocket/Case-c | Solve 107 / Match 92 / **floor 74** (no headline gain) | camcge step-1 scalar-`fx` emit fix (`stat_mps`→Case-a) · P5 objective-defining Case-c classifier (`case_c_objdef`, ISSUE_1236 closed) | mine [5th coupling→S33] · camcge Walras [Epic 5] · sarf [symbolic-emit→S33] · fawley [qsb/pbal sameas, 96%→S33] · rocket [PATH input finalized] |
| 33 | 31–32 | PATH author consultation & solution forcing | (planned) | — | — |
| 34 | 33–34 | Quality, performance & PATH-feedback integration | (planned) | — | — |
| 35 | 35–36 | v2.0.0 release & Epic 5 planning | (planned) | — | — |

## Cross-epic threads (to expand at Epic-4 close)

- **The genuine-floor ramp** (S30 70 → S31 74 → **S32 74** [≥ 75 missed]): advances **only** via emit-changing cold-matches (S31's polygon +4), never presolve-methodology reclassification — the Sprint-30 §3 / Sprint-31 §3 conditionality lesson. S32's movers (mine/camcge cold-match, P6 emit) all REPLAN'd/re-triaged.
- **The control-first REPLAN discipline** (PR24/PR27): S29–S32 REPLAN'd most deep tracks *before* any bad ship, via the KKT-residual harness + `/tmp` controls. S32 REPLAN'd mine/camcge/sarf/fawley on control evidence (no broken emit shipped); each hands a de-risked, control-confirmed diagnosis to the next sprint.
- **The banked-diagnosis pipeline**: each REPLAN produces a precisely-pinned root cause (mine 5th-coupling wrong-sign `N`; camcge Walras residual-singularity; sarf 369K task-column enumeration; fawley qsb/pbal `sameas` gap [473→18]) → the next sprint implements against a specification, not an open question.

---

**Document Created:** 2026-07-15 (Sprint 32 Day 12 — skeleton)
**Owner:** Epic 4 lead
