# Parser: Model Attribute Assignment Fails for Multiple Model Declarations (lop)

**GitHub Issue:** [#729](https://github.com/jeffreyhorn/nlp2mcp/issues/729)
**Status:** Resolved
**Severity:** High -- Blocks parsing of lop model
**Discovered:** 2026-02-15 (Sprint 19, after Issue #726 fixed multi-dimensional set index expansion)
**Resolved:** 2026-02-15 (Sprint 19)
**Affected Models:** lop (and any model with multiple Model declarations and model attribute assignments)

---

## Problem Summary

The lop model fails to parse with the error:

```
Error: Invalid model - Symbol 'ilp' not declared as a variable, parameter, equation, or model [context: expression] (line 312, column 1)
```

The parser tracks only a single `declared_model` name (the first `Model` statement encountered). When a model file contains multiple `Model` declarations (lop has 7), attribute assignments like `ilp.optCr = 0` for non-first models fail because the parser doesn't recognize `ilp` as a model name.

---

## Reproduction

**Model:** `lop` (`data/gamslib/raw/lop.gms`)

**Command:**
```bash
python -m src.cli data/gamslib/raw/lop.gms -o /tmp/lop_mcp.gms
```

**Error output (before fix):**
```
Error: Invalid model - Symbol 'ilp' not declared as a variable, parameter, equation, or model [context: expression] (line 312, column 1)
```

---

## Root Cause

### Multiple Model declarations in lop.gms

The lop model declares 7 models across the file:

```
Line 149: Model sp 'shortest path model' / balance, defspobj /;
Line 231: Model dtlop:
Line 259: Model lopdt / deffreqlop, dtlimit, defobjdtlop /;
Line 273: Model ILP:
Line 317: Model ilp / defobjilp, deffreqilp, defloadilp, oneilp, couplexy /;
Line 336: Model EvalDT:
Line 361: Model evaldt / dtllimit, sumbound, defobjdtlop /;
```

### Parser's single-model tracking

In `src/ir/model_ir.py`, the `ModelIR` dataclass had:
- `declared_model: str | None` -- stored only the first model name

When validating attribute access (e.g., `ilp.optCr = 0`), the parser checked `base_name != self.model.declared_model`. Since `declared_model` was `"sp"` (the first model), `ilp != sp` was True, and the error was raised.

---

## Resolution

Replaced the single `declared_model` string with a `declared_models: set[str]` that tracks all model names (lowercase, for case-insensitive matching consistent with GAMS semantics). Added a backward-compatible `declared_model` property that returns the first declared model name.

### Files Changed

1. **`src/ir/model_ir.py`**:
   - Replaced `declared_model: str | None` field with `declared_models: set[str]` and `_first_declared_model: str | None`
   - Added `declared_model` property (getter returns first model, setter adds to set with lowercase)

2. **`src/ir/parser.py`**:
   - Updated 4 model handler methods (`_handle_model_all`, `_handle_model_with_list`, `_handle_model_decl`, `_handle_model_multi`) to use the setter which adds all model names to the set
   - Updated 2 attribute-access validation checks to use `base_name.lower() not in self.model.declared_models` instead of `base_name != self.model.declared_model`
   - `_handle_model_multi` now registers all model names from multi-model declarations, not just the first

3. **`tests/unit/test_model_sections.py`**:
   - Added `TestMultiModelAttributeAccess` class with 2 tests:
     - `test_attr_on_second_model`: attribute assignment on non-first model
     - `test_attr_case_insensitive_model`: Model declared as `ILP`, accessed as `ilp`
   - Updated `test_multiple_model_statements` to verify both models tracked in `declared_models`
   - Updated `test_model_name_case_sensitive` → `test_model_name_case_insensitive` (GAMS is case-insensitive)

### Post-fix status

The lop model now parses past the `ilp.optCr = 0` lines. It encounters a separate downstream error ("Domain mismatch during normalization") which is unrelated to this issue.

---

## Additional Context

- The `ilp.optCr = 0` and `ilp.resLim = 100` are solver option assignments that set the optimality gap tolerance and time limit. These are runtime directives that don't affect the mathematical model structure.
- The parser already handles attribute assignments for the first declared model by returning early (no-op). The same behavior now applies to all declared models.
- GAMS files with multiple models and sequential solves are common in benchmarking and comparison scenarios (as lop does: comparing DT, ILP, and EvalDT approaches).
