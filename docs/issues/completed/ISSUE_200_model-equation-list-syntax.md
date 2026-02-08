# Parser Enhancement: Model Equation List Syntax Support

**GitHub Issue:** #200  
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/200  
**Priority:** HIGH  
**Impact:** 20% of GAMSLib Tier 1 models blocked  
**Effort:** Low  
**Sprint:** Sprint 6  

---

## Problem Statement

The GAMS parser currently only supports the `Model <name> / all /;` syntax, but does not support explicit equation list syntax `Model <name> / eq1, eq2, ... /;`. This blocks 2 out of 10 (20%) Tier 1 GAMSLib models from parsing and is a common pattern in production GAMS code for selective model execution.

### Evidence from Sprint 6 Day 5 Ingestion

**Models Affected:**
- `hs62.gms` - Line 35: `Model mx / objdef, eq1x /;`
- `mingamma.gms` - Line 26: `Model m2 / y2def /;`

**Parse Error:**
```
No terminal matches 'm' in the current parser context, at line 35 col 4
   mx / objdef, eq1x /;
   ^
Expected one of: 
    * SEMI
```

---

## Current Behavior

The parser only recognizes the `/all/` keyword in model declarations:

**Works:**
```gams
Model mymodel / all /;
```

**Fails:**
```gams
Model mymodel / eq1, eq2, eq3 /;
Model mymodel / objdef, constraint1 /;
```

---

## Expected Behavior

The parser should support explicit equation lists in model declarations, allowing users to selectively include equations in a model.

**Syntax Patterns:**
```gams
// Single equation
Model m1 / eq1 /;

// Multiple equations
Model m2 / eq1, eq2, eq3 /;

// Mixed equation types
Model m3 / objdef, constraint1, constraint2, bound1 /;

// All equations (current behavior)
Model m4 / all /;
```

---

## Proposed Solution

### Phase 1: Grammar Extension (Sprint 7)

Update `src/gams/gams_grammar.lark` to support equation lists:

```lark
// Current rule (simplified)
model_stmt: MODEL ID "/" "all" "/" ";"

// Updated rule
model_stmt: MODEL ID "/" equation_list "/" ";"
          | MODEL ID "/" "all" "/" ";"

equation_list: ID ("," ID)*
```

### Phase 2: Parser Implementation

Update `src/ir/parser.py` to handle equation lists:

```python
def _handle_model_stmt(self, tree: Tree) -> None:
    """Process model statement with equation list."""
    model_name = tree.children[0].value
    
    # Check if using /all/ or explicit list
    equation_list_node = tree.children[1]
    
    if equation_list_node.data == "all":
        # Current behavior: include all equations
        equations = self._get_all_equations()
    else:
        # New behavior: explicit equation list
        equations = []
        for eq_name_token in equation_list_node.children:
            eq_name = eq_name_token.value
            if eq_name not in self.equations:
                raise ParserSemanticError(
                    f"Equation '{eq_name}' not defined",
                    line=eq_name_token.line,
                    column=eq_name_token.column
                )
            equations.append(eq_name)
    
    # Store model with selected equations
    self.models[model_name] = equations
```

### Phase 3: ModelIR Integration

Update ModelIR to track which equations belong to which model:
- Currently assumes all equations are in the model
- Need to support partial equation sets
- May need to filter equations during MCP generation

---

## Implementation Steps

1. **Update Grammar** (1 hour)
   - Add `equation_list` rule
   - Update `model_stmt` to support both syntaxes
   - Test parsing isolated examples

2. **Update Parser** (2 hours)
   - Add handler for explicit equation lists
   - Add validation (equation must be defined)
   - Handle multiple models with different equation sets

3. **Add Tests** (1-2 hours)
   - Unit tests for equation list parsing
   - Test with single equation, multiple equations
   - Test error handling (undefined equation)
   - Integration tests with GAMSLib models

4. **Re-run Ingestion** (30 minutes)
   - Run `python scripts/ingest_gamslib.py`
   - Verify 2 additional models now parse
   - Combined with variable attributes: target ≥80% parse rate

