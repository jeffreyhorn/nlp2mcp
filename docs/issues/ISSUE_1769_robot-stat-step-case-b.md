# ISSUE #1769 — R-B-robot: case_b at stat_step (rel 10.1) — confirmed member of the Sprint 40 P5 stat_step class

**GitHub:** [#1769](https://github.com/jeffreyhorn/nlp2mcp/issues/1769) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 4 (2026-10-20), routed, not fixed in place

**Route:** R-B-robot (Sprint 40 P2 routing note) → **Sprint 40 P5** (the `stat_step` class) · **Model:** `robot` (MCP-gated, COPS) · **Measured at:** `de0a7186` (Day 3 batch `f1771435`), GAMS 54.2.1 licensed

## Fingerprint (reproduced)

- **Outcome:** `model_infeasible` (MS 5), `MCP-FAILED`. The presolve retry is also MS 5.
- **`kkt_residual.py`: `case_b`.** The dual transfer is consistent (max equality residual 1e-14) and the dual scale is 6.65.

| row | raw residual | relative |
|---|---|---|
| **`stat_step`** | 67.37 | **10.13** |
| `stat_the(h0)` | 1.369 | 0.206 |
| `stat_rho(h0)` | -1.181 | 0.178 |
| `stat_rho(h50)` | -1.144 | 0.172 |

## Routing

- **robot's worst row is `stat_step`, the same row as lnts** (relative 9.66 with lnts's collision removed; `LNTS_LANDABILITY.md`).
- That makes robot one of the **two confirmed members** of the `stat_step` emit class, which is P5's object this sprint: COPS time-step models with `tf =e= step*nh`.
- P5's REPLAN rule applies: if the lnts and robot `stat_step` rows do not share a mechanism under a per-row trace, split them and land nothing on a guessed shared cause.
- The secondary `h0` rows (`stat_the`, `stat_rho`) are boundary-time terms. Re-measure them after P5 before treating them as a separate defect.

**Not fixed in place.**
