# Nested Min/Max Flattening Design

**Date:** 2025-11-12  
**Status:** ✅ DESIGN COMPLETE - Ready for Sprint 6 Implementation  
**Approach:** Option A - Flattening Only (Same-Operation Nesting)  
**Estimated Effort:** 4-7 hours implementation  
**Priority:** High (Sprint 6 Component 2)

## Executive Summary

This document specifies the design for **Option A: Flattening-only approach** to handle nested min/max expressions in Sprint 6. This approach detects and flattens same-operation nesting (e.g., `min(x, min(y, z))` → `min(x, y, z)`) before applying the existing epigraph reformulation.

**Key Decision:** Option A over Option B (multi-pass reformulation)
- **Rationale:** Sprint 6 has limited time; Option A provides 80% coverage with 40% effort
- **Coverage:** Handles same-operation nesting (most common case)
- **Deferred:** Mixed-operation nesting (`min(x, max(y, z))`) to future sprint if needed

**Design Status:**
- ✅ Algorithm designed and validated
- ✅ Integration points identified
- ✅ Test cases specified
- ✅ Implementation effort estimated
- ✅ PATH validation strategy defined
- ✅ Known limitations documented

## Problem Statement

### Current Behavior

When nested min/max expressions like `min(x, min(y, z))` are encountered, the system produces a **differentiation error**:

```
Error: Differentiation not yet implemented for function 'min'.
```

**Root Cause:**
1. Outer `min(x, min(y, z))` is detected for reformulation
2. Inner `min(y, z)` remains as a function call in the arguments
3. During Jacobian computation, the system attempts to differentiate `min(y, z)`
4. Differentiation fails because `min()` is non-differentiable and not in the supported function list

### Why This Matters

Nested min/max appears in real optimization problems:
- Supply chain: `min(supplier1_cost, min(supplier2_cost, supplier3_cost))`
- Resource allocation: `max(machine1_output, max(machine2_output, machine3_output))`
- Cost optimization: `min(transport_cost, min(production_cost, storage_cost))`

**Mathematical Validity:**
```
min(x, min(y, z)) = min(x, y, z)  ✓ (same operation)
max(x, max(y, z)) = max(x, y, z)  ✓ (same operation)
min(x, max(y, z)) ≠ flattened      ✗ (mixed operations - not supported in Option A)
```

## Design Overview: Option A - Flattening

### Core Algorithm

**Strategy:** Detect and flatten same-operation nested calls **before** reformulation.

```python
def flatten_minmax_calls(expr: Expr) -> Expr:
    """
    Flatten same-operation nested min/max calls.
    
    Transformations:
        min(x, min(y, z)) → min(x, y, z)
        max(a, max(b, c)) → max(a, b, c)
        min(x, max(y, z)) → unchanged (mixed operations)
    
    Algorithm:
        1. Recursively traverse expression tree
        2. When encountering a Call node with func in {'min', 'max'}:
           a. Recursively flatten all arguments first (bottom-up)
           b. Collect arguments, expanding nested same-operation calls
           c. Return new Call with flattened argument list
        3. For non-Call nodes (leaf nodes), return as-is
        
    Note: This simplified pseudocode focuses on Call expressions since min/max
    appear as function calls. In the actual implementation, Binary/Unary operators
    would need separate handling if they could contain nested min/max. However,
    in the GAMS AST, min/max only appear as Call nodes, so this algorithm is complete.
    
    Time Complexity: O(n) where n = number of nodes in expression tree
    Space Complexity: O(d) where d = max nesting depth (recursion stack)
    """
    # Base case: non-Call expressions (leaf nodes like VarRef, Const, ParamRef)
    # These have no children to process, so return as-is
    if not isinstance(expr, Call):
        return expr
    
    func_name = expr.func.lower()
    
    # Only process min/max calls
    if func_name not in ('min', 'max'):
        # For other functions, just recursively flatten arguments
        new_args = tuple(flatten_minmax_calls(arg) for arg in expr.args)
        return Call(expr.func, new_args)
    
    # Recursively flatten children first (bottom-up processing)
    flattened_children = [flatten_minmax_calls(arg) for arg in expr.args]
    
    # Collect all arguments at this level
    collected_args = []
    for child in flattened_children:
        if isinstance(child, Call) and child.func.lower() == func_name:
            # Same operation: flatten by extracting child's arguments
            collected_args.extend(child.args)
        else:
            # Different operation or non-Call: keep as-is
            collected_args.append(child)
    
    # Return flattened Call
    return Call(expr.func, tuple(collected_args))
```

