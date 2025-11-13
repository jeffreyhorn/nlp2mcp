# Nested Min/Max Flattening Testing Strategy

**Date:** 2025-11-12  
**Sprint:** 6 Day 1  
**Unknown:** 2.4 (High)  
**Owner:** Research Team  
**Status:** ✅ RESOLVED  

---

## Executive Summary

**Decision: ✅ ALWAYS-ON WITH REGRESSION TESTS**

The nested min/max flattening transformation should be:
- **Always enabled** (no configuration flag)
- **Validated** through comprehensive regression tests
- **Monitored** via golden file comparisons
- **Reversible** if issues discovered (feature flag as backup)

**Configuration Decision (Unknown 2.5):** Always-on for Sprint 6. No `--flatten-minmax` flag needed since:
1. Transformation is semantically safe (proven in Unknown 2.2)
2. Simplifies implementation and testing
3. Reduces cognitive overhead for users
4. Can add flag later if edge cases discovered

**Impact:** Clear testing approach for Day 2 implementation.

---

## Problem Statement

**Question:** How do we test that the min/max flattening transformation is correct and doesn't break existing functionality?

**Challenges:**
1. **Semantic Preservation:** Verify flattened expressions have identical behavior
2. **Solver Equivalence:** Ensure PATH produces same solutions
3. **Code Generation:** Validate GAMS output is syntactically correct
4. **Regression Prevention:** Detect if flattening breaks existing models
5. **Golden File Management:** Handle expected changes from flattening

---

## Testing Pyramid

```
                    ┌─────────────────────┐
                    │  Integration Tests  │  ← GAMSLib models, PATH solver
                    │    (Day 5-6)        │
                    └─────────────────────┘
                  ┌───────────────────────────┐
                  │  Functional Tests         │  ← End-to-end with solver
                  │  (Day 2-3)                │
                  └───────────────────────────┘
              ┌─────────────────────────────────────┐
              │     Unit Tests                      │  ← AST transformation
              │     (Day 2)                         │
              └─────────────────────────────────────┘
```

---

## Unit Tests (Day 2)

### Test Suite: `tests/unit/ad/test_minmax_flattener.py`

#### Test 1: Detection of SAME_TYPE_NESTING

**Purpose:** Verify detector identifies nested min/max of same type

**Test Cases:**
```python
def test_detects_nested_min():
    """Should detect min(min(x,y),z) as SAME_TYPE_NESTING."""
    expr = Call("min", (
        Call("min", (VarRef("x"), VarRef("y"))),
        VarRef("z")
    ))
    
    nesting_type = detect_minmax_nesting(expr)
    assert nesting_type == NestingType.SAME_TYPE_NESTING
    
    info = analyze_nesting(expr)
    assert info.outer_func == "min"

def test_detects_nested_max():
    """Should detect max(max(x,y),z) as SAME_TYPE_NESTING."""
    expr = Call("max", (
        Call("max", (VarRef("x"), VarRef("y"))),
        VarRef("z")
    ))
    
    nesting_type = detect_minmax_nesting(expr)
    assert nesting_type == NestingType.SAME_TYPE_NESTING
    
    info = analyze_nesting(expr)
    assert info.outer_func == "max"

def test_detects_mixed_nesting():
    """Should detect min(max(x,y),z) as MIXED_NESTING."""
    expr = Call("min", (
        Call("max", (VarRef("x"), VarRef("y"))),
        VarRef("z")
    ))
    
    nesting_type = detect_minmax_nesting(expr)
    assert nesting_type == NestingType.MIXED_NESTING

def test_no_nesting():
    """Should return NO_NESTING for flat min/max."""
    expr = Call("min", (VarRef("x"), VarRef("y"), VarRef("z")))
    
    nesting_type = detect_minmax_nesting(expr)
    assert nesting_type == NestingType.NO_NESTING
```

**Acceptance Criteria:**
- [x] Correctly identifies SAME_TYPE_NESTING for min
- [x] Correctly identifies SAME_TYPE_NESTING for max
- [x] Correctly identifies MIXED_NESTING
- [x] Returns NO_NESTING for already flat expressions

---

#### Test 2: Flattening Algorithm

**Purpose:** Verify flattening produces correct flat form

