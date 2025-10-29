# Issue: Power Operator (^) Not Implemented in AD Module

## Summary

The automatic differentiation (AD) module does not yet support the power operator (`^`) for differentiation. Integration test `test_nonlinear_mix_model` fails because the test model contains power operations (e.g., `x^2`, `y^3`) which cannot be differentiated with the current implementation.

## Severity

- **Status**: OPEN 🔴
- **Severity**: Medium - Missing feature, blocks 1 integration test
- **Component**: Sprint 2 (AD / Automatic Differentiation)
- **Affects**: Models with power operations, nonlinear functions
- **Discovered**: Sprint 2 Day 10 (2025-10-29) while fixing Issue #22
- **GitHub Issue**: #25 - https://github.com/jeffreyhorn/nlp2mcp/issues/25
- **Planned Implementation**: Day 3 (per error message)
- **Type**: Feature not implemented (planned enhancement)

## Problem Description

The AD module currently supports basic arithmetic operations (`+`, `-`, `*`, `/`) and some unary functions (`sin`, `cos`, etc.), but does not support the power operator (`^`). When attempting to differentiate expressions containing power operations, a `ValueError` is raised with a clear message that this feature is planned for Day 3.

### Error Details

**Test**: `TestNonlinearFunctions::test_nonlinear_mix_model` in `tests/ad/test_integration.py`

**Example File**: `examples/nonlinear_mix.gms`
Contains expressions like:
- `x^2` (x squared)
- `y^3` (y cubed)  
- `x^0.5` (square root)
- `z^(-1)` (reciprocal)

**Error Message**:
```
ValueError: Unsupported binary operation '^' for differentiation. 
Supported operations: +, -, *, /. Power (^) will be implemented on Day 3.
```

**Error Location**: Likely in `src/ad/differentiate.py` or similar differentiation module

**Test Code**:
```python
@skip_not_implemented
def test_nonlinear_mix_model(self):
    """Test model with mix of nonlinear functions."""
    model_ir = parse_model_file("nonlinear_mix.gms")
    normalize_model(model_ir)
    gradient, J_g, J_h = compute_derivatives(model_ir)  # ❌ Fails here
    
    # Should have gradient
    assert gradient.num_nonzeros() > 0
    
    # All gradient components should be non-None
    for col_id in range(gradient.num_cols):
        deriv = gradient.get_derivative(col_id)
        assert deriv is not None
```

## Expected Behavior

When power operations are implemented, the AD module should:

1. **Recognize power operator**: Parse and handle `^` in expressions
2. **Differentiate correctly**: Apply power rule: `d/dx(x^n) = n * x^(n-1)`
3. **Handle special cases**:
   - Constant exponents: `x^2` → `2*x`
   - Variable exponents: `x^y` → `x^y * (y/x + ln(x) * dy/dx)`
   - Fractional exponents: `x^0.5` → `0.5 * x^(-0.5)`
   - Negative exponents: `x^(-1)` → `-x^(-2)`
   - Zero exponent: `x^0` → `0` (constant)

### Mathematical Background

**Power Rule for Differentiation**:

For constant exponent `n`:
```
d/dx(x^n) = n * x^(n-1)
```

For variable exponent (general case):
```
d/dx(f^g) = f^g * (g' * ln(f) + g * f'/f)
```

Where:
- `f` and `g` are functions of `x`
- `f'` and `g'` are their derivatives

**Special Cases**:
1. `f^n` (constant exponent): `f^n * n * f' / f = n * f^(n-1) * f'`
2. `a^g` (constant base): `a^g * ln(a) * g'`
3. `x^x`: `x^x * (ln(x) + 1)`

## Implementation Requirements

### 1. Expression Parsing

Ensure power operations are correctly parsed from GAMS files:
```gams
Variables x, y, obj ;
Equations objective ;

objective.. obj =e= x**2 + y**3 + sqrt(x) ;
```

Note: GAMS uses `**` for power, which should be normalized to `^` in IR.

### 2. Expression Representation

Verify `Expr` class supports power operations:
```python
# In src/ir/expression.py or similar
@dataclass
class Expr:
    const: float = 0.0
    terms: dict = field(default_factory=dict)
    binary_ops: list = field(default_factory=list)  # Should include '^'
    unary_ops: list = field(default_factory=list)
```

### 3. Differentiation Rules

Implement power rule in differentiation module:
```python
# In src/ad/differentiate.py or similar

def _differentiate_binary_op(op: str, left: Expr, right: Expr, 
                              var_name: str, var_indices: tuple) -> Expr:
    """Differentiate a binary operation."""
    
    if op == '^':
        # Power operation: left^right
        return _differentiate_power(left, right, var_name, var_indices)
    elif op == '+':
        # ...
    # ... other operations ...

def _differentiate_power(base: Expr, exponent: Expr, 
                         var_name: str, var_indices: tuple) -> Expr:
    """
    Differentiate power expression: base^exponent
    
    Uses the general formula:
    d/dx(f^g) = f^g * (g' * ln(f) + g * f'/f)
    """
    
    # Check if exponent is constant
    if _is_constant(exponent, var_name, var_indices):
        # Simple power rule: d/dx(f^n) = n * f^(n-1) * f'
        n = _evaluate_constant(exponent)
        base_deriv = _differentiate(base, var_name, var_indices)
        
        # Result: n * base^(n-1) * base'
        return _multiply(
            _multiply(exponent, _power(base, _subtract(exponent, Expr(const=1.0)))),
            base_deriv
        )
    
    # Check if base is constant
    elif _is_constant(base, var_name, var_indices):
        # d/dx(a^g) = a^g * ln(a) * g'
        a = _evaluate_constant(base)
        exp_deriv = _differentiate(exponent, var_name, var_indices)
        
        # Result: base^exponent * ln(base) * exponent'
        return _multiply(
            _multiply(_power(base, exponent), _log(base)),
            exp_deriv
        )
    
    # General case: both base and exponent are functions
    else:
        # d/dx(f^g) = f^g * (g' * ln(f) + g * f'/f)
        base_deriv = _differentiate(base, var_name, var_indices)
        exp_deriv = _differentiate(exponent, var_name, var_indices)
        
        # Result: base^exponent * (exponent' * ln(base) + exponent * base'/base)
        fg = _power(base, exponent)
        term1 = _multiply(exp_deriv, _log(base))
        term2 = _multiply(exponent, _divide(base_deriv, base))
        
        return _multiply(fg, _add(term1, term2))
```

