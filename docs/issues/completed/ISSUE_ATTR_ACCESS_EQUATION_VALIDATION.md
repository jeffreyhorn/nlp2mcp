# Issue: attr_access/attr_access_indexed Does Not Validate Equations

**GitHub Issue:** [#558](https://github.com/jeffreyhorn/nlp2mcp/issues/558)  
**Status:** Closed (Fixed)  
**Priority:** Medium  
**Discovered:** Sprint 16 Day 6 (2026-01-23)  
**Affected Models:** apl1p

---

## Summary

The `attr_access` and `attr_access_indexed` handlers in the IR builder validate that the base symbol exists as a variable, parameter, or model, but they do not account for **equations**. In GAMS, equations can also have attributes like `.stage` set on them for stochastic programming.

This causes models like `apl1p` to fail during IR building with the error:
```
Symbol 'cmin' not declared as a variable, parameter, or model
```

Even though `cmin` is a valid equation declared in the model.

## Error Message

```
ParserSemanticError: Symbol 'cmin' not declared as a variable, parameter, or model [context: expression] (line 77, column 1)
```

## Reproduction Steps

1. Run parse on model `apl1p`:
   ```bash
   python scripts/gamslib/batch_parse.py --model apl1p --verbose
   ```

2. Or directly:
   ```python
   from src.ir.parser import parse_model_file
   parse_model_file('data/gamslib/raw/apl1p.gms')
   ```

## Example GAMS Code (from apl1p.gms)

```gams
* Equation declarations (lines 50-55)
Equation
   cost       'total cost'
   cmin(g)    'minimum capacity'
   cmax(g)    'maximum capacity'
   omax(g)    'maximum operating level'
   demand(dl) 'satisfy demand';

* ... equation definitions ...

* Setting decision stages (lines 74-81)
x.stage(g)       = 1;   * x is a variable - works
y.stage(g,dl)    = 2;   * y is a variable - works
s.stage(dl)      = 2;   * s is a variable - works
cmin.stage(g)    = 1;   * cmin is an EQUATION - fails!
cmax.stage(g)    = 1;   * cmax is an EQUATION - fails
omax.stage(g)    = 2;   * omax is an EQUATION - fails
demand.stage(dl) = 2;   * demand is an EQUATION - fails
```

## Root Cause Analysis

The handlers for `attr_access` and `attr_access_indexed` in `src/ir/parser.py` (lines 2793-2826) only validate against:
- `self.model.variables`
- `self.model.params`
- `self.model.declared_model`

They do not check `self.model.equations`, causing the validation to fail for equation attributes.

### Current Code (src/ir/parser.py:2812-2826)

```python
if target.data == "attr_access_indexed":
    # Handle indexed attribute access: x.stage(g), var.scale(i), etc.
    # Issue #554: Parse but don't process - stochastic programming not modeled
    # Validate that the base object exists (variable, parameter, or model)
    base_name = _token_text(target.children[0])
    if (
        base_name not in self.model.variables
        and base_name not in self.model.params
        and base_name != self.model.declared_model
    ):
        raise self._error(
            f"Symbol '{base_name}' not declared as a variable, parameter, or model",
            target,
        )
    return
```

## Proposed Fix

Add `self.model.equations` to the validation check in both `attr_access` and `attr_access_indexed` handlers:

```python
if target.data == "attr_access_indexed":
    base_name = _token_text(target.children[0])
    if (
        base_name not in self.model.variables
        and base_name not in self.model.params
        and base_name not in self.model.equations  # ADD THIS
        and base_name != self.model.declared_model
    ):
        raise self._error(
            f"Symbol '{base_name}' not declared as a variable, parameter, equation, or model",
            target,
        )
    return
```

The same fix should be applied to the `attr_access` handler (lines 2793-2811).

## Files to Modify

1. `src/ir/parser.py` - Add equations to validation in both handlers (~lines 2802-2810 and ~2817-2825)

## Testing

After fix, verify:
1. Model `apl1p` parses successfully (or fails at a later stage)
2. No regressions in existing 41 parsing models
3. Add unit test for equation attribute access

## Impact

- **Models affected:** apl1p (and likely apl1pca and other stochastic programming models)
- **Severity:** Medium - blocks parsing of stochastic programming models that set `.stage` on equations
- **Fix effort:** Low (~15 minutes)

## Related Issues

- Issue #554: x.stage() Stochastic Attribute Syntax Not Supported (closed - parsing fixed)
- PR #553: Sprint 16 Day 6 Parse Improvements

## References

- GAMS Documentation: [Stochastic Programming](https://www.gams.com/latest/docs/UG_EMP_SP.html)
- Model source: `data/gamslib/raw/apl1p.gms`
