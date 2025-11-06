# Parser Limitation: Asterisk Notation Not Supported in Set Definitions

**GitHub Issue**: [#136](https://github.com/jeffreyhorn/nlp2mcp/issues/136)

## Status
**Open** - Parser limitation  
**Priority**: Medium  
**Component**: Parser (src/ir/parser.py)  
**Discovered**: 2025-11-06 during Sprint 5 Prep Task 8

## Description

The GAMS parser does not support the asterisk (`*`) notation for defining ranges of set elements. This is standard GAMS syntax used to define sequences like `/i1*i100/` to represent elements `i1, i2, i3, ..., i100`.

## Current Behavior

When parsing a GAMS file with asterisk notation in set definitions, the parser fails with:

```
Error: Unexpected error - No terminal matches '*' in the current parser context, at line X col Y

    i /i1*i100/
           ^
Expected one of:
	* SLASH
	* COMMA
```

## Expected Behavior

The parser should accept and expand asterisk notation in set definitions, treating `/i1*i100/` as equivalent to `/i1, i2, i3, ..., i100/`.

## Reproduction

### Minimal Test Case

Create a file `test_asterisk.gms`:

```gams
Sets
    i /i1*i10/
;

Variables
    x(i)
    obj
;

Equations
    objdef
;

objdef.. obj =e= sum(i, x(i));

Model test /all/;
Solve test using NLP minimizing obj;
```

Run:
```bash
nlp2mcp test_asterisk.gms -o output.gms
```

**Result**: Parser error as shown above.

### Working Workaround

Replace asterisk notation with explicit comma-separated lists:

```gams
Sets
    i /i1, i2, i3, i4, i5, i6, i7, i8, i9, i10/
;
```

This works but is impractical for large sets.

## Impact

**Moderate Impact:**
- **User Experience**: Users must manually expand large set definitions
- **Model Size**: Makes large models (100+ elements) tedious to write
- **GAMS Compatibility**: Standard GAMS syntax not supported
- **Performance**: Long comma-separated lists (200+ elements) approach parser performance limits

**Workaround Available**: Yes, but tedious for large sets

## Examples from Codebase

Several example files in the repository use asterisk notation but cannot be converted:

1. **examples/sprint4_abs_portfolio.gms**:
   ```gams
   i Assets /stock1*stock4, bond1*bond2/
   ```

2. **examples/sprint4_comprehensive.gms**:
   ```gams
   t Time periods /t1*t4/
   ```

3. **examples/sprint4_fixed_vars_design.gms**:
   ```gams
   i Components /comp1*comp4/
   ```

4. **examples/sprint4_minmax_production.gms**:
   ```gams
   i Products /prod1*prod3/
   ```

None of these files can currently be converted due to this limitation.

## Technical Details

### Grammar Location

The parser grammar is defined in the Lark grammar file. The relevant section for set element lists needs to be enhanced to support the pattern:

```
IDENTIFIER "*" IDENTIFIER
```

### Suggested Implementation

1. **Lexer Enhancement**: Recognize the asterisk in set element context (not as multiplication)

2. **Parser Rule**: Add production rule for range syntax:
   ```
   set_element: IDENTIFIER
              | IDENTIFIER "*" IDENTIFIER  -> set_range
   ```

3. **AST Transformation**: In the transformer, expand ranges:
   ```python
   def set_range(self, items):
       start, end = items
       # Extract base and numeric parts
       # e.g., "i1" -> base="i", start_num=1
       #       "i10" -> base="i", end_num=10
       # Generate: ["i1", "i2", ..., "i10"]
       return expanded_list
   ```

4. **Edge Cases to Handle**:
   - Non-numeric suffixes: `/item*itez/` (should error)
   - Different prefixes: `/a1*b10/` (should error)
   - Reversed order: `/i10*i1/` (should error or generate empty)
   - Single character: `/a*z/` (should work for single letters)

### Parsing Complexity

The asterisk operator is context-sensitive:
- In expressions: multiplication operator
- In set definitions: range operator

The grammar needs to disambiguate these contexts, likely by restricting the range syntax to only appear within set element lists (between `/` and `/` or between commas).

## Related Issues

- Performance issues with very long comma-separated lists (see separate issue)
- Parser limitations prevent conversion of several example models

## Suggested Fix Priority

**Medium Priority:**
- High value for user experience
- Enables conversion of existing example models
- Required for generating realistic large test models
- Has acceptable workaround for now

## Testing Requirements

When implementing, add tests for:
1. Basic range: `/i1*i10/`
2. Single element: `/i1*i1/`
3. Mixed notation: `/i1*i3, i5, i7*i9/`
4. Multiple ranges: `/i1*i5, j1*j3/`
5. Error cases:
   - Different prefixes: `/i1*j10/`
   - Non-numeric: `/item*itez/`
   - Invalid order: `/i10*i1/`
6. Edge case: Single character ranges `/a*z/`

## References

- **GAMS Documentation**: Set element range notation
- **Sprint 5 Prep Task 8**: Discovered during large model test fixture creation
- **Files affected**: All Sprint 4 examples using asterisk notation
