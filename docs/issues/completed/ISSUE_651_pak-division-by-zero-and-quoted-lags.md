# Issue: pak Translation Bugs - Division by Zero and Quoted Lag References

**Status**: FIXED (Sprint 18)
**GitHub Issue**: #651 (https://github.com/jeffreyhorn/nlp2mcp/issues/651)
**Model**: `pak.gms`
**Component**: Grammar / Scalar Parsing / Variable Initialization

## Fix Summary

| Bug | Status | Fixed In |
|-----|--------|----------|
| Quoted lag references | FIXED | Commit a256657 (P2 fix) |
| Division by zero (scalar initialization) | FIXED | Sprint 18 |
| GAMS Error 141 (variable initialization) | FIXED | Sprint 18 |

## Original Problem

### Bug 1: Division by Zero in Computed Parameters

The `pak` model uses scalars `r` and `g` as divisors in the computed parameter `dis`:
```gams
dis = (1 + r) ** ((-1) * (card(t))) * (1 - alpha) * (1 + g) / (r - g);
```

But the MCP output showed `r = 0.0` and `g = 0.0`, causing division by zero.

### Root Cause

The original `pak.gms` declares scalars in a multi-line block with quoted descriptions:
```gams
Scalar
   fbb   'foreign aid 1962'   /  1.183 /
   r     'post plan discount' /   .10  /
   g     'post plan growth'   /   .073 /
```

The `scalar_item` grammar rule used `ID` which matched both unquoted identifiers AND quoted strings (via the `ESCAPED` pattern in the `ID` terminal). This caused ambiguity in newline-separated lists:

- `fbb` and `sb` parsed correctly (first two items)
- From `tib` onwards, the parser split entries incorrectly:
  - `tib` → `scalar_plain` (no data)
  - `'total investment 1962' / 4.564 /` → `scalar_with_data` (STRING as name)

### Fix: Use SYMBOL_NAME in scalar_item

Changed `scalar_item` in `src/gams/gams_grammar.lark` to use `SYMBOL_NAME` instead of `ID`:

```diff
-scalar_item: ID "/" scalar_data_items "/" (ASSIGN expr)?  -> scalar_with_data
-           | ID ASSIGN expr                               -> scalar_with_assign
-           | ID                                           -> scalar_plain
+scalar_item: SYMBOL_NAME STRING "/" scalar_data_items "/" (ASSIGN expr)?  -> scalar_with_data
+           | SYMBOL_NAME "/" scalar_data_items "/" (ASSIGN expr)?         -> scalar_with_data
+           | SYMBOL_NAME STRING ASSIGN expr                               -> scalar_with_assign
+           | SYMBOL_NAME ASSIGN expr                                      -> scalar_with_assign
+           | SYMBOL_NAME                                                  -> scalar_plain
```

`SYMBOL_NAME` only matches unquoted identifiers (`/[a-zA-Z_][a-zA-Z0-9_]*/`), so quoted strings like `'post plan discount'` cannot be interpreted as the start of a new scalar item.

### Bug 2: GAMS Error 141 (Variable Initialization)

After fixing the scalar parsing, the translation succeeded but GAMS validation failed with Error 141:
```
*** Error 141: Symbol declared but no values have been assigned.
```

This occurred because the variable initialization code tried to read `.l` and `.up` attributes of variables that were never assigned:
```gams
v.l(t,j) = min(1, v.up(t,j));  * Error 141: v never had values assigned
```

### Fix: Direct Assignment Without Reading Attributes

Changed `src/emit/emit_gams.py` to not read from `.l` or `.up` when initializing unassigned variables:

```python
# Before (caused Error 141):
init_lines.append(f"{var_name}.l({domain_str}) = min(1, {var_name}.up({domain_str}));")

# After (direct assignment):
init_lines.append(f"{var_name}.l({domain_str}) = 1;")
```

For variables that DO have explicit `.l` values, the original max/min clamping is preserved.

## Verification

```bash
# Translation now succeeds
python scripts/gamslib/batch_translate.py --model pak --validate

# Scalars have correct values
python -c "
from src.ir.parser import parse_model_file
ir = parse_model_file('data/gamslib/raw/pak.gms')
print('r:', ir.params['r'].values)  # {(): 0.1}
print('g:', ir.params['g'].values)  # {(): 0.073}
"
```

## Files Modified

1. `src/gams/gams_grammar.lark` - Use SYMBOL_NAME in scalar_item to prevent quoted strings from being parsed as scalar names
2. `src/emit/emit_gams.py` - Direct assignment for uninitialized POSITIVE variables to avoid GAMS Error 141

## Tests

All 3258 tests pass after fix.
