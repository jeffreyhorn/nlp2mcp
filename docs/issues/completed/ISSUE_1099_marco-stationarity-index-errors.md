# marco: Stationarity Equation Index Errors ($148/$170/$171)

**GitHub Issue:** [#1099](https://github.com/jeffreyhorn/nlp2mcp/issues/1099)
**Model:** marco (GAMSlib SEQ=165)
**Status:** FIXED
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
3. **$170 — `qs("lim",cf,q)`**: The first index is the string literal `"lim"` instead of the set variable `lim`. Should be `qs("upper",cf,q)` preserving the equation condition literal.

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

Two bugs in `src/kkt/stationarity.py`:

1. **`_compute_index_offset_key()`** used element-value string matching to determine which variable dimensions correspond to which equation dimensions. This fails when independent sets share element labels (e.g., "hydro" in both `m` and `p`) or when multiple subsets of the same parent set create ambiguous matches (e.g., `cf`, `cr`, `ci` all subsets of `c`). Fix: replaced with domain/alias-based matching using `_resolve_alias_target()` with a two-pass approach (exact canonical match first, then root/parent match).

2. **Multiplier reference construction** for dimension-mismatch cases used `matched_var_dims` (variable positions that matched equation positions) instead of `mult_domain` (the equation's own domain). This produced scalar or wrong-dimensional multiplier references. Fix: use `mult_domain` directly.

3. **`_replace_matching_indices()`** replaced concrete element literals (like `"upper"` from set `lim`) with the declared domain set name (`lim`) even when that set was completely independent of the equation domain. Fix: preserve the original index when the declared domain target is not in or a subset of the equation domain.

---

## Fix Details

**Files modified:**
- `src/kkt/stationarity.py`: Three changes:
  1. `_compute_index_offset_key()` (~line 2285): Domain-based matching with two-pass approach
  2. Multiplier reference construction (~line 2646): Use `mult_domain` for dim-mismatch
  3. `_replace_matching_indices()` (~line 1727): Preserve fixed literals from independent sets

**Verification:**
- GAMS compilation: 0 errors (was 7)
- MODEL STATUS 1 (Optimal)
- All 4209 tests pass, no regressions

---

## Impact

5 primary compilation errors. Model now compiles and solves successfully.
