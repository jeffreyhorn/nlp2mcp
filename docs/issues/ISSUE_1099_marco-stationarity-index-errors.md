# marco: Stationarity Equation Index Errors ($148/$170/$171)

**GitHub Issue:** [#1099](https://github.com/jeffreyhorn/nlp2mcp/issues/1099)
**Model:** marco (GAMSlib SEQ=165)
**Status:** OPEN
**Error Category:** Compilation — $148 Dimension different, $170/$171 Domain violation
**Severity:** Medium — model translates but GAMS compilation fails (7 errors)
**Sprint:** 22 Day 12

---

## Problem Summary

After resolving the duplicate parameter data issue (#913), the marco MCP still fails to compile due to incorrect symbol indexing in stationarity equations `stat_w` and `stat_z`. Multiplier variables are referenced with wrong indices, missing indices, or literal strings where set references are expected.

---

## Error Details

### stat_w (line 146): 3 errors

```gams
stat_w(cr,ci,cf)$(bp(cf,ci)).. ... + nu_bb(ci) + ... lam_qub(cf) ... $(qs("lim",cf,q)) ...
```

1. **$171 — `nu_bb(ci)`**: `nu_bb` is declared with domain `(cf)` but indexed by `ci`. Should be `nu_bb(cf)`.
2. **$148 — `lam_qub(cf)`**: `lam_qub` is declared with domain `(cf,q)` but referenced with only 1 index. Inside `sum(q, ...)`, should be `lam_qub(cf,q)`.
3. **$170 — `qs("lim",cf,q)`**: The first index is the string literal `"lim"` instead of the set variable `lim`. Should be `qs(lim,cf,q)` inside a `sum(lim, ...)`.

### stat_z (line 148): 2 errors

```gams
stat_z(cr,p).. ... sum(m, b(m,p) * lam_cc) + sum(m, b(m,p) * lam_cc(p)) ...
```

1. **$148 — `lam_cc`**: `lam_cc` is declared with domain `(m)` but referenced with 0 indices. Inside `sum(m, ...)`, should be `lam_cc(m)`.
2. **$171 — `lam_cc(p)`**: `lam_cc` domain is `(m)` but indexed by `p`. Inside `sum(m, ...)`, should be `lam_cc(m)`.

### Cascading: 2 errors

- **$257 (line 228)**: Solve statement not checked due to previous errors
- **$141 (line 231)**: `phi.l` has no value (solve didn't execute)

---

## Root Cause

The KKT stationarity builder generates incorrect multiplier index references when:
1. A constraint equation's domain differs from the variable domain being differentiated
2. The Jacobian term involves summation over indices not in the stationarity equation's domain
3. Set names used as domain qualifiers (like `lim` in `qs(lim,cf,q)`) are emitted as string literals

This is a **stationarity index mapping bug** in `src/kkt/stationarity.py` where multiplier references are not correctly aligned to the sum domains in which they appear.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/marco.gms -o /tmp/marco_mcp.gms --skip-convexity-check
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/marco_mcp.gms lo=2 o=/tmp/marco_mcp.lst
grep '^\*\*\*\*' /tmp/marco_mcp.lst
```

---

## Original GAMS Context

```gams
* marco.gms — key equations
bb(cf)..       sum((cr,ci)$bp(cf,ci), w(cr,ci,cf)) =l= x(cf);
mb(cr,ci)..    sum(cf$bp(cf,ci), w(cr,ci,cf)) + ui(cr,ci)$cd(ci) =e= u(cr);
qub(cf,q)..    sum((cr,ci)$bp(cf,ci), atc(cr,ci,q)*w(cr,ci,cf)) =l= qs("upper",cf,q)*x(cf);
cc(m)..        sum(p, b(m,p)*sum(cr, z(cr,p))) =l= k(m);
```

The multiplier `nu_bb` corresponds to `bb(cf)`, so it should only be indexed by `cf`. The multiplier `lam_qub` corresponds to `qub(cf,q)`, so it should be indexed by `(cf,q)`. The multiplier `lam_cc` corresponds to `cc(m)`, so it should be indexed by `(m)`.

---

## Suggested Fix

1. Fix multiplier index generation in `_add_indexed_jacobian_terms()` to correctly map constraint equation domains to multiplier references within sum expressions
2. Ensure set-name domain qualifiers (like `lim` in `qs(lim,cf,q)`) are not emitted as quoted string literals
3. Ensure multiplier references inside `sum(idx, ...)` use `idx` as the index, not the stationarity equation's own domain variables

---

## Impact

5 primary compilation errors. Model cannot compile or solve.