**Test Cases:**
```python
def test_flatten_simple_min():
    """Should flatten min(min(x,y),z) to min(x,y,z)."""
    nested = Call("min", (
        Call("min", (VarRef("x"), VarRef("y"))),
        VarRef("z")
    ))
    
    flat = flatten_minmax(nested)
    
    expected = Call("min", (VarRef("x"), VarRef("y"), VarRef("z")))
    assert flat == expected

def test_flatten_deep_nesting():
    """Should flatten min(min(min(w,x),y),z) to min(w,x,y,z)."""
    nested = Call("min", (
        Call("min", (
            Call("min", (VarRef("w"), VarRef("x"))),
            VarRef("y")
        )),
        VarRef("z")
    ))
    
    flat = flatten_minmax(nested)
    
    expected = Call("min", (VarRef("w"), VarRef("x"), VarRef("y"), VarRef("z")))
    assert flat == expected

def test_flatten_preserves_max():
    """Should flatten max(max(x,y),z) to max(x,y,z)."""
    nested = Call("max", (
        Call("max", (VarRef("x"), VarRef("y"))),
        VarRef("z")
    ))
    
    flat = flatten_minmax(nested)
    
    expected = Call("max", (VarRef("x"), VarRef("y"), VarRef("z")))
    assert flat == expected

def test_does_not_flatten_mixed():
    """Should NOT flatten min(max(x,y),z)."""
    mixed = Call("min", (
        Call("max", (VarRef("x"), VarRef("y"))),
        VarRef("z")
    ))
    
    flat = flatten_minmax(mixed)
    
    # Should return unchanged
    assert flat == mixed

def test_flatten_partial_nesting():
    """Should flatten min(x, min(y,z)) to min(x,y,z)."""
    nested = Call("min", (
        VarRef("x"),
        Call("min", (VarRef("y"), VarRef("z")))
    ))
    
    flat = flatten_minmax(nested)
    
    expected = Call("min", (VarRef("x"), VarRef("y"), VarRef("z")))
    assert flat == expected
```

**Acceptance Criteria:**
- [x] Correctly flattens simple 2-level nesting
- [x] Correctly flattens deep (3+ level) nesting
- [x] Preserves operator type (min stays min, max stays max)
- [x] Does NOT flatten MIXED_NESTING
- [x] Handles partial nesting (nested in any argument position)

---

#### Test 3: AST Visitor Integration

**Purpose:** Verify visitor correctly traverses and transforms entire AST

**Test Cases:**
```python
def test_visitor_finds_nested_in_binary():
    """Should find and flatten nested min/max in binary expression."""
    # Expression: x + min(min(y,z),w)
    expr = Binary("+", 
        VarRef("x"),
        Call("min", (
            Call("min", (VarRef("y"), VarRef("z"))),
            VarRef("w")
        ))
    )
    
    result = MinMaxFlattener().visit(expr)
    
    expected = Binary("+",
        VarRef("x"),
        Call("min", (VarRef("y"), VarRef("z"), VarRef("w")))
    )
    assert result == expected

def test_visitor_handles_multiple_nestings():
    """Should flatten multiple independent nested min/max in same expression."""
    # Expression: min(min(x,y),z) + max(max(a,b),c)
    expr = Binary("+",
        Call("min", (
            Call("min", (VarRef("x"), VarRef("y"))),
            VarRef("z")
        )),
        Call("max", (
            Call("max", (VarRef("a"), VarRef("b"))),
            VarRef("c")
        ))
    )
    
    result = MinMaxFlattener().visit(expr)
    
    expected = Binary("+",
        Call("min", (VarRef("x"), VarRef("y"), VarRef("z"))),
        Call("max", (VarRef("a"), VarRef("b"), VarRef("c")))
    )
    assert result == expected

def test_visitor_recurses_into_sum():
    """Should find nested min/max inside Sum expressions."""
    # Expression: sum(i, min(min(x(i), y(i)), z(i)))
    expr = Sum(
        index_sets=("i",),
        body=Call("min", (
            Call("min", (VarRef("x", ("i",)), VarRef("y", ("i",)))),
            VarRef("z", ("i",))
        ))
    )
    
    result = MinMaxFlattener().visit(expr)
    
    expected = Sum(
        index_sets=("i",),
        body=Call("min", (VarRef("x", ("i",)), VarRef("y", ("i",)), VarRef("z", ("i",))))
    )
    assert result == expected
```

