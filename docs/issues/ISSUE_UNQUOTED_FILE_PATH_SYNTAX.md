# Issue: Unquoted File Path Syntax Not Supported

**GitHub Issue:** [#556](https://github.com/jeffreyhorn/nlp2mcp/issues/556)  
**Status:** Open  
**Priority:** Medium  
**Discovered:** Sprint 16 Day 6 (2026-01-23)  
**Affected Models:** apl1p, apl1pca

---

## Summary

The GAMS grammar does not support unquoted file paths in `File` statements. The current grammar only accepts quoted strings or compile-time constants as file paths.

## Error Message

```
Parse error at line 118, column 12: Unexpected character: 'M'
  File stg / MODEL.STG /;
             ^
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

## Example GAMS Code (from apl1p.gms, line 118)

```gams
File stg / MODEL.STG /;
put stg;

put "INDEP DISCRETE" /;
```

The syntax `File stg / MODEL.STG /;` declares a file handle named `stg` that writes to the file `MODEL.STG`. GAMS allows unquoted file paths when they don't contain special characters.

## Root Cause Analysis

The current grammar rule for `file_stmt` is:

```lark
file_stmt: "file"i ID "/" file_path "/" SEMI

file_path: STRING
         | compile_time_const
```

The `file_path` rule only allows:
1. `STRING` - quoted paths like `'MODEL.STG'` or `"MODEL.STG"`
2. `compile_time_const` - compile-time variables like `%gams.scrdir%model.stg`

It does not allow unquoted identifiers like `MODEL.STG`.

## Proposed Fix

### Option A: Add ID Pattern to file_path (Simple)

Extend `file_path` to accept unquoted identifiers:

```lark
file_path: STRING
         | compile_time_const
         | FILE_PATH_UNQUOTED

// Pattern for unquoted file paths: allows letters, numbers, dots, underscores, hyphens
FILE_PATH_UNQUOTED: /[a-zA-Z0-9_][a-zA-Z0-9_.\-]*/
```

### Option B: Use Existing ID with Dot Extension

Allow dotted identifiers as file paths:

```lark
file_path: STRING
         | compile_time_const
         | dotted_file_path

dotted_file_path: ID ("." ID)*
```

This would parse `MODEL.STG` as `MODEL` `.` `STG`.

### Option C: More Permissive Pattern

Use a more permissive pattern that captures the entire path:

```lark
// Match anything between slashes that isn't a slash or semicolon
FILE_PATH_UNQUOTED: /[^\s\/;]+/
```

### Recommendation

Option A is recommended as it's explicit about what characters are allowed in unquoted file paths and won't conflict with other grammar rules. The pattern should match common file naming conventions.

## Affected Models

| Model | Line | Syntax |
|-------|------|--------|
| apl1p | 118 | `File stg / MODEL.STG /;` |
| apl1pca | 111 | `File stg / MODEL.STG /;` (same pattern) |

## Testing

After fix, verify:
1. Both apl1p and apl1pca parse successfully (or progress to next blocking issue)
2. No regressions in existing parsing models
3. Both quoted and unquoted file paths work:
   - `File f / 'output.txt' /;` (quoted - already works)
   - `File f / output.txt /;` (unquoted - new)
   - `File f / MODEL.STG /;` (unquoted with dot - new)

## Related Issues

- Sprint 16 Day 6 grammar fixes (PR #553)
- Issue #554 (stage attribute) - fixing that revealed this secondary issue
- Sprint 12 file_stmt implementation (Issue #447)

## References

- GAMS Documentation: [File Statement](https://www.gams.com/latest/docs/UG_Put.html#UG_Put_TheFileStatement)
- Model source: `data/gamslib/raw/apl1p.gms`
- Current grammar: `src/gams/gams_grammar.lark` lines 408-411
