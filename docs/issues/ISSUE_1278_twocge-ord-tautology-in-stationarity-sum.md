# twocge: Stationarity Contains `ord(r) <> ord(r)` Tautology (Always False) in Sum Coupling

**GitHub Issue:** [#1278](https://github.com/jeffreyhorn/nlp2mcp/issues/1278)
**Status:** OPEN — Deferred to Sprint 25
**Severity:** Medium — Silent correctness bug: the coupling to `rr` in twocge's trade-equation stationarity is effectively dropped, but no error is raised
**Date:** 2026-04-19
**Last Updated:** 2026-04-19
**Affected Models:** `twocge` (primary); any model where the AD instance enumeration collapses an inner alias back to its outer name
**Labels:** `sprint-25`

---

## Problem Summary

In `data/gamslib/mcp/twocge_mcp.gms` line ~482, stationarity equations for twocge contain clauses of the form:

```gams
... + sum(rr, <expr>$(ord(r) <> ord(r))) ...
```

The condition `ord(r) <> ord(r)` is a tautology — always false — so every term in the `sum(rr, ...)` is guarded to zero. The sum contributes nothing to stationarity, which means the coupling to the aliased index `rr` is silently dropped.

The **intended** condition is almost certainly `ord(rr) <> ord(r)` (i.e., "different regions"), which matches the pattern in the original twocge NLP and in sibling stationarity equations. The emitted form is a bug.

## Reproduction

```bash
grep -n "ord(r) <> ord(r)" data/gamslib/mcp/twocge_mcp.gms | head -3
# → one or more hits in stat_* equations
```

Expected after fix: `ord(rr) <> ord(r)` in every case, with no tautological `ord(X) <> ord(X)` surviving.

---

## Suspected Root Cause

An AD / substitution bug in derivative enumeration. When the twocge NLP's trade equation contains `sum(rr, <body>$(ord(r) <> ord(rr)))` and we differentiate with respect to a variable indexed on `rr`, the chain rule rewrites the inner alias `rr` to a concrete reference. During this rewrite, the `$(ord(r) <> ord(rr))` guard's `rr` gets rewritten to `r` alongside the body's `rr` — collapsing the comparison into the tautology.

The correct behavior is to preserve the guard's `rr` as the summation index (it's distinct from the body's `rr`-bound reference), OR to substitute a fresh alias if name collision is unavoidable.

## Distinct From #1251

**Important**: this is a **different** bug from #1251 (`twocge: Empty trade equations when r=rr`). #1251 is about the semantically-correct guard `ord(r) <> ord(rr)` producing 0=0 equations when `r = rr` — a legitimate consequence of the condition that requires multiplier fixing. This bug (#1278) is about the guard being **wrongly emitted** as `ord(r) <> ord(r)`, a different root cause that needs a fix in the AD / emitter index-preservation path.

---

## Suggested Fix

1. Reproduce with a minimal parsing + AD trace for twocge's `eqpw` / `eqw` differentiated w.r.t. variables on `rr`.
2. Inspect the substitution step that rewrites the inner alias — it's likely in `src/ad/*.py` or the instance-enumeration code in `src/kkt/stationarity.py`.
3. Fix the substitution to preserve the summation index distinct from the bound reference.
4. Add a unit test: construct a synthetic expression `sum(j, x(j)$(ord(i) <> ord(j)))`, differentiate w.r.t. `x(k)`, and assert the result's guard still reads `ord(i) <> ord(j)` (or equivalent with fresh aliases), NOT `ord(i) <> ord(i)`.

## Regression Guards

After the fix:

- Rerun twocge pipeline; the `ord(r) <> ord(r)` tautology must disappear.
- Currently-matching models (verified by dispatch canary + golden files from Sprint 24) must continue matching.

---

## References

- PR #1273 review comment #3106233160
- Related (same model, different bug): #1251 (empty trade equations), #1277 (stat_tz mixed offsets), #906 (SAM data ordering)
- Sibling Sprint 25 issues: #1275–#1277, #1279, #1280

## Estimated Effort

3–4 hours (trace, fix, regression test, dispatch canary).

---

## Files Involved

- `src/ad/*.py` — derivative rules for aliased summation
- `src/kkt/stationarity.py` — instance enumeration
- `data/gamslib/mcp/twocge_mcp.gms` — reference artifact
- `data/gamslib/raw/twocge.gms` — source model
