# ISSUE #1766 — R-PRE-140: presolve dual transfer initializes multipliers the MCP never declared ($140) — egypt (#1755 drop), srpchase (#1385 drop)

**GitHub:** [#1766](https://github.com/jeffreyhorn/nlp2mcp/issues/1766) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 4 (2026-10-20), routed, not fixed in place

**Route:** R-PRE-140 (Sprint 40 P2 routing note) · **Models:** `egypt`, `srpchase` · **Measured at:** `de0a7186`, GAMS 54.2.1 licensed

## Fingerprint (reproduced)

Both `--nlp-presolve` emits fail compile with `$140 Unknown symbol` ×2 + `$257`. The unknown symbols are multipliers initialized by the presolve dual-transfer block (`* Transfer NLP duals to MCP multiplier initialization`, `src/emit/emit_gams.py` ~L1648) that **the MCP never declares**:

| model | unknown symbols | source equations | in the cold golden? |
|---|---|---|---|
| `egypt` | `lam_landb(r,tm)`, `lam_waterb` | `landb(r,tm)`, `waterb` (`=l=`) | **absent**: no equation, no multiplier |
| `srpchase` | `nu_slack(srn)`, `lam_demand(srn)` | `slack(srn)$(not leaf(srn))`, `demand(leaf(srn))` | **absent**: no equation, no multiplier |

So the `$140` is a **symptom**. The transfer block iterates the source equations rather than the multipliers the MCP declares. Two different upstream defects drop the equations:

1. **`egypt` — #1776, an AD defect found by this routing (a sibling of #1755, Sprint 40 P7).**
   - `landb(r,tm).. sum((c,z)$zr(z,r), xcrop(r,c)*land(c,z,tm)) =l= …` gets **0 Jacobian entries** (60 rows), and `waterb` gets 0 (1 row).
   - **Traced:** `_diff_sum` (`src/ad/derivative_rules.py`) takes equal binder/index counts (`(c,z)` against `xcrop(r,c)`) as positional correspondence, because its partial-match branches are gated on `>` and `<`. A 10-line reproducer is in #1776.
   - ⚠ **`labbal` loses its `xcrop` terms the same way, silently:** the committed `stat_xcrop(r,c)` carries only `lam_comb` and `lam_vegetb`. `labbal` survives only because its RHS has the variables `tlab` and `flab`.
   - So egypt's cold `model_infeasible` has an AD cause **in addition to** the Class-A `tranc(rp,rp)` that P4 owns.
2. **`srpchase` — the #1385 short-circuit.**
   - The translate warns `Equation 'slack' / 'demand': skipping AD enumeration of the #1385 dynamic-subset Cartesian blow-up shape`, and both constraints vanish.
   - Without `demand`, the cold MCP "solves" at **objective 0** against an NLP of 0.4001.
   - These are the same `nu_slack` / `lam_demand` multipliers that #1385 describes. That short-circuit is Sprint 40 P6's surface (sarf).

## Fix surfaces

- **Symptom (small, independent):** the dual-transfer block should emit `.l` initializers only for multipliers in the MCP's declared set (the S33 `_declared_mcp_vars` pattern). That turns a compile failure into a runnable presolve, which unblocks `kkt_residual.py` for both models.
- **egypt:** #1776 (with P7 / #1755). Re-run egypt after it lands.
- **srpchase:** #1385 (P6).

⚠ Fixing only the symptom would make both presolve emits run while still missing the constraints. Do not book a match from it without `kkt_residual.py`.
