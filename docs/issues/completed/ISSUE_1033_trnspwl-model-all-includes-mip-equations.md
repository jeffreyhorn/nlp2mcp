# trnspwl: `Model / all /` includes MIP equations — MCP reformulation scope not filtered by solve statement

**GitHub Issue:** [#1033](https://github.com/jeffreyhorn/nlp2mcp/issues/1033)
**Status:** FIXED
**Severity:** High — produces incorrect MCP formulation with discrete variables (GAMS Error 65)
**Date:** 2026-03-10
**Fixed:** 2026-03-10
**Affected Models:** trnspwl (GAMSlib SEQ=351), potentially any multi-model file

---

## Problem Summary

The trnspwl model defines **three separate GAMS models** in one file:

1. `Model transport / all /;` — pure NLP with `cost`, `supply`, `demand` (lines 96–107)
2. `Model trnsdiscA / supply, demand, defsos1, defsos2, defsos3, defobjdisc /;` — MIP with SOS2 (line 165)
3. `Model trnsdiscB / supply, demand, defx, defsqrt, defseg, defgs, defobjdisc /;` — MIP with Binary (line 218)

The first solve is `solve transport using nlp minimizing z;` (line 119). The NLP model `transport` only uses continuous variables (`x`, `z`) and three equations (`cost`, `supply`, `demand`).

However, our pipeline generated an MCP formulation that included **all** equations and variables from the entire file — including SOS2 variable `xs`, Binary variable `gs`, and equations from formulations A and B. This caused GAMS Error 65 ("discrete variable not allowed").

---

## Fix

### 1. Per-model equation map (`src/ir/parser.py`, `src/ir/model_ir.py`)

Added `model_equation_map: dict[str, list[str]]` to `ModelIR` — stores equation list snapshots per model name (lowercase). Populated in:
- `_handle_model_all()`: snapshots `list(self.model.equations.keys())` at declaration point
- `_handle_model_with_list()`: stores explicit equation refs or snapshot for `/all/`
- `_handle_model_multi()`: stores per-item equation lists

### 2. Equation filtering in normalization (`src/ir/normalize.py`)

`normalize_model()` now looks up the solved model's equation set from `model_equation_map` (falling back to `model_equations`). Equations not in the set are excluded from normalization and KKT assembly.

### 3. Variable filtering (`src/ir/normalize.py`)

Added `_collect_vars_in_equations()` helper. After equation filtering, variables not referenced in any included equation or objective are removed from `ir.variables`.

### 4. Objective-defining equation scoping (`src/ir/normalize.py`, `src/kkt/objective.py`)

Both `_extract_objective_expression()` and `extract_objective_info()` now respect the model equation filter. For multi-model files (e.g., himmel16 with `small / obj1 /` and `large / obj2, areadef /`), the correct objective-defining equation is selected based on the solved model.

### Verification

```
$ python -m src.cli data/gamslib/raw/trnspwl.gms -o /tmp/trnspwl_mcp.gms
$ gams /tmp/trnspwl_mcp.gms
# PATH solution found, Normal completion, residual 9.6e-07
```

MCP now contains only `cost`, `supply`, `demand` equations and `x(i,j)`, `z` variables. No discrete variables.

---

## Affected Files

| File | Change |
|------|--------|
| `src/ir/model_ir.py` | Added `model_equation_map` field |
| `src/ir/parser.py` | Populate `model_equation_map` in model declaration handlers |
| `src/ir/normalize.py` | Equation/variable filtering by model membership; objective extraction scoping |
| `src/kkt/objective.py` | Objective-defining equation filtered by model equation set |
| `tests/integration/emit/test_fx_complementarity.py` | Updated ps3_s_scp test for correct model scoping |
| `tests/e2e/test_gamslib_match.py` | Updated himmel16 reference value |
