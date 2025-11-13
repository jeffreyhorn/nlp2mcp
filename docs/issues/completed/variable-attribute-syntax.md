# Parser Enhancement: Variable Attribute Syntax Support

**GitHub Issue:** #199  
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/199  
**Priority:** HIGH  
**Impact:** 60% of GAMSLib Tier 1 models blocked  
**Effort:** Medium  
**Sprint:** Sprint 7  

---

## Problem Statement

The GAMS parser currently does not support variable attribute assignment syntax (`.l`, `.lo`, `.up`, `.m`, `.fx`), which is a fundamental GAMS feature used to set initial values, bounds, and marginals. This blocks 6 out of 10 (60%) Tier 1 GAMSLib models from parsing.

### Evidence from Sprint 6 Day 5 Ingestion

**Models Affected:**
- `trig.gms` - Line 27: `x1.l = 1;`
- `rbrock.gms` - Line 19: `x1.l = -1.2;`
- `mathopt1.gms` - Line 27: `x1.l = 8; x2.l = -14;`
- `mhw4d.gms` - Line 27: `x1.l = -1;`
- `mhw4dx.gms` - Line 31: `x1.l = -1;`
- `rbrock.gms` - Line 19: `x1.lo = -10; x1.up = 5;`

**Parse Error:**
```
No terminal matches 'l' in the current parser context, at line 27 col 4
x1.l = -1;
   ^
Expected one of: 
    * BOUND_K
```

---

## Current Behavior

The parser treats variable names as complete identifiers and does not recognize the dot notation for accessing variable attributes.

**Example that fails:**
```gams
Variable x1, x2;

x1.l = 1.5;      // Initial level (starting value)
x1.lo = 0;       // Lower bound
x1.up = 10;      // Upper bound
x2.m = 0;        // Initial marginal value
```

---

## Expected Behavior

The parser should recognize and handle variable attribute assignments:

**Syntax Pattern:**
```gams
<variable_name>.<attribute> = <value>;
```

**Supported Attributes:**
- `.l` - Level (initial value)
- `.lo` - Lower bound
- `.up` - Upper bound
- `.m` - Marginal value
- `.fx` - Fixed value (sets .lo = .up = value)
- `.prior` - Priority for branching
- `.scale` - Scaling factor

**Most Common (Priority for Sprint 7):**
- `.l`, `.lo`, `.up` (used in 60% of failing models)

---

## Proposed Solution

### Phase 1: Grammar Extension (Sprint 7)

Update `src/gams/gams_grammar.lark` to support dot notation:

```lark
// Add variable attribute assignment rule
variable_attr_assign: ID "." attribute_name "=" expr ";"

attribute_name: "l" | "lo" | "up" | "m" | "fx" | "prior" | "scale"

// Update statement rule to include variable attributes
statement: ... 
         | variable_attr_assign
```

### Phase 2: Parser Implementation

Update `src/ir/parser.py` to handle attribute assignments:

```python
def _handle_variable_attr_assign(self, tree: Tree) -> None:
    """Process variable attribute assignment (e.g., x.l = 5)."""
    var_name = tree.children[0].value
    attr_name = tree.children[1].value  # 'l', 'lo', 'up', etc.
    value = self._eval_expr(tree.children[2])
    
    # Map to appropriate ModelIR structure
    if attr_name == "l":
        # Set initial level
        self._set_initial_value(var_name, value)
    elif attr_name == "lo":
        # Set lower bound
        self._set_lower_bound(var_name, value)
    elif attr_name == "up":
        # Set upper bound
        self._set_upper_bound(var_name, value)
    # ... handle other attributes
```

### Phase 3: ModelIR Integration

Ensure ModelIR can store attribute information:
- Initial values for variables
- Bounds (already supported via VariableDef)
- Marginals (if needed for warm starts)

---

## Implementation Steps

1. **Update Grammar** (1-2 hours)
   - Add `variable_attr_assign` rule
   - Add `attribute_name` terminal
   - Test parsing isolated examples

2. **Update Parser** (2-3 hours)
   - Add handler for attribute assignments
   - Map to existing ModelIR structures
   - Handle indexed variables (e.g., `x(i).l = data(i);`)

3. **Add Tests** (2-3 hours)
   - Unit tests for attribute assignment parsing
   - Integration tests with real GAMSLib models
   - Edge cases (multiple attributes on same line)

4. **Re-run Ingestion** (1 hour)
   - Run `python scripts/ingest_gamslib.py`
   - Verify 6 models now parse successfully
   - Target: ≥60% parse rate

**Total Effort:** 6-9 hours

---

## Test Cases

### Test 1: Basic Level Assignment
```gams
Variable x;
x.l = 5;
```

**Expected:** Parse successfully, set x initial value to 5

### Test 2: Multiple Attributes
```gams
Variable x;
x.lo = 0;
x.up = 10;
x.l = 5;
```

**Expected:** Parse successfully, set bounds and initial value

### Test 3: Multiple Attributes on One Line
```gams
Variable x;
x.lo = 0; x.up = 10; x.l = 5;
```

**Expected:** Parse successfully

### Test 4: Indexed Variable Attributes
```gams
Variable x(i);
x.l(i) = data(i);
```

**Expected:** Parse successfully (may be Phase 2)

### Test 5: Expression on RHS
```gams
Variable x, y;
x.l = 2 * y.l + 5;
```

**Expected:** Parse successfully, evaluate expression

---

## Acceptance Criteria

- [ ] Grammar updated to support `.l`, `.lo`, `.up` attributes
- [ ] Parser correctly handles attribute assignments
- [ ] Unit tests added and passing (≥5 test cases)
- [ ] All 6 affected GAMSLib models parse successfully
- [ ] Parse rate increases from 0% to ≥60%
- [ ] Documentation updated with attribute syntax support
- [ ] No regressions in existing tests

---

## References

- **Sprint 6 Day 5 Ingestion Report:** `reports/gamslib_ingestion_sprint6.json`
- **Parse Error Analysis:** `docs/research/gamslib_parse_errors.md`
- **GAMS Documentation:** Variable attributes are documented in GAMS User's Guide
- **Related Models:** `tests/fixtures/gamslib/{trig,rbrock,mathopt1,mhw4d,mhw4dx}.gms`

---

## Dependencies

- None - can be implemented independently

---

## Related Issues

- Issue #200: Support model equation list syntax (20% impact)
- Epic: Sprint 7 Parser Improvements
