# Add Support for Power Operator Syntax (`**` or `^`)

## Issue Type
Enhancement

## Priority  
Low

## Summary

The GAMS grammar currently requires the `power(base, exponent)` function syntax for exponentiation. Standard GAMS also supports `**` (and mathematically `^`) for power operations, which is more concise and commonly used.

Users expecting standard GAMS syntax will get parser errors when using these operators.

## Current Behavior

### Works

```gams
objective.. obj =e= power(x, 2) + power(y, 2);
```

### Fails

```gams
objective.. obj =e= x**2 + y**2;
```

Error:
```
Error: Unexpected error - No terminal matches '*' in the current parser context, at line X col Y

    obj =e= x**2 + y**2;
              ^
Expected one of:
	* ID
	* NUMBER  
	* LPAR
	* MINUS
	* PLUS
	* FUNCNAME
```

Also fails:
```gams
objective.. obj =e= x^2 + y^2;  
```

## Reproduction Steps

1. Create test file `power_test.gms`:
```gams
Variables x, y, obj;
Equations objective;

objective.. obj =e= x**2 + y**2;

Model power_nlp / objective /;
Solve power_nlp using NLP minimizing obj;
```

2. Try to parse:
```bash
python -m src.cli power_test.gms -o power_mcp.gms
```

3. **Expected**: Parses successfully

4. **Actual**: Parser error

## Technical Analysis

### Grammar Structure

Current grammar (`src/gams/gams_grammar.lark`):

```lark
?factor: power
       | MINUS power  -> uneg
       | PLUS power   -> upos

?power: atom
      | atom "^" power -> binop    # This handles ^ but as exponentiation

?atom: NUMBER                             -> number
     | func_call                          -> funccall
     | ref_indexed
     | symbol_plain
     | "(" expr ")"
```

The issue is that `^` is already used for exponentiation in the grammar, but `**` is not recognized at all.

### AST Representation

When `power(x, 2)` is parsed, it creates:
```python
Call("power", (VarRef("x"), Const(2)))
```

When `x^2` is parsed, it creates:
```python
Binary("^", VarRef("x"), Const(2))
```

The differentiation and emission modules already handle `Binary("^", ...)` correctly, converting it to GAMS `**` syntax in output.

## Proposed Solution

### Option 1: Add `**` as Token (Preferred)

Modify grammar to recognize `**` as a power operator:

```lark
?factor: power
       | MINUS power  -> uneg
       | PLUS power   -> upos

?power: atom
      | atom POW power -> binop    # Use POW token

POW: "**" | "^"

?atom: NUMBER                       -> number
     | func_call                    -> funccall  
     | ref_indexed
     | symbol_plain
     | "(" expr ")"
```

This approach:
- ✅ Treats `**` and `^` as equivalent
- ✅ Minimal changes to grammar
- ✅ AST structure unchanged (still `Binary("^", ...)`)
- ✅ No changes needed to differentiation or emission

### Option 2: Expand in Parser

Keep grammar as-is but handle `**` in lexer:

```lark
// In terminal definitions
POWER: "**"
POW: "^"

// In grammar rules  
?power: atom
      | atom (POWER | POW) power -> binop
```

This approach:
- ✅ Explicit about two operators
- ❌ More verbose
- ⚠️ Need to ensure both map to same operation

### Option 3: Preprocessing

Add preprocessing step before parsing that replaces `**` with `^`:

```python
def preprocess_power_operator(source: str) -> str:
    return source.replace("**", "^")
```

This approach:
- ⚠️ Hacky solution
- ❌ May replace `**` in strings or comments
- ❌ Doesn't address the real issue

## Implementation Steps

Using **Option 1** (recommended):

1. **Update Grammar** (`src/gams/gams_grammar.lark`)
   ```lark
   # Add POW token
   POW: "**" | "^"
   
   # Update power rule
   ?power: atom
         | atom POW power -> binop
   ```

2. **Update Tests** (`tests/unit/gams/test_parser.py`)
   ```python
   def test_power_operator_syntax():
       """Test that ** and ^ both work for exponentiation."""
       source1 = "x**2"
       source2 = "x^2"  
       # Both should parse to same AST
   ```

3. **Update Documentation**
   - Add to README that both `**` and `^` are supported
   - Note that output always uses `**` (GAMS standard)

4. **Test Emission**
   - Verify that `Binary("^", ...)` still emits as `**` in GAMS

## Test Cases

```python
def test_power_double_star():
    """Test ** operator."""
    model = parse_model("objective.. obj =e= x**2;")
    # Should create Binary("^", VarRef("x"), Const(2))
    
def test_power_caret():
    """Test ^ operator (already works)."""
    model = parse_model("objective.. obj =e= x^2;")
    # Should create Binary("^", VarRef("x"), Const(2))
    
def test_power_function():
    """Test power() function (already works)."""
    model = parse_model("objective.. obj =e= power(x, 2);")
    # Should create Call("power", (...))
    
def test_mixed_power_syntax():
    """Test mixing different power syntaxes."""
    model = parse_model("objective.. obj =e= x**2 + power(y, 3) + z^4;")
    # Should parse all three forms correctly
```

## Files Involved

- `src/gams/gams_grammar.lark` - Grammar definition
- `tests/unit/gams/test_parser.py` - Parser tests
- `examples/` - May want to add example using ** syntax
- `docs/` - Documentation updates

## Acceptance Criteria

- [ ] Parser accepts `x**2` syntax
- [ ] Parser still accepts `x^2` syntax (existing)
- [ ] Parser still accepts `power(x, 2)` syntax (existing)
- [ ] All three forms create equivalent AST
- [ ] Generated GAMS code uses `**` syntax
- [ ] All existing tests still pass
- [ ] New tests added for `**` operator

## Backwards Compatibility

This change is backwards compatible:
- Existing models using `^` will continue to work
- Existing models using `power()` will continue to work  
- Only adds new syntax support

## Related Issues

None

## References

- GAMS Documentation - Arithmetic Operators
- Lark Parser Documentation - Token Definitions
- `src/emit/expr_to_gams.py` - Already handles Binary("^") → "**" conversion