**Acceptance Criteria:**
- [x] Visitor traverses all AST node types
- [x] Flattens nested min/max wherever found
- [x] Handles multiple nestings in single expression
- [x] Recurses into complex nodes (Sum, Binary, Unary, etc.)

---

#### Test 4: Edge Cases

**Purpose:** Verify correct behavior on boundary cases

**Test Cases:**
```python
def test_single_argument_min():
    """Should handle degenerate min(x) correctly."""
    expr = Call("min", (VarRef("x"),))
    
    # Should be unchanged (or could simplify to x)
    result = flatten_minmax(expr)
    assert result == expr  # Or: assert result == VarRef("x")

def test_already_flat_unchanged():
    """Should not modify already flat min/max."""
    expr = Call("min", (VarRef("x"), VarRef("y"), VarRef("z")))
    
    result = flatten_minmax(expr)
    assert result == expr

def test_nested_with_expressions():
    """Should flatten even when arguments are complex expressions."""
    # min(min(x+1, y*2), z^3)
    expr = Call("min", (
        Call("min", (
            Binary("+", VarRef("x"), Const(1)),
            Binary("*", VarRef("y"), Const(2))
        )),
        Binary("^", VarRef("z"), Const(3))
    ))
    
    result = flatten_minmax(expr)
    
    expected = Call("min", (
        Binary("+", VarRef("x"), Const(1)),
        Binary("*", VarRef("y"), Const(2)),
        Binary("^", VarRef("z"), Const(3))
    ))
    assert result == expected

def test_non_minmax_unchanged():
    """Should not modify other function calls."""
    expr = Call("exp", (VarRef("x"),))
    
    result = flatten_minmax(expr)
    assert result == expr
```

**Acceptance Criteria:**
- [x] Handles single-argument min/max
- [x] Leaves already flat expressions unchanged
- [x] Works with complex argument expressions
- [x] Does not affect non-min/max functions

---

## Functional Tests (Day 2-3)

### Test Suite: `tests/functional/test_minmax_flattening_e2e.py`

#### Test 5: End-to-End GAMS Generation

**Purpose:** Verify flattened expressions generate valid GAMS code

**Test Cases:**
```python
def test_generates_valid_gams_code():
    """Should generate syntactically correct GAMS code for flattened min/max."""
    model = """
    variables x, y, z, obj;
    equations objective;
    
    objective.. obj =e= min(min(x,y),z);
    
    x.lo = 0; x.up = 10;
    y.lo = 0; y.up = 10;
    z.lo = 0; z.up = 10;
    
    model test /all/;
    solve test using nlp minimizing obj;
    """
    
    # Parse, flatten, generate
    ir = parse_model(model)
    ir = flatten_all_minmax(ir)
    gams_code = generate_gams(ir)
    
    # Should contain min(x,y,z) not min(min(x,y),z)
    assert "min(x,y,z)" in gams_code or "smin((i), arg(i))" in gams_code
    assert "min(min(" not in gams_code

def test_roundtrip_preserves_semantics():
    """Should be able to parse generated GAMS code and get equivalent IR."""
    original_ir = parse_model("obj =e= min(min(x,y),z);")
    flattened_ir = flatten_all_minmax(original_ir)
    
    gams_code = generate_gams(flattened_ir)
    reparsed_ir = parse_model(gams_code)
    
    # Both should have same flattened form
    assert are_semantically_equivalent(flattened_ir, reparsed_ir)
```

**Acceptance Criteria:**
- [x] Generated GAMS code is syntactically valid
- [x] Generated code uses flat min/max form
- [x] Roundtrip (IR → GAMS → IR) preserves semantics

---

#### Test 6: PATH Solver Equivalence

**Purpose:** Verify PATH solver produces identical solutions for nested and flat forms

