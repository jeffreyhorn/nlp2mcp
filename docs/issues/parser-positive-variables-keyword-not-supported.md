# Parser Limitation: Positive Variables Keyword Not Supported

## Status
**Open** - Parser limitation  
**Priority**: Low  
**Component**: Parser (src/ir/parser.py)  
**Discovered**: 2025-11-06 during Sprint 5 Prep Task 8

## Description

The GAMS parser does not support the `Positive Variables` declaration keyword. This is standard GAMS syntax used to declare variables that are constrained to be non-negative (equivalent to setting `.lo = 0`).

## Current Behavior

When parsing a GAMS file with `Positive Variables` declaration, the parser fails with:

```
Error: Unexpected error - No terminal matches 'V' in the current parser context, at line X col Y

Positive Variables x;
         ^
Expected one of:
	* LPAR
	* __ANON_0
	* DOT
	* ASSIGN
```

The parser appears to interpret `Positive` as a variable name, then gets confused by the following `Variables` keyword.

## Expected Behavior

The parser should recognize `Positive Variables` as a variable type declaration keyword (similar to `Variables`, `Binary Variables`, `Integer Variables`) and treat all listed variables as having an implicit lower bound of zero.

## Reproduction

### Minimal Test Case

Create a file `test_positive.gms`:

```gams
Variables
    x
    y
    obj
;

Positive Variables x, y;

Equations
    objdef
;

objdef.. obj =e= x + y;

Model test /all/;
Solve test using NLP minimizing obj;
```

Run:
```bash
nlp2mcp test_positive.gms -o output.gms
```

**Result**: Parser error as shown above.

### Working Workaround

Use explicit lower bound constraints instead:

```gams
Variables
    x
    y  
    obj
;

Equations
    objdef
    x_nonneg
    y_nonneg
;

objdef.. obj =e= x + y;
x_nonneg.. x =g= 0;
y_nonneg.. y =g= 0;

Model test /all/;
Solve test using NLP minimizing obj;
```

This works but is more verbose and creates additional constraints.

## Impact

**Low Impact:**
- **Workaround Quality**: Excellent workaround available (explicit constraints)
- **Semantic Equivalence**: Constraints achieve the same mathematical meaning
- **User Experience**: Minor inconvenience, more verbose code
- **GAMS Compatibility**: Common GAMS syntax not supported

**Note**: In the MCP reformulation, both `Positive Variables x` and explicit constraints `x =g= 0` produce the same KKT conditions, so there's no mathematical difference in the output.

## Examples from Codebase

Several example files use `Positive Variables`:

1. **examples/sprint4_comprehensive.gms**:
   ```gams
   Positive Variables production, inventory, shortage;
   ```

2. **examples/sprint4_minmax_production.gms**:
   ```gams
   Positive Variables x, shortage, maxShortage;
   ```

3. **examples/sprint4_abs_portfolio.gms**:
   ```gams
   Positive Variables w;
   ```

4. **examples/sprint4_fixed_vars_design.gms**:
   ```gams
   Positive Variables x;
   ```

All these files currently fail to parse due to this limitation.

## Technical Details

### GAMS Variable Type Keywords

GAMS supports several variable type keywords:

1. **Variables**: Unconstrained (default)
2. **Positive Variables**: Lower bound = 0
3. **Negative Variables**: Upper bound = 0
4. **Binary Variables**: Integer, bounds [0, 1]
5. **Integer Variables**: Integer, unbounded
6. **Free Variables**: Synonym for Variables (unconstrained)

### Current Parser Behavior

The parser successfully handles:
- `Variables` keyword
- Variable lists with attributes

But does not recognize variable type modifiers like `Positive`, `Negative`, `Binary`, `Integer`.

### Grammar Requirements

The grammar needs to recognize variable type declarations:

```
variable_block: "Variables" variable_list ";"
              | "Positive" "Variables" variable_list ";"
              | "Negative" "Variables" variable_list ";"
              | "Binary" "Variables" variable_list ";"
              | "Integer" "Variables" variable_list ";"
              | "Free" "Variables" variable_list ";"
```

Or more compactly:

