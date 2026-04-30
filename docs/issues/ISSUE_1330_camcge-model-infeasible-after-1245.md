# camcge: PATH returns MODEL STATUS 4 Infeasible after #1245 unblocks structural EXECERROR=4

**GitHub Issue:** [#1330](https://github.com/jeffreyhorn/nlp2mcp/issues/1330)
**Status:** OPEN — TWO partial fixes landed 2026-04-30 (`_preferred_decl_domain` arity-guard drop in round 1, `_diff_prod` collapse fix in round 2). Residuals reduced 3× under `--nlp-presolve` (24.76 → 8.58). Deeper issue still blocks `MODEL STATUS 1 Optimal`. See §"Investigation 2026-04-30 (round 2)" below for current state.
**Severity:** Medium — model compiles and PATH runs but returns INFEASIBLE; users get no usable solution
**Date:** 2026-04-30
**Last Updated:** 2026-04-30
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

---

## Investigation 2026-04-30 — partial fix landed; deeper issue remains

### Summary

Investigated all three approaches from §"Fix Approach". Approach 1
(`--nlp-presolve`) was tried first because it was the cheapest path
and would address other camcge-class models too. The `--nlp-presolve`
emit had a previously unidentified compile bug (`$318 — Domain list
redefined`) which has been **fixed in this branch**. With the fix,
the presolve path compiles cleanly and the NLP solves to `MODEL
STATUS 2 Locally Optimal`. **However**, the subsequent MCP solve
still returns `MODEL STATUS 4 Infeasible` (now with a different
residual count of 119 INFES, sum ≈ 24.76) — even with the NLP's
optimum as warm-start. This indicates the KKT system itself is
inconsistent at the NLP solution: a structural correctness bug,
likely in AD or stationarity-equation generation.

### What was fixed

**`src/emit/templates.py::_preferred_decl_domain`** — dropped the
arity-equality guard. Previously, when an equation's `domain` (body
head) and `declaration_domain` (source declaration) had different
arities, the emitter fell back to `domain` for the declaration line.
For camcge's `gdeq` (declared `Equation gdeq;` scalar but defined
`gdeq(i)..` indexed), this meant the MCP emitted `gdeq(i)` while the
`$include`'d source declared `gdeq` scalar — GAMS rejected with `$318
— Domain list redefined`.

The fix mirrors the source's declaration form exactly, regardless of
arity. The body emission still uses `domain`. Combined with GAMS's
auto-promotion of scalar-declared / indexed-body equations, the MCP
now compiles cleanly under `--nlp-presolve`.

The change is safe: KKT-side machinery (`multiplier_domain_widenings`,
comp equation construction, fix-inactive emit) has its own arity
guards in `complementarity.py`, so comp equations only carry
`declaration_domain` when arities match. Only original-equality
declaration emission is affected by this change.

Tests added:
- `test_scalar_decl_indexed_body_records_arity_mismatch` — IR-level.
- `test_emit_uses_declaration_domain_even_when_arity_differs` —
  emitter-level.

Existing test suite (4,664 tests) passes; quality gate
(typecheck / lint / format / test) clean.

### What's left (deeper issue)

Even with `--nlp-presolve`, camcge's MCP returns `MODEL STATUS 4
Infeasible` with 119 INFES rows. Looking at the listing report:

```
stat_cd(ag-subsist).. (0.32...)*p(ag-subsist) - (0.00...)*cd(ag-subsist) +
  ... + (1.00011)*nu_cdeq(ag-subsist) - nu_equil(ag-subsist) =E= 0;
  (LHS = -1.4157, INFES = 1.4157 ****)
