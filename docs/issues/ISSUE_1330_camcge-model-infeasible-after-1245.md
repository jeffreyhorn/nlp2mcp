# camcge: PATH returns MODEL STATUS 4 Infeasible after #1245 unblocks structural EXECERROR=4

**GitHub Issue:** [#1330](https://github.com/jeffreyhorn/nlp2mcp/issues/1330)
**Status:** OPEN
**Severity:** Medium — model compiles and PATH runs but returns INFEASIBLE; users get no usable solution
**Date:** 2026-04-30
**Affected Models:** camcge
**Predecessors:**
- [#1245](https://github.com/jeffreyhorn/nlp2mcp/issues/1245) (CLOSED, PR #1329) — wrapped traded-only multiplier terms in `stat_pd` / `stat_xxd` with `$(it(i))` to remove EXECERROR=4 from `1/gamma(in) = 1/0` and `0**negative`.
- [#1327](https://github.com/jeffreyhorn/nlp2mcp/issues/1327) (CLOSED, PR #1328) — `declaration_domain` machinery used by #1245.

---

## Problem Summary

After PR #1329 (#1245) eliminates the `EXECERROR=4` from non-traded
indices in `stat_pd` / `stat_xxd`, camcge compiles cleanly and PATH
runs to completion — but returns `MODEL STATUS 4 Infeasible` with 84
infeasible rows (residual sum ~8638, max residual ~2696). The original
NLP solves to `Locally Optimal`, so the KKT system is structurally
correct but PATH cannot find a feasible point from the default
starting point.

---

## Current Status

- **Translation:** Success
- **GAMS compilation:** Success (0 errors after #1245)
- **PATH solve:** Aborts with `MODEL STATUS 4 Infeasible`
- **Pipeline category:** `model_infeasible`
- **Original NLP:** `MODEL STATUS 2 Locally Optimal`, `OBJECTIVE VALUE 25.5085` (not directly comparable; camcge maximizes `omega`)

---

## Reproduction (verified 2026-04-30 with PR #1329 in place)

```bash
.venv/bin/python -m src.cli data/gamslib/raw/camcge.gms -o /tmp/camcge_mcp.gms --quiet
cd /tmp && gams camcge_mcp.gms lo=0

# Expected output:
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      4 Infeasible
# **** REPORT SUMMARY :        0     NONOPT
#                             84 INFEASIBLE (INFES)
#                     SUM       8638.0104
#                     MAX       2696.9008
#                     MEAN       102.8335
```

---

## Hypothesis: starting-point / warm-start issue

camcge is a non-trivial CGE model (~430 lines of source, multi-region
with traded/non-traded sectors, CES production, Armington trade).
PATH starts from the default `.l = 0` (or `.lo`-clamped values) for
most variables. The KKT system has many simultaneous CES-related
nonlinearities (Armington composite, CET export, capital allocation,
labor wage normalization), and the default starting point is far from
any feasible KKT manifold.

Hypotheses, ordered by likelihood:

1. **Warm-start would solve it.** The original NLP source has a
   sophisticated calibration block (lines 188-230) that pre-computes
   `delta`, `ac`, `gamma`, `at`, `etc.` from the SAM, and the NLP
   solver starts from those calibrated parameter values. In the MCP,
   those parameter calibrations ARE emitted, but the variable `.l`
   values are not warm-started from a prior NLP solve. The
   `--nlp-presolve` flag exists for this purpose but currently has 59
   compile errors on camcge (a separate pre-existing issue with
   presolve emit on this model — see §6 below).

2. **Bound multipliers are over-fixed.** Variables with `.lo = .01`
   (like `pd.lo(i) = .01`) have `piL_pd` multipliers. After #1327's
   fix-inactive emit, `piL_pd.fx(in)$(not (it(i))) = ...` — wait, this
   doesn't apply: piL multipliers are bound multipliers, not equation
   multipliers. They don't have a `multiplier_domain_widening`. So
   they're declared over `(i)` and active for ALL `i`. For non-traded
   `in`, `pd.lo(in) = .01` was set, but `pd` is also fixed via... let
   me check. Actually `pd` for non-traded is NOT fixed; only `e`, `m`
   are. So `pd(in)` is free with `.lo = .01`. The KKT system has
   `comp_lo_pd(i).. pd(i) - .01 =G= 0;` paired with `piL_pd(i)` over
   ALL `i`, including non-traded. For non-traded, the stationarity
   `stat_pd(in)` has only `nu_absorption(in)` and `nu_sales(in)`
   contributions (since the others are wrapped in `$(it(i))`). PATH
   needs to find `nu_absorption(in)`, `nu_sales(in)` such that this
   equals `piL_pd(in)`. If the absorption / sales equations evaluate
   to a contradiction for non-traded `in`, PATH reports infeasible.

3. **Non-traded equations themselves are over-constrained.** Looking
   at the source, `absorption(i)` and `sales(i)` are defined over ALL
   `i`. For non-traded `in`, `e(in)=0` and `m(in)=0` are fixed, so
   `pd(in)*xxd(in) = pd(in)*xxd(in)` (trivially true) and
   `px(in)*xd(in) = pd(in)*xxd(in)` (one equation). These are
   numerically OK if `pd`, `xxd`, `px`, `xd` are positive. Their
   `.lo = .01` enforces this. So absorption / sales for non-traded
   are well-posed — likely feasible.

4. **Bounds-collapse interaction.** The `.lo = .01` is small but
   nonzero. PATH's initial point may set variables exactly at `.lo`,
   making `piL` strictly positive — which then over-constrains other
   equations. A specific guess is that the `pmdef` / `pedef` / `pwm` /
   `pwe` equations interact poorly when `pd(in)` / `pe(in)` values
   are at `.lo` rather than at the calibrated SAM values.

---

## Reproduction Details

```bash
# Show INFEASIBLE rows (top of the .lst report)
grep -A 60 "REPORT SUMMARY" /tmp/camcge_mcp.lst | head -80

# Compare against original NLP solution
gams /Users/jeff/experiments/nlp2mcp/data/gamslib/raw/camcge.gms lo=0
# **** MODEL STATUS      2 Locally Optimal
```

---

## Fix Approach

### Approach 1 — Fix the `--nlp-presolve` path on camcge (RECOMMENDED)

The `--nlp-presolve` mode emits the original NLP solve before the
MCP, capturing the optimal `.l` values as the MCP warm-start. This is
exactly what camcge needs. Currently it has 59 compile errors
specifically on camcge. Investigation:

```bash
.venv/bin/python -m src.cli data/gamslib/raw/camcge.gms \
    -o /tmp/camcge_ps.gms --nlp-presolve --quiet
cd /tmp && gams camcge_ps.gms lo=0
# **** 59 ERROR(S)   0 WARNING(S)
```

The 59 errors need triage — likely interactions between the presolve
include and post-#1327 / #1245 emission. A separate investigation,
likely 4–6 hours.

### Approach 2 — Pre-compute and emit `.l` warm-start values from the calibration block

The camcge calibration block (lines 188-230) computes `delta`, `ac`,
`gamma`, `at`, `pd0`, `xxd0`, `e0`, `m0`, `pwe0`, `pwm0`, etc. from
the SAM data. These calibrated values are the natural starting point
for the variables. The emitter could detect parameter values like
`pd0(i)`, `xxd0(i)`, `e0(it)`, `m0(it)`, `pe0(it)`, `pm0(it)` and
emit corresponding `pd.l(i) = pd0(i);`, `xxd.l(i) = xxd0(i);`, etc.

**Pros:** Self-contained, no `--nlp-presolve` dependency.

**Cons:** Heuristic — relies on naming conventions (`<var>0` suffix
for initial-value parameters). Many CGE models follow this pattern
but not all. Hard to detect generically.

**Estimated effort:** 4–8 hours.

### Approach 3 — Investigate INFEASIBLE rows and identify the specific KKT contradiction

Run with `lo=2` or `lo=4` and `option iterlim=0` to dump the model
listing, then trace which specific stationarity / complementarity
rows PATH reports as infeasible. The 84 infeasible rows are a strong
signal — they likely cluster around a specific equation family
(e.g., all `stat_pwm(in)` or `comp_costmin(it)`).

**Pros:** Pinpoints the exact bug; may reveal a subtler issue than
warm-start.

**Cons:** Investigative work; could uncover a deeper issue requiring
a more invasive fix.

**Estimated effort:** 4–6 hours.

---

## Estimated Effort

Total: 8–12 hours, depending on whether Approach 1 (fix presolve) or
Approach 2 (emit warm-start) is chosen, plus testing and CGE-family
regression sweep.

---

## Acceptance Criterion

1. ✅ camcge reaches `MODEL STATUS 1 Optimal` (or `MODEL STATUS 2
   Locally Optimal` is acceptable for non-convex CGE).
2. ✅ Pipeline category is `model_optimal` or `model_optimal_presolve`.
3. ✅ Stretch: objective value matches the NLP reference within 1e-3
   (CGE non-convexity may yield different KKT points; document if
   different but feasible).

---

## Files Involved

- `data/gamslib/raw/camcge.gms` — original source (unchanged)
- `src/emit/emit_gams.py` — variable initialization + presolve emit
  (depending on chosen approach)
- `src/emit/_emit_nlp_presolve` (within emit_gams.py) — if pursuing
  Approach 1

---

## Related Issues

- **#1245** (CLOSED, PR #1329) — fixed the structural EXECERROR=4
- **#1327** (CLOSED, PR #1328) — fixed declaration_domain
- **#1192** (CLOSED) — gtm runtime div-by-zero (similar warm-start
  concern; gtm now needs `--nlp-presolve` to reach Optimal)
- **#1138** — CGE-family alias-AD mismatch (separate issue, lists
  irscge / lrgcge / moncge / stdcge — different root cause)
