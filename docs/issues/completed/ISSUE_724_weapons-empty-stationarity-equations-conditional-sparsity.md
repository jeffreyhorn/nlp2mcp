# KKT: Empty Stationarity Equations from Conditional Equation Sparsity (weapons)

**GitHub Issue:** [#724](https://github.com/jeffreyhorn/nlp2mcp/issues/724)
**Status:** Fixed
**Severity:** High — Generated MCP code fails GAMS compilation; 35 EXECERROR instances
**Discovered:** 2026-02-13 (Sprint 19, after Issue #720 fixed the AD condition preservation)
**Fixed:** 2026-02-13 (Sprint 19)
**Affected Models:** weapons

---

## Problem Summary

After the Issue #720 fix (preserving dollar conditions on sum collapse and fixing the condition evaluator), the weapons model now generates MCP code that compiles but fails with 35 instances of:

```
**** MCP pair stat_x.x has empty equation but associated variable is NOT fixed
```

The root cause is that the stationarity equations `stat_x(w,t)` are generated for ALL `(w,t)` pairs, but many `(w,t)` combinations have `td(w,t) = 0`, making all terms in the stationarity equation evaluate to zero. GAMS treats these as "empty" equations, yet the paired variable `x(w,t)` is not fixed to zero, causing the MCP pairing to fail.

---

## Reproduction

**Model:** `weapons` (`data/gamslib/raw/weapons.gms`)

**Command:**
```bash
python -m src.cli data/gamslib/raw/weapons.gms -o /tmp/weapons_mcp.gms
gams /tmp/weapons_mcp.gms
```

**GAMS output (35 errors):**
```
**** MCP pair stat_x.x has empty equation but associated variable is NOT fixed
     x(ICBM,2)
... (35 total instances)
**** SOLVE from line 140 ABORTED, EXECERROR = 35
```

---

## Root Cause Analysis

Three interrelated bugs were identified:

### Bug 1: `_diff_prod` didn't handle index-aware differentiation

In `src/ad/derivative_rules.py`, the `_diff_prod()` function used the logarithmic derivative:

```
d(prod(i, f(i)))/dx = prod(i, f(i)) * sum(i, df(i)/dx / f(i))
```

When differentiating with concrete `wrt_indices` (e.g., `x('ICBM','1')`), the body differentiation compared `x(w,t)` against `x('ICBM','1')`. Since `w != 'ICBM'`, it returned 0, producing `sum(w$(td(w,t)), 0)` in the generated code. The existing `_diff_sum` already handled this via `_sum_should_collapse` and `_partial_index_match`, but `_diff_prod` did not.

### Bug 2: `power()` with variable exponents

The general power derivative rule created `Call("power", (base, variable_exponent))`, but GAMS `power(base, exp)` requires `exp` to be a constant. Variable exponents must use `base ** exp` syntax.

### Bug 3: Missing dollar conditions on stationarity equations

Even with correct derivatives, `stat_x(w,t)` was generated for ALL `(w,t)` pairs. When `td(w,t) = 0`, all terms evaluate to zero, creating empty equations. GAMS MCP requires every variable to be paired with a non-empty equation or be fixed.

---

## Fix

### Sub-fix 1: Index-aware `_diff_prod` (`src/ad/derivative_rules.py`)

Added index remapping logic to `_diff_prod` mirroring what `_diff_sum` does. When `wrt_indices` contains concrete instances of prod-bound symbolic indices, the concrete indices are replaced with the symbolic prod indices before body differentiation. This uses the existing `_sum_should_collapse` (exact match) and `_partial_index_match` (partial match) helper functions.

### Sub-fix 2: `Binary("**")` for variable exponents (`src/ad/derivative_rules.py`, `src/emit/expr_to_gams.py`, `src/ad/evaluator.py`)

Changed the general power derivative case from `Call("power", (base, exponent))` to `Binary("**", base, exponent)`. Added a safety net in `expr_to_gams.py` to convert `power()` calls with non-constant exponents to `**` syntax. Added `**` operator support in the evaluator alongside `^`.

### Sub-fix 3: Variable access condition detection (`src/kkt/stationarity.py`, `src/kkt/kkt_system.py`, `src/emit/emit_gams.py`)

1. **`_find_variable_access_condition()`** in `stationarity.py`: Walks all model equations to detect the common dollar condition under which a variable is accessed. For `x(w,t)` in weapons, this correctly identifies `td(w,t)` as the condition — every equation that references `x(w,t)` does so inside `sum(w$(td(w,t)), ...)` or similar conditioned aggregations.

2. **Dollar condition on stationarity equations**: The detected condition is applied to the stationarity equation: `stat_x(w,t)$(td(w,t))..`, so it only generates for `(w,t)` pairs where `td(w,t) > 0`.

3. **`.fx` statements for excluded instances** in `emit_gams.py`: For variable instances excluded by the condition, emit `.fx` statements to fix them to their lower bound (e.g., `x.fx(w,t)$(not (td(w,t))) = 0;`). Also handles multipliers whose complementarity equation has a condition (e.g., `lam_minw.fx(t)$(not (tm(t))) = 0;`).

4. **`stationarity_conditions` field** added to `KKTSystem` dataclass in `kkt_system.py` to propagate condition information from stationarity construction to the emitter.

### Files Modified

| File | Change |
|------|--------|
| `src/ad/derivative_rules.py` | Index-aware `_diff_prod`; `Binary("**")` for variable exponents |
| `src/ad/evaluator.py` | Added `**` operator support |
| `src/emit/expr_to_gams.py` | Safety net: `power()` with variable exponent → `**` |
| `src/emit/emit_gams.py` | `.fx` emission for conditioned stationarity equations and multipliers |
| `src/kkt/stationarity.py` | `_find_variable_access_condition()`, condition on stationarity equations |
| `src/kkt/kkt_system.py` | `stationarity_conditions` field on `KKTSystem` |
| `tests/unit/ad/test_transcendental.py` | Updated test to expect `Binary("**")` |

---

## Verification

After fix, the weapons model:
- Generates valid MCP code with no empty stationarity equations
- Solves with Normal Completion, Model Status 1 (Optimal)
- 0 EXECERROR instances

Quality gate:
- Typecheck: 0 errors
- Lint: All checks passed
- Format: 268 files unchanged
- Tests: 3315 passed, 10 skipped, 1 xfailed