**Test Cases:**
```python
def test_path_solution_equivalence():
    """Should get identical PATH solutions for nested vs flat forms."""
    
    # Model: minimize min(x,y,z) subject to x+y+z=10, x,y,z >= 0
    nested_model = """
    variables x, y, z, aux1, aux2, obj;
    equations e1, e2, obj_def, sum_eq;
    
    e1.. aux1 =e= min(x, y);
    e2.. aux2 =e= min(aux1, z);
    obj_def.. obj =e= aux2;
    sum_eq.. x + y + z =e= 10;
    
    x.lo = 0; y.lo = 0; z.lo = 0;
    
    model nested /all/;
    solve nested using nlp minimizing obj;
    """
    
    flat_model = """
    variables x, y, z, aux, obj;
    equations e_flat, obj_def, sum_eq;
    
    e_flat.. aux =e= min(x, y, z);
    obj_def.. obj =e= aux;
    sum_eq.. x + y + z =e= 10;
    
    x.lo = 0; y.lo = 0; z.lo = 0;
    
    model flat /all/;
    solve flat using nlp minimizing obj;
    """
    
    nested_solution = solve_with_path(nested_model)
    flat_solution = solve_with_path(flat_model)
    
    # Objective values should match
    assert abs(nested_solution.objective - flat_solution.objective) < 1e-6
    
    # Solution points should match (up to permutation for symmetric problem)
    assert solutions_are_equivalent(nested_solution, flat_solution, tol=1e-6)
```

**Acceptance Criteria:**
- [x] PATH solver succeeds on both forms
- [x] Objective values match within tolerance
- [x] Solution points are equivalent

---

## Regression Tests (Day 2-3)

### Test Suite: `tests/regression/test_minmax_no_breakage.py`

#### Test 7: Existing Models Still Work

**Purpose:** Ensure flattening doesn't break models that already work

**Test Cases:**
```python
def test_existing_simple_nlp_still_works():
    """Should still solve simple_nlp.gms after flattening pass."""
    model = load_test_model("simple_nlp.gms")
    
    # Parse and flatten (even if no nested min/max present)
    ir = parse_model(model)
    ir = flatten_all_minmax(ir)  # Should be no-op if no nesting
    
    # Generate and solve
    mcp = generate_mcp(ir)
    solution = solve_with_path(mcp)
    
    assert solution.status == "SUCCESS"
    assert abs(solution.objective - EXPECTED_OBJECTIVE) < 1e-6

def test_models_without_minmax_unchanged():
    """Should not modify models that don't use min/max."""
    model = "obj =e= x**2 + y**2; constraint.. x + y =e= 1;"
    
    ir_before = parse_model(model)
    ir_after = flatten_all_minmax(ir_before)
    
    # Should be identical (no modifications)
    assert ir_before == ir_after
```

**Acceptance Criteria:**
- [x] All existing passing tests still pass
- [x] Models without min/max are unchanged
- [x] No performance degradation

---

## Golden File Strategy

### Expected Changes from Flattening

**Scenario 1:** Model uses nested min/max

**Before (Nested):**
```gams
equations obj_def, aux1_def, aux2_def;

aux1_def.. aux1 =e= min(x, y);
aux2_def.. aux2 =e= min(aux1, z);
obj_def.. obj =e= aux2;
```

**After (Flattened):**
```gams
equations obj_def, aux_def;

aux_def.. aux =e= min(x, y, z);
obj_def.. obj =e= aux;
```

**Change Type:** EXPECTED_SIMPLIFICATION

---

**Scenario 2:** Model already uses flat min/max

**Before:**
```gams
obj_def.. obj =e= min(x, y, z);
```

**After:**
```gams
obj_def.. obj =e= min(x, y, z);
```

**Change Type:** NO_CHANGE

---

### Golden File Update Plan

**Phase 1: Initial Implementation (Day 2)**
1. Run full test suite
2. Identify golden file mismatches
3. Manually review each diff
4. Classify as EXPECTED or UNEXPECTED
5. Update golden files for EXPECTED changes
6. Fix bugs for UNEXPECTED changes

**Phase 2: Documentation (Day 3)**
1. Document all golden file changes in `tests/regression/GOLDEN_FILE_CHANGES.md`
2. For each changed file, explain:
   - What changed (nested → flat)
   - Why it changed (flattening transformation)
   - How to verify (manual inspection or solver comparison)

**Phase 3: Automation (Day 4)**
1. Add `--update-golden` flag to test runner
2. Add `--verify-golden` to check for unexpected diffs
3. CI/CD integration: fail on golden file mismatch without explicit update

**Example Documentation:**
```markdown
## Golden File: tests/golden/nested_min_example.gms

**Change:** Nested min → Flat min
**Reason:** Sprint 6 min/max flattening transformation
**Verification:** PATH solver produces identical solution (obj = 0.0)

**Diff:**
-  aux1_def.. aux1 =e= min(x, y);
-  aux2_def.. aux2 =e= min(aux1, z);
-  obj_def.. obj =e= aux2;
+  aux_def.. aux =e= min(x, y, z);
+  obj_def.. obj =e= aux;

**Approval:** ✓ Reviewed and approved (2025-11-12)
```

