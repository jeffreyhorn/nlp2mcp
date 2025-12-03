# Parser Enhancement: Variable Indexing in Declarations

**GitHub Issue**: #391 - https://github.com/jeffreyhorn/nlp2mcp/issues/391  
**Status**: Open  
**Priority**: Medium  
**Component**: Parser (src/ir/parser.py, src/gams/gams_grammar.lark)  
**Effort**: 3h  
**Impact**: Unlocks 1 Tier 2 model - 5.6% parse rate improvement

## Summary

GAMS allows variables to be declared with their domain/indexing specified using parentheses notation directly in the declaration block. The parser currently does not support this syntax, blocking 1 Tier 2 model from parsing.

## Current Behavior

When parsing GAMS files with indexed variable declarations, the parser fails with:

**Example from inscribedsquare.gms (line 42):**
```
Error: Parse error at line 42, column 2: Unexpected character: '('
Variables
  z     "area of square to be maximized",
  t(i)  "position of square corner points on curve",
  ^
```

## Expected Behavior

The parser should accept variable declarations with domain specifications:
- `t(i)` - variable indexed by set `i`
- `x(i,j)` - variable indexed by sets `i` and `j`
- `flow(i,j,k)` - variable indexed by sets `i`, `j`, and `k`

This is equivalent to later declaring the domain but is more concise.

## GAMS Syntax Reference

**Variable Declaration with Indexing:**
```gams
Set i / 1*4 /;
Variables
    z        "objective value"
    t(i)     "indexed by set i"
    x(i,i)   "2-dimensional indexing";
```

This is equivalent to:
```gams
Variables z, t, x;
* Domain implied by usage
```

But the explicit indexing provides:
1. Documentation of domain
2. Compile-time domain checking
3. Clearer model structure

From GAMS User's Guide, Section 6.1 "Variable Declarations":
- Variables can be declared with their domain in parentheses
- Syntax: `variable_name(index_set1, index_set2, ...)  "description"`
- Domain specification is optional but recommended for clarity
- Commas separate multiple variable declarations in a declaration

## Reproduction

### Test Case 1: Single-index variable (inscribedsquare.gms)
```gams
Set i / 1*4 /;
Variables
    z     "area of square"
    t(i)  "position of corner points";
```

**Current Result:** Parse error at `(`  
**Expected Result:** Parse successfully

### Test Case 2: Multi-index variable
```gams
Set i / 1*10 /;
Set j / 1*10 /;
Variables
    x(i,j)  "flow from i to j";
```

**Current Result:** Would fail at `(`  
**Expected Result:** Parse successfully

### Test Case 3: Mixed declarations
```gams
Variables
    z           "scalar variable"
    x(i)        "indexed by i"
    y(i,j)      "indexed by i and j";
```

**Current Result:** Would fail at first `(`  
**Expected Result:** Parse successfully

## Implementation Plan

### Complexity Estimate: 3h

**Breakdown:**
- Grammar update (1h): Extend variable declaration syntax to support indexing
- AST changes (0.5h): Add domain field to VariableDef
- Parser semantic handler (1h): Extract and store domain information
- Testing (0.5h): 15+ test cases covering:
  - Single-index variables
  - Multi-index variables
  - Mixed scalar and indexed variables
  - Parameters with indexing (if applicable)
  - Edge cases

### Implementation Checklist

**AST (src/ir/symbols.py):**
- [ ] Add optional `domain` field to VariableDef
- [ ] Store list of index set names
- [ ] Update VariableDef initialization

**Grammar (src/gams/gams_grammar.lark):**
- [ ] Update variable_decl to support optional index specification
- [ ] Add index_spec rule for domain specification
- [ ] Handle commas between multiple variable declarations

**Current Grammar Pattern:**
```lark
variable_block: "Variable"i variable_kind? variable_list SEMI
variable_list: variable_decl ("," variable_decl)*
variable_decl: ID STRING?
```

**Proposed Grammar Pattern:**
```lark
variable_block: "Variable"i variable_kind? variable_list SEMI
variable_list: variable_decl ("," variable_decl)*
variable_decl: ID index_spec? STRING?
index_spec: "(" ID ("," ID)* ")"
```

**Parser Semantic Handler:**
- [ ] Update `handle_variable_decl` to extract domain
- [ ] Validate that index sets are defined
- [ ] Store domain information in VariableDef AST node
- [ ] Apply same pattern to parameters if applicable

