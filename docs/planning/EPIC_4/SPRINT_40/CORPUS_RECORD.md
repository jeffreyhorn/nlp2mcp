# Sprint 40 — the corpus record (P3, Decision 2 = A)

**Derived at `de0a7186`** (`main`, clean DB) with `scripts/sprint_audit/kpi_block.py --corpus continuity|current`. Every figure below comes from that tool at that commit (close rule C6). Re-derive it; do not copy it forward.

## The two denominators

- **Continuity (140)** is the base series: the re-based 140-candidate corpus (owner decision 2026-10-19, PROJECT_PLAN footnote ⁹). It excludes every id in `data/corpus_admissions.json`. **The headline is on this corpus (C4).**
- **Current (149)** is everything the DB classifies convex and does not skip: 140 plus the 9 models admitted by rule on Day 3 (`191ed91f`).

| quantity | continuity (140) | current (149) | difference: the admitted 9 |
|---|---|---|---|
| candidates | **140** | **149** | +9 |
| Parse | 140 | 146 | +6 |
| Translate | 135 | 139 | +4 |
| Solve | 115 | 117 | +2 |
| Match | 97 | 99 | +2 |
| &nbsp;&nbsp;cold | 65 | 65 | 0 |
| &nbsp;&nbsp;presolve | 32 | 34 | +2 |
| `model_infeasible` | 12 | 12 | 0 |
| `path_syntax_error` | 6 | 7 | +1 |
| `path_solve_terminated` | 2 | 3 | +1 |
| `path_solve_license` | 0 | 0 | 0 |
| all-219 Match (never corpus-scoped) | 102 | 102 | — |

The tool's one-line forms, verbatim:

> Solve 115/135 · Match 97/140 (65 cold + 32 presolve) · Translate 135/140 · mi 12 · pse 6 · all-219 102 — derived at de0a7186 · corpus continuity (140 candidates, 9 admitted)
>
> Solve 117/139 · Match 99/149 (65 cold + 34 presolve) · Translate 139/146 · mi 12 · pse 7 · all-219 102 — derived at de0a7186 · corpus current (149 candidates, 9 admitted)

## The admitted 9, by identity

All 9 were admitted by rule: the licensed verifier classified each one convex (Sprint 40 Day 2), and `apply_convexity_results.py --admit` applied them on Day 3.

| model | classification | reaches | outcome | route |
|---|---|---|---|---|
| `airsp2` | verified_convex | MCP | **match** via presolve (1037.246), `MCP-SOLVED` | ⚠ multi-solve, out of the headline |
| `torsion` | likely_convex | MCP | **match** via presolve (-0.4175), `MCP-SOLVED` | ⚠ multi-solve, out of the headline |
| `jbearing` | likely_convex | MCP | `path_syntax_error` (`$171`) | #1770 (R-JB-171) |
| `minsurf` | likely_convex | MCP | `path_solve_terminated` | #1767 (R-EXEC) + #1771 (R-B-minsurf) |
| `airsp` | verified_convex | — | translate timeout (600 s) | #1775 |
| `msm` | verified_convex | — | translate timeout (600 s) | #1775 |
| `emfl` | likely_convex | — | parse: inline-guarded `$eval` does not define `%new%` (standalone `$eval` is already implemented) | #1772 |
| `indus89` | verified_convex | — | parse: `Singleton Set` unsupported | #1773 |
| `phosdis` | verified_convex | — | parse: `for` statement unsupported | #1774 |

## What the expanded scope may and may not claim

- **A scope addition is never a recovery (C4).** The +2 Solve and +2 Match on `current` exist because the corpus grew, not because anything was fixed.
- **Both matches are presolve-only**, so under C5 they are methodology: not counted in the floor and not in the `license_unlocked` ledger.
- **Both are multi-solve models.** Their comparison stays out of any headline until the multi-solve reference question (Day 3, `SPRINT_LOG.md` P3) is settled: which of the model's solves is the comparison's reference.
- **The headline sentence is Day 5's (C4).** It carries the continuity figure and the expanded figure in one sentence, plus a Rolling-KPIs footnote. This record is its source.