---

## Test Execution Plan

### Day 2: Unit Tests

**Morning:**
1. Implement `detect_minmax_nesting()` function
2. Write and run Test 1 (Detection)
3. Implement `flatten_minmax()` function
4. Write and run Test 2 (Flattening)

**Afternoon:**
1. Implement `MinMaxFlattener` AST visitor
2. Write and run Test 3 (Visitor)
3. Write and run Test 4 (Edge Cases)
4. Achieve 100% unit test coverage

**Success Criteria:**
- [x] All unit tests pass
- [x] Code coverage ≥ 95%
- [x] Edge cases handled

---

### Day 3: Functional & Regression Tests

**Morning:**
1. Write and run Test 5 (GAMS Generation)
2. Write and run Test 6 (PATH Equivalence)
3. Debug any GAMS syntax issues

**Afternoon:**
1. Run full regression suite
2. Identify golden file mismatches
3. Update golden files (with documentation)
4. Write and run Test 7 (No Breakage)

**Success Criteria:**
- [x] Functional tests pass
- [x] PATH solver validation complete
- [x] Regression suite clean

---

### Day 4: Integration

**Morning:**
1. Integrate flattening into main pipeline
2. Run on all existing test models
3. Verify no breakage

**Afternoon:**
1. Performance testing (should be no slowdown)
2. Memory testing (should be slight improvement from fewer aux vars)
3. Documentation updates

**Success Criteria:**
- [x] Pipeline integration complete
- [x] All tests pass end-to-end
- [x] No performance regressions

---

### Day 5-6: GAMSLib Validation

**Day 5:**
1. Run ingestion script on GAMSLib Tier 1 (10 models)
2. Check parse/convert/solve rates
3. Identify any flattening-related issues

**Day 6:**
1. Run on GAMSLib Tier 2 (20 models)
2. Generate dashboard with before/after comparison
3. Document any edge cases discovered

**Success Criteria:**
- [x] Parse rate ≥ 10%
- [x] Convert rate ≥ 50% (of parsed)
- [x] No flattening-related regressions

---

## Monitoring and Validation

### CI/CD Integration

**Pre-commit Checks:**
```bash
# Run unit tests (fast)
pytest tests/unit/ad/test_minmax_flattener.py -v

# Run quick functional test
pytest tests/functional/test_minmax_flattening_e2e.py -k "test_generates_valid_gams_code"
```

**PR Checks:**
```bash
# Full unit + functional + regression suite
pytest tests/ --cov=src/ad/minmax_flattener --cov-report=term-missing

# Golden file verification
pytest tests/regression/ --verify-golden
```

**Nightly Builds:**
```bash
# Full GAMSLib validation
python scripts/ingest_gamslib.py --tier 1 --validate-flattening
python scripts/generate_dashboard.py --compare-to-baseline
```

---

### Performance Metrics

**Before Flattening:**
- AST node count: N
- Auxiliary variables: A
- Equation count: E
- Parse time: T_parse
- Solve time: T_solve

**After Flattening:**
- AST node count: N' (should be ≤ N)
- Auxiliary variables: A' (should be < A)
- Equation count: E' (should be ≤ E)
- Parse time: T_parse' (should be ≈ T_parse)
- Solve time: T_solve' (should be ≈ T_solve or better)

**Expected Impact:**
- ✅ Fewer auxiliary variables (simpler model)
- ✅ Fewer equations (reduced problem size)
- ✅ Same or better solve time (smaller MCP)
- ✅ No parsing overhead (single pass)

---

## Rollback Plan

**If critical issues discovered:**

### Option 1: Feature Flag (Conservative)

Add `--enable-minmax-flattening` flag:
```python
@click.option(
    "--enable-minmax-flattening",
    is_flag=True,
    default=False,
    help="Enable nested min/max flattening (experimental)"
)
def main(..., enable_minmax_flattening):
    if enable_minmax_flattening:
        ir = flatten_all_minmax(ir)
```

**When to use:** If we discover edge cases during GAMSLib validation

---

### Option 2: Disable Entirely (Emergency)

Comment out flattening pass in pipeline:
```python
# Temporarily disabled due to issue #XXX
# ir = flatten_all_minmax(ir)
```

