# Derivative: Parameter 'gamma' Misidentified as Built-in gamma() Function (ganges, gangesx)

**GitHub Issue:** [#727](https://github.com/jeffreyhorn/nlp2mcp/issues/727)
**Status:** Open
**Severity:** High -- Blocks MCP translation of ganges and gangesx models
**Discovered:** 2026-02-14 (Sprint 19, after Issue #723 fixed dynamic subset empty domain)
**Affected Models:** ganges, gangesx (and any model using a parameter named `gamma`)

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

**Error output (both models):**
```
Error: Invalid model - gamma() expects 1 argument, got 2
```

The models parse and validate successfully. The error occurs during the "Computing derivatives..." stage (constraint Jacobian computation).

---

## Root Cause

### The ganges model's parameter declaration

In `data/gamslib/raw/ganges.gms`, line 220:

```gams
Table gamma(i,r) 'per capita committed consumption (units)'
```

This `gamma` is a 2-dimensional parameter (table), not the built-in `gamma()` function. It is used in equations like:

```gams
les(i,r)..    pc(i)*ch(i,r) =e= pop(r)*(pc(i)*gamma(i,r)
                             +  ac(i,r)*(mc(r) - sum(j, pc00(j)*gamma(j,r)))

utildef(r).. util(r)*pop(r) =e= prod(i, (ch(i,r)-gamma(i,r)*pop(r))**ac(i,r));
```

### The name collision in the derivative engine

In `src/ad/derivative_rules.py`, line 575:

```python
elif func in ("gamma", "loggamma"):
    # Check arity first for consistent error semantics with other functions
    if len(expr.args) != 1:
        raise ValueError(f"{func}() expects 1 argument, got {len(expr.args)}")
```

The derivative dispatch matches on `func == "gamma"` without first checking whether the AST node represents a parameter reference or a built-in function call. When differentiating the `utildef` equation (which contains `gamma(i,r)`), the engine encounters a `Call("gamma", (i, r))` node, checks the arity (2 != 1), and raises the error.

### AST representation ambiguity

The core issue is that parameter references with indices and function calls share the same `Call` AST node type. A `Call("gamma", (i, r))` could mean either:
- The parameter `gamma` indexed by `(i, r)` -- what the model intends
- The built-in function `gamma()` called with 2 arguments -- what the derivative engine assumes

The derivative engine should check whether `gamma` is a declared parameter in the model before treating it as a built-in function.

---

## Fix Approach

The derivative dispatch in `_diff_call()` (or wherever function names are resolved) should consult the model's symbol table before dispatching to built-in function derivative rules. If the name corresponds to a declared parameter, it should be treated as a `ParamRef` (parameter reference) rather than a function call, and differentiated accordingly (derivative of a parameter w.r.t. a variable is 0, since parameters are constants).

Possible approaches:

1. **Check symbol table in derivative dispatch**: Before matching `func` against built-in function names, check if `func` is a declared parameter in `model_ir.params`. If so, return `Const(0)` (derivative of a constant parameter is zero).

2. **Fix at the AST/IR level**: Ensure that parameter references are represented as `ParamRef` nodes rather than `Call` nodes during IR construction, so they never reach the function derivative dispatch.

3. **Fix in the parser/semantic analysis**: When building the AST, resolve whether an identifier followed by `(...)` is a function call or a parameter reference based on the symbol table, and produce the appropriate node type.

Approach 2 or 3 would be the most robust, preventing the ambiguity from propagating through the pipeline.

---

## Additional Notes

- The ganges and gangesx models also show warnings about `SetMembershipTest` evaluation failures and dynamic subset fallbacks, but these are non-blocking (they include instances by default)
- GAMS has many built-in function names (`gamma`, `beta`, `normal`, etc.) that could collide with user-declared parameter names
- The `gamma` parameter is used in multiple equations (les, utildef, hbudget, ch.l initialization), so the collision is triggered as soon as any of these equations are differentiated
- Both ganges and gangesx share the same model structure and parameter names, so the fix will apply to both
