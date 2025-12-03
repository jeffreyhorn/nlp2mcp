# Parser Enhancement: Variable/Parameter Attribute Assignment

**GitHub Issue**: #389 - https://github.com/jeffreyhorn/nlp2mcp/issues/389  
**Status**: Open  
**Priority**: Medium  
**Component**: Parser (src/ir/parser.py, src/gams/gams_grammar.lark)  
**Effort**: 3h  
**Impact**: Unlocks 1 Tier 2 model - 5.6% parse rate improvement

## Summary

GAMS allows assignment to variable and parameter attributes (also called "suffixes") such as `.scale`, `.prior`, `.lo`, `.up`, `.l`, `.m`, etc. The parser currently does not support attribute assignments, blocking 1 Tier 2 model from parsing.

## Current Behavior

When parsing GAMS files with attribute assignments, the parser fails with:

**Example from bearing.gms (line 114):**
```
Error: Parse error at line 114, column 1: Unsupported assignment target [context: expression]
mu.scale = 1.0e-6;
^

Suggestion: Assignment targets must be scalars, parameters, or variable attributes (e.g., x.l, x.lo, x.up)
```

## Expected Behavior

The parser should accept attribute assignments in the form:
- `variable.attribute = value;`
- `parameter.attribute(indices) = value;`

Common attributes include:
- **Scaling:** `.scale` - scaling factor for variable
- **Bounds:** `.lo`, `.up` - lower and upper bounds
- **Initial values:** `.l` - level (initial value)
- **Marginals:** `.m` - marginal value
- **Priority:** `.prior` - branching priority
- **Stage:** `.stage` - stage assignment (stochastic programming)

## GAMS Syntax Reference

**Variable Scaling:**
```gams
mu.scale = 1.0e-6;
h.scale  = hmin;
W.scale  = Ws;
```

**Variable Bounds:**
```gams
x.lo = 0;
x.up = 100;
y.lo(i) = lower(i);
y.up(i) = upper(i);
```

**Initial Values:**
```gams
x.l = 10;
y.l(i) = init_val(i);
```

**Branching Priority:**
```gams
z.prior = 1;
```

From GAMS User's Guide, Section 6.3 "Variable Attributes":
- Variables have attributes that can be read or assigned
- Attributes are accessed using dot notation: `variable.attribute`
- Indexed variables can have indexed attributes: `x.lo(i,j) = bound(i,j)`
- Attribute assignments are regular assignment statements

## Reproduction

### Test Case 1: Variable scaling (bearing.gms)
```gams
Variable mu, h, W;
mu.scale = 1.0e-6;
h.scale  = hmin;
W.scale  = Ws;
```

**Current Result:** Parse error at `mu.scale`  
**Expected Result:** Parse successfully

### Test Case 2: Variable bounds
```gams
Variable x;
x.lo = 0;
x.up = 100;
```

**Current Result:** Would fail at `x.lo`  
**Expected Result:** Parse successfully

### Test Case 3: Indexed attribute assignment
```gams
Variable y(i);
y.lo(i) = lower_bound(i);
y.up(i) = upper_bound(i);
```

**Current Result:** Would fail at `y.lo(i)`  
**Expected Result:** Parse successfully

## Implementation Plan

### Complexity Estimate: 3h

**Breakdown:**
- Grammar extension (1h): Add attribute access to assignment targets
- AST changes (0.5h): Add AttributeRef node type
- Parser semantic handler (1h): Handle attribute assignments
- Testing (0.5h): 15+ test cases covering:
  - Variable attributes (.scale, .lo, .up, .l, .m, .prior)
  - Parameter attributes
  - Indexed attributes
  - Chained attributes
  - Edge cases (invalid attributes, read-only attributes)

### Implementation Checklist

**AST (src/ir/ast.py):**
- [ ] Add `AttributeRef` expression node
- [ ] Include `base` (variable/parameter) and `attribute` (name)
- [ ] Support optional indexing on base

**Grammar (src/gams/gams_grammar.lark):**
- [ ] Update assignment_target to include attribute references
- [ ] Add attribute_ref rule: `ID "." ID indices?`
- [ ] Ensure precedence is correct (dot binds tighter than indexing)

**Current Grammar Pattern:**
```lark
assignment_stmt: ID indices? "=" expr SEMI
```

**Proposed Grammar Pattern:**
```lark
assignment_stmt: assignment_target "=" expr SEMI
assignment_target: ID indices?
                 | ID "." ID indices?
```