```

At the NLP-warm-started point, the `stat_cd(ag-subsist)` row
evaluates to LHS = −1.4157, not zero. The KKT system is structurally
inconsistent with the NLP at its own solution. Hypotheses:

1. **AD bug specific to the `cdeq` Cobb-Douglas demand block.**
   `cdeq(i).. cd(i) =e= cles(i) * y / p(i);` is a standard
   Cobb-Douglas, but the alpha indices and price normalization may
   interact poorly with the AD pipeline.

2. **Alias-AD mismatch (#1138 family).** camcge does NOT use the
   `(u,v) / (i,j) / (h,k)` aliases that #1138 lists for
   irscge / lrgcge / moncge / stdcge — but it uses similar SAM-like
   structures and may have analogous gradient-derivation issues
   that #1138's fix doesn't cover.

3. **Subset-conditioned gradient propagation.** The objective `omega`
   depends on `y`, which depends on `cd(i)`, which is constrained by
   `cdeq(i)`. The gradient w.r.t. `p(i)` propagates through the chain
   but the partial derivative `∂cdeq/∂p(i)` for non-traded `i` may
   be incorrectly computed because of the `(pm(i)*m(i))$it(i)` filter
   in `absorption(i)..`.

### Required next steps before another fix attempt

1. **Compare KKT residuals with explicit derivatives.** Hand-derive
   `∂cdeq/∂p(i)` and `∂cdeq/∂cd(i)` for both traded and non-traded
   `i`, then dump the AD-generated entries for the same partial.
   Identify which terms differ.

2. **Reduce camcge to a minimal failing block.** Strip the source
   to just `cdeq` + `equil` + `omega` and see if the smaller MCP
   still has the inconsistency. If yes, the bug is reproducible at
   small scale. If no, the issue is from an interaction across
   blocks.

3. **Compare against a known-good CGE.** irscge / lrgcge / moncge /
   stdcge match post-#1245. Diff their emitted stat_cd / cdeq
   bodies against camcge's to spot what's different. The CGE family
   may use a slightly different consumption-equation form that
   doesn't trigger the issue.

4. **AD-side instrumentation.** Add a debug flag that dumps every
   gradient/Jacobian term as it's generated, with provenance back
   to the source equation it was differentiated from. This would
   pinpoint exactly which AD step injects the wrong term.

Estimated effort to reach `MODEL STATUS 1 Optimal`: **8–16 hours**
once the AD bug is identified. Could be much higher if the bug is in
a subtle alias-or-subset interaction.

---

## Investigation 2026-04-30 (round 2) — second AD bug found, partial fix landed; deeper issue remains

Executed steps 1–3 from "Required next steps". Step 1 (hand-derive)
revealed a real bug in `_diff_prod`. Step 3 (CGE-family comparison)
confirmed the bug pattern was specific to camcge's objective form
(Cobb-Douglas with asymmetric `cles(i)` shares).

### What was fixed

**`src/ad/derivative_rules.py::_diff_prod`** — collapse the
logarithmic-derivative sum when wrt indices name-match the prod's
bound indices.

The mathematical identity for Cobb-Douglas / power products:

```
d(prod_i f(i)) / d(x(j))  =  prod * δ(i, j) * f'(i) / f(i)
                          =  prod * f'(j) / f(j)        (single term)
```

The old code always produced `prod * sum(i, df(i)/dx / f(i))` — a
SUM over all bound i. This is correct only when:
- `df(i)/dx` includes the kronecker δ(i,j) (so the sum collapses to a
  single term at i=j), OR
- All `f(i)` are equal (e.g. lmp2's `prod(p, y(p))` at a symmetric
  optimum where all y(p) coincide).

For asymmetric data like camcge's `cles(i)` per sector, the AD's body
differentiation didn't produce the kronecker delta. The naive sum
iterated over all i and gave the SAME value for all stationarity rows
(since the inner sum is i-independent), making the KKT structurally
inconsistent even at the NLP optimum.

**The fix:** when `effective_wrt` (post-collapse-substitution wrt
indices) name-matches the prod's bound indices, return
`prod * (body_deriv / body)` directly — no Sum wrapper. The body_deriv
is already at the symbolic bound index, which represents the wrt's
free index by name; the emitter aliases the prod's bound to a fresh
name (e.g. `i → i__`) at output time, so the post-`*` term references
the outer free index correctly.

The collapsed term inherits the prod's `$-condition` via a
`DollarConditional` wrap.

### Empirical impact

For camcge:
- Pre-AD-fix presolve: 119 INFES rows, sum 24.76, max 2.70
- Post-AD-fix presolve: 108 INFES rows, sum **8.58** (3× smaller),
  max 1.42

Other models (canary check, all preserved):
- irscge / lrgcge / moncge / stdcge / splcge / quocge / gtm: still
  Optimal at unchanged objective values
- twocge: still EXECERROR=8 from #1331 (unrelated)
- lmp2: still Optimal (multi-solve random; final-iteration obj
  shifts 35.598 → 35.292 due to slightly different KKT convergence
  per random instance — both valid local optima)

### Tests added

- `tests/unit/ad/test_diff_prod_collapse.py` — 4 unit cases:
  - Symbolic wrt collapses to single term.
  - Prod condition inherited as DollarConditional wrap.
  - Concrete wrt with set-membership lookup also collapses.
  - Public `differentiate_expr` API produces collapsed form.

Test suite: 4,670 passed (5 new tests; quality gate clean).

### What's still left

camcge under `--nlp-presolve` still returns `MODEL STATUS 4
Infeasible` with 108 INFES rows. The largest residual remains the
`gdp` equation (residual 131.96), suggesting either:
- A separate AD bug in another derivative path, OR
- A variable warm-start propagation issue under `--nlp-presolve`
  (some `.l` value gets clobbered).

Before another fix attempt, would benefit from:
1. **AD-side instrumentation** (next step 4 from above) — dump
   per-term gradient provenance to identify the next mismatched term.
2. **Variable-init audit under `--nlp-presolve`** — verify no `.l`
   values are clobbered by the MCP-side init pass after the NLP
   warm-start.

Estimated remaining effort: **6–12 hours**.

### Status

Issue stays **OPEN** with TWO partial fixes shipped: the
`_preferred_decl_domain` arity-guard drop (round 1) and the
`_diff_prod` collapse fix (round 2). Camcge still doesn't reach
`MODEL STATUS 1 Optimal`, but residuals are 3× smaller under
`--nlp-presolve`.

### Out of scope for this attempt

- Approach 2 (warm-start from calibration parameters) — not pursued;
  Approach 1 was preferred and partially succeeded.
- Approach 3 (INFEASIBLE-row investigation) — partially done above
  (the `cdeq` row was identified as inconsistent), but full
  investigation requires AD-side work (next step 1).
