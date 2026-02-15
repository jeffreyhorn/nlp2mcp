# Parser: Model Attribute Assignment Fails for Multiple Model Declarations (lop)

**GitHub Issue:** [#729](https://github.com/jeffreyhorn/nlp2mcp/issues/729)
**Status:** Open
**Severity:** High -- Blocks parsing of lop model
**Discovered:** 2026-02-15 (Sprint 19, after Issue #726 fixed multi-dimensional set index expansion)
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

**Error output:**
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

And multiple solve statements:

```
Line 151: solve sp minimzing spobj using lp;
Line 265: solve lopdt maximizing obj using mip;
Line 325: solve ilp minimizing obj using mip;
Line 367: solve evaldt maximizing obj using lp;
Line 379: solve evaldt maximizing obj using lp;
```

### Parser's single-model tracking

In `src/ir/parser.py`, the `ModelIR` dataclass has:
- `declared_model: str | None` -- stores only the first model name
- `model_name: str | None` -- stores the model name from solve statements

When validating attribute access (e.g., `ilp.optCr = 0`), the parser checks at line ~3266:

```python
if (
    base_name not in self.model.variables
    and base_name not in self.model.params
    and base_name not in self.model.equations
    and base_name != self.model.declared_model
):
    raise self._error(
        f"Symbol '{base_name}' not declared as a variable, parameter, equation, or model",
        target,
    )
```

Since `self.model.declared_model` is `"sp"` (the first model), `ilp != sp` evaluates to True, and the error is raised.

The same check exists for `attr_access_indexed` at line ~3283.

---

## Fix Approach

Replace the single `declared_model` model-name check with a set of all declared model names. Options:

1. **Track all model names in a set**: Add a `declared_models: set[str]` field to `ModelIR` (or use a `CaseInsensitiveDict`), populated each time a `Model` statement is parsed. Update the validation checks to use `base_name in self.model.declared_models`.

2. **Minimal fix**: Change `declared_model` to a `set[str]` and add each model name to it. Update the two attribute-access validation checks at lines ~3266 and ~3283.

Either way, the model attribute assignments (`ilp.optCr`, `ilp.resLim`) should be silently accepted and skipped (as they are for the first model), since they control solver behavior that's irrelevant to MCP translation.

---

## Additional Context

- The `ilp.optCr = 0` and `ilp.resLim = 100` are solver option assignments that set the optimality gap tolerance and time limit. These are runtime directives that don't affect the mathematical model structure.
- The parser already handles attribute assignments for the first declared model by returning early (no-op). The same behavior should apply to all declared models.
- Even after this fix, the lop model may encounter additional issues downstream since it uses MIP (mixed-integer programming) models and multiple solve statements, which may not be supported by the NLP-to-MCP pipeline.
- GAMS files with multiple models and sequential solves are common in benchmarking and comparison scenarios (as lop does: comparing DT, ILP, and EvalDT approaches).