**Parser Semantic Handler:**
- [ ] Add `handle_attribute_ref` method
- [ ] Validate attribute names against known attributes
- [ ] Create AttributeRef AST nodes
- [ ] Update assignment handling to support AttributeRef targets

**Testing:**
- [ ] Unit tests for variable attribute assignments
- [ ] Unit tests for parameter attribute assignments
- [ ] Unit tests for indexed attribute assignments
- [ ] Integration test with bearing.gms
- [ ] Edge case tests (invalid attributes, read-only attributes)

## Affected Models

**Tier 2 Models (1 blocked by this issue):**
- ✅ bearing.gms (154 lines, NLP) - Journal Bearing Problem

**Impact:** Unlocking this model improves Tier 2 parse rate from 27.8% → 33.3% (5/18 → 6/18)

## Related Issues

- Similar to parameter indexing syntax
- Related to expression parsing (attribute access is a special expression form)
- Independent of other blockers

## Technical Notes

### Common Variable Attributes

**Bounds and Levels:**
- `.lo` - lower bound
- `.up` - upper bound
- `.l` - level (current/initial value)
- `.m` - marginal value (dual/shadow price)
- `.fx` - fixed value (sets both .lo and .up)

**Scaling and Priority:**
- `.scale` - scaling factor
- `.prior` - branching priority (MIP)
- `.stage` - stage assignment (stochastic)

**Information Attributes (read-only in some contexts):**
- `.infeas` - infeasibility measure
- `.slack` - slack variable value

### AST Representation

```python
@dataclass
class AttributeRef(Expr):
    """Reference to variable/parameter attribute (e.g., x.lo, y.scale)."""
    base: str              # Variable/parameter name
    attribute: str         # Attribute name (.lo, .up, .scale, etc.)
    indices: list[Expr]    # Optional indices
    location: SourceLocation
```

### Grammar Details

The attribute access `.` operator should bind tightly:
```gams
x.lo(i) = 0;   # (x.lo)(i) = 0, not x.(lo(i)) = 0
```

This means the grammar should be:
```lark
attribute_ref: ID "." ID ("(" expr_list ")")?
```

### Example Assignments

**Scalar attribute:**
```gams
mu.scale = 1.0e-6;
```
AST: `AttributeRef(base="mu", attribute="scale", indices=[])`

**Indexed attribute:**
```gams
x.lo(i) = lower(i);
```
AST: `AttributeRef(base="x", attribute="lo", indices=[SymbolRef("i")])`

**Multi-dimensional indexed attribute:**
```gams
cost.l(i,j) = init_cost(i,j);
```
AST: `AttributeRef(base="cost", attribute="l", indices=[SymbolRef("i"), SymbolRef("j")])`

## Success Criteria

- [ ] bearing.gms parses successfully
- [ ] All existing tests continue to pass (no regressions)
- [ ] 15+ new test cases added for attribute assignments
- [ ] Support for all common attributes (.scale, .lo, .up, .l, .m, .prior)
- [ ] Parse rate for Tier 2 models ≥ 33%

## References

- **GAMS Documentation:** User's Guide Section 6.3 "Variable Attributes"
- **GAMS Documentation:** User's Guide Section 7.2 "Parameter Attributes"
- **GAMS Attribute Reference:** https://www.gams.com/latest/docs/UG_VariableAttributes.html
- **Sprint 12 Planning:** Tier 2 model blocker analysis

## Example Test Cases

### Test 1: Variable scaling
```gams
Variable x;
x.scale = 1000;
```

### Test 2: Variable bounds
```gams
Variable y;
y.lo = -10;
y.up = 10;
```

### Test 3: Variable initial value
```gams
Variable z;
z.l = 5;
```

### Test 4: Indexed variable bounds
```gams
Variable x(i);
x.lo(i) = 0;
x.up(i) = capacity(i);
```

### Test 5: Multi-dimensional indexed attribute
```gams
Variable flow(i,j);
flow.l(i,j) = init_flow(i,j);
```

### Test 6: Multiple attributes
```gams
Variable x;
x.lo = 0;
x.up = 100;
x.l = 50;
x.scale = 100;
```

### Test 7: Fixed value
```gams
Variable x;
x.fx = 42;  # Equivalent to x.lo = 42; x.up = 42;
```

### Test 8: Branching priority
```gams
Variable z;
z.prior = 1;
```

### Test 9: Parameter attribute (if applicable)
```gams
Parameter p;
p.default = 0;
```
