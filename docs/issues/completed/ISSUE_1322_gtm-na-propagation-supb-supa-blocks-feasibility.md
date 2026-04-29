# gtm: NA propagation through `supb`/`supa` parameters blocks PATH feasibility (residual after #1192 + #1320)

**GitHub Issue:** [#1322](https://github.com/jeffreyhorn/nlp2mcp/issues/1322)
**Status:** OPEN — Sprint 26 follow-up
**Severity:** Medium — gtm now reaches PATH (no listing-time abort), but PATH returns `MODEL STATUS 4 Infeasible` due to NA-derived coefficients
**Date:** 2026-04-29
**Affected Models:** gtm
**Parent / Predecessors:**
- [#1192](https://github.com/jeffreyhorn/nlp2mcp/issues/1192) (parent — closed by PR #1321 for the `stat_s` listing-time portion)
- [#1320](https://github.com/jeffreyhorn/nlp2mcp/issues/1320) (closed by PR #1321 for the `bdef` listing-time portion)

---

## Problem Summary

PR #1321 closes the listing-time div-by-zero aborts on gtm by adding
parameter-bounds-aware stationarity guards (#1192 / Option D) and
parameter-divisor `$`-condition injection on parsed-source equation
sums (#1320 / Approach 1). With both fixes in place, gtm progresses
from `path_solve_terminated` (EXECERROR=2/3) to `model_infeasible`
(MODEL STATUS 4): GAMS now compiles cleanly and PATH is invoked, but
PATH cannot find a feasible point.

The residual root cause is that **`supb(i)` and `supa(i)` evaluate to
`NA`** for the three regions where `supc(i) = 0` (mexico, alberta-bc,
atlantic). The pre-solve assignments `supb(i) = (...) / (1/(supc-q1)
- 1/(supc-q2))` and `supa(i) = ... - supb(i) / (supc(i) - q1)`
contain divisor expressions that produce `NA` when their inputs
include `0`. Even though my fixes correctly skip those instances in
`bdef` and `stat_s`, the NA values still propagate into PATH's
Jacobian as gigantic coefficients (e.g., `5E30 * s(mexico)` in the
listing) because PATH evaluates the equation symbolically with the
NA parameters substituted.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success (0 errors)
- **PATH solve**: MODEL STATUS 4 (Infeasible)
- **Pipeline category**: `model_infeasible`
- **Predecessors fixed**: stat_s div-by-zero (#1192 PR #1321), bdef
  listing-time div-by-zero (#1320 PR #1321)

---

## Reproduction (verified 2026-04-29 on `sprint25-plan-fix-1192` branch
with PR #1321 in place)

```bash
.venv/bin/python -m src.cli data/gamslib/raw/gtm.gms \
    -o /tmp/gtm_mcp.gms --skip-convexity-check
cd /tmp && gams gtm_mcp.gms lo=2

# Expected output:
# **** EXECERROR AT LINE 59 CLEARED (EXECERROR=0)
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      4 Infeasible
```

Original NLP comparison (matches as expected):

```bash
cp /Users/jeff/experiments/nlp2mcp/data/gamslib/raw/gtm.gms /tmp/gtm_orig.gms
cd /tmp && gams gtm_orig.gms lo=2

# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      2 Locally Optimal
# **** OBJECTIVE VALUE             -543.5651
```

Inspect the NA-derived coefficients in the post-PR-#1321 listing:

```bash
grep -A3 "bdef\.\." /tmp/gtm_mcp.lst | head -10
# Look for `5E30 * s(mexico)`, `2.4E31 * s(alberta-bc)`, etc.
```

---

## Root Cause Detail

### Source data (gtm.gms:28-40)

```
Table sdat(i,*) 'supply data'
                 ref-p1  ref-q1  ref-p2  ref-q2  limit
   mexico                  2.0             .5     2.5
   alberta-bc              3.0            1.6     3.75
   atlantic                 .25             .03     .3
   appalacia        3.5     .58     7.0    .65     .72
   ...
```

Note that `mexico`, `alberta-bc`, `atlantic` have **empty cells in
ref-p1, ref-p2, and ref-q2**. The `limit` cell is also empty for
these regions, but it is also empty for several other rows (see
parameter-init below).

### Pre-solve assignments (gtm.gms:67-75)

```gams
supc(i)  = sdat(i, "limit");            # mexico/alberta-bc/atlantic → 0
supb(i)  = ((sdat(i, "ref-p1") - sdat(i, "ref-p2"))
         / (1/(supc(i) - sdat(i, "ref-q1")) - 1/(supc(i) - sdat(i, "ref-q2"))))
         $ (supc(i) <> inf);
supa(i)  = sdat(i, "ref-p1") - supb(i) / (supc(i) - sdat(i, "ref-q1"));
supc(i)$(supc(i) = inf) = 100;          # only fixes inf, not 0
```

For mexico (supc=0):
- `supb(mexico) = ((NA - NA) / (1/(-2.0) - 1/(0-NA))) $ true`
  - `(NA - NA)` evaluates to `NA`
  - `(1/-2 - 1/(-NA))` → `(-0.5 - NA)` → `NA`
  - `NA / NA` → `NA`
- `supa(mexico) = NA - NA / -2.0` → `NA`

So `supb(mexico) = supa(mexico) = NA`. Same for `alberta-bc` and
`atlantic`.

### Why PATH cannot solve

When PATH evaluates the (now-guarded) `bdef` and `stat_s` Jacobian,
the NA values propagate through ANY remaining uses of `supb(i) *
s(i)` or `supa(i) * x` even with my `$(supc <> 0)` guard, because
the GAMS solver expansion can still substitute the symbolic
parameter into Jacobian rows that involve other indices.

Specifically, the listing shows `bdef..  benefit + 0.25*x(mexico,
mexico) + ... + (5E30)*s(mexico) + (2.4E31)*s(alberta-bc) +
(4.5E28)*s(atlantic) + ...`. The huge coefficients (5e30, 2.4e31)
come from the symbolic Jacobian expansion of `supb(mexico) *
log(...)` even though the body sum was guarded out via my
`$(supc(i) <> 0)`. The guard works at row generation but the
Jacobian column-expansion still touches NA values in some path.

### Why the original NLP works

The original NLP succeeds because GAMS NLP-mode listing **substitutes
fixed variables with their values** at the listing pass, so
`s(mexico) = 0` gets substituted before the equation expression is
evaluated. Then `supa(mexico) * 0 = 0` (NA absorbs in the limit case
of `0 *`-multiplication for some GAMS NLP listing semantics) and
`supb(mexico) * log(...) * 0 = 0`. So the bdef row has all-zero
contribution from those regions, no NA propagation.

The MCP doesn't get that simplification because PATH requires the
equation to be linearized at the initial point, not at a fixed-value
substitution.

---

## Fix Approaches

### Approach 1 — NA-cleanup pass at MCP emit (recommended)

Add a parameter-sanity pass that, after the original parameter
assignments are emitted, overrides any indexed parameter that is
still `NA` to `0`. Specifically:

```gams
* NA-cleanup for safety
loop(i, supb(i)$(NOT (supb(i) > -inf and supb(i) < inf)) = 0; );
loop(i, supa(i)$(NOT (supa(i) > -inf and supa(i) < inf)) = 0; );
```

For gtm specifically, these cleanups make `supb*s = 0*s = 0` and
`supa*s = 0*s = 0` at any zero-supc instance, eliminating the
gigantic Jacobian coefficients.

**Detection logic:** any indexed parameter that appears in a Sum
body (or in any equation expression) AND is assigned via an
expression that contains a `Binary("/")` whose denominator could be
`0` — i.e., parameters in the same dependency chain as `supc`. For
generality, the simpler rule is: emit NA-cleanup for ALL indexed
parameters that appear in equation expressions AND are computed from
other parameters (i.e., have a non-trivial assignment expression).

**Estimated effort:** 6–8 hours (helper + emitter wiring +
regression).

### Approach 2 — Force-zero NA via `$onUndf`/`$ifThen` guards

Wrap the equation listing in `$onUndf ... $offUndf` and use
`option NaN = 0` (if supported) to make NA arithmetic resolve to 0
at PATH's symbolic evaluation. Less invasive than Approach 1 but
relies on GAMS-version-specific behavior that may not be portable.

**Estimated effort:** 2–4 hours (1 emitter line + verify).

### Approach 3 — Parameter-substitution hack at listing

Detect that `supb`/`supa` are computed from `supc` via division,
and at MCP emit time generate a guarded reassignment:

```gams
supb(i)$(supc(i) = 0) = 0;
supa(i)$(supc(i) = 0) = 0;
```

This is a more targeted form of Approach 1.

**Estimated effort:** 4–6 hours (parameter-dependency analysis +
emitter wiring).

---

## Recommended Approach

**Approach 1** (generic NA-cleanup) is the most robust and
addresses the underlying NA-propagation issue. Approach 2 is
faster but version-fragile. Approach 3 is a targeted variant that
might work for gtm specifically but doesn't generalize.

---

## Files Involved

- `src/emit/original_symbols.py` or `src/emit/emit_gams.py` —
  Parameter assignment emission; new sanity-cleanup pass would slot
  in after the original assignments.
- `data/gamslib/raw/gtm.gms` — Original source (unchanged).

---

## Acceptance Criterion

After the fix, gtm should reach PATH and produce `MODEL STATUS 1
Optimal` or `MODEL STATUS 2 Locally Optimal` with `OBJECTIVE VALUE`
matching the NLP's `-543.5651` (within the standard 0.2% tolerance).

---

## Related Issues

- **#1192** (closed by PR #1321) — stat_s listing-time div-by-zero
- **#1320** (closed by PR #1321) — bdef listing-time div-by-zero
- **#1243** — lmp2: similar runtime div-by-zero in stat_y (different
  variable, different equation, same broader class)
- **#1245** — camcge: similar runtime div-by-zero for non-traded
  elements
- **#983** — elec: similar division-by-zero
