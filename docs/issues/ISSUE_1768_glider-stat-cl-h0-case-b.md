# ISSUE #1768 — R-B-glider: case_b emit bug, stat_cl(h0) worst row, relative residual 2.0 on the global dual scale (stat_step second; P5 candidate)

**GitHub:** [#1768](https://github.com/jeffreyhorn/nlp2mcp/issues/1768) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 4 (2026-10-20), routed, not fixed in place

**Route:** R-B-glider (Sprint 40 P2 routing note) · **Model:** `glider` (MCP-gated, COPS) · **Measured at:** `de0a7186` (Day 3 batch `f1771435`), GAMS 54.2.1 licensed

## Fingerprint (reproduced)

- **Outcome:** `model_optimal_presolve` (MS 1), **mismatch**: MCP 1286.9774 against NLP 1282.3997 (rel 3.6e-3). `MCP-SOLVED`.
- **`kkt_residual.py`: `case_b` (emit bug).** The dual transfer is consistent (max equality residual 4e-12) and the dual scale is 129.2.

| row | raw residual | relative |
|---|---|---|
| `stat_cl(h0)` | 258.4 | **2.000** |
| `stat_step` | -49.17 | 0.381 |
| `stat_vel(x,h50)` | -30.19 | 0.234 |
| `stat_cl(h10)`, `stat_cl(h11)` | 17.8 | 0.137 |

## Reading

- **How to read 2.000 (corrected in PR #1777 review).** `kkt_residual.py` normalizes every row by **one global dual scale**: the largest transferred multiplier magnitude, floored at 1 (129.2 here). The relative 2.000 is raw 258.4 over that scale, not over the magnitude of any term in `stat_cl(h0)`. **It does not by itself establish a doubled or sign-flipped term.**
- *Hypothesis, pending the per-row derivative trace:* an initial-condition or boundary term at the **first** time point emitted twice, or with the wrong sign. The concentration at `h0`, with `h10`/`h11` at 0.137, points that way, but it is not evidence of the mechanism.
- **`stat_step` is second.** glider is one of P5's two unconfirmed `stat_step` candidates (`KNOWN_UNKNOWNS.md` 5.x; lnts and robot are the confirmed pair). If P5's fix lands, re-measure glider before tracing `stat_cl(h0)`: the two may interact through `step`.

## First step

Trace `stat_cl(h0)`'s terms against a hand derivative at `h0`: is any term missing, doubled or sign-flipped? Then check whether `stat_step` reproduces P5's mechanism.

**Not fixed in place** (P10's rule: route, then fix with a Phase-0 gate).