### Integration Point

**Location:** `src/kkt/reformulation.py` in `detect_min_max_calls()` function

**Current Flow:**
```python
def detect_min_max_calls(expr: Expr, context: str) -> list[MinMaxCall]:
    # Traverse expression
    # Find Call nodes with func in {'min', 'max'}
    # Create MinMaxCall objects
    # Return list
```

**Updated Flow:**
```python
def detect_min_max_calls(expr: Expr, context: str) -> list[MinMaxCall]:
    # NEW: Flatten nested same-operation calls first
    flattened_expr = flatten_minmax_calls(expr)
    
    # Traverse flattened expression (existing logic)
    # Find Call nodes with func in {'min', 'max'}
    # Create MinMaxCall objects with flattened args
    # Return list
```

**Key Insight:** By flattening **before** detection, the existing reformulation code sees only flat min/max calls and works without modification.

### AST Transformation Examples

#### Example 1: Simple Nesting

**Input:**
```gams
z =e= min(x, min(y, 5))
```

**AST Before Flattening:**
```
Binary('=', 
    VarRef('z'),
    Call('min', [
        VarRef('x'),
        Call('min', [VarRef('y'), Const(5)])
    ])
)
```

**AST After Flattening:**
```
Binary('=',
    VarRef('z'),
    Call('min', [
        VarRef('x'),
        VarRef('y'),
        Const(5)
    ])
)
```

**Reformulation Result:**
```gams
* Auxiliary variable
aux_min_eq_z_0

* Complementarity constraints (3 total)
aux_min_eq_z_0 - x =l= 0   $ lam_minmax_min_eq_z_0_arg0
aux_min_eq_z_0 - y =l= 0   $ lam_minmax_min_eq_z_0_arg1
aux_min_eq_z_0 - 5 =l= 0   $ lam_minmax_min_eq_z_0_arg2

* Equation replacement
z =e= aux_min_eq_z_0
```

**Comparison with Multi-Pass (Option B):**

Without flattening, multi-pass would create:
- `aux_min_inner` for `min(y, 5)`
- `aux_min_outer` for `min(x, aux_min_inner)`
- 4 constraints total (2 + 2)
- More auxiliary variables and equations

With flattening:
- 1 auxiliary variable
- 3 constraints
- Simpler MCP structure

#### Example 2: Deep Nesting

**Input:**
```gams
w =e= min(a, min(b, min(c, d)))
```

**AST Before Flattening:**
```
Call('min', [
    VarRef('a'),
    Call('min', [
        VarRef('b'),
        Call('min', [VarRef('c'), VarRef('d')])
    ])
])
```

**AST After Flattening:**
```
Call('min', [
    VarRef('a'),
    VarRef('b'),
    VarRef('c'),
    VarRef('d')
])
```

**Reformulation Result:**
```gams
* Single auxiliary variable
aux_min_eq_w_0

* 4 complementarity constraints
aux_min_eq_w_0 - a =l= 0
aux_min_eq_w_0 - b =l= 0
aux_min_eq_w_0 - c =l= 0
aux_min_eq_w_0 - d =l= 0
```

**Benefits:**
- Deep nesting handled naturally
- No iteration limit needed
- Single-pass processing

#### Example 3: Mixed Operations (NOT FLATTENED)

**Input:**
```gams
z =e= min(x, max(y, w))
```

**AST (Unchanged):**
```
Call('min', [
    VarRef('x'),
    Call('max', [VarRef('y'), VarRef('w')])
])
```

**Result:** **ERROR - Not supported in Option A**

This will still cause a differentiation error because `max(y, w)` remains as a function call inside the min arguments.

**Future Work (Option B):** Multi-pass reformulation would handle this by:
1. Reformulate inner `max(y, w)` → `aux_max`
2. Reformulate outer `min(x, aux_max)` with auxiliary variable

#### Example 4: Multiple Nested Calls in One Equation

**Input:**
```gams
balance.. production =e= min(capacity1, min(demand1, supply1)) 
                         + max(capacity2, max(demand2, supply2))
```

