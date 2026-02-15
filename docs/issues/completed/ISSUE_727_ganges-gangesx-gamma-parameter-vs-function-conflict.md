# Derivative: Parameter 'gamma' Misidentified as Built-in gamma() Function (ganges, gangesx)

**GitHub Issue:** [#727](https://github.com/jeffreyhorn/nlp2mcp/issues/727)
**Status:** Resolved
**Severity:** High -- Blocks MCP translation of ganges and gangesx models
**Discovered:** 2026-02-14 (Sprint 19, after Issue #723 fixed dynamic subset empty domain)
**Resolved:** 2026-02-15 (Sprint 19)
**Affected Models:** ganges, gangesx (and any model using a parameter named after a built-in function)

---

## Problem Summary

The ganges and gangesx models fail during MCP translation with the error:

```
Error: Invalid model - gamma() expects 1 argument, got 2
```

The model declares a parameter `gamma(i,r)` (a table of per capita committed consumption values), but the derivative engine in `src/ad/derivative_rules.py` treats any `Call` node with `func == "gamma"` as the built-in GAMS `gamma()` mathematical function (Euler's gamma function), which takes exactly 1 argument. When the parameter `gamma(i,r)` appears in an equation, it is represented as a `Call("gamma", (i, r))` AST node with 2 arguments, triggering the arity check error.

---

## Reproduction

**Models:** `ganges` and `gangesx` (`data/gamslib/raw/ganges.gms`, `data/gamslib/raw/gangesx.gms`)

**Command:**
```bash
python -m src.cli data/gamslib/raw/ganges.gms -o /tmp/ganges_mcp.gms --skip-convexity-check
python -m src.cli data/gamslib/raw/gangesx.gms -o /tmp/gangesx_mcp.gms --skip-convexity-check
```

**Error output (before fix, both models):**
```
Error: Invalid model - gamma() expects 1 argument, got 2
```

---

## Root Cause

### AST representation ambiguity

Parameter references with indices and function calls share the same `Call` AST node type. A `Call("gamma", (i, r))` could mean either:
- The parameter `gamma` indexed by `(i, r)` -- what the model intends
- The built-in function `gamma()` called with 2 arguments -- what the derivative engine assumed

### The name collision in the derivative engine

In `src/ad/derivative_rules.py`, the `_diff_call` function dispatched on function name without checking whether the name was a declared parameter:

```python
elif func in ("gamma", "loggamma"):
    if len(expr.args) != 1:
        raise ValueError(f"{func}() expects 1 argument, got {len(expr.args)}")
```

---

## Resolution

Added a symbol table check at the top of `_diff_call()`: before matching against built-in function names, consult `config.model_ir.params` to determine if the `Call` node represents a parameter reference. If so, return `Const(0.0)` (derivative of a constant parameter w.r.t. a variable is always zero).

### Files Changed

1. **`src/ad/derivative_rules.py`**:
   - Added parameter vs function disambiguation check at the top of `_diff_call()`
   - Uses `config.model_ir.params` (CaseInsensitiveDict) for lookup
   - Gracefully handles missing config or model_ir (falls through to existing behavior)

2. **`tests/unit/ad/test_ad_core.py`**:
   - Added `TestParameterFunctionDisambiguation` test class with 4 tests:
     - `test_gamma_param_returns_zero`: gamma(i,r) as param returns Const(0)
     - `test_gamma_builtin_still_errors_without_model_ir`: no config preserves existing behavior
     - `test_gamma_builtin_still_errors_when_not_a_param`: gamma not in params still errors
     - `test_case_insensitive_param_lookup`: case-insensitive matching (GAMS convention)

### Post-fix status

Both ganges and gangesx models now translate successfully to MCP format (1446 lines each). Non-blocking warnings about SetMembershipTest evaluation remain but do not affect output.

---

## Additional Notes

- This fix applies to any built-in function name that collides with a user-declared parameter (gamma, beta, normal, etc.)
- The fix is minimal and targeted: it only affects the derivative dispatch, not the AST representation
- Existing tests for actual gamma/loggamma differentiation errors (Issue #676) continue to pass since they don't provide a model_ir with a gamma parameter