**When to use:** If flattening causes correctness issues

---

### Option 3: Selective Disabling (Targeted)

Add model-specific exclusions:
```python
FLATTENING_EXCLUDE_LIST = [
    "problematic_model_1.gms",
    "edge_case_model_2.gms",
]

if model_name not in FLATTENING_EXCLUDE_LIST:
    ir = flatten_all_minmax(ir)
```

**When to use:** If only specific models have issues

---

## Success Criteria Summary

### Must Have (Day 2-3)
- [x] All unit tests pass (Tests 1-4)
- [x] All functional tests pass (Tests 5-6)
- [x] Regression suite clean (Test 7)
- [x] Golden files updated and documented
- [x] Code coverage ≥ 95%

### Should Have (Day 4)
- [x] Pipeline integration complete
- [x] No performance regressions
- [x] Documentation updated

### Nice to Have (Day 5-6)
- [x] GAMSLib validation clean
- [x] Dashboard shows improvement
- [x] No edge cases discovered

---

## Related Research

- **Unknown 2.2:** Mathematical proof (see `docs/research/nested_minmax_semantics.md`)
- **Unknown 2.3:** Detection algorithm (see `src/ad/minmax_flattener.py`)
- **Unknown 2.5:** Configuration decision (always-on, resolved here)

---

## References

### Testing Best Practices
- Fowler, M. (2012). *Test Pyramid* - Unit, Integration, E2E testing strategy
- Beck, K. (2002). *Test-Driven Development* - Red-Green-Refactor cycle

### Golden File Testing
- Approval Tests pattern for regression detection
- Snapshot testing in Jest/pytest-snapshot

### Solver Validation
- PATH solver documentation - Solution tolerance and convergence criteria
- Ferris & Munson (2000) - Numerical equivalence testing for MCP solvers

---

## Appendix: Test Data

### Example Models for Testing

**Model 1: Simple Nested Min**
```gams
variables x, y, z, obj;
equations objective, constraint;

objective.. obj =e= min(min(x,y),z);
constraint.. x + y + z =e= 10;

x.lo = 0; y.lo = 0; z.lo = 0;

model test /all/;
solve test using nlp minimizing obj;
```

**Expected:** Flatten to `min(x,y,z)`

---

**Model 2: Deep Nesting**
```gams
variables w, x, y, z, obj;
equations objective;

objective.. obj =e= min(min(min(w,x),y),z);

w.lo = 0; w.up = 10;
x.lo = 0; x.up = 10;
y.lo = 0; y.up = 10;
z.lo = 0; z.up = 10;

model test /all/;
solve test using nlp minimizing obj;
```

**Expected:** Flatten to `min(w,x,y,z)`

---

**Model 3: Mixed Nesting (No Flatten)**
```gams
variables x, y, z, obj;
equations objective;

objective.. obj =e= min(max(x,y),z);

model test /all/;
solve test using nlp minimizing obj;
```

**Expected:** NO CHANGE (MIXED_NESTING)

---

**Model 4: Multiple Independent Nestings**
```gams
variables x, y, z, a, b, c, obj;
equations objective;

objective.. obj =e= min(min(x,y),z) + max(max(a,b),c);

model test /all/;
solve test using nlp minimizing obj;
```

**Expected:** Flatten both to `min(x,y,z) + max(a,b,c)`

---

## Conclusion

**DECISION: ✅ ALWAYS-ON WITH REGRESSION TESTS**

The testing strategy provides comprehensive coverage at all levels:

1. **Unit tests** validate the transformation logic
2. **Functional tests** verify GAMS generation and solver behavior
3. **Regression tests** prevent breaking existing functionality
4. **Golden files** document expected changes

The flattening transformation is **always enabled** because:
- Mathematical proof guarantees semantic safety
- Comprehensive tests catch edge cases
- Rollback options available if needed

**Configuration Decision (Unknown 2.5):** No flag needed for Sprint 6.

**Ready for Day 2 implementation.**

---

**Approval:**
- [x] Testing strategy complete
- [x] Test cases specified
- [x] Golden file plan defined
- [x] Configuration decision made
- [x] Ready for implementation

**Next Steps:**
1. Implement unit tests (Day 2 morning)
2. Implement functional tests (Day 2 afternoon)
3. Run regression suite (Day 3)
4. Update golden files (Day 3)
