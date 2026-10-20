# ISSUE #1771 — R-B-minsurf: case_b at stat_v (rel 40.2), outer sum((i,j)) over terms that do not depend on i,j

**GitHub:** [#1771](https://github.com/jeffreyhorn/nlp2mcp/issues/1771) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 4 (2026-10-20), routed, not fixed in place

**Route:** R-B-minsurf (Sprint 40 P3 routing note) · **Model:** `minsurf` (NLP-gated, admitted by rule Sprint 40 Day 3) · **Measured at:** `de0a7186`, GAMS 54.2.1 licensed

## Fingerprint (reproduced)

- **Outcome:** `path_solve_terminated`: the cold MCP aborts before PATH (R-EXEC #1767, `EXECERROR = 4`, the four corner `v_fx_*` pairs).
- **`kkt_residual.py`** (presolve emit): **`case_b`**. The dual transfer is consistent and the dual scale is 1.0.

| row | relative |
|---|---|
| `stat_v(x39,y6)`, `stat_v(x12,y20)` | **40.18** |
| `stat_v(x39,y20)`, `stat_v(x12,y6)` | 30.06 |
| `stat_v(x12,y7)` | 26.84 |

This reproduces Prep Task 7 (`stat_v(x39,y6)` rel 40.2). The worst rows are **symmetric pairs about the grid centre**, so the error is structural, not numerical noise.

## Reading

`stat_v(nx,ny)` wraps its terms in **`sum((i,j), … * 1$(nx(i) and ny(j)))`**, but the terms reference `v(nx±1,ny)` and `v(nx,ny±1)`, not `i`/`j`.
- Read literally, that multiplies each term by the number of `(i,j)` pairs in `nx × ny`: an over-count of order `card(nx)·card(ny)`.
- The same outer sum appears in jbearing's `stat_v` (R-JB-171, #1770), where it sits beside an index collapse.

## First step

Hand-derive `∂/∂v(x39,y6)` of `defsurf` and compare it term by term with the emitted row. Confirm or refute the outer-sum over-count before anything else, then check whether it is the shape elec's Sprint 38 fix removed ("spurious outer sum").

**Not fixed in place.**
