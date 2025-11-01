# Error Message Guidelines

This document provides guidelines for creating user-friendly error messages in nlp2mcp.

## Error Hierarchy

nlp2mcp uses a structured error hierarchy defined in `src/utils/errors.py`:

```
NLP2MCPError (base)
├── UserError (input problems)
│   ├── ParseError (syntax errors)
│   ├── ModelError (semantic errors)
│   ├── UnsupportedFeatureError (unsupported GAMS features)
│   └── FileError (file I/O problems)
└── InternalError (bugs in nlp2mcp)
```

## When to Use Each Error Type

### UserError
Use for problems with user input that the user can fix:
- Invalid variable names
- Missing declarations
- Type mismatches
- Invalid bounds

**Example:**
```python
from src.utils.errors import UserError

# Bad
raise ValueError(f"Variable {var} not found")

# Good
available_vars = ', '.join(sorted(model.variables.keys()))
raise UserError(
    f"Variable '{var}' not found in model",
    suggestion=f"Available variables: {available_vars}\n\n"
               f"Variables are case-sensitive. Check your spelling."
)
```

### ParseError
Use for GAMS syntax errors:

**Example:**
```python
from src.utils.errors import ParseError

raise ParseError(
    "Expected equation name before '=e='",
    line=5,
    column=12,
    source_line="  x + y =e= 0;",
    suggestion="Equation definitions must have a name.\n"
               "Try: myeq.. x + y =e= 0;"
)
```

### ModelError
Use for semantic problems in the model structure:

**Example:**
```python
from src.utils.errors import ModelError

raise ModelError(
    "Model has no objective function defined",
    suggestion="Add an objective using:\n"
               "  objective.. obj =e= <expression>;\n"
               "  Model mymodel /all/;\n"
               "  Solve mymodel using NLP minimizing obj;"
)
```

### UnsupportedFeatureError
Use for valid GAMS features that nlp2mcp doesn't support yet:

**Example:**
```python
from src.utils.errors import UnsupportedFeatureError

# With default suggestion (file issue)
raise UnsupportedFeatureError("dollar control directives")

# With custom workaround
raise UnsupportedFeatureError(
    "$include directives",
    suggestion="nlp2mcp currently only supports single-file models.\n"
               "Please combine your files manually before processing."
)
```

### InternalError
Use for bugs in nlp2mcp (consistency violations, assertion failures):

**Example:**
```python
from src.utils.errors import InternalError

if gradient.num_cols != jacobian.num_cols:
    raise InternalError(
        "Gradient and Jacobian have mismatched column counts",
        context={
            'gradient_cols': gradient.num_cols,
            'jacobian_cols': jacobian.num_cols,
            'gradient_vars': list(gradient.mapping.instances),
            'jacobian_vars': list(jacobian.col_mapping.instances),
        }
    )
```

### FileError
Use for file I/O problems:

**Example:**
```python
from src.utils.errors import FileError
import os

if not os.path.exists(filepath):
    raise FileError(
        f"GAMS file '{filepath}' not found",
        suggestion=f"Check that the file path is correct.\n"
                   f"Current directory: {os.getcwd()}"
    )
```

## Error Message Best Practices

### 1. Be Specific
**Bad:** "Invalid input"
**Good:** "Variable 'cost' not found in model"

### 2. Provide Context
**Bad:** "Variable not found"
**Good:** "Variable 'cost' not found. Available variables: costs, demand, supply"

### 3. Suggest Fixes
**Bad:** "Syntax error"
**Good:** "Expected equation name before '=e='. Try: myeq.. x + y =e= 0;"

### 4. Show Location (for parse errors)
```
Parse error at line 5, column 12:
  x + y =e= 0;
           ^
Expected: equation name before '=e='
```

### 5. Use Fuzzy Matching (when applicable)
```python
import difflib

similar = difflib.get_close_matches(var_name, available_vars, n=3)
if similar:
    suggestion += f"\n\nDid you mean: {', '.join(similar)}?"
```

### 6. Explain Rules
```
Variables are case-sensitive.
Equation names cannot start with numbers.
Bounds must be constants or parameters, not variables.
```

## Examples by Category

