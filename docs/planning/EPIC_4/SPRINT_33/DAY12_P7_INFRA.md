# Sprint 33 — Day 12: P7 infrastructure

**Date:** 2026-07-17 · **Day:** 12 · **Branch:** `planning/sprint33-day12-p7-infra`
**Scope:** the P7 items that apply given the sprint's actual landings — a regression fixture for the P6 sample fix, the genuine-floor tracking recompute (74 → 75), and the Epic-4 `SUMMARY.md` row-33 continuation. The shape12/shape13/fawley property fixtures are **correctly deferred** (their P1/P2/P3 fixes did not land). Tests-only + docs.

---

## 1. Property fixture — the one fix that landed (P6 sample)

The prep plan scoped **shape12** (head-offset, guards P1), **shape13** (sarf symbolic, guards P2), and a **fawley 2-D second-index** fixture (guards P3), each "**only once its fix landed**". **None of P1/P2/P3 landed** (mine REPLAN'd, sarf REPLAN'd, fawley H-b) → those three fixtures are correctly **not added** (a fixture that can't fail-before guards nothing — the Sprint-28 lesson).

The genuine emit fix that **did** land — the P6 sample pruned-variable `.l`-init guard — gets its regression fixture: **`tests/integration/emit/test_sample_pruned_var_l_init.py`**. It emits `sample.gms` and asserts the pruned original-formulation variable `n` is **not referenced** (`\bn\.l\b` absent) while the reciprocal primal `nr` still gets its stationarity (`stat_nr`). **Verified fail-before/pass-after:** with the guard neutralized (pre-fix behavior) the test **fails** (`n.l` reappears); with the fix it **passes**. Skips when the gitignored raw `sample.gms` is absent (CI-safe), following the `test_1374_robot_l_init_dedup.py` pattern.

## 2. Genuine-floor tracking recompute — 74 → **75**

The Day-0 anchor was **74** (`BASELINE_METRICS.md` §4: genuine 74 / methodology 21 / all-219 Match 95). The **P6 sample landing is a genuine cold-emit correction** — the corrected *cold* MCP matches the NLP optimum (726.679), not a presolve/methodology recovery — so it advances the **genuine floor to 75**, meeting the Sprint-33 ≥ 75 target.

| Partition | Day-0 | Sprint-33 close |
|---|---|---|
| Genuine, stable (floor) | 74 | **75** (+1: sample cold-match) |
| Methodology-recovered | 21 | 21 (unchanged) |
| As-measured (all-219) Match | 95 | **96** (+1: sample) |
| 142-corpus Match (as-measured) | 92 | **93** (+1: sample) |

The +1 is genuine (not methodology): sample was `path_syntax_error` (no prior match at all); the emit fix produces a cold MCP that solves and matches. `--resolve-changed` re-confirmed clean with the blast radius = sample only (the checkpoint targets are unchanged — no new emit sites beyond `sample_mcp.gms`).

## 3. Epic-4 `SUMMARY.md` row-33 continuation

Row 33 previously read `| 33 | 31–32 | PATH author consultation & solution forcing | (planned) | — | — |` — the **theme was Sprint 34's** (the renumbered PATH-consultation sprint). Reconciled + filled in the rows-28–32 format:
- **Theme:** "S32 carryforward — mine cross-term, sarf symbolic-emit, fawley 2nd-index, camcge Walras [Epic 5], rocket/Case-c".
- **Headline KPIs:** Solve 107 → **108** / Match 92 → **93** / **floor 74 → 75 (+1)** · path_syntax_error 8 → 7.
- **Firm landing:** P6 sample pruned-var `.l`-init fix (genuine cold-emit → +1 Solve/Match/floor).
- **REPLAN'd → carryforward:** mine [H1 value-invariant → S34 head-offset dual] · sarf [symbolic-emit → S34] · fawley [H-b; sameas + bound-transfer → S34] · camcge [Walras → Epic 5] · rocket [PATH → S34] · agreste/ganges/gangesx [banked].

## 4. REPLAN-slack — the freed budget's realized use

Per the Task-9 reallocation order (P6 → P7 → rocket tail), the budget freed by the P1/P2/P3 REPLANs flowed to **P6** — which delivered the sprint's only in-sprint bucket move (sample). P7 lands this fixture + the tracking recompute + the SUMMARY continuation. The residual banked follow-ons (Sprint-34 hand-offs: the mine head-offset dual, the sarf symbolic-emit subsystem, the fawley sameas + the max-convention bound-transfer track; plus the ganges/gangesx `$141/$145/$149` root and the agreste CASE_B scope-verify) are documented, not in-sprint.

---
**Document Created:** 2026-07-17 · **Owner:** Sprint 33 execution (Day 12) · P7 fixture + floor 74→75 + SUMMARY row-33.