**Total Effort:** 4-5 hours

---

## Test Cases

### Test 1: Single Equation Model
```gams
Equation eq1;
eq1.. x =e= 5;
Model m1 / eq1 /;
```

**Expected:** Parse successfully, model contains only eq1

### Test 2: Multiple Equations
```gams
Equations eq1, eq2, eq3;
eq1.. x =e= 5;
eq2.. y =l= 10;
eq3.. x + y =g= 3;
Model m1 / eq1, eq2 /;
```

**Expected:** Parse successfully, model contains eq1 and eq2 only

### Test 3: All vs. Explicit List
```gams
Equations eq1, eq2, eq3;
eq1.. x =e= 5;
eq2.. y =l= 10;
eq3.. x + y =g= 3;
Model m1 / all /;        // Contains eq1, eq2, eq3
Model m2 / eq1, eq3 /;   // Contains only eq1, eq3
```

**Expected:** Both parse successfully

### Test 4: Undefined Equation Error
```gams
Equations eq1;
eq1.. x =e= 5;
Model m1 / eq1, undefined_eq /;
```

**Expected:** Parse error with clear message about undefined equation

### Test 5: Real GAMSLib Models
```gams
// From hs62.gms
Equations objdef, eq1x;
objdef.. obj =e= ...;
eq1x.. ... =l= ...;
Model mx / objdef, eq1x /;
```

**Expected:** Parse successfully

---

## Acceptance Criteria

**Note:** As of Sprint 6, this feature was discovered to be already implemented. Comprehensive test coverage was added to verify functionality. Full GAMSLib model testing is pending due to additional syntax issues in those models.

- [x] Grammar updated to support explicit equation lists *(already implemented)*
- [x] Parser correctly handles equation list syntax *(already implemented)*
- [x] Parser validates that all equations in list are defined *(already implemented)*
- [x] Unit tests added and passing (≥7 test cases)
- [ ] Both affected GAMSLib models parse successfully *(pending: models have additional syntax issues)*
- [ ] Parse rate increases (combined with variable attributes: ≥80%) *(pending: models have additional syntax issues)*
- [x] Backward compatibility: `/all/` syntax still works
- [x] Documentation updated with equation list syntax support
- [x] No regressions in existing tests

---

## Use Cases

### Use Case 1: Debugging Models
Users often create multiple models with different equation subsets to isolate issues:
```gams
Model full_model / all /;
Model without_constraints / objdef /;  // Unconstrained optimization
Model only_feasibility / constraint1, constraint2 /;  // Check feasibility
```

### Use Case 2: Model Variants
Different model formulations using shared equations:
```gams
Model linear_model / objdef, linear_constraints /;
Model nonlinear_model / objdef, nonlinear_constraints /;
```

### Use Case 3: Progressive Complexity
Building up model complexity incrementally:
```gams
Model basic / obj, eq1 /;
Model intermediate / obj, eq1, eq2 /;
Model advanced / obj, eq1, eq2, eq3, eq4 /;
```

---

## References

- **Sprint 6 Day 5 Ingestion Report:** `reports/gamslib_ingestion_sprint6.json`
- **Parse Error Analysis:** `docs/research/gamslib_parse_errors.md` (Error Category 4)
- **GAMS Documentation:** Model statement syntax in GAMS User's Guide Chapter 3
- **Related Models:** `tests/fixtures/gamslib/{hs62,mingamma}.gms`

---

## Dependencies

- None - can be implemented independently
- Works well in combination with variable attribute syntax (Issue #TBD)

---

## Related Issues

- Issue #199: Variable attribute syntax support (60% impact)
- Epic: Sprint 7 Parser Improvements

---

## Implementation Priority

**Priority: HIGH (after variable attributes)**

Rationale:
1. Low implementation effort (4-5 hours)
2. High user value (common pattern in production code)
3. 20% of models blocked by this issue
4. Combined with variable attributes: 80% parse rate achievable
