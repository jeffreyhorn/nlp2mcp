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