**Testing:**
- [ ] Unit tests for single-index variable declarations
- [ ] Unit tests for multi-index variable declarations
- [ ] Unit tests for mixed scalar/indexed declarations
- [ ] Integration test with inscribedsquare.gms
- [ ] Edge case tests (undefined sets, empty domain)

## Affected Models

**Tier 2 Models (1 blocked by this issue):**
- ✅ inscribedsquare.gms (106 lines, NLP) - Inscribed Square Problem

**Impact:** Unlocking this model improves Tier 2 parse rate from 27.78% → 33.33% (5/18 → 6/18)

## Related Issues

- Similar syntax may apply to Parameters, Equations
- Related to domain checking and validation
- Independent of other blockers

## Technical Notes

### Domain Specification Benefits

**Without explicit domain:**
```gams
Variable x;
Equation balance;
balance.. sum(i, x) =e= total;  * Domain inferred from usage
```

**With explicit domain:**
```gams
Variable x(i);
Equation balance;
balance.. sum(i, x(i)) =e= total;  * Domain explicit
```

Benefits:
1. Compiler can catch domain errors earlier
2. Better documentation
3. More explicit model structure

### AST Representation

```python
@dataclass
class VariableDef:
    """Variable definition."""
    name: str
    kind: VarKind  # binary, integer, positive, negative, free
    domain: list[str] | None  # None for scalar, list of set names for indexed
    description: str | None
    location: SourceLocation
```

Example:
```gams
Variable t(i) "position";
```
AST: `VariableDef(name="t", kind=VarKind.FREE, domain=["i"], description="position", ...)`

### Grammar Details

The index specification should come before the description:
```gams
Variable t(i) "position of points";
         ^    ^
         |    description
         domain
```

Parsing order:
1. Variable keyword
2. Optional variable kind (Binary, Integer, Positive, etc.)
3. Variable name (ID)
4. Optional domain specification `(set1, set2, ...)`
5. Optional description (STRING)

### Multiple Variables

GAMS allows multiple variables in one declaration:
```gams
Variables
    x(i)     "first variable"
    y(i,j)   "second variable"
    z        "third variable";
```

Each variable can have its own domain specification.

### Parameter Indexing

The same syntax applies to Parameters:
```gams
Parameter cost(i,j) "transportation cost";
```

We should implement this for parameters as well if not already supported.

## Success Criteria

- [ ] inscribedsquare.gms parses successfully
- [ ] All existing tests continue to pass (no regressions)
- [ ] Domain information is captured in AST
- [ ] 15+ new test cases added for indexed declarations
- [ ] Parse rate for Tier 2 models ≥ 33%
- [ ] Support for Variables, Parameters, and Equations (if applicable)

## References

- **GAMS Documentation:** User's Guide Section 6.1 "Variable Declarations"
- **GAMS Documentation:** User's Guide Section 3.2 "Parameter Declarations"
- **GAMS Documentation:** User's Guide Section 8.1 "Equation Declarations"
- **Sprint 12 Planning:** Tier 2 model blocker analysis

## Example Test Cases

### Test 1: Single-index variable
```gams
Set i / 1*10 /;
Variable x(i) "indexed variable";
```

### Test 2: Two-dimensional variable
```gams
Set i / 1*5 /;
Set j / 1*5 /;
Variable flow(i,j) "flow from i to j";
```

### Test 3: Three-dimensional variable
```gams
Set i, j, k;
Variable cube(i,j,k) "3D variable";
```

### Test 4: Mixed scalar and indexed
```gams
Variables
    total        "total cost"
    x(i)         "decision variable"
    y(i,j)       "allocation variable";
```

### Test 5: Multiple variables with same domain
```gams
Set i / 1*10 /;
Variables
    x(i)   "first variable"
    y(i)   "second variable"
    z(i)   "third variable";
```

### Test 6: Binary variable with domain
```gams
Set i / 1*10 /;
Binary Variable b(i) "binary decision";
```

### Test 7: Parameter with domain
```gams
Set i / 1*10 /;
Parameter cost(i) "cost per unit" / 1 10, 2 20, 3 30 /;
```

### Test 8: Equation with domain
```gams
Set i / 1*10 /;
Equation balance(i) "balance constraint";
```

### Test 9: Variable without domain (scalar)
```gams
Variable total "total value";
```

### Test 10: Complex domain
```gams
Set i, j, k, t;
Variable x(i,j,k,t) "4-dimensional variable";
```
