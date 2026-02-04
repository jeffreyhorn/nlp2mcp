# Issue: Compile-Time Constants in Set Ranges Not Supported

**GitHub Issue:** #614
**GitHub URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/614
**Status:** Resolved
**Priority:** Medium
**Category:** Parser/Grammar
**Resolution:** Already working via `preprocess_gams_file()`. Added `preprocess_text()` for string-based usage.

## Summary

The parser does not support compile-time constants (e.g., `%N%`) within set range expressions. GAMS allows `$set` directives to define values that can be used in set ranges like `/n0*n%N%/`.

## Resolution

Upon investigation, the compile-time constant expansion **already works correctly** when using `parse_model_file()`, which calls `preprocess_gams_file()` to handle all preprocessing including `$set` directive expansion and `%variable%` substitution.

The original error occurred because:
1. The test was using `parse_model_text()` directly, which doesn't apply preprocessing
2. Files parsed via `parse_model_file()` work correctly

**Changes made:**
- Added `preprocess_text()` function to `src/ir/preprocessor.py` for direct string preprocessing
- This function performs the same preprocessing as `preprocess_gams_file()` but without file-based operations

**Usage:**
```python
# For files (already worked):
model = parse_model_file("model.gms")  # Preprocessing is automatic

# For strings (use preprocess_text first):
from src.ir.preprocessor import preprocess_text
preprocessed = preprocess_text(raw_gams_code)
model = parse_model_text(preprocessed)
```

**Note:** The `springchain.gms` model still fails to parse, but for a **different reason** - it uses square brackets `[...]` in parameter data blocks, which is a separate grammar limitation (not related to compile-time constants).

## Affected Models

- `springchain.gms` - Uses `%N%` in set range and parameter data

## Original Error Message

```
Error: Parse error at line 24, column 28: Unexpected character: '%'
  Set n "spring index"  /n0*n%N%/;
                             ^

Suggestion: This character is not valid in this context
```

## Reproduction

### Minimal Example
```gams
$set N 10
Set i / i1*i%N% /;
```

### From springchain.gms (lines 22-24)
```gams
$set N 100
$eval NM1 %N%-1
Set n "spring index"  /n0*n%N%/;
```

## Expected Behavior

1. The preprocessor should expand `%N%` to its defined value (e.g., `100`)
2. The resulting `Set n / n0*n100 /;` should parse correctly

## Current Behavior

The preprocessor may not be expanding compile-time constants in all contexts, or the grammar doesn't allow `%...%` within set element identifiers used in ranges.

## Analysis

### Preprocessor Status
The preprocessor in `src/ir/preprocessor.py` handles:
- `$set` directives to define variables
- `%var%` substitution in most contexts

However, the substitution may not be happening before the lexer tokenizes set member ranges.

### Grammar Status
The `range_bound` rule in `src/gams/gams_grammar.lark`:
```lark
range_expr: range_bound TIMES range_bound
range_bound: NUMBER | SET_ELEMENT_ID | STRING | ID
```

This doesn't include `compile_time_const` as a valid range bound.

## Proposed Fix

### Option 1: Preprocessor Enhancement (Preferred)
Ensure compile-time constants are fully expanded before parsing:
1. Review `src/ir/preprocessor.py` to ensure `%var%` is substituted in all contexts
2. The preprocessing pass should happen before any lexing/parsing

### Option 2: Grammar Enhancement (Alternative)
Add compile-time constant support to range expressions:
```lark
range_bound: NUMBER | SET_ELEMENT_ID | STRING | ID | compile_time_const
```

### Files to Modify
- `src/ir/preprocessor.py` - Ensure full substitution of compile-time constants
- `src/gams/gams_grammar.lark` - Optionally add compile_time_const to range_bound
- `src/ir/parser.py` - Handle compile_time_const in range context if grammar changed

## Test Cases

```python
def test_compile_time_constant_in_set_range():
    """Test compile-time constant in set range."""
    code = """
    $set N 5
    Set i / i1*i%N% /;
    """
    model = parse_model_text(code)
    assert "i" in model.sets
    assert model.sets["i"].members == ["i1", "i2", "i3", "i4", "i5"]

def test_eval_directive_in_range():
    """Test $eval directive used in range."""
    code = """
    $set N 10
    $eval NM1 %N%-1
    Set i / i0*i%NM1% /;
    """
    model = parse_model_text(code)
    assert "i" in model.sets
    # Should have i0 through i9 (10 elements)
    assert len(model.sets["i"].members) == 10
```

## Additional Context

The `springchain.gms` model also uses compile-time constants in other contexts:
- Parameter data: `m(n) "mass" /n1*n%NM1% 1/;`
- Expressions: `(ord(n)-1)/%N%`
- Variable bounds: `x.FX['n%N%'] = b_x;`

A comprehensive fix should handle all these contexts.

## Related Issues

- Preprocessor compile-time constant handling
- `$set` and `$eval` directive support

## References

- `docs/planning/EPIC_3/SPRINT_17/LEXER_IMPROVEMENT_PLAN.md` - Related to compile-time processing
- `data/gamslib/raw/springchain.gms` - Example model
- `src/ir/preprocessor.py` - Current preprocessor implementation
