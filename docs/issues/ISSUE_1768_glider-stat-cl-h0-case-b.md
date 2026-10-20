# ISSUE #1768 — R-B-glider: case_b emit bug, stat_cl(h0) relative residual exactly 2.0 (stat_step second; P5 candidate)

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

- **`stat_cl(h0)` at exactly 2.000** looks like a doubled or sign-flipped term at the **first** time point. That is the shape of an initial-condition or boundary term emitted twice, or with the wrong sign.
- **`stat_step` is second.** glider is one of P5's two unconfirmed `stat_step` candidates (`KNOWN_UNKNOWNS.md` 5.x; lnts and robot are the confirmed pair). If P5's fix lands, re-measure glider before tracing `stat_cl(h0)`: the two may interact through `step`.

## First step

Trace `stat_cl(h0)`'s terms against a hand derivative at `h0`: which term is doubled? Then check whether `stat_step` reproduces P5's mechanism.

**Not fixed in place** (P10's rule: route, then fix with a Phase-0 gate).