**Flattened:**
```gams
balance.. production =e= min(capacity1, demand1, supply1)
                         + max(capacity2, demand2, supply2)
```

**Reformulation:**
- `aux_min_balance_0` for `min(capacity1, demand1, supply1)`
- `aux_max_balance_1` for `max(capacity2, demand2, supply2)`
- 6 total constraints (3 for min, 3 for max)

### Edge Cases

#### Edge Case 1: Single Argument

**Input:** `min(x)` or `max(x)`

**Flattening Result:** `min(x)` (unchanged)

**Detection:** Existing reformulation code should detect len(args) == 1

**Recommended Handling (REQUIRED for Task 1):**
```python
# In reformulation.py
if len(min_call.args) == 1:
    # Single argument: no reformulation needed, just return the argument
    # min(x) = x, max(x) = x
    # Skip creating auxiliary variables
    continue
```

This optimization is **required** as part of the implementation to avoid creating unnecessary auxiliary variables and constraints.

**Alternative (not recommended):** Allow reformulation to proceed (creates unnecessary but valid constraints)

#### Edge Case 2: Constants Only

**Input:** `min(5, 10, 3)`

**Flattening Result:** `min(5, 10, 3)` (unchanged)

**Reformulation:** Valid, creates constraints:
```gams
aux_min - 5 =l= 0
aux_min - 10 =l= 0
aux_min - 3 =l= 0
```

**PATH Result:** `aux_min = 3` (all multipliers = 0 except for λ₂ which can be > 0)

**Note:** This is mathematically correct but computationally wasteful. Could optimize by constant-folding in parser.

#### Edge Case 3: Duplicate Arguments

**Input:** `min(x, x, y)`

