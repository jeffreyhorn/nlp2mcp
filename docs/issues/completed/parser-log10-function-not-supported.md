# Parser: log10() Function Not Supported

**GitHub Issue:** #378  
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/378  
**Priority:** HIGH  
**Tier 2 Models Blocked:** bearing.gms

## Problem

The parser does not support the `log10()` function (base-10 logarithm), which is a standard mathematical function in GAMS.

## Example from Tier 2 Model

### bearing.gms (line 158)
```gams
oil_viscosity..    log10(8.112e6*mu + 0.8) =e= (T**cn)*(10**C1);
                        ^
                   log10 function call
```

## Current Error

```
Error: Parse error at line 158, column 26: Unexpected character: '8'
  oil_viscosity..    log10(8.112e6*mu + 0.8) =e= (T**cn)*(10**C1);
                           ^

Suggestion: This character is not valid in this context
```

The error occurs because `log10` is being parsed as an identifier followed by `10`, rather than being recognized as a function name.

## GAMS Specification

GAMS provides several logarithm functions:
- `log(x)` - Natural logarithm (base e)
- `log10(x)` - Common logarithm (base 10)
- `log2(x)` - Binary logarithm (base 2)

### Semantics
- `log10(x)` returns the base-10 logarithm of x
- Domain: x > 0
- Result: y such that 10^y = x
- Example: `log10(100)` = 2, `log10(1000)` = 3

## Current Parser Status

The parser currently supports:
- `log(x)` - Natural logarithm
- `exp(x)` - Exponential
- `sqrt(x)` - Square root
- `sin`, `cos`, `tan` - Trigonometric functions
- And others...

But does NOT support:
- `log10(x)` - Base-10 logarithm
- `log2(x)` - Base-2 logarithm (if used anywhere)

## Technical Details

### Grammar Status

The lexer likely treats `log10` as an identifier `log` followed by a number `10`, rather than recognizing it as a function name token.

### Required Changes

1. **Lexer:** Add `log10` and `log2` as reserved function names
2. **Grammar:** Ensure function call syntax handles these functions
3. **IR:** Add `Log10` and `Log2` function types to `FunctionCall` enum
4. **Converter:** Map to appropriate numerical library functions
5. **AD (if needed):** Implement derivatives:
   - d/dx[log10(x)] = 1 / (x * ln(10))
   - d/dx[log2(x)] = 1 / (x * ln(2))

### Implementation Approach

#### 1. Update Lexer/Grammar
```lark
FUNC_NAME: "log" | "log10" | "log2" | "exp" | "sqrt" | ...
```

#### 2. Update FunctionCall IR
```python
class FunctionType(Enum):
    LOG = "log"
    LOG10 = "log10"  # Add
    LOG2 = "log2"    # Add
    EXP = "exp"
    # ... others
```

#### 3. Converter Support
```python
def convert_function_call(self, func: FunctionCall) -> str:
    if func.function == FunctionType.LOG10:
        return f"np.log10({self.convert_expr(func.arguments[0])})"
    elif func.function == FunctionType.LOG2:
        return f"np.log2({self.convert_expr(func.arguments[0])})"
    # ... others
```

#### 4. Automatic Differentiation (if used)
```python
def diff_log10(arg: Expr, var: str) -> Expr:
    # d/dx[log10(f(x))] = f'(x) / (f(x) * ln(10))
    ln10 = 2.302585092994046  # ln(10)
    return BinaryOp(
        diff(arg, var),
        BinaryOp(arg, Const(ln10), "*"),
        "/"
    )
```

## Impact

- **Blocks:** 1 Tier 2 model (bearing.gms)
- **Frequency:** Common mathematical function in engineering models
- **Workaround:** Could manually rewrite using `log(x)/log(10)`, but model modification not ideal

## Test Cases Needed

1. **Basic usage:** `log10(100)` should evaluate to 2
2. **In equations:** `y =e= log10(x);`
3. **Nested:** `log10(exp(x))`
4. **With expressions:** `log10(a*x + b)`
5. **Derivative:** Verify automatic differentiation if used
6. **Edge cases:** `log10(0)`, `log10(-1)` should error appropriately
7. **log2 support:** Add similar tests for `log2()` if implementing both

## Priority Justification

**HIGH Priority** because:
- Blocks 1 Tier 2 model
- Common mathematical function
- Straightforward to implement (similar to existing `log` function)
- Part of standard GAMS function library

## Related Functions to Consider

While implementing `log10`, consider also adding:
- `log2(x)` - Base-2 logarithm (less common but part of GAMS)
- Verify other mathematical functions are supported:
  - Hyperbolic: `sinh`, `cosh`, `tanh`
  - Inverse trig: `arcsin`, `arccos`, `arctan`, `arctan2`
  - Rounding: `ceil`, `floor`, `round`
  - Other: `abs`, `sign`, `min`, `max`

## Notes

The error message suggests the lexer is treating `log10` as identifier `log` followed by number `10`. This is a lexer tokenization issue rather than a grammar issue. Need to ensure function names with digits (like `log10`, `log2`) are recognized as single tokens.
