# ISSUE #1770 — R-JB-171: jbearing stat_v body collapses v(nx,ny) to v(nx,nx) ($171 domain violation)

**GitHub:** [#1770](https://github.com/jeffreyhorn/nlp2mcp/issues/1770) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 4 (2026-10-20), routed, not fixed in place

**Route:** R-JB-171 (Sprint 40 P3 routing note) · **Model:** `jbearing` (NLP-gated, admitted by rule Sprint 40 Day 3) · **Measured at:** `de0a7186`, GAMS 54.2.1 licensed

## Fingerprint (reproduced)

- **Outcome:** `path_syntax_error`. The cold golden fails compile with `$171 Domain violation for set` ×3, then `$257`/`$141`. The `--nlp-presolve` residual fails the same way, so `kkt_residual.py` has no verdict.
- **The violating references are an index collapse in the stationarity body.** `stat_v(nx,ny)` contains:

  ```gams
  stat_v(nx,ny).. sum((i,j), hx*hy/12*(wq(nx) + 2*wq(nx+1)) * (2*(v(nx+1,nx) - v(nx,nx))/hx*… + 2*(v(nx,ny+1) - v(nx,nx))/hy*…) * 1$(nx(i) and ny(j)) - …
  ```

  `v(nx+1,nx)` and `v(nx,nx)` should be `v(nx+1,ny)` and `v(nx,ny)`. **The second position takes the first position's index.** GAMS rejects `v(·,nx)`, because the second domain is `ny`'s.

## Class (a hypothesis, not traced)

The shape matches the **repeated-index family** (Sprint 39 Task 7; #1737, #1741 Pattern C B-3): an index resolved positionally, collapsing one position onto another. The writing builder has not been traced, so treat the classification as a lead.
- `check-index-repeats` P1 checks emitted **heads** only, so it cannot see this in a body.
- P2 checks `$(…)` guards, not references.

There is also an **outer `sum((i,j), …)` around terms that do not depend on `i`/`j`**, carrying a `1$(nx(i) and ny(j))` indicator. minsurf has the same shape (R-B-minsurf, #1771). It may be the spurious-outer-sum pattern elec's Sprint 38 fix removed.

## First step

Find which builder writes `v(nx,nx)`: the offset-neighbour rewrite of `v(i+1,j)` under the `nx(i)`/`ny(j)` restriction. Check it against minsurf, which shares the construction (COPS `minsurf` vs `jbearing`).

**Not fixed in place.**
