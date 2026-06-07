# launch: `--nlp-presolve` double-applies self-referential source parameter assignments, corrupting the objective (PATH-numerics mismatch)

**GitHub Issue:** [#1378](https://github.com/jeffreyhorn/nlp2mcp/issues/1378)
**Status:** FIXED (Sprint 27 Day 9, 2026-06-07) — launch `compare_objective_mismatch` (13.3%) → `compare_match`.
**Severity:** Medium — produced a valid-looking `model_optimal_presolve` solve that converged to a 13.3% rel_diff vs the NLP optimum; a silent correctness bug in the warm-start emit, not a solver-tuning gap.
**Date:** 2026-05-12
**Last Updated:** 2026-06-07 (Sprint 27 Day 9 — root cause found + fixed)
**Affected Models:** launch (target); any presolve model whose source performs in-place self-referential parameter assignments (`p = p * f`). cesam has the same shape (`X("total") = sum(ii, X(ii))`) but is blocked by `model_infeasible` separately.

## Problem Summary

launch's cold MCP (`launch_mcp.gms`) solves to MODEL STATUS 5 Locally Infeasible (6194 iters). The pipeline's STATUS-5 presolve-retry (`scripts/gamslib/run_full_test.py`) re-translates with `--nlp-presolve` and recovers MODEL STATUS 1 (`model_optimal_presolve`) — but the recovered objective was **2604.01 vs the NLP reference 2257.80 (13.3% rel_diff → `compare_objective_mismatch`)**.

Root cause: launch.gms adjusts two engine-cost coefficients **in place**:

```gams
pre2('stage-3') = pre2('stage-3')*10**pre3('stage-3');
pre4('stage-3') = pre4('stage-3')*10**pre5('stage-3');
```

The `--nlp-presolve` emit re-emitted these assignments (translated from the source) **and** `$include`d launch.gms for the NLP warm-start. Under `$onMultiR` the `/data/` re-declaration does **not** reset the value, so the adjustment was applied **twice** (`pre2('stage-3')`: −0.001 → −3.95e-5; `pre4('stage-3')`: 52.5 → 165.3). This corrupted the engine-cost term of the objective for **both** the embedded NLP pre-solve and the final MCP, so 2604.01 is the optimum of a *corrupted* model, not a bad local optimum of launch.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/launch.gms \
  -o /tmp/launch_ps.gms --nlp-presolve --skip-convexity-check --quiet
gams /tmp/launch_ps.gms lo=2 | grep -E 'MODEL STATUS'
# Pre-fix: embedded NLP cost=2604.01, MCP cost=2604.01 (vs NLP ref 2257.80)
```

## Phase 0: Acceptance Gate

**Authored:** 2026-06-07 (Sprint 27 Day 9; per CONTRIBUTING PR20 — this PR touches `src/emit/`).
**Target surface:** parameter-assignment emission under `--nlp-presolve` (`emit_computed_parameter_assignments` in `src/emit/original_symbols.py`), NOT a KKT-equation shape. This is a numerics/data-emit bug: the stationarity/complementarity **structure is correct**; only the parameter **values** feeding the (correct) objective gradient were wrong.

### Hand-Derived KKT Shape

The KKT system shape is **unchanged** by this fix — no stationarity, complementarity, or bound equation is added, removed, or re-indexed. The defect is purely in the numeric value of two objective coefficients.

launch minimizes `cost` s.t. the engineering constraints; the objective gradient that enters every `stat_<var>` equation depends on `pre2`/`pre4` through the engine-production-cost term:

```
costdef.. cost =e= ... + sum(s, (pre1(s)*ethrust(s)/1000
                               + pre2(s)*(ethrust(s)/1000)**pre3(s)
                               + pre4(s)*(ethrust(s)/1000)**pre5(s))
                              * (nume(s)*numl)**0.93) + ...
```

The correct coefficients are the **single-application** values: `pre2('stage-3') = -0.01807 * 10**(-1.33) = -0.001`, `pre4('stage-3') = 16.687 * 10**0.498 = 52.526`. With these, the unique KKT/stationary point of launch is the NLP optimum `cost = 2257.7976` (the published GAMSlib solution). This was confirmed to be a **valid MCP fixed point**: warm-starting the MCP from the good NLP optimum (via a GDX hand-off of levels + marginals) → the MCP converges to and **stays at** `cost = 2257.7976` (MODEL STATUS 1). The double-applied coefficients (`pre2 = -3.95e-5`, `pre4 = 165.3`) define a *different* objective whose stationary point is `cost = 2604.01`.

### Expected Emit Pattern

Under `--nlp-presolve` (where the MCP `$include`s the source to run the NLP pre-solve), the MCP must **NOT** re-emit the source's self-referential parameter assignments — the `$include` executes them exactly once:

```gams
* CORRECT presolve emit: no MCP-side pre2/pre4 self-assignment;
* the value is provided once by the $include below.
$onMultiR
$include "data/gamslib/raw/launch.gms"   * runs pre2 = pre2*10**pre3 ONCE
$offMulti
```

The **cold** (non-presolve) emit MUST still emit the assignment (there is no `$include` to apply it):

```gams
* CORRECT cold emit (launch_mcp.gms): the in-place adjustment is present.
pre2("stage-3") = pre2("stage-3") * 10 ** pre3("stage-3");
pre4("stage-3") = pre4("stage-3") * 10 ** pre5("stage-3");
```

The fix gates exactly this: `skip_self_ref_presolve` (True only under `--nlp-presolve`) skips parameter assignments whose LHS symbol appears on the RHS. Mirrors the existing #1330 var-init presolve skip and #1281 redundant-declaration suppression.

### Verification Methodology

```bash
# 1. Presolve emit must OMIT the self-referential assignment, keep the $include.
.venv/bin/python -m src.cli data/gamslib/raw/launch.gms \
  -o /tmp/launch_ps.gms --nlp-presolve --skip-convexity-check --quiet
grep -E 'pre2\("stage-3"\) *= *pre2|pre4\("stage-3"\) *= *pre4' /tmp/launch_ps.gms   # expect: (none)
grep -c '\$include' /tmp/launch_ps.gms                                                # expect: >=1

# 2. Cold emit must KEEP it AND be byte-identical to the committed golden (anchor).
.venv/bin/python -m src.cli data/gamslib/raw/launch.gms \
  -o /tmp/launch_cold.gms --skip-convexity-check --quiet
grep -cE 'pre2\("stage-3"\) *= *pre2' /tmp/launch_cold.gms                            # expect: 1
diff /tmp/launch_cold.gms data/gamslib/mcp/launch_mcp.gms                             # expect: identical

# 3. Presolve solve must reach MODEL STATUS 1 with cost == NLP optimum 2257.7976.
gams /tmp/launch_ps.gms lo=2 | grep -E 'MODEL STATUS'                                 # expect: ... 1 Optimal
.venv/bin/python scripts/gamslib/run_full_test.py --model launch --verbose | grep COMPARE   # expect: [COMPARE] MATCH

# 4. No regression on currently-matching presolve models (none have self-ref → byte-identical).
for m in bearing korcge mathopt3 robustlp rocket agreste camshape; do
  .venv/bin/python -m src.cli data/gamslib/raw/$m.gms -o /tmp/${m}_ps.gms --nlp-presolve --skip-convexity-check --quiet
  diff -q /tmp/${m}_ps.gms data/gamslib/mcp/${m}_mcp_presolve.gms   # (subject to pre-existing staleness; fix-delta must be 0)
done
```

### PROCEED/REPLAN Signal

**PROCEED** with the `src/emit/` implementation if ALL of:

- (a) Presolve emit omits the `pre2`/`pre4` self-referential assignment AND keeps the `$include` (Step 1). ✅
- (b) Cold `launch_mcp.gms` regenerates **byte-identical** to the committed golden — the Priority 1 byte-stability anchor is preserved and no `_apply_pattern_c_swap_to_term` change is made (Step 2). ✅
- (c) launch presolve solve reaches MODEL STATUS 1 with `cost = 2257.7976` → `[COMPARE] MATCH` (Step 3). ✅
- (d) Fix-delta on currently-matching presolve models is **zero lines** (they have no self-referential assignments) (Step 4). ✅

**REPLAN** if:

- The presolve solve reaches MODEL STATUS 1 but a *different* objective (≠ 2257.7976) → the double-application is not the (only) corruption; re-diagnose the embedded-NLP-vs-native divergence.
- The cold emit changes (byte-stability anchor moves) → the gate is firing outside presolve; tighten `skip_self_ref_presolve` to presolve-only.
- A currently-matching presolve model regresses → the self-reference detector is over-broad; restrict it.

**Result: PROCEED — all 4 criteria met (Sprint 27 Day 9).**

## Fix

`skip_self_ref_presolve` parameter in `emit_computed_parameter_assignments` (`src/emit/original_symbols.py`), threaded from `emit_gams.py` via a hoisted `presolve_will_emit` and passed to both parameter-assignment passes. Under `--nlp-presolve`, self-referential source parameter assignments are skipped; the `$include` applies them once. With it, launch's embedded NLP and MCP both reach `cost = 2257.7976` → `compare_match` (rel_diff 0.0).

**Blast radius (presolve-only):** cold `launch_mcp.gms` byte-identical (anchor preserved). True fix-delta touches only launch (→ match) and cesam (`model_infeasible`; presolve emit made more correct, compiles clean `action=c`). The 7 currently-matching presolve models have no self-referential assignments → unaffected. fawley/korcge presolve-golden diffs are pre-existing staleness on main, unrelated to this fix.
