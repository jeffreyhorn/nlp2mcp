# Parser Limitation: Hyphens Not Allowed in Equation Descriptions

## Status
**Open** - Parser limitation  
**Priority**: Low  
**Component**: Parser (src/ir/parser.py)  
**Discovered**: 2025-11-06 during Sprint 5 Prep Task 8

## Description

The GAMS parser does not allow hyphens in equation description text. When an equation declaration includes a description with hyphens (e.g., "non-negativity constraints"), the parser fails with an error.

## Current Behavior

When parsing a GAMS file with hyphens in equation descriptions, the parser fails with:

```
Error: Unexpected error - No terminal matches '-' in the current parser context, at line X col Y

    non_negative(i) non-negativity constraints
                       ^
Expected one of:
	...
```

## Expected Behavior

The parser should accept hyphens in equation description text, treating the description as a freeform text string. Standard GAMS allows arbitrary text in descriptions.

## Reproduction

### Minimal Test Case

Create a file `test_hyphen.gms`:

```gams
Sets
    i /i1, i2/
;

Variables
    x(i)
    obj
;

Equations
    objdef objective definition
    non_negative(i) non-negativity constraints
;

objdef.. obj =e= sum(i, x(i));
non_negative(i).. x(i) =g= 0;

Model test /all/;
Solve test using NLP minimizing obj;
```

Run:
```bash
nlp2mcp test_hyphen.gms -o output.gms
```

**Result**: Parser error when encountering the hyphen in "non-negativity".

### Working Workaround

Remove hyphens from equation descriptions:

```gams
Equations
    objdef objective definition
    non_negative(i) nonnegativity constraints
;
```

Or use underscores:

```gams
Equations
    objdef objective definition
    non_negative(i) non_negativity constraints
;
```

Both workarounds work perfectly.

## Impact

**Very Low Impact:**
- **Cosmetic Only**: Affects only description text, not semantics
- **Easy Workaround**: Simply remove hyphens or use underscores
- **No Mathematical Effect**: Descriptions are comments, don't affect computation
- **User Experience**: Minor cosmetic limitation

**Workaround Quality**: Excellent - trivial to avoid hyphens

## Examples

Common equation descriptions that would fail:

```gams
Equations
    balance(i) supply-demand balance
    flow_limit(i,j) arc-capacity constraint
    non_neg(i) non-negativity bounds
    piece_wise(i) piece-wise linear approximation
;
```

All must be rewritten without hyphens:

```gams
Equations
    balance(i) supply demand balance
    flow_limit(i,j) arc capacity constraint
    non_neg(i) nonnegativity bounds
    piece_wise(i) piecewise linear approximation
;
```

## Technical Details

### Current Parser Behavior

The parser appears to treat the description text as part of the grammar rather than as a freeform string literal. When it encounters a hyphen, it tries to parse it as a minus operator, which is invalid in that context.

### Grammar Issue

The equation declaration likely has a rule like:

```
equation_decl: equation_name [description]
description: WORD+
```

Where `WORD` is defined as alphanumeric only, not including hyphens.

### Suggested Implementation

The grammar should treat equation descriptions as freeform text:

```
equation_decl: equation_name [description] NEWLINE
description: TEXT_UNTIL_NEWLINE
TEXT_UNTIL_NEWLINE: /[^\n]+/
```

Or with explicit string literals:

```
equation_decl: equation_name [ESCAPED_STRING]
ESCAPED_STRING: /"[^"]*"/ | /[^\n]+/
```

### Similar Issues

This likely affects:
1. **Equation descriptions**: ✓ Confirmed
2. **Variable descriptions**: Probably (untested)
3. **Set descriptions**: Probably (untested)
4. **Parameter descriptions**: Probably (untested)
5. **Model descriptions**: Probably (untested)

Example:

```gams
Variables
    x "decision-variable"  # Likely fails
    y "decision variable"  # Works
;
```

### Lexer Context

The issue is that the lexer needs to switch contexts:

- **In code context**: Hyphen is minus operator
- **In description context**: Hyphen is literal character

This requires either:
1. Context-sensitive lexing (complex)
2. Quoted string literals (simple, but changes syntax)
3. Specific description token (moderate complexity)

## Related Issues

- General handling of freeform text/comments in declarations
- String literal support in GAMS syntax

## Suggested Fix Priority

**Very Low Priority:**
- Trivial workaround available
- Purely cosmetic issue
- No impact on functionality
- Low user friction

**Recommendation**: Fix only if doing broader work on description/comment handling.

## Testing Requirements

When implementing, add tests for:

1. **Hyphens in Equation Descriptions**:
   ```gams
   Equations
       eq1 multi-word description
       eq2(i) indexed-equation description
   ;
   ```

2. **Hyphens in Variable Descriptions**:
   ```gams
   Variables
       x "decision-variable"
       y(i) "indexed-variable"
   ;
   ```

3. **Hyphens in Other Declarations**:
   ```gams
   Sets
       i "element-set" /i1, i2/
   ;
   
   Parameters
       a "cost-parameter"
   ;
   ```

4. **Special Characters**:
   - Hyphens: `multi-word`
   - Underscores: `multi_word` (already works)
   - Parentheses: `equation (version 2)`
   - Apostrophes: `can't`, `won't`
   - Quotes: nested quotes handling

5. **Edge Cases**:
   - Empty descriptions
   - Very long descriptions
   - Unicode characters
   - Leading/trailing whitespace

## Alternative Solutions

### 1. Require Quoted Strings

Require all descriptions to be quoted:

```gams
Equations
    eq1 "This is a multi-word description with hyphens"
;
```

**Pros**: Clean, unambiguous
**Cons**: Changes GAMS syntax expectations

### 2. End-of-Line Delimiter

Parse everything until end of line as description:

```gams
Equations
    eq1 This is a multi-word description with hyphens
;
```

**Pros**: Most flexible
**Cons**: Can't have multiple equations per line

### 3. Explicit Description Keyword

Use keyword to delimit descriptions:

```gams
Equations
    eq1 TEXT "multi-word description"
;
```

**Pros**: Explicit and unambiguous
**Cons**: Verbose, not standard GAMS

### Recommendation

Option 2 (end-of-line delimiter) matches standard GAMS behavior and is most user-friendly.

## Comparison with GAMS

Standard GAMS allows:

```gams
Equations
    supply-demand-balance(i,t) "Supply-demand balance in period t for product i"
    arc-capacity(i,j) Arc capacity limits between nodes i and j
;
```

Both quoted and unquoted descriptions work, with arbitrary characters including hyphens.

## Quick Fix Alternative

If a proper fix is complex, consider a preprocessing step:

```python
def preprocess_descriptions(gams_code):
    """Replace hyphens with spaces in equation descriptions."""
    # Identify description text context
    # Replace hyphens with spaces or underscores
    return transformed_code
```

This would be invisible to users but preserve parser simplicity.

## References

- **GAMS Documentation**: Text fields in declarations
- **Sprint 5 Prep Task 8**: Discovered during test model generation
- **Standard GAMS**: Allows arbitrary text in descriptions
