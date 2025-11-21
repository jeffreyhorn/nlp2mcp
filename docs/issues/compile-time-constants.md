# Issue: Support Compile-Time Constants (%...% syntax)

**Status:** Open  
**Priority:** Medium  
**Effort:** 2-3 hours  
**Blocking:** mingamma.gms parsing  

## Description

GAMS allows compile-time constants using the `%identifier%` syntax. These are evaluated at compile-time and replaced with their values before the model is parsed. This syntax is not currently supported by the parser, blocking mingamma.gms from parsing.

## Example Syntax

```gams
if(m1.solveStat <> %solveStat.capabilityProblems%,
   abort$[abs(x1delta) > xtol or abs(y1delta) > ytol] "inconsistent results with gamma";
);
```

In this example, `%solveStat.capabilityProblems%` is a compile-time constant that references a system-defined value.

## Current Behavior

Parser fails with:
```
Parse error at line 58, column 20: Unexpected character: '%'
  if(m1.solveStat <> %solveStat.capabilityProblems%,
                     ^

Suggestion: This character is not valid in this context
```

The parser does not recognize `%` as a valid character in expressions, causing it to fail when encountering compile-time constants.

## Expected Behavior

Parser should accept `%identifier%` syntax in expressions and either:
1. Treat them as special constants in the IR (recommended for now)
2. Support compile-time evaluation (more complex, may not be needed)

## Impact

**Blocks:** mingamma.gms (Sprint 9 target model)  
**Parse Rate Impact:** +10% (1/10 models)

## Related Files

- `tests/fixtures/gamslib/mingamma.gms` - Line 58, 62
- `src/gams/gams_grammar.lark` - Expression rules need to support `%` tokens

## Common Use Cases

Compile-time constants are commonly used for:
1. System parameters: `%solveStat.capabilityProblems%`, `%system.date%`
2. User-defined macros: `$set myvar 10` then `%myvar%`
3. Conditional compilation based on system state

## Suggested Implementation

### 1. Grammar Update (0.5h)

Add support for compile-time constants in the expression grammar:

```lark
// Add to atom production
?atom: NUMBER                             -> number
     | func_call                          -> funccall
     | sum_expr
     | compile_time_const                 -> compile_const
     | ref_bound
     | ref_indexed
     | symbol_plain
     | "(" expr ")"

// New rule for compile-time constants
compile_time_const: "%" compile_const_path "%"
compile_const_path: ID ("." ID)*
```

### 2. Semantic Handler (0.5h)

Add IR representation for compile-time constants:

```python
# In src/ir/ir_types.py
@dataclass
class CompileTimeConstant:
    """Represents a GAMS compile-time constant %identifier%"""
    path: List[str]  # e.g., ['solveStat', 'capabilityProblems']
    
# In src/ir/parser.py
def _handle_compile_const(self, node: Tree) -> CompileTimeConstant:
    """Handle compile-time constant like %solveStat.capabilityProblems%"""
    path_node = node.children[0]
    path = [child.value for child in path_node.children]
    return CompileTimeConstant(path=path)
```

### 3. Expression Integration (0.5h)

Update expression handling to include compile-time constants as valid operands:

```python
# In _handle_expr method
elif node.data == "compile_const":
    return self._handle_compile_const(node)
```

### 4. Testing (0.5-1h)

- Test basic compile-time constant: `%identifier%`
- Test dotted path: `%system.date%`, `%solveStat.capabilityProblems%`
- Test in expressions: `x <> %value%`, `if(%flag%, ...)`
- Test mingamma.gms parsing

## Verification

After implementation:
```bash
python -m src.ir.parser tests/fixtures/gamslib/mingamma.gms
# Should parse successfully
```

Parse rate should increase from 50% to 60% (6/10 models).

## Alternative Approaches

### Option 1: Ignore/Skip (Simplest)
Treat `%...\%` as a special token that gets ignored in the grammar. This allows parsing but loses semantic information.

### Option 2: Full Macro System (Complex)
Implement a preprocessing phase that evaluates compile-time constants. This is more accurate but significantly more complex and may not be necessary for the nlp2mcp use case.

**Recommendation:** Implement Option 1 (IR representation) first, as it balances simplicity with preserving semantic information.

## Discovery Context

Discovered while fixing Issue #278 (abort$ statements). After implementing abort$ with square brackets, mingamma.gms still failed to parse due to the `%solveStat.capabilityProblems%` compile-time constant on line 58.

The abort$ fix is complete and working correctly - mingamma.gms is now blocked solely by this compile-time constant issue.

## References

- mingamma.gms line 58: `if(m1.solveStat <> %solveStat.capabilityProblems%,`
- mingamma.gms line 62: Same pattern on second if-statement
- GAMS Documentation: Dollar Control Options and Compile-Time Variables
- Issue #278: abort$ statements (now resolved, revealed this issue)
