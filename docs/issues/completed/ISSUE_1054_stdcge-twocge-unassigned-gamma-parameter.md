# stdcge / twocge: Unassigned Parameter `gamma` in MCP ($66 Error)

**GitHub Issue:** [#1054](https://github.com/jeffreyhorn/nlp2mcp/issues/1054)
**Status:** FIXED
**Severity:** High — path_syntax_error, model fails to compile
**Date:** 2026-03-11
**Fixed:** 2026-03-12
**Affected Models:** stdcge, twocge

---

## Problem Summary

The stdcge and twocge models' generated MCP files declare the parameter `gamma` but never assign its values. GAMS reports error $66 ("Use of a symbol that has not been defined or assigned") when the stationarity equations reference `gamma`.

Both models are CGE (Computable General Equilibrium) models that share the same Armington function structure and the same root cause.

---

## Error Details

GAMS compilation error (stdcge):
```
Solve mcp_model using MCP;
                           $66,256
****  66  Use of a symbol that has not been defined or assigned
**** 256  Error(s) in analyzing solve statement.
**** The following MCP errors were detected in model mcp_model:
****  66 equation stat_d.. symbol "gamma" has no values assigned
```

GAMS compilation error (twocge):
```
Solve mcp_model using MCP;
                           $66,256
****  66 equation stat_d.. symbol "gamma" has no values assigned
```

---

## Root Cause

In the original GAMS models, `gamma(i)` is a **computed parameter** — its values are assigned via a formula after declaration:

**stdcge:**
```gams
Parameter gamma(i) 'scale par. in Armington func.';
gamma(i) = Q0(i) / (deltam(i)*M0(i)**eta(i) + deltad(i)*D0(i)**eta(i))**(1/eta(i));
```

**twocge:**
```gams
Parameter gamma(i,r) 'scale par. in Armington func.';
gamma(i,r) = Q0(i,r) / (deltam(i,r)*M0(i,r)**eta(i) + deltad(i,r)*D0(i,r)**eta(i))**(1/eta(i));
```

The parser treats `gamma(i)` as `Call(func="gamma", args=(SymbolRef("i"),))` — a function call — rather than `ParamRef("gamma", ("i",))`. The `_collect_model_relevant_params()` function in `emit_gams.py` only checked for `ParamRef` nodes when walking equation expressions. Since `gamma` was referenced via a `Call` node, it was classified as "non-model-relevant" and excluded from the emitted computed parameter assignments.

---

## Fix

**File:** `src/emit/emit_gams.py` — `_collect_model_relevant_params()` (~line 99-108)

Added detection of `Call` nodes whose `func` attribute matches a declared parameter name:

```python
param_names_lower = {p.lower() for p in model_ir.params}

def _walk(expr: Expr) -> None:
    if isinstance(expr, ParamRef):
        referenced.add(expr.name.lower())
    # Issue #1054: Parameters referenced via Call nodes (parser treats
    # param(i) as a function call when not resolved to ParamRef).
    elif isinstance(expr, Call) and expr.func.lower() in param_names_lower:
        referenced.add(expr.func.lower())
    for child in expr.children():
        _walk(child)
```

This ensures that parameters like `gamma` are correctly identified as model-relevant regardless of whether the parser represents them as `ParamRef` or `Call` nodes. Their computed assignment statements are then emitted in the MCP output.

---

## Verification

- **stdcge:** Compiles and solves optimally (MODEL STATUS 1, obj=25.508)
- **twocge:** Compiles without $66 error (MODEL STATUS 5 — locally infeasible is a pre-existing issue #970)
- **Quality gate:** 4141 tests pass, typecheck/lint/format all clean
- **Integration test:** `TestCallBasedParameterDetection::test_stdcge_gamma_assignment_emitted` verifies the gamma assignment appears in the MCP output

---

## Related

- #970 twocge MCP locally infeasible (different issue — about KKT correctness)
- #906 twocge missing USA SAM post-solve trade equations (different issue)
- #1036 model-relevant parameter filtering (original implementation that this fix extends)
