# NaN Parameter Validation Rejects `na` Special Value in Parsed Data

**GitHub Issue:** [#751](https://github.com/jeffreyhorn/nlp2mcp/issues/751)
**Status:** Open
**Severity:** Medium - Blocks 2 GAMSLib models (tforss, lands)
**Date:** 2026-02-13

---

## Problem Summary

After Sprint 19 Day 3 added grammar support for GAMS special values (`na`, `inf`, `eps`, `undf`) in scalar and parameter data blocks, models containing `na` values now parse successfully through the grammar stage but fail in the numerical validation stage. The `validate_parameter_values()` function in `src/validation/numerical.py` rejects any parameter value that is not finite (NaN or Inf), but GAMS's `na` (Not Available) is a legitimate sentinel value that maps to NaN internally.

---

## Affected Models

### tforss.gms

**Error:**
```
Error: Numerical error in parameter 'rho': Invalid value (value is NaN)
```

**Source (line 79):**
```gams
Scalar
   mup     'planting cost          (us$ per ha)' / 150.0 /
   muc     'cutting cost           (us$ per m3)' /   7.0 /
   life    'plant life                  (years)' /  30   /
   rho     'discount rate'                       /    na /;
```

The scalar `rho` is initialized to `na` (Not Available). In the original GAMS model, `rho` is later computed via an assignment statement (e.g., `rho = ...;`). The `na` value is a placeholder indicating "to be computed later."

### lands.gms

**Error:**
```
Error: Numerical error in parameter 'd[mode-1]': Invalid value (value is NaN)
```

**Source (line 32):**
```gams
Parameter
   c(i) 'investment cost' / plant-1 10, plant-2 7, plant-3 16, plant-4 6 /
   d(j) 'energy demand'   / mode-1  na, mode-2 3,  mode-3 2              /;
```

The parameter `d('mode-1')` is set to `na`. In the original GAMS model, `d('mode-1')` is later assigned a computed value. The `na` is a placeholder.

---

## Reproduction

```bash
# tforss
python -m src.cli data/gamslib/raw/tforss.gms --diagnostics

# lands
python -m src.cli data/gamslib/raw/lands.gms --diagnostics
```

Both will report `Numerical error ... Invalid value (value is NaN)`.

---

## Root Cause

**File:** `src/validation/numerical.py`, lines 37-62

The `validate_parameter_values()` function uses `math.isfinite(value)` to check all parameter values. `math.isfinite()` returns `False` for both NaN and Inf. While Inf from division-by-zero or overflow is genuinely problematic, NaN from an explicit `na` assignment is a legitimate GAMS pattern — it represents a placeholder value that will be overwritten by a later assignment statement before the model is solved.

The current validation makes no distinction between:
1. **Intentional `na`** — explicitly assigned by the modeler as a placeholder
2. **Accidental NaN** — from uninitialized parameters or bad arithmetic

---

## Suggested Fix

### Option A: Track `na` provenance (recommended)

When parsing `na` special values, mark the parameter entry with a provenance flag indicating it was explicitly set to `na`. During validation, skip entries with this flag. If the parameter is later overwritten by an assignment statement, the flag is irrelevant. If it reaches the MCP stage still as `na`, emit a warning rather than an error.

### Option B: Skip validation for parameters with later assignments

Before running numerical validation, check if the parameter has a computed assignment expression in `model_ir.params[name].expressions`. If it does, the data value is just an initial value that will be overwritten, so NaN is acceptable.

### Option C: Relax validation to warning

Change `validate_parameter_values()` to emit a warning for NaN values instead of raising `NumericalError`. This is the simplest fix but loses the guardrail for genuinely problematic NaN values.

### Option D: Only validate parameters used directly in the model

Skip validation for parameters that have computed expressions (since those expressions will produce the actual runtime values). Only validate parameters whose values are used as-is (no expressions defined).

---

## Technical Details

- **Grammar fix:** Already complete (Sprint 19 Day 3, PR #750)
- **Parser fix:** Already complete — `na` correctly maps to `float('nan')` via `GAMS_SPECIAL_VALUES` dict in `src/ir/parser.py:121`
- **Validation:** `src/validation/numerical.py:37-62` — `validate_parameter_values()` raises `NumericalError` for any non-finite value
- **GAMS semantics:** `na` is GAMS's "Not Available" marker. It is commonly used as a placeholder in data declarations when the actual value will be computed later via assignment statements.

---

## Files to Modify

| File | Change |
|------|--------|
| `src/validation/numerical.py` | Update `validate_parameter_values()` to allow NaN from explicit `na` |
| `src/ir/parser.py` | Possibly add provenance tracking for `na` values |
| `tests/unit/test_numerical_validation.py` | Add tests for `na` parameter handling |