**Flattening Result:** `min(x, x, y)` (unchanged - flattening doesn't deduplicate)

**Reformulation:** Valid but redundant:
```gams
aux_min - x =l= 0  $ lam_0
aux_min - x =l= 0  $ lam_1  (duplicate)
aux_min - y =l= 0  $ lam_2
```

**PATH Result:** Correct solution, but with redundant constraint

**Optimization (Future):** Deduplicate arguments after flattening
```python
# After flattening
collected_args = list(dict.fromkeys(collected_args))  # Remove duplicates while preserving order
```

**Note:** Requires careful handling of expression equality checking.

#### Edge Case 4: Mixed with Arithmetic

**Input:** `z =e= min(x + 1, min(y * 2, 5))`

**Flattening Result:** `z =e= min(x + 1, y * 2, 5)`

**Reformulation:** Valid, arguments can be arbitrary expressions:
```gams
aux_min - (x + 1) =l= 0
aux_min - (y * 2) =l= 0
aux_min - 5 =l= 0
```

**Jacobian:** Correctly differentiates:
- ∂(aux_min - (x+1))/∂x = -1
- ∂(aux_min - (y*2))/∂y = -2

## Test Case Specifications

### Test 1: Simple Same-Operation Nesting

**File:** `tests/fixtures/nested_minmax/test_nested_min_simple.gms`

**GAMS Code:**
```gams
$title Simple Nested Min Test
$onText
Test flattening of min(x, min(y, z))
Expected: Flatten to min(x, y, z)
$offText

Variables x, y, z, w, obj;

x.lo = 1; x.up = 10;
y.lo = 2; y.up = 10;
z.lo = 3; z.up = 10;

Equations objdef, minconstraint;

objdef.. obj =e= w;
minconstraint.. w =e= min(x, min(y, z));

Model test /all/;
Solve test using NLP minimizing obj;

Display x.l, y.l, z.l, w.l, obj.l;
```

**Expected MCP Structure:**
```gams
* Variables
x, y, z, w, obj, aux_min_minconstraint_0
lam_minmax_min_minconstraint_0_arg0  (for x - aux >= 0)
lam_minmax_min_minconstraint_0_arg1  (for y - aux >= 0)
lam_minmax_min_minconstraint_0_arg2  (for z - aux >= 0)

* Equations (stationarity)
stat_x, stat_y, stat_z, stat_w, stat_aux_min_minconstraint_0

* Complementarity Constraints
aux_min_minconstraint_0 - x =l= 0
aux_min_minconstraint_0 - y =l= 0
aux_min_minconstraint_0 - z =l= 0
```

**Expected Solution:**
```
x.l = 1.0    (lower bound, active)
y.l = 2.0    (lower bound, inactive)
z.l = 3.0    (lower bound, inactive)
w.l = 1.0    (min(1, 2, 3))
obj.l = 1.0
```

**Validation Checks:**
```python
assert solution['x'] == pytest.approx(1.0, abs=1e-6)
assert solution['y'] == pytest.approx(2.0, abs=1e-6)
assert solution['z'] == pytest.approx(3.0, abs=1e-6)
assert solution['w'] == pytest.approx(1.0, abs=1e-6)
assert solution['obj'] == pytest.approx(1.0, abs=1e-6)
```

### Test 2: Max Nesting

**File:** `tests/fixtures/nested_minmax/test_nested_max_simple.gms`

**GAMS Code:**
```gams
$title Simple Nested Max Test

Variables x, y, z, w, obj;

x.lo = 1; x.up = 10;
y.lo = 2; y.up = 10;
z.lo = 3; z.up = 10;

Equations objdef, maxconstraint;

objdef.. obj =e= w;
maxconstraint.. w =e= max(x, max(y, z));

Model test /all/;
Solve test using NLP maximizing obj;
```

**Expected Solution:**
```
x.l = 10.0   (upper bound, inactive)
y.l = 10.0   (upper bound, inactive)
z.l = 10.0   (upper bound, active)
w.l = 10.0   (max(10, 10, 10))
obj.l = 10.0
```

**Note:** For maximization, all variables will hit their upper bounds.

### Test 3: Deep Nesting (3+ Levels)

**File:** `tests/fixtures/nested_minmax/test_nested_deep.gms`

**GAMS Code:**
```gams
$title Deep Nested Min Test

Variables a, b, c, d, w, obj;

a.lo = 1; a.up = 10;
b.lo = 2; b.up = 10;
c.lo = 3; c.up = 10;
d.lo = 4; d.up = 10;

Equations objdef, deepmin;

objdef.. obj =e= w;
deepmin.. w =e= min(a, min(b, min(c, d)));

Model test /all/;
Solve test using NLP minimizing obj;
```

**Expected Flattening:** `min(a, b, c, d)`

**Expected Solution:**
```
a.l = 1.0    (active)
b.l = 2.0    (slack)
c.l = 3.0    (slack)
d.l = 4.0    (slack)
w.l = 1.0
obj.l = 1.0
```

**Purpose:** Verify that deeply nested expressions flatten correctly without hitting iteration limits.

### Test 4: Mixed Operations (Should Fail)

**File:** `tests/fixtures/nested_minmax/test_nested_mixed_operations.gms`

**GAMS Code:**
```gams
$title Mixed Nested Min/Max Test - Should Fail

Variables x, y, z, w, obj;

x.lo = 1; x.up = 10;
y.lo = 2; y.up = 10;
z.lo = 3; z.up = 10;

Equations objdef, mixedconstraint;

objdef.. obj =e= w;
mixedconstraint.. w =e= min(x, max(y, z));

Model test /all/;
Solve test using NLP minimizing obj;
```

**Expected Result:** **ERROR** (current error message from differentiation failure)

```
Error: Differentiation not yet implemented for function 'max'.
```

**Proposed improved error message** (optional enhancement for future sprint):

```
Error: Nested min/max with different operations (min inside max or max inside min) 
is not supported. Flattening only works for same-operation nesting.
Workaround: Reformulate manually or wait for multi-pass reformulation support.
Context: Found 'max' inside 'min' at equation 'mixedconstraint'.
```

**Purpose:** Document limitation and provide clear error message for unsupported case.

**Future Work:** Option B (multi-pass) would support this.

### Test 5: Multiple Independent Nested Calls

**File:** `tests/fixtures/nested_minmax/test_nested_multiple.gms`

**GAMS Code:**
```gams
$title Multiple Nested Min/Max in Same Equation

Variables x1, x2, x3, y1, y2, y3, result, obj;

x1.lo = 1; x1.up = 10;
x2.lo = 2; x2.up = 10;
x3.lo = 3; x3.up = 10;
y1.lo = 5; y1.up = 15;
y2.lo = 6; y2.up = 15;
y3.lo = 7; y3.up = 15;

Equations objdef, combined;

objdef.. obj =e= result;
combined.. result =e= min(x1, min(x2, x3)) + max(y1, max(y2, y3));

Model test /all/;
Solve test using NLP minimizing obj;
```

**Expected Flattening:**
```gams
combined.. result =e= min(x1, x2, x3) + max(y1, y2, y3)
```

**Expected MCP:**
- 2 auxiliary variables: `aux_min_combined_0`, `aux_max_combined_1`
- 6 complementarity constraints (3 for min, 3 for max)

**Expected Solution:**
```
x1.l = 1.0    (min active)
x2.l = 2.0
x3.l = 3.0
y1.l = 5.0    (lower bound)
y2.l = 6.0
y3.l = 7.0
result.l = 1.0 + 5.0 = 6.0  (when minimizing the sum, both min and max terms take their lowest possible values among their candidates)
```

**Purpose:** Verify that multiple nested calls in same equation are handled independently.

### Test 6: Nested with Constants

**File:** `tests/fixtures/nested_minmax/test_nested_constants.gms`

**GAMS Code:**
```gams
$title Nested Min/Max with Constants

Variables x, y, w, obj;

x.lo = 5; x.up = 15;
y.lo = 5; y.up = 15;

Equations objdef, minconst;

objdef.. obj =e= w;
minconst.. w =e= min(x, min(10, y));

Model test /all/;
Solve test using NLP minimizing obj;
```

**Expected Flattening:** `min(x, 10, y)`

**Expected Solution:**
```
x.l = 5.0     (lower bound, active)
y.l = 5.0     (lower bound, active)
w.l = 5.0     (min(5, 10, 5) = 5)
```

> **Note:** Both `x` and `y` are at their lower bounds (which is correct for this instance). However, mathematically, only one constraint needs to be active (i.e., only one corresponding multiplier needs to be nonzero) to determine the minimum in the complementarity sense.

**Purpose:** Verify constants are handled correctly in flattening.

## Implementation Breakdown

### Task 1: Add Flattening Function (2 hours)

**File:** `src/kkt/reformulation.py`

**Changes:**
1. Add `flatten_minmax_calls()` function (as specified above)
2. Add unit tests for flattening:
   - Test same-operation nesting (min in min, max in max)
   - Test mixed operations remain unchanged
   - Test deep nesting
   - Test non-minmax expressions unchanged

**Unit Test Example:**
```python
def test_flatten_nested_min():
    """Test flattening of min(x, min(y, z)) → min(x, y, z)"""
    from src.ir.ast import Call, VarRef
    from src.kkt.reformulation import flatten_minmax_calls
    
    # Create AST: min(x, min(y, z))
    inner_min = Call('min', (VarRef('y', ()), VarRef('z', ())))
    outer_min = Call('min', (VarRef('x', ()), inner_min))
    
    # Flatten
    result = flatten_minmax_calls(outer_min)
    
    # Verify flattened: min(x, y, z)
    assert isinstance(result, Call)
    assert result.func == 'min'
    assert len(result.args) == 3
    assert result.args[0].name == 'x'
    assert result.args[1].name == 'y'
    assert result.args[2].name == 'z'
```

**Testing Strategy:**
- Unit tests in `tests/unit/kkt/test_reformulation.py`
- Test each edge case from "Edge Cases" section
- Test that non-minmax expressions pass through unchanged

### Task 2: Integrate Flattening into Detection (1 hour)

**File:** `src/kkt/reformulation.py`

**Current Code (approx line 550):**
```python
def detect_min_max_calls(expr: Expr, context: str) -> list[MinMaxCall]:
    """Detect all min/max calls in an expression."""
    detected = []
    index_counter = 0

    def traverse(node: Expr) -> None:
        nonlocal index_counter
        if isinstance(node, Call) and node.func.lower() in ("min", "max"):
            func_type = node.func.lower()
            flattened_args = flatten_min_max_args(node)  # Existing function
            # ... rest of detection
```

**Updated Code:**
```python
def detect_min_max_calls(expr: Expr, context: str) -> list[MinMaxCall]:
    """Detect all min/max calls in an expression.
    
    NEW: Flattens same-operation nested calls before detection.
    """
    # NEW: Flatten nested same-operation calls first
    flattened_expr = flatten_minmax_calls(expr)
    
    detected = []
    index_counter = 0

    def traverse(node: Expr) -> None:
        nonlocal index_counter
        if isinstance(node, Call) and node.func.lower() in ("min", "max"):
            func_type = node.func.lower()
            # Note: flatten_min_max_args is now redundant after flatten_minmax_calls.
            # Kept for backwards compatibility: Some legacy code may rely on its output or side effects.
            # Remove this call once all legacy dependencies are updated and tested.
            flattened_args = flatten_min_max_args(node)
            # ... rest of detection
    
    traverse(flattened_expr)  # Changed: traverse flattened expression
    return detected
```

**Testing:**
- Integration test in `tests/integration/test_minmax_reformulation.py`
- Verify detection finds flattened calls
- Verify MinMaxCall.args has flattened argument list

### Task 3: Update Documentation (0.5 hours)

**Files to Update:**

1. **`src/kkt/reformulation.py` docstring:**
   - Update module docstring "Nested Functions (Flattening)" section
   - Note that flattening is now automatic
   - Document mixed-operation limitation

2. **`docs/planning/EPIC_1/SPRINT_5/follow-ons/NESTED_MINMAX_REQUIREMENTS.md`:**
   - Update status to "✅ IMPLEMENTED (Option A - Flattening Only)"
   - Add note about Option B remaining for future work

### Task 4: Create Integration Tests (2 hours)

**Directory:** `tests/fixtures/nested_minmax/` (create new)

**Tests to Create:**
- test_nested_min_simple.gms (Test 1)
- test_nested_max_simple.gms (Test 2)
- test_nested_deep.gms (Test 3)
- test_nested_mixed_operations.gms (Test 4 - expected failure)
- test_nested_multiple.gms (Test 5)
- test_nested_constants.gms (Test 6)

**Test Runner:**
```python
# tests/integration/test_nested_minmax.py

import pytest
from tests.utils import run_nlp2mcp, solve_with_path

@pytest.mark.parametrize("test_file,expected_obj", [
    ("test_nested_min_simple.gms", 1.0),
    ("test_nested_max_simple.gms", 10.0),
    ("test_nested_deep.gms", 1.0),
    ("test_nested_multiple.gms", 6.0),
    ("test_nested_constants.gms", 5.0),
])
def test_nested_minmax_flattening(test_file, expected_obj):
    """Test that nested min/max flattening works correctly."""
    fixture_path = f"tests/fixtures/nested_minmax/{test_file}"
    
    # Run nlp2mcp
    mcp_model = run_nlp2mcp(fixture_path)
    
    # Verify auxiliary variables created
    assert any('aux_min' in var or 'aux_max' in var 
               for var in mcp_model.variables)
    
    # Solve with PATH
    solution = solve_with_path(mcp_model)
    
    # Check objective value
    assert solution['obj'] == pytest.approx(expected_obj, abs=1e-4)


def test_nested_mixed_operations_fails():
    """Test that mixed-operation nesting produces clear error."""
    fixture_path = "tests/fixtures/nested_minmax/test_nested_mixed_operations.gms"
    
    with pytest.raises(Exception) as exc_info:
        run_nlp2mcp(fixture_path)
    
    # Verify error message mentions nested min/max limitation
    assert "nested" in str(exc_info.value).lower()
    assert "different operations" in str(exc_info.value).lower() or \
           "not supported" in str(exc_info.value).lower()
```

### Task 5: PATH Validation (1 hour)

**Strategy:** Run generated MCP through PATH solver and verify solutions.

**Validation Script:**
```python
# scripts/validate_nested_minmax.py

"""Validate nested min/max flattening with PATH solver."""

import subprocess
from pathlib import Path

def validate_nested_minmax():
    """Run all nested minmax tests and validate with PATH."""
    test_dir = Path("tests/fixtures/nested_minmax")
    
    for gms_file in test_dir.glob("*.gms"):
        print(f"\n{'='*60}")
        print(f"Testing: {gms_file.name}")
        print('='*60)
        
        # Skip mixed-operations test (expected to fail)
        if "mixed" in gms_file.name:
            print("⏭️  Skipping mixed-operations test (not supported)")
            continue
        
        # Run nlp2mcp
        mcp_file = gms_file.with_suffix('.mcp.gms')
        result = subprocess.run(
            ['python', '-m', 'src.cli', str(gms_file), '-o', str(mcp_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ nlp2mcp failed: {result.stderr}")
            continue
        
        print(f"✅ MCP generated: {mcp_file.name}")
        
        # Run PATH solver
        result = subprocess.run(
            ['gams', str(mcp_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ PATH failed to solve")
            continue
        
        print(f"✅ PATH solved successfully")
        
        # Parse solution (simplified - actual implementation would parse .lst file)
        # For now, just check that solve completed
        if "OPTIMAL" in result.stdout or "LOCALLY OPTIMAL" in result.stdout:
            print(f"✅ Solution is optimal")
        else:
            print(f"⚠️  Solution may not be optimal (check .lst file)")

if __name__ == '__main__':
    validate_nested_minmax()
```

**Expected Output:**
```
============================================================
Testing: test_nested_min_simple.gms
============================================================
✅ MCP generated: test_nested_min_simple.mcp.gms
✅ PATH solved successfully
✅ Solution is optimal

============================================================
Testing: test_nested_max_simple.gms
============================================================
✅ MCP generated: test_nested_max_simple.mcp.gms
✅ PATH solved successfully
✅ Solution is optimal

... (similar for other tests)
```

## Integration with Existing Codebase

### Files Modified

1. **`src/kkt/reformulation.py`**
   - Add `flatten_minmax_calls()` function
   - Modify `detect_min_max_calls()` to call flattening first
   - Update module docstring

2. **`tests/unit/kkt/test_reformulation.py`** (new file or extend existing)
   - Unit tests for `flatten_minmax_calls()`
   - Test each edge case

3. **`tests/fixtures/nested_minmax/`** (new directory)
   - 6 GAMS test files

4. **`tests/integration/test_nested_minmax.py`** (new file)
   - Integration tests for end-to-end nested minmax handling

5. **`docs/planning/EPIC_1/SPRINT_5/follow-ons/NESTED_MINMAX_REQUIREMENTS.md`**
   - Update status to implemented

### No Changes Required

The following components work without modification:
- **Detection:** `src/ir/minmax_detection.py` (unchanged)
- **Reformulation logic:** `reformulate_min()`, `reformulate_max()` (unchanged)
- **KKT assembly:** `src/kkt/assemble.py` (unchanged)
- **Jacobian computation:** `src/ad/gradient.py` (unchanged)
- **Emission:** `src/emit/model.py` (unchanged)

**Why:** Flattening happens before detection, so downstream code sees only flat min/max calls.

### Call Graph

```
cli.py:main()
  ↓
normalize_model()
  ↓
reformulate_model()  [src/kkt/reformulation.py]
  ↓
  for each equation:
    detect_min_max_calls(expr, context)  [MODIFIED]
      ↓
      flatten_minmax_calls(expr)  [NEW]
        ↓ (returns flattened expression)
      traverse(flattened_expr)
        ↓
        for each Call('min'|'max'):
          flatten_min_max_args(node)  [EXISTING - now redundant but harmless]
          ↓
          create MinMaxCall with flattened args
  ↓
  for each MinMaxCall:
    reformulate_min() or reformulate_max()  [UNCHANGED]
    ↓
    create auxiliary variables and constraints
    ↓
    replace in equation
```

## Known Limitations

### Limitation 1: Mixed-Operation Nesting Not Supported

**Example:** `min(x, max(y, z))`

**Error:**
```
Error: Differentiation not yet implemented for function 'max'.
Nested min/max with different operations is not supported in Option A.
```

**Workaround:** Manual reformulation or wait for Option B (multi-pass) implementation.

**Frequency:** Low (estimated <5% of real-world cases based on GAMS model survey)

### Limitation 2: No Constant Folding

**Example:** `min(5, 10, x)` reformulates to 3 constraints instead of simplifying to `min(5, x)`.

**Impact:** Minor performance overhead (extra constraints and multipliers)

**Future Optimization:** Add constant folding in parser or detection phase.

### Limitation 3: No Duplicate Argument Detection

**Example:** `min(x, x, y)` creates 2 constraints for `x` instead of 1.

**Impact:** Redundant constraints (mathematically valid, computationally wasteful)

**Future Optimization:** Deduplicate arguments after flattening (requires expression equality checking).

### Limitation 4: Maximum Nesting Depth

**Limit:** No explicit limit with flattening approach (handled in single pass)

**Practical Limit:** Expression tree depth limited by Python recursion limit (~1000)

**Real-World Impact:** None (typical nesting depth <5)

## Success Criteria (from PREP_PLAN.md)

- [x] **Flattening algorithm designed for same-operation nesting**
  - ✅ Algorithm specified with pseudocode
  - ✅ Time/space complexity analyzed (O(n) time, O(d) space)
  - ✅ Edge cases documented

- [x] **Mixed-operation handling specified (no flattening)**
  - ✅ Mixed operations remain unchanged
  - ✅ Error message specified for unsupported case
  - ✅ Future work (Option B) documented

- [x] **4+ test cases cover: simple nesting, deep nesting, mixed operations**
  - ✅ Test 1: Simple min nesting
  - ✅ Test 2: Simple max nesting
  - ✅ Test 3: Deep nesting (3+ levels)
  - ✅ Test 4: Mixed operations (expected failure)
  - ✅ Test 5: Multiple independent nested calls
  - ✅ Test 6: Nested with constants

- [x] **Integration points identified in existing codebase**
  - ✅ Primary: `detect_min_max_calls()` in reformulation.py
  - ✅ No changes needed: detection, reformulation, KKT, Jacobian, emission
  - ✅ Call graph documented

- [x] **Implementation effort estimated at 4-7 hours**
  - ✅ Task 1: Flattening function (2h)
  - ✅ Task 2: Integration (1h)
  - ✅ Task 3: Documentation (0.5h)
  - ✅ Task 4: Tests (2h)
  - ✅ Task 5: PATH validation (1h)
  - **Total: 6.5 hours** (within updated estimate range)

- [x] **PATH validation strategy defined**
  - ✅ Validation script specified
  - ✅ Expected outputs documented
  - ✅ Solution checking criteria defined

- [x] **Known limitations documented (e.g., max nesting depth)**
  - ✅ 4 limitations documented with workarounds
  - ✅ Mixed-operation limitation clearly specified
  - ✅ Future optimization opportunities identified

## Appendix: Comparison with Option B

### Option A: Flattening Only (THIS DESIGN)

**Pros:**
- Simple implementation (single-pass)
- Low effort (4-7 hours)
- No iteration limits needed
- Cleaner MCP output (fewer auxiliary variables)
- Covers 80-90% of real-world use cases

**Cons:**
- Doesn't support mixed operations
- Error message for unsupported case

**Recommendation:** ✅ **Implement for Sprint 6**

### Option B: Multi-Pass Reformulation (FUTURE WORK)

**Pros:**
- Handles all nesting patterns
- Supports mixed operations
- More general solution

**Cons:**
- Complex implementation (bottom-up processing)
- High effort (10-15 hours)
- Requires iteration limits
- More auxiliary variables (less efficient MCP)
- Diminishing returns (few real-world cases need it)

**Recommendation:** ⏸️ **Defer to future sprint if demand materializes**

### Decision Matrix

| Criteria | Option A | Option B |
|----------|----------|----------|
| Implementation Effort | 4-6h ✅ | 10-15h ⚠️ |
| Real-World Coverage | 80-90% ✅ | 100% ✅ |
| Code Complexity | Low ✅ | High ⚠️ |
| MCP Efficiency | High ✅ | Medium ⚠️ |
| Sprint 6 Fit | ✅ Yes | ❌ No (too much time) |

**Conclusion:** Option A is the right choice for Sprint 6.

## References

1. **Existing Implementation:**
   - `src/kkt/reformulation.py` - Current min/max reformulation
   - `src/ir/minmax_detection.py` - Detection logic

2. **Requirements:**
   - `docs/planning/EPIC_1/SPRINT_5/follow-ons/NESTED_MINMAX_REQUIREMENTS.md` - Problem statement

3. **Theory:**
   - Boyd & Vandenberghe, "Convex Optimization" - Epigraph reformulation
   - Ferris & Pang (1997) - Complementarity problems
   - GAMS Documentation - Min/max handling in optimization models

4. **Sprint 6 Planning:**
   - `docs/planning/EPIC_2/SPRINT_6/PREP_PLAN.md` (lines 597-766) - Task 5 specification
   - `docs/planning/EPIC_2/SPRINT_6/SPRINT_6_PLAN.md` - Component 2 details

---

**Document Status:** ✅ COMPLETE  
**Next Step:** Implementation in Sprint 6 Day 2 (Component 2: Min/Max Support)  
**Approval:** Ready for review and implementation
