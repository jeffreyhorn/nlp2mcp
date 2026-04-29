# gtm: bdef equation hits div-by-zero on log((supc-s)/supc) for zero-supc regions (residual after #1192 stat_s fix)

**GitHub Issue:** [#1320](https://github.com/jeffreyhorn/nlp2mcp/issues/1320)
**Status:** OPEN — Sprint 26 follow-up
**Severity:** Medium — Model compiles but EXECERROR=2 aborts solve at the original benefit equation
**Date:** 2026-04-28
**Last Updated:** 2026-04-28
**Affected Models:** gtm
**Parent Issue:** [#1192](https://github.com/jeffreyhorn/nlp2mcp/issues/1192) (fixes the `stat_s` portion via PR #1321; this doc tracks the residual `bdef` portion)

---

## Problem Summary

Sprint 25 PR #1321 addresses **#1192**'s primary symptom (the `stat_s`
division-by-zero on gtm's three zero-supc regions) by emitting a bounds-aware
conditional stationarity guard. After that fix lands, gtm translates cleanly
and `stat_s` no longer aborts at GAMS model-listing time. **However, gtm still
aborts** with EXECERROR=2 at the **original `bdef` equation** because its body
contains `log((supc(i) - s(i))/supc(i))` summed over all `i`, including the
three `supc = 0` regions.

This is a separate, mathematically-distinct root cause from #1192's `stat_s`
symptom. It cannot be addressed by the variable-bounds-aware guard from
PR #1321 because `bdef` is the **original, source-level** benefit equation
emitted verbatim from the parsed IR — not a stationarity equation generated
by the KKT builder.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success (0 errors)
- **PATH solve**: EXECERROR=2 (`bdef` div-by-zero at model-listing)
- **Pipeline category**: `path_solve_terminated`
- **Previous fixes**:
  - #1192 / PR #1321 (stat_s div-by-zero, MERGED for the stat_s portion only)
- **Previous attempts that did NOT fix this**:
  - `option domlim = N` (controls solver-level domain violations, not
    listing-time evaluation errors)
  - `$onUndf` (allows UNDF arithmetic results, but does NOT suppress the
    underlying `0/0` division-by-zero error class)

---

## Error Details

After PR #1321 lands and gtm is re-translated:

```
**** EXECERROR AT LINE 59 CLEARED (EXECERROR=0)
**** Exec Error at line 172: division by zero (0)
**** Exec Error at line 172: A constant in a nonlinear expression in equation bdef evaluated to UNDF
**** SOLVE from line 222 ABORTED, EXECERROR = 2
```

Pre-#1321 the same model also showed `stat_s` evaluation errors at line 155;
those are gone post-#1321. Line 172 is the `bdef` equation.

---

## Root Cause

The original NLP source for gtm contains:

```
* gtm.gms:154
bdef..    benefit =e= sum(j, dema(j)*d(j)**demb(j))
                   -  sum(i, supa(i)*s(i) - supb(i)*log((supc(i) - s(i))/supc(i)))
                   -  sum((i,j)$ij(i,j), utc(i,j)*x(i,j));
```

For three regions (`mexico`, `alberta-bc`, `atlantic`) the source data has
empty `sdat(i, "limit")` cells, so `supc(i) = 0` after the parameter
assignment chain (the subsequent `supc(i)$(supc(i) = inf) = 100;` rewrite
only matches `inf`, not `0`). Consequently:

- `supb(i)` and `supa(i)` are both `NA` for those three regions because their
  pre-solve assignments contain `supb / (supc - q1)` factors that evaluate
  to `NA / -q1 = NA` when `supc = 0`.
- The `bdef` body computes `log((supc(i) - s(i))/supc(i))` per `i`. For the
  zero-supc regions: `(0 - s)/0`, where the division `1/0` triggers the
  div-by-zero error during model listing — BEFORE the multiplication by
  `supb(i) = NA` could absorb it.

### Why the original NLP works but the MCP doesn't

The original NLP succeeds because GAMS NLP-mode listing skips equation
evaluation for **fixed** variables. With `s.up(i) = 0.99 * supc(i) = 0` and
`s.lo(i) = 0` (positive default), `s(i)` is implicitly fixed at 0 for the
three regions. NLP listing skips the `bdef` body for those rows.

The MCP, however, requires `bdef` to be in the model (paired complementarily
with `benefit`). The body `sum(i, ...)` is at **scalar scope** — there is no
per-`i` MCP pair to skip; the entire sum must evaluate to a single value at
listing time. That sum evaluates **every** `i`, including zero-supc, and hits
`log(0/0)`.

PR #1321's bounds-aware guard for `stat_s(i)` does not help here because
`bdef` is not a stationarity equation and is not built by the KKT pipeline —
it is emitted verbatim from the parsed IR.

### Cannot work around with parameter overrides alone

Tested during PR #1321 development: even if we override `supc(i)$(supc(i) =
0) = 1e-30;` after the original parameter assignments, the model becomes
**INFEASIBLE** (PATH MODEL STATUS 4) instead of aborted. The bdef equation
in the listing has gigantic NA-derived coefficients (e.g., `5E30 *
s(mexico)`) because `supb(mexico) = NA` and `1/sqr(supc) = 1/sqr(1e-30)
≈ 1e60`. PATH cannot solve such a numerically-degenerate system.

So a complete fix requires structurally excluding the zero-supc rows from
`bdef`, not just numerically smoothing the denominator.

---

## Reproduction

**Prerequisite:** GAMSlib raw sources in `data/gamslib/raw/` and PR #1321
merged into `main`.

```bash
.venv/bin/python -m src.cli data/gamslib/raw/gtm.gms \
    -o /tmp/gtm_mcp.gms --skip-convexity-check
cd /tmp && gams gtm_mcp.gms lo=2

# Output (post-#1321):
# **** Exec Error at line 172: division by zero (0)
# **** Exec Error at line 172: A constant in a nonlinear expression in equation bdef evaluated to UNDF
# **** SOLVE from line 222 ABORTED, EXECERROR = 2
```

To verify the original NLP works:

```bash
cd /tmp && cp /Users/jeff/experiments/nlp2mcp/data/gamslib/raw/gtm.gms ./
gams gtm.gms lo=2

# Output:
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      2 Locally Optimal
# **** OBJECTIVE VALUE             -543.5651
```

---

## Potential Fix Approaches

### Approach 1 — Equation-body $-condition rewrite (recommended)

At MCP-emit time, modify the emitted `bdef` body to add `$(supc(i) <> 0)`
on the relevant `sum(i, ...)`:

```
bdef..    benefit =e= sum(j, dema(j)*d(j)**demb(j))
                   -  sum(i$(supc(i) <> 0),
                          supa(i)*s(i) - supb(i)*log((supc(i) - s(i))/supc(i)))
                   -  sum((i,j)$ij(i,j), utc(i,j)*x(i,j));
```

**Benefits:** structural fix — the zero-supc rows are excluded from the sum,
so `log(0/0)` never evaluates. Mathematically correct: those regions
contribute zero benefit anyway because their fixed-at-zero supply means no
production cost.

**Cost:** requires AST-level rewriting of the parsed equation. Detection
logic must:
1. Scan equation bodies for `Binary("/", _, X)` and `Call("log", X)` patterns.
2. Identify the parameter(s) inside `X` that could be zero.
3. Add the appropriate `$(param <> 0)` condition on the smallest enclosing
   `Sum` node whose body references that parameter as a denominator.

Estimated effort: **4–6 hours** (single-file emitter pass + 2–3 unit tests
+ gtm integration test).

### Approach 2 — Symbolic NA-cleanup at MCP emit

After the original parameter assignments are emitted, add a sanity-init pass
that overrides NA-valued and zero-valued parameters that appear in
denominators:

```
supc(i)$(supc(i) = 0) = 1e-30;  // safety
supb(i)$(NOT (supb(i) > -inf and supb(i) < inf)) = 0;
supa(i)$(NOT (supa(i) > -inf and supa(i) < inf)) = 0;
```

**Benefits:** doesn't require AST equation rewriting.

**Cost:** changes parameter values broadly; relies on GAMS' `0 * NA = ?`
arithmetic which is not always `0` (varies by context). Tested during
PR #1321 dev — model still INFEASIBLE due to coefficient blow-up. Not viable
on its own.

Estimated effort: **6–10 hours** (parameter-value tracking, NA-detection,
test coverage). Not recommended given the INFEASIBLE outcome.

### Approach 3 — bdef replacement with post-solve assignment

Since `bdef` only exists to define `benefit = f(x)` for output, replace it
with a post-solve parameter assignment instead of a constraint:

```
* AFTER solve:
benefit.l = sum(j, ...) - sum(i$(supc(i) <> 0), ...) - sum((i,j)$ij(i,j), ...);
```

**Benefits:** sidesteps the listing-time evaluation entirely.

**Cost:** large blast radius — changes the MCP/NLP equation parity for
output reporting; would need to be conditional on the parser detecting that
`benefit` is purely an output variable not referenced in stationarity. Risky
for other models that rely on `bdef`-style equations being in the model.

Estimated effort: **6–8 hours**.

---

## Recommended Approach

**Approach 1** (equation-body $-condition rewrite) is the cleanest. The
detection rule is local (per-equation expression scan), the rewrite is
mathematically correct (zero-supc regions are degenerate and contribute
nothing), and the blast radius is limited (only fires on equations whose
body has parameter-denominator divisions).

If Approach 1's detection turns out to over-fire on other models, fall back
to a narrowly-scoped per-model emitter pass that targets only gtm's `bdef`.

---

## Files Involved

- `src/emit/equations.py` — Equation-body rendering; new pre-emit AST scan
  + rewrite for $-conditioned sums.
- `src/emit/emit_gams.py` — Equation emission orchestration.
- `data/gamslib/raw/gtm.gms` — Original source (unchanged; the rewrite
  happens at MCP emit time only).

---

## Acceptance Criterion

After the fix, `gtm` should at minimum reach the PATH solve attempt without
EXECERROR=2 (i.e., move from `path_solve_terminated` to either
`model_optimal`, `model_optimal_presolve`, or some other PATH outcome). The
stretch goal is full `match` against the NLP reference (`-543.5651`).

---

## Related Issues

- **#1192** (parent — `stat_s` div-by-zero, addressed by PR #1321)
- **#1243** — lmp2: similar runtime div-by-zero in `stat_y` (different
  variable / different equation, but same root-cause class)
- **#1245** — camcge: similar runtime div-by-zero for non-traded elements
- **#983** — elec: division-by-zero in distance calculation

All four belong to a "**parameter-denominator at degenerate instances**"
fix family that may benefit from a generalized equation-body $-condition
rewrite (Approach 1) covering the original equations as well as the
KKT-built stationarity rows.
