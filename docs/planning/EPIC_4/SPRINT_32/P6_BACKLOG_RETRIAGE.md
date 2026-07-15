# Sprint 32 Day 11 — P6 Adjacent-Backlog Re-Triage (offset-alias + failure-cohort)

**Date:** 2026-07-15
**Day:** 11 (Priority 6 — adjacent backlog + REPLAN-slack, #1111/#1112 generalization + failure-cohort)
**Outcome:** 🟡 **Cohort re-triaged with banked diagnoses; no clean in-sprint +Solve/floor; no `src/` change.** The deliverable ("≥ 1 model recovered **OR** the cohort re-triaged") is met via the re-triage — including a **control-confirmed 96%-diagnosed fawley emit bug** handed to Sprint 33.
**Discipline:** every candidate probed with the harness + a `/tmp` control **before** any `src/` change (PR24/PR27).

---

## 1. Offset-alias generalization (§2) — no gain: the candidates already solve / are emit-correct

The Task-10 §2 structural audit surfaced polygon-family distance-shape candidates. The harness + DB re-triage shows they are **not** offset-alias-fix opportunities:

| Candidate | DB solve | harness | Verdict |
|---|---|---|---|
| **cpack** | `success` | **CASE_A** (residual 1.4e-17) | Already solves **and** emit-correct — the core is a no-op. |
| ps5_s_mn / ps10_s_mn / partssupply | `success` | (convex, solves) | Already solve — no +Solve; no dropped cross-term to convert. |
| ps3_s_scp | `success` | — | `non_convex` (out of the 142-candidate corpus). |

**The landed #1111/#1112 core already covers these** (cpack's distance shape emits a correct `stat_x`, CASE_A). The offset-alias generalization yields **no genuine-floor gain** — the structural-audit candidates were false leads (structural shape ≠ a dropped cross-term).

## 2. Failure-cohort (§3) — fawley: a real emit bug, 96%-diagnosed, but a deeper generalization

**fawley** (`solve=failure`, `verified_convex`, LP optimum **2899.25**) is a genuine CASE_B (`stat_bq(*,fuel-oil)` rel 0.973, raw +473, duals CONSISTENT). **Root cause (found + control-confirmed):** `bq(c,cf)` appears in `qsb(cfq,l,s)` and `pbal(cfq,m)` as `bq(c,cfq)` — the **#1111/#1112 second-index-transpose shape** (the equation's first index `cfq` must equal `bq`'s second index `cf`). The emitted `stat_bq` applies the second-index restriction `$(sameas(cfq__, cf))` to the **mbal** cross-term but **NOT** to the **qsb / pbal** cross-terms — they sum `nu_qsb(cfq__,l,s)` / `nu_pbal(cfq__,m)` over **all** `cfq__`, over-counting. The landed core covers the mbal-shape (variable's *first* index = equation index) but leaks on the qsb-shape (variable's *second* index = equation index).

**`/tmp` control (PR27, before src):** patch the qsb/pbal multipliers with `$(sameas(cfq__, cf))` →

| | `max|stat_bq|` (warm, iterlim=0) | MCP solve |
|---|---|---|
| original | **473.412** | MS-5 @ profit 6862 |
| **+ sameas patch** | **18.468** (473 → 18, **96% closed**) | MS-5 @ profit 5739 |

So the diagnosis direction is **right** (the sameas gap is the primary bug), but the fix is **incomplete**: a residual 18.47 remains, and the patched MCP still diverges (MS-5 @ 5739, **not** the LP optimum 2899.25). fawley is a **deeper AD-core generalization + LP-convergence issue**, not a bounded in-sprint change — the Task-9-flagged "#1111/#1112 gate leaks" REPLAN risk, confirmed empirically.

**agreste** (`solve=failure`, `verified_convex`, CASE_B `stat_sales` rel 2.0) — a **double-`solve` scenario driver** (Task 10 scope caveat). With fawley (the cleaner candidate) not yielding a bounded fix, agreste's scope-verification + likely-similar-depth fix is lower-value; **re-triaged** (banked). **cesam / lnts** stay banked genuine Case-c (bilinear SAM / bilinear-`step` optimal-control) per Task 10.

## 3. Disposition + Sprint-33 hand-off

- **No `src/` change.** The offset-alias core is a no-op on the §2 candidates (already correct); the fawley fix is incomplete (96% of `stat_bq`, MCP still diverges) + high-blast-radius (the general cross-term emit) — a Sprint-33 workstream, not a Day-11 landing.
- **The de-risked Sprint-33 hand-off (fawley):** the precise, control-confirmed diagnosis — the qsb/pbal `stat_bq` cross-terms need the `sameas(cfq__, cf)` second-index restriction the mbal term already has (closes 473 → 18); a secondary `stat_bq` residual (18.47) + the MS-5 LP-convergence remain to diagnose. The #1111/#1112 core's second-index gate must extend from the variable's-first-index shape to the variable's-**second**-index-summed shape.
- **REPLAN-slack absorption:** the freed mine/camcge/sarf budget flowed here (P6) per Task 9; with P6 not landing a bounded gain, the residual flows to **P7** (Day 12 — property fixtures + genuine-floor tracking + Epic-4-SUMMARY groundwork).
- **KPI impact:** **no headline gain** — Solve 107 / Translate 135 / genuine floor 74 hold at Day-0. Sprint 32's realized value is the two genuine landings (camcge step-1 scalar-`fx` emit fix; the P5 Case-c classifier) + the banked de-risked diagnoses (mine 5th-coupling, camcge Walras/Epic-5, sarf symbolic-emit, fawley qsb/pbal sameas, rocket PATH-consultation).

## 4. Evidence

`kkt_residual.py` on cpack (CASE_A) / fawley (CASE_B `stat_bq` 0.973); the DB `model_id` solve status; GAMS 53 on the `/tmp` fawley controls — raw LP MS-1 @ 2899.25; original presolve MS-5 @ 6862 (`max|stat_bq|` 473.4); the sameas-patched presolve MS-5 @ 5739 (`max|stat_bq|` 18.47). Anchor `4cbf8bff`. See `TOOLING_AND_BACKLOG_ANALYSIS.md` §2–§3.

---

**Document Created:** 2026-07-15
**Owner:** Sprint 32 execution (AD/emit specialist)
