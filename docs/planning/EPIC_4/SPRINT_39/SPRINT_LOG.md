# Sprint 39 — Sprint Log

**Weeks 43–44** *(project-relative, not ISO)* · **Days 0–13 = 2026-09-03 … 2026-09-16**
Plan: `PLAN.md` · prompts: `prompts/PLAN_PROMPTS.md`

---

## Day 0 — 2026-09-03 · P1: the floor-classification decision · 6 h

**Branch:** `planning/sprint39-day0-floor` · **Measured at:** `388082b0` · **No production code changed (`src/`, `tests/` untouched); `*.py` under `docs/` did change, so the quality gate was run — see below**

### Baseline, re-derived at execution time (close rule C5)

| quantity | value |
|---|---|
| convex candidates | 142 |
| Parse | 142 |
| Translate | **135** |
| Solve | **111** |
| Match | **96** (65 cold + 31 presolve) |
| model_infeasible | 7 |
| path_syntax_error | 6 |
| **`path_solve_terminated`** | **0** |
| path_solve_license | 11 |
| all-219 Match | 99 |
| **genuine floor** | **73 → 75** *(decided today)* |

Derived by `scripts/sprint_audit/kpi_block.py` and `floor_tracker.py`, not recalled.

### ✅ DECISION 1 — the genuine floor is **75**

**Owner decision, taken 2026-09-03.** Both `twocge` and `elec` owe provenance entries; `data/floor_provenance.json` now carries them with `expected_floor` **75**, and `floor_tracker.py` agrees (it exits non-zero on divergence).

**Every figure the brief rests on was re-verified before applying it**, because the brief was measured at `8a5a88bc` and close rule C5 requires derivation at execution time. Nothing had moved — **0 commits to `src/`, to the goldens, or to the DB** since — and all three cold solves reproduce exactly:

| model | cold status | cold objective | NLP | cold match? |
|---|---|---|---|---|
| **twocge** | **MS-1 Optimal** | **55.508** | 56.7778 | ✗ (−2.2 %) |
| **elec** | **MS-1 Optimal** | **244.624** | 243.8128 | ✗ (+0.33 %) |
| **polygon** *(the precedent)* | **MS-5 Locally Infeasible** | 0.766 | 0.7797 | ✗ |

And the convexity/corpus facts that decide the case: `polygon`, `twocge` and `elec` are all **`likely_convex` and in-corpus**; the `non_convex` `ps2_f_s` / `ps2_s` / `ps3_s_gic` are all **out-of-corpus** — the three the 2026-08-18 re-baseline removed.

**The reasoning applied.** The written definition classifies *methodology* as "cold emit byte-identical to pre-fix". Both models fail that test — each had its cold emit changed by a real fix, each was aborting beforehand (`path_solve_terminated`, `solver_version: None`), each MCP now produces its own status, and each matches via the presolve warm start, which the definition explicitly admits as genuine. `polygon` is the in-corpus precedent of identical shape. **Sprint 38 Day 9 applied the wrong test** ("matched via presolve ⇒ methodology"), which is what produced the flat-73 report.

**Consequence:** Sprint 39 opens at **floor 75**. "No floor regression" means **≥ 75**. Sprint 38's close record re-reads **73 → 75 (+2)**.

**Downstream sites updated in this change:** `data/floor_provenance.json` (2 entries + `expected_floor`), `SUMMARY.md` (the S38 row and its open-decision note), `PROJECT_PLAN.md` (P1's deliverable), `SPRINT_39/PLAN.md` (baseline + acceptance criterion).

### ✅ DECISION 2 — P4 takes **branch B** (re-scope)

**Owner decision, taken 2026-09-03**, on Task 6's measurement: the four call sites are **0.5 %** of wall-clock, `gradient.py:453` is **dead code**, and **70.9 %** sits in `compute_constraint_jacobian` — a path Sprint 38 Day 7 already changed.

Days 7–8 become **diagnosis of the differentiation path plus a Phase-0 gate for it**. **No implementation this sprint.** P4 drops **26 h → 11 h**.

**Where the freed 15 h went.** P5 and P10 each rose to the **top of their own estimates** (13 → 16 h, 14 → 16 h), absorbing **5 h**. The remaining **10 h returned to slack** — neither can take more without exceeding its band, and inflating a track to spend a budget is what P10 exists to prevent. **Sprint total 140 h → 130 h**, heaviest day 11 h.

**⚠ Consequences, both pre-registered:**
- **C6 is VOID.** Translate reports **135 flat**, naming the re-scope.
- **The sprint has no upward KPI mover.** Its only KPI movement is P7's Match **96 → 95**, a *correction* (C2). That is the honest shape given P4's premise was refuted, not an underperformance.

**⚠ C6's precondition was also corrected today.** It read *"P4 branch A or B started"* — but branch B explicitly does not implement, so it can never produce a golden. Fixed before the sprint runs rather than discovered at close, which is exactly what 8c's precondition discipline is for.

### Gate

- `floor_tracker.py` → **75**, agreeing with the recorded decision, **exit 0**
- `artifacts/validate_plan.py` → **PLAN VALIDATES** after the re-budget
- `make check-doc-figures` → clean
- Quality gate **RUN, not waived** — `src/` and `tests/` are untouched, but `artifacts/validate_plan.py` was extended during review, and it is `*.py`. typecheck / format / lint clean; `make test` **5301 passed / 10 skipped / 1 xfailed**.
  - ⚠ This line originally read *"N/A — no `*.py` changed"*, which was **true when Day 0 was written and false by the time the PR merged** — the review rounds added the validator. The waiver test is now stated over `src/`/`tests/`, which a review round cannot invalidate. Same aging-out class as the banked-staleness findings: **a claim about a PR's contents must be re-read against the PR's final file list, not its first commit.**

---
