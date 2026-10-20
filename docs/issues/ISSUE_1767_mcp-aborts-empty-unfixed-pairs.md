# ISSUE #1767 — R-EXEC: cold MCP aborts before PATH — data-empty inequality pairs left unfixed (ferts, tabora), unmatched corner fix pairs (minsurf)

**GitHub:** [#1767](https://github.com/jeffreyhorn/nlp2mcp/issues/1767) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 4 (2026-10-20), routed, not fixed in place

**Route:** R-EXEC (Sprint 40 P2/P3 routing note) · **Models:** `ferts`, `tabora` (MCP-gated), `minsurf` (NLP-gated, admitted by rule) · **Measured at:** `de0a7186`, GAMS 54.2.1 licensed

## Fingerprint (reproduced; the execution-error lines captured this time, sanitized)

Each cold MCP aborts **before PATH reports** (`path_solve_terminated`, `NO-SOLVE`). The committed golden, compiled and run licensed:

| model | abort | the error, from the listing |
|---|---|---|
| `ferts` | `SOLVE from line 546 ABORTED, EXECERROR = 36` | 36× `MCP pair comp_mb.lam_mb has empty equation but associated variable is NOT fixed`, e.g. `lam_mb(nitr-acid,assiout)` |
| `tabora` | `SOLVE from line 295 ABORTED, EXECERROR = 36` | 36× `MCP pair comp_lb.lam_lb has empty equation but associated variable is NOT fixed`, e.g. `lam_lb(y01,jun)` |
| `minsurf` | `SOLVE from line 415 ABORTED, EXECERROR = 4` | 4× `MCP pair v_fx_<corner>.nu_v_fx_<corner> has unmatched equation` for the corners `x0_y0`, `x0_y26`, `x51_y0` and `x51_y26` (and `984 fixed-and-unmatched column(s) will be treated as constant`) |

The `--nlp-presolve` residual runs abort the same way: `ferts` `EXECERROR = 46`, `tabora` `36`.

## Two shapes

1. **`ferts`, `tabora`: data-empty inequality instances whose multiplier is left free.**
   - `mb(c,i)` (ferts) and `lb(t,m)` (tabora) are unconditioned in the source.
   - For some instances **no variable survives the data**: every term is conditioned out (`ppos`, `cposi`, `cposr`, `cposd` in ferts) or multiplied by a zero coefficient (tabora's `lb`, which is unconditioned). GAMS then sees a constant row. Which data zeroes each listed instance is to confirm.
   - GAMS drops such a row from the NLP, but an MCP must pair it, so the multiplier has to be fixed: `lam_mb.fx(c,i)$(<row empty>) = 0`.
   - Same class as #1041 (cesam2) and the completed ISSUE_1021 (spatequ).
2. **`minsurf`: the four boundary corners.** The corners lie on two fixed edges, and their per-element fix equations `v_fx_<corner>` end up unmatched.
   - **First step:** check whether the corner `v` is fixed twice (once per edge), leaving its `nu_v_fx_<corner>` pair with nothing to match.
   - Its stationarity is wrong independently: see R-B-minsurf (#1771).

## Fix surface

The emitter's empty-instance handling for inequality multipliers ("Fix inactive variable instances"). For minsurf, the per-element `.fx` equation emission at a doubly-fixed point.