### Variable Not Found
```python
from src.utils.errors import UserError
import difflib

def get_variable(model, var_name):
    if var_name not in model.variables:
        available = list(model.variables.keys())
        suggestion = f"Available variables: {', '.join(sorted(available))}"
        
        similar = difflib.get_close_matches(var_name, available, n=3)
        if similar:
            suggestion += f"\n\nDid you mean: {', '.join(similar)}?"
        
        suggestion += "\n\nVariables are case-sensitive."
        
        raise UserError(
            f"Variable '{var_name}' not found in model",
            suggestion=suggestion
        )
    
    return model.variables[var_name]
```

### Undefined Equation
```python
from src.utils.errors import ModelError

def get_equation(model, eq_name):
    if eq_name not in model.equations:
        available = list(model.equations.keys())
        raise ModelError(
            f"Equation '{eq_name}' is not defined",
            suggestion=f"Available equations: {', '.join(available)}\n\n"
                       f"Define the equation before using it:\n"
                       f"  {eq_name}.. <expression> =e= <expression>;"
        )
    
    return model.equations[eq_name]
```

### Missing Objective
```python
from src.utils.errors import ModelError

def validate_objective(model):
    if model.objective is None:
        raise ModelError(
            "Model has no objective function defined",
            suggestion="Add an objective function:\n"
                       "1. Define the objective variable in Variables section\n"
                       "2. Define an equation that computes it\n"
                       "3. Use 'Solve ... minimizing <objvar>' or 'maximizing <objvar>'"
        )
```

### Type Mismatch
```python
from src.utils.errors import UserError

def check_types(expected, actual, location):
    if expected != actual:
        raise UserError(
            f"Type mismatch at {location}: expected {expected}, got {actual}",
            suggestion=f"Check that the expression produces a {expected} value.\n"
                       f"Indexed variables need domain specifications."
        )
```

### Invalid Bound
```python
from src.utils.errors import UserError

def validate_bound(bound_expr):
    if not is_constant(bound_expr):
        raise UserError(
            f"Bound must be a constant or parameter, got: {bound_expr}",
            suggestion="Bounds cannot depend on variables.\n"
                       "Use parameters or scalar values:\n"
                       "  x.lo = 0;      (constant)\n"
                       "  x.up = maxval; (parameter)"
        )
```

### Unsupported Construct
```python
from src.utils.errors import UnsupportedFeatureError

def parse_dollar_directive(directive):
    raise UnsupportedFeatureError(
        f"${directive} directive",
        suggestion="nlp2mcp does not support dollar control directives.\n"
                   "Please remove or comment out the directive."
    )
```

### Internal Consistency Check
```python
from src.utils.errors import InternalError

def validate_kkt_dimensions(gradient, jacobian):
    if gradient.num_cols != jacobian.num_cols:
        raise InternalError(
            "KKT system dimension mismatch",
            context={
                'component': 'gradient vs jacobian',
                'gradient_cols': gradient.num_cols,
                'jacobian_cols': jacobian.num_cols,
                'operation': 'assemble_kkt_system',
            }
        )
```

## Testing Error Messages

All error messages should be tested to ensure they're helpful:

```python
def test_variable_not_found_error():
    """Verify variable not found error is helpful."""
    with pytest.raises(UserError) as exc_info:
        get_variable(model, 'cost')  # 'costs' exists, not 'cost'
    
    error_msg = str(exc_info.value)
    
    # Should mention the variable name
    assert 'cost' in error_msg
    
    # Should list available variables
    assert 'Available variables' in error_msg
    
    # Should suggest similar names
    assert 'costs' in error_msg
    
    # Should explain the rule
    assert 'case-sensitive' in error_msg
```

## Migration Strategy

When improving error messages:

1. **Keep existing tests passing** - Don't change exception types in ways that break existing tests
2. **Add suggestions gradually** - It's okay to improve error messages over time
3. **Test the new messages** - Add tests that verify error messages are helpful
4. **Document limitations** - If you can't provide a good suggestion, say so

## Future Improvements

Areas where error messages could be improved (not required for Sprint 4):

- [ ] Fuzzy matching for all name lookups
- [ ] Suggesting fixes for common parse errors
- [ ] Context-aware suggestions based on model structure
- [ ] Error recovery and multiple error reporting
- [ ] Colorized error output in CLI
- [ ] Error message localization

## References

- Error hierarchy: `src/utils/errors.py`
- Error tests: `tests/unit/utils/test_errors.py`
- Example usage: This document