```
variable_block: variable_type "Variables" variable_list ";"
variable_type: "Positive" | "Negative" | "Binary" | "Integer" | "Free" | ε
```

### Suggested Implementation

1. **Parser Rule**: Add optional variable type modifier:
   ```python
   ?variable_declaration: [variable_type] "Variables" variable_list ";"
   variable_type: "Positive" | "Negative" | "Binary" | "Integer" | "Free"
   ```

2. **AST Transformation**: Store variable type information:
   ```python
   {
       "name": "x",
       "domain": [],
       "attributes": {
           "type": "positive",  # or "negative", "binary", "integer"
           "lower_bound": 0.0,  # implicit from "positive"
       }
   }
   ```

3. **Normalization**: Convert variable types to explicit bounds:
   - `Positive Variables x` → `x.lo = 0`
   - `Negative Variables x` → `x.up = 0`
   - `Binary Variables x` → `x.lo = 0; x.up = 1` (and integer flag)
   - `Integer Variables x` → Set integer flag

### Edge Cases to Handle

1. **Multiple Declarations**:
   ```gams
   Variables x, y;
   Positive Variables x;  # x already declared - should this error or override?
   ```

2. **Conflicting Types**:
   ```gams
   Positive Variables x;
   Negative Variables x;  # Conflicting constraints
   ```

3. **Explicit Bounds Override**:
   ```gams
   Positive Variables x;
   x.lo = -5;  # Should this override the implicit bound?
   ```

4. **Binary/Integer with Bounds**:
   ```gams
   Binary Variables x;
   x.lo = 0.5;  # Invalid for binary variable
   ```

## Comparison: Keyword vs Constraint

Both approaches are mathematically equivalent in the MCP reformulation:

### Using Keyword:
```gams
Positive Variables x;
```
Produces bound: `x >= 0`

### Using Constraint:
```gams
Variables x;
Equations x_nonneg;
x_nonneg.. x =g= 0;
```
Produces constraint: `x >= 0`

In the KKT/MCP output, both generate the same complementarity condition:
```gams
x ⊥ (stationarity_x + pi_x) >= 0
```

Where `pi_x` is the multiplier for the bound/constraint.

## Related Issues

- Parser support for other variable types: `Binary`, `Integer`, `Negative`, `Free`
- Variable attribute handling (`.lo`, `.up`, `.fx`)

## Suggested Fix Priority

**Low Priority:**
- Excellent workaround available (explicit constraints)
- Same mathematical meaning in MCP output
- Low user friction (workaround is idiomatic GAMS)
- Nice-to-have for GAMS compatibility

**Recommendation**: Defer until higher priority parser issues are resolved (asterisk notation, multi-dimensional parameters).

## Testing Requirements

When implementing, add tests for:

1. **Positive Variables**:
   ```gams
   Positive Variables x, y, z;
   ```

2. **Other Variable Types**:
   ```gams
   Negative Variables a;
   Binary Variables b;
   Integer Variables n;
   Free Variables f;
   ```

3. **Mixed Declarations**:
   ```gams
   Variables x;
   Positive Variables y, z;
   ```

4. **Indexed Variables**:
   ```gams
   Positive Variables x(i);
   ```

5. **Integration with Bounds**:
   - Verify `Positive Variables x` equivalent to `x.lo = 0`
   - Test interaction with explicit `.lo` assignments
   - Verify MCP output matches constraint-based approach

6. **Error Cases**:
   - Conflicting type declarations
   - Invalid types for special variables (e.g., Binary with continuous bound)

## Alternative: Preprocessing

An alternative to full parser support would be preprocessing:

```python
def preprocess_variable_types(gams_code):
    """Convert 'Positive Variables' to explicit bounds."""
    # Replace: Positive Variables x, y;
    # With:    Variables x, y;
    #          x.lo = 0; y.lo = 0;
    return transformed_code
```

This would allow the tool to handle these declarations without grammar changes, though it's less elegant than native parser support.

## References

- **GAMS Documentation**: Variable type declarations
- **Sprint 5 Prep Task 8**: Limitation discovered during test model generation
- **Example Files**: Multiple Sprint 4 examples use this syntax
- **MCP Theory**: Both approaches produce identical KKT/MCP formulations
