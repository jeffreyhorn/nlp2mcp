# elec: Pairwise-distance div-by-zero in stat_x KKT-built equations, residual after #1320 divisor-guard

**GitHub Issue:** [#1325](https://github.com/jeffreyhorn/nlp2mcp/issues/1325)
**Status:** OPEN — Sprint 26 follow-up
**Severity:** High — `path_solve_terminated` (EXECERROR) at GAMS model-listing time on stat_x derivatives
**Date:** 2026-04-29
**Affected Models:** elec
**Predecessors / closely-related:**
- [#983](https://github.com/jeffreyhorn/nlp2mcp/issues/983) — Original elec division-by-zero issue
- [#1320](https://github.com/jeffreyhorn/nlp2mcp/issues/1320) (closed by PR #1321) — bdef divisor guard. **elec was probed as an "adjacent model" but Approach 1 from #1320 did NOT unblock it because elec's blocker is in KKT-built `stat_x` equations (which #1320 explicitly bypasses), not in original parsed equations.**

---

## Problem Summary

elec is a non-convex pairwise-distance optimization (the standard
"electron repulsion" problem). The objective involves
`sum((i,j)$(ord(i) < ord(j)), 1/distance(i,j))` with
`distance(i,j) = sqrt(sqr(x(i)-x(j)) + sqr(y(i)-y(j)) +
sqr(z(i)-z(j)))`. The KKT-built stationarity equation `stat_x(i)`
contains the gradient `1/(2*distance) * 2*(x(i) - x(j))` etc., which
evaluates to `1/0` when two points coincide at the initial value
(default 0 for variables x,y,z).

PR #1321's #1320 fix targets parsed-source equation Sum bodies and
explicitly bypasses KKT-built `stat_*` equations to avoid double-
conditioning. So elec gets no benefit. The blocker is purely in the
KKT layer.

---

## Current Status

- **Translation**: Success
- **GAMS compilation**: Success (0 errors)
- **PATH solve**: EXECERROR (div-by-zero in stat_x for all 6
  electrons i1..i6)
- **Pipeline category**: `path_solve_terminated`
- **Predecessors fixed**: none specifically for elec; #1320's
  Approach 1 explicitly skips KKT-built equations.

---

## Reproduction (verified 2026-04-29 with PR #1321 in place)

```bash
.venv/bin/python -m src.cli data/gamslib/raw/elec.gms \
    -o /tmp/elec_mcp.gms --skip-convexity-check
cd /tmp && gams elec_mcp.gms lo=2

# Expected output:
# **** Exec Error at line 99: division by zero (0)
# **** Evaluation error(s) in equation "stat_x(i1)"
# **** Evaluation error(s) in equation "stat_x(i2)"
# ... (i3..i6 similar)
```

Inspect the offending equation:

```bash
$ grep "^stat_x" /tmp/elec_mcp.gms
stat_x(i).. sum(j, sum(j__$(ut(i,i)),
    ((-1) * (1 / (2 * sqrt(sqr(x(i) - x(j__)) + ...)) * 2 * (x(i) - x(j__))))
    / sqr(sqrt(...))) + ... =E= 0;
```

The outer `1 / (2 * sqrt(...))` is `1/0` when `x(i) = x(j__) = 0`
at the initial point.

---

## Root Cause Detail

The KKT-built `stat_x(i)` differentiates the objective
`1/distance(i,j)` w.r.t. `x(i)`, producing terms like:

```
(-1) * (1 / (2 * sqrt(sqr(x(i)-x(j)) + sqr(y(i)-y(j)) + sqr(z(i)-z(j))))
       * 2 * (x(i) - x(j)))
/ sqr(sqrt(sqr(x(i)-x(j)) + sqr(y(i)-y(j)) + sqr(z(i)-z(j))))
```

This is the standard chain-rule derivative of `1/||p_i - p_j||`. It
involves division by `sqrt(0)` when all three coordinate differences
are 0 at the initial point.

The original NLP works because:
1. The NLP solver (CONOPT/IPOPT) handles starting-point infeasibility
   by perturbing variables to non-zero values internally.
2. NLP listing doesn't strictly evaluate every equation at the
   initial point.

The MCP can't take either shortcut. PATH requires the Jacobian to be
well-defined at the initial point, and GAMS evaluates `stat_x` at
listing time before PATH is invoked.

---

## Fix Approaches

### Approach 1 — Variable initialization to non-coincident points
(recommended; targeted)

Detect that `stat_x(i)` contains `1/sqrt(...)` distance derivatives
and emit non-degenerate initial values for the position variables:

```gams
x.l(i) = ord(i) * 0.1;
y.l(i) = ord(i) * 0.1;
z.l(i) = ord(i) * 0.1;
```

This ensures all electrons start at distinct positions, so `sqrt(...) >
0` for all (i,j) pairs and the listing-time evaluation succeeds.

**Detection logic:** scan `stat_*` equations for `1/sqrt(...)` and
`1/distance`-like patterns; for each variable that appears under the
sqrt, emit a per-instance non-zero `.l` initialization.

**Estimated effort:** 4–6 hours (detection + emitter wiring +
regression). Generalizes to other distance-based objectives.

### Approach 2 — Variable-bounds-aware-equivalent guard for KKT-built equations

Currently PR #1321's #1192 fix wraps `stat_v(d)` in `$(v.up(d) -
v.lo(d) > eps)`. We could similarly wrap stat_x in a runtime guard
on the distance: `$(distance(i,j) > eps)`. But this requires
detecting the offending denominator pattern in the KKT-built body
(parallel to my #1320 helper but applied to stat_*).

**Estimated effort:** 8–12 hours (extend #1320's `_inject_divisor_guards`
to optionally apply to stat_* equations + handle the bounds-vs-divisor
guard interaction).

### Approach 3 — Force PATH preprocessing (model.iterlim, .nodlim,
warm-start)

Run PATH with `--nlp-presolve` so an NLP solve produces a non-
degenerate starting point first. Less invasive at the emitter level
but ties elec to the warm-start path (currently blocked by #1313's
Error 141 cascade in `--nlp-presolve` for some models).

**Estimated effort:** 1–2 hours (verify --nlp-presolve works for
elec specifically).

---

## Recommended Approach

**Approach 1** (variable initialization) is the most pragmatic and
targeted. It's a localized fix to elec-class problems
(distance-based objectives) without rewriting the KKT layer.

**Approach 2** is the "principled" fix but couples elec to a deeper
emitter pass that doesn't yet exist. Plan for Sprint 27+ if Approach
1 is insufficient.

---

## Files Involved

- `src/emit/emit_gams.py` — variable-initialization emission section
  (already exists; extend with distance-pattern detection).

---

## Acceptance Criterion

1. elec no longer aborts at GAMS model-listing time.
2. elec progresses to PATH solve attempt.
3. Stretch: PATH solves; elec is non-convex so a "different KKT
   point" outcome may be acceptable rather than full match.

---

## Related Issues

- **#983** — Original elec division-by-zero (this issue is a
  refined post-Sprint-25 framing).
- **#1320** (closed by PR #1321) — Why PR #1321's #1320 didn't help
  elec: Approach 1 only targets parsed-source equations.
- **#1192** (closed by PR #1321) — Bounds-aware guard for KKT-built
  stationarity; doesn't apply to elec because the variables aren't
  bounds-collapsed (their `.lo`/`.up` are unconstrained for x/y/z).
- **#1245**, **#1243**, **#1320 follow-up (gtm NA propagation)** —
  related runtime div-by-zero family.

## Phase 0: Acceptance Gate

**Authored:** Sprint 38 Day 2 (P7 backfill) · **Fingerprint re-reproduced at `b823a9a5`**, GAMS 54.2.1 / PATH 5.2.01.

### Hand-Derived KKT Shape

The objective sums over the **strictly upper-triangular** pair set `ut(i,j)` (so `i ≠ j` always):

```gams
obj.. potential =e= sum{ut(i,j), 1.0/sqrt(sqr(x[i]-x[j]) + sqr(y[i]-y[j]) + sqr(z[i]-z[j]))};
```

Write `d(a,b) = sqrt(sqr(x_a-x_b) + sqr(y_a-y_b) + sqr(z_a-z_b))`. A given point `p` appears in a pair **either as the first member or as the second**, so

> ∂/∂x_p Σ_{ut(a,b)} 1/d(a,b)  =  **Σ_{b : ut(p,b)}** −(x_p−x_b)/d(p,b)³  **+**  **Σ_{a : ut(a,p)}** +(x_a−x_p)/d(a,p)³

**Both sums must be restricted to pairs that actually contain `p`**, and because `ut` is strictly upper-triangular, **every surviving term has `a ≠ b`, so `d > 0` and the expression is finite.** That is the whole correctness argument: `ut` guarantees the divisor is non-zero, and any emitted term whose index pair can collapse to `(p,p)` is outside the mathematics.

### Expected Emit Pattern

```gams
stat_x(i).. sum(j$(ut(i,j)), -(x(i)-x(j)) / power(dist(i,j),3))
          + sum(i__$(ut(i__,i)), (x(i__)-x(i)) / power(dist(i__,i),3))
          + 2*x(i)*nu_ball(i) =E= 0;
```

**The invariant to assert: every condition's index tuple must be exactly the summation index paired with the free index** — `ut(i,j)` under `sum(j,…)`, `ut(i__,i)` under `sum(i__,…)`. **No condition may name a pair that excludes its own summation index.**

**What is emitted today is wrong on exactly that invariant** (emitted `stat_x(i)`, `b823a9a5`):

```gams
sum(j, sum(j__$(ut(i,i)), … x(i) - x(j__) …)          ← ut(i,i): the DIAGONAL of a strictly
     + sum(i__$(ut(i,j)),  … x(i__) - x(i) …))          upper-triangular set — always FALSE
                                                        ← ut(i,j) does not constrain i__ at all,
                                                          so i__ = i is admitted → d = 0
```

Two distinct defects: the first condition is `ut(i,i)` (**structurally empty**, so that half of the gradient is silently dropped), and the second conditions on `(i,j)` while summing over `i__` (**unconstrained**, so `i__ = i` reaches the divisor). The spurious outer `sum(j, …)` wrapper is a third symptom of the same index-binding confusion.

**Traced fix-surface (Day-2):** the stationarity term-assembly that pairs a derivative's summation index with the originating equation's condition — the condition is being carried over verbatim from the objective's `ut(i,j)` instead of being **re-indexed to the summation variable**. **⚠ Traced hypothesis; confirm before implementing.**

### Verification Methodology

Run from a **scratch directory**.

1. **Fail-before** (`b823a9a5`): `gams elec_mcp.gms lo=0 errmsg=1` → `rc=3`, with anchored diagnostics
   ```
   **** Exec Error at line  99: division by zero (0)      ← stat_x
   **** Exec Error at line 100: division by zero (0)      ← stat_y
   **** Exec Error at line 101: division by zero (0)      ← stat_z
   **** SOLVE from line 133 ABORTED, EXECERROR = 3
   ```
   plus **30 × `Evaluation error(s) in equation "stat_x(iN)"`**. **The line↔equation mapping is part of the fingerprint** — 99/100/101 are exactly `stat_x`/`stat_y`/`stat_z`, so an exec error at a *different* line is a different defect.
2. **Structural assertion, stronger than the error count:** `grep -c 'ut(i,i)' elec_mcp.gms` must go **from non-zero to 0**, and every `$(ut(...))` must name its own enclosing summation index. A run that merely stops erroring while keeping `ut(i,i)` has **dropped half the gradient** and is a false pass.
3. **Correctness, not just termination:** the KKT residual at the NLP optimum must be clean (`kkt_residual.py elec` → `CASE_A`). **This is the check that separates "no longer divides by zero" from "computes the right gradient".**
4. **Pass-after:** zero exec errors; no `ABORTED`; `modelstat` asserted before any objective read. **Leak gate:** only `elec` drifts, **stating the in-scope count** (185 post-P4). Determinism ×3.

### PROCEED/REPLAN Signal

**PROCEED** — zero division-by-zero exec errors, **no `ut(i,i)` remains**, the residual reaches `CASE_A`, and nothing outside `elec` drifts.

**REPLAN** — the residual stays `CASE_B` (the gradient is still structurally wrong even if it evaluates), or the index re-binding perturbs another model in the sweep. **A merely non-erroring emit is NOT a pass** — that is precisely how #983 came to be recorded as resolved while the defect persisted (see below).

### Bucket / KPI

**0 bucket expected.** `elec` is `path_solve_terminated` with `solver_version: None` — it aborts at **GAMS execution before PATH is invoked**. Clearing it lets `elec` *reach* PATH. `elec` is non-convex, so **no Solve or Match gain may be projected**.

### Relationship to #983

**#983 and this issue are the same defect at different stages.** #983's doc contains a section titled *"Why Division-by-Zero No Longer Occurs"* — **that is stale: division by zero reproduces today at `b823a9a5`**, at lines 99/100/101. Treat **this** gate as the live specification for both, and do not read #983's resolved-sounding narrative as current state.