### 4. Expression Simplification

Add simplification rules for power expressions:
```python
def _simplify_power(base: Expr, exponent: Expr) -> Expr:
    """Simplify power expressions."""
    
    # x^0 = 1
    if _is_zero(exponent):
        return Expr(const=1.0)
    
    # x^1 = x
    if _is_one(exponent):
        return base
    
    # 0^n = 0 (for n > 0)
    if _is_zero(base) and _is_positive(exponent):
        return Expr(const=0.0)
    
    # 1^n = 1
    if _is_one(base):
        return Expr(const=1.0)
    
    # (constant)^(constant) = evaluate
    if _is_constant_expr(base) and _is_constant_expr(exponent):
        b = _evaluate_constant(base)
        e = _evaluate_constant(exponent)
        return Expr(const=b ** e)
    
    # No simplification possible
    return _create_power_expr(base, exponent)
```

### 5. Test Cases

Add unit tests for power differentiation:
```python
# In tests/ad/test_differentiation.py

def test_power_constant_exponent():
    """Test d/dx(x^2) = 2*x"""
    expr = parse_expr("x^2")
    deriv = differentiate(expr, var='x')
    assert deriv == parse_expr("2*x")

def test_power_fractional_exponent():
    """Test d/dx(x^0.5) = 0.5*x^(-0.5)"""
    expr = parse_expr("x^0.5")
    deriv = differentiate(expr, var='x')
    assert deriv == parse_expr("0.5*x^(-0.5)")

def test_power_negative_exponent():
    """Test d/dx(x^(-1)) = -x^(-2)"""
    expr = parse_expr("x^(-1)")
    deriv = differentiate(expr, var='x')
    assert deriv == parse_expr("-x^(-2)")

def test_power_chain_rule():
    """Test d/dx((2*x + 1)^3) = 3*(2*x + 1)^2 * 2"""
    expr = parse_expr("(2*x + 1)^3")
    deriv = differentiate(expr, var='x')
    expected = parse_expr("6*(2*x + 1)^2")
    assert deriv == expected

def test_power_variable_exponent():
    """Test d/dx(x^y) where y is variable"""
    expr = parse_expr("x^y")
    deriv_x = differentiate(expr, var='x')
    # Should be: x^y * y/x = y * x^(y-1)
    assert deriv_x == parse_expr("y*x^(y-1)")
    
    deriv_y = differentiate(expr, var='y')
    # Should be: x^y * ln(x)
    assert deriv_y == parse_expr("x^y * log(x)")
```

## Related Functions

Power operations may be represented as:
- Direct power: `x^2`
- Function calls: `sqr(x)`, `sqrt(x)`, `power(x, 2)`
- Reciprocal: `1/x` or `x^(-1)`

Implementation should handle these equivalent forms.

## Files Affected

### Implementation Files
- `src/ad/differentiate.py` - Add power differentiation logic
- `src/ad/expression.py` - Ensure power operations supported in Expr
- `src/ad/simplify.py` - Add power simplification rules

### Test Files
- `tests/ad/test_integration.py` - Remove `@skip_not_implemented` marker after implementation
- `tests/ad/test_differentiation.py` - Add unit tests for power rule

### Example Files
- `examples/nonlinear_mix.gms` - Already exists as test case

## Test Execution

### Before Implementation
```bash
$ python -m pytest tests/ad/test_integration.py::TestNonlinearFunctions::test_nonlinear_mix_model -xvs
SKIPPED (Feature not yet implemented (power operator planned for Day 3))
```

### After Implementation (Expected)
```bash
$ python -m pytest tests/ad/test_integration.py::TestNonlinearFunctions::test_nonlinear_mix_model -xvs
PASSED
```

## Implementation Priority

- **Priority**: Medium
- **Complexity**: Medium-High
- **Estimated Effort**: 1-2 days
- **Dependencies**: None (can be implemented independently)
- **Blocks**: 1 integration test, models with power operations

## Related Issues

- **GitHub Issue #22** (RESOLVED ✅): Integration Tests API Mismatch
  - https://github.com/jeffreyhorn/nlp2mcp/issues/22
  - This issue was identified while fixing Issue #22
  - Power operator is a known planned enhancement

## References

### Mathematical Resources
- [Power Rule - Wikipedia](https://en.wikipedia.org/wiki/Power_rule)
- [Differentiation rules - Wikipedia](https://en.wikipedia.org/wiki/Differentiation_rules)

### GAMS Documentation
- GAMS power operators: `**` and `power(x, n)` function
- GAMS intrinsic functions: `sqr()`, `sqrt()`

## Next Steps

1. **Design**: Review expression representation and ensure power ops supported
2. **Implement**: Add power differentiation logic with all special cases
3. **Test**: Add comprehensive unit tests for power rule
4. **Simplify**: Implement power expression simplification rules
5. **Integrate**: Test with `nonlinear_mix.gms` example
6. **Document**: Add power rule to AD module documentation
