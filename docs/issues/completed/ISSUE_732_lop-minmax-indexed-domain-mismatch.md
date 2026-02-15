# Min/Max Reformulation: Auxiliary Variables Ignore Equation Domain (lop)

**GitHub Issue:** [#732](https://github.com/jeffreyhorn/nlp2mcp/issues/732)
**Status:** Fixed
**Severity:** High -- Blocks MCP translation of lop model
**Discovered:** 2026-02-15 (Sprint 19, after Issue #729 fixed multi-model attribute assignment)
**Fixed:** 2026-02-13 (Sprint 19)
**Affected Models:** lop (and any model using `min()` or `max()` inside indexed equations)

---

## Problem Summary

The lop model fails during normalization with:

```
Error: Invalid model - Domain mismatch during normalization
```

After parsing succeeds (Issue #729 fixed), the min/max reformulation pass in `src/kkt/reformulation.py` replaces `min()`/`max()` calls with scalar auxiliary variables (`domain=()`), even when the `min()`/`max()` appears inside an indexed equation. The replacement `VarRef` has no domain attributes, causing `_merge_domains()` in `src/ir/normalize.py` to fail when it tries to merge `('s1', 's2')` with `None`.

---

## Reproduction

**Model:** `lop` (`data/gamslib/raw/lop.gms`)

**Command:**
```bash
python -m src.cli data/gamslib/raw/lop.gms -o /tmp/lop_mcp.gms --skip-convexity-check
```

**Error output (before fix):**
```
Error: Invalid model - Domain mismatch during normalization
```

---

## Root Cause

Three interrelated issues in `src/kkt/reformulation.py`:

### 1. Scalar auxiliary variables for indexed equations

The reformulation code created auxiliary variables with `domain=()` (scalar) regardless of the equation domain. `reformulate_min()`, `reformulate_max()`, and `reformulate_model()` all hardcoded empty domains for `VarRef`, `VariableDef`, and `EquationDef` objects.

### 2. Domain attributes lost during AST replacement

`_replace_min_max_call()` creates new `Binary`, `Unary`, `Call`, and `Sum`/`Prod` nodes when recursing through the expression tree. These new nodes lost the `domain`, `free_domain`, and `rank` attributes that the normalization pass had set on the original nodes via `object.__setattr__()`.

### 3. Strategy 1 over-eager substitution

`apply_strategy1_objective_substitution()` replaced intermediate variable references in ALL equations, not just objective-defining equations. For lop, `dt` is in the objective chain, so `sumbound`'s `... =e= dt(s2,s3)` had its RHS replaced with `VarRef(aux_min_dtlimit_0, ())` even though `sumbound` is an unrelated constraint.

---

## Fix

Three changes in `src/kkt/reformulation.py`:

### 1. Propagate equation domain to auxiliary variables

Added `eq_domain: tuple[str, ...] = ()` parameter to `reformulate_min()` and `reformulate_max()`. The caller (`reformulate_model()`) passes `eq_domain=eq_def.domain`. All created `VarRef`, `VariableDef`, and `EquationDef` objects now use the equation's domain instead of `()`.

### 2. Preserve domain attributes in `_replace_min_max_call()`

Added `_copy_domain_attrs()` helper that copies `domain`, `free_domain`, and `rank` attributes from original nodes to newly created nodes using `object.__setattr__()`.

### 3. Scope Strategy 1 to objective-chain equations only

`apply_strategy1_objective_substitution()` now uses `_build_variable_definitions()` to identify which equations define objective-chain variables and only substitutes in those equations. Also copies domain attributes from the original `VarRef` to the replacement.

---

## Additional Context

- After this fix, lop advances past normalization but hits: `Differentiation not yet implemented for function 'sameas'`
- The lop model is a Line Optimization Problem that compares DT, ILP, and EvalDT solution approaches
- It uses multiple `Model` and `Solve` statements (Issue #729 addressed the multi-model parsing)
