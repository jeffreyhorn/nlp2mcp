# Parser Enhancement: Dynamic Set Ranges (% Syntax)

**GitHub Issue**: #387 - https://github.com/jeffreyhorn/nlp2mcp/issues/387  
**Status**: Open  
**Priority**: High  
**Component**: Parser (src/ir/parser.py, src/gams/gams_grammar.lark)  
**Effort**: 4h  
**Impact**: Unlocks 5 Tier 2 models - 27.8% parse rate improvement

## Summary

GAMS supports dynamic set range notation using `%variable%` syntax for compile-time constant substitution in set declarations. This allows sets to be defined with ranges that depend on scalar values. The parser currently does not support this syntax, blocking 5 Tier 2 models from parsing.

## Current Behavior

When parsing GAMS files with dynamic set ranges, the parser fails with:

**Example from chain.gms (line 27):**
```
Error: Parse error at line 27, column 14: Unexpected character: '%'
Set nh / i0*i%nh% /;
             ^
```

**Example from elec.gms (line 35):**
```
Error: Parse error at line 35, column 26: Unexpected character: '%'
i 'electrons' /i1*i%np%/
                         ^
```

**Example from gasoil.gms (line 42):**
```
Error: Parse error at line 42, column 37: Unexpected character: '%'
nh 'partition intervals' / nh1*nh%nh% /
                                    ^
```

## Expected Behavior

The parser should accept dynamic set range notation and expand it based on compile-time constants:
- `i1*i%nh%` where `nh=50` should expand to `i1*i50`
- The expansion happens during preprocessing before parsing

## GAMS Syntax Reference

**Dynamic Set Range Notation:**
```gams
$if not set nh $set nh 50
Set nh / i0*i%nh% /;
```

This is equivalent to:
```gams
Set nh / i0*i50 /;
```

**Common Patterns:**
```gams
Set i 'points' / i1*i%np% /;     # 1-indexed range
Set j 'nodes'  / j0*j%nn% /;     # 0-indexed range
Set k 'edges'  / k1*k%ne% /;     # Custom prefix
```

From GAMS User's Guide, Section 3.5 "Dollar Control Options":
- `$set` defines compile-time constants
- `%variable%` performs textual substitution
- Substitution occurs during preprocessing, before parsing

## Reproduction

### Test Case 1: Basic dynamic range (chain.gms)
```gams
$if not set nh $set nh 50
Set nh / i0*i%nh% /;
```

**Current Result:** Parse error at `%`  
**Expected Result:** Parse successfully, expand to `i0*i50`

### Test Case 2: 1-indexed range (elec.gms)
```gams
Set i 'electrons' /i1*i%np%/;
```

**Current Result:** Parse error at `%`  
**Expected Result:** Parse successfully

### Test Case 3: Multi-character substitution (gasoil.gms)
```gams
nh 'partition intervals' / nh1*nh%nh% /
```

**Current Result:** Parse error at `%`  
**Expected Result:** Parse successfully

## Implementation Plan

### Complexity Estimate: 4h

**Breakdown:**
- Preprocessor enhancement (2h): Handle `%variable%` substitution
- Grammar update (0.5h): Ensure expanded ranges parse correctly
- Testing (1.5h): 20+ test cases covering:
  - Basic substitution
  - Nested substitution
  - Multiple substitutions in one set
  - Default values with `$if not set`
  - Edge cases (undefined variables, recursive substitution)

### Implementation Checklist

**Preprocessor (src/ir/preprocessor.py):**
- [ ] Add `$set` directive tracking to maintain symbol table
- [ ] Implement `%variable%` pattern matching and substitution
- [ ] Handle `$if not set` conditional defaults
- [ ] Support `$setGlobal` and `$setLocal` variants
- [ ] Validate substitution order (process all $set before % expansion)

**Grammar (src/gams/gams_grammar.lark):**
- [ ] Verify set range patterns work with numeric suffixes
- [ ] Ensure `ID DECIMAL* ID DECIMAL*` pattern is supported

**Parser:**
- [ ] No changes needed - preprocessor handles expansion before parsing

**Testing:**
- [ ] Unit tests for preprocessor `$set` directive
- [ ] Unit tests for `%variable%` substitution
- [ ] Integration tests with chain.gms, elec.gms, gasoil.gms, jbearing.gms, polygon.gms
- [ ] Edge case tests (undefined variables, circular references, empty values)

## Affected Models

**Tier 2 Models (5 blocked by this issue):**
- ✅ chain.gms (71 lines, NLP) - Hanging Chain Problem
- ✅ elec.gms (78 lines, NLP) - Electron Equilibrium
- ✅ gasoil.gms (107 lines, NLP) - Gas-Oil Separation
- ✅ jbearing.gms (88 lines, NLP) - Journal Bearing Problem
- ✅ polygon.gms (101 lines, NLP) - Polygon Optimization

**Impact:** Unlocking these 5 models improves Tier 2 parse rate from 27.8% → 55.6% (5/18 → 10/18)

## Related Issues

- Preprocessor directive handling is fundamental to GAMS parsing
- Similar to `$include`, `$if`, and other compile-time directives
- This blocker is independent of other syntax issues

## Technical Notes

### Current Preprocessor Capabilities

The preprocessor already handles:
- `$include` directives
- `$onText`/`$offText` comment blocks
- Basic file inclusion

### Proposed Enhancement

Add symbol table for compile-time constants:
```python
class Preprocessor:
    def __init__(self):
        self.symbols = {}  # Store $set variables
    
    def process_set_directive(self, line):
        # $set variable value
        match = re.match(r'\$set\s+(\w+)\s+(.+)', line, re.IGNORECASE)
        if match:
            var, value = match.groups()
            self.symbols[var] = value.strip()
    
    def substitute_variables(self, text):
        # Replace %variable% with value
        pattern = r'%(\w+)%'
        def replace(match):
            var = match.group(1)
            return self.symbols.get(var, match.group(0))
        return re.sub(pattern, replace, text)
```

### Processing Order

1. **First pass:** Process all `$set` directives and build symbol table
2. **Second pass:** Substitute all `%variable%` references
3. **Third pass:** Parse the expanded text

### Edge Cases

**Undefined Variable:**
```gams
Set i / i1*i%undefined% /;
```
**Behavior:** Should error with "Undefined compile-time constant: undefined"

**Conditional Default:**
```gams
$if not set nh $set nh 50
```
**Behavior:** Set `nh=50` only if not already defined (e.g., via command line)

**Recursive Substitution:**
```gams
$set a b
$set b%a% value
```
**Behavior:** Not typically supported, should error or use single-pass substitution

## Success Criteria

- [ ] chain.gms parses successfully
- [ ] elec.gms parses successfully
- [ ] gasoil.gms parses successfully
- [ ] jbearing.gms parses successfully
- [ ] polygon.gms parses successfully
- [ ] All existing tests continue to pass (no regressions)
- [ ] 20+ new test cases added for preprocessor directives
- [ ] Parse rate for Tier 2 models ≥ 55%

## References

- **GAMS Documentation:** User's Guide Section 3.5 "Dollar Control Options"
- **GAMS Dollar Control:** https://www.gams.com/latest/docs/UG_DollarControlOptions.html
- **Sprint 12 Planning:** Tier 2 model blocker analysis

## Example Test Cases

### Test 1: Basic substitution
```gams
$set n 10
Set i / i1*i%n% /;
```

### Test 2: Conditional default
```gams
$if not set nx $set nx 20
Set x / x0*x%nx% /;
```

### Test 3: Multiple substitutions
```gams
$set m 5
$set n 10
Set i / i1*i%m% /;
Set j / j1*j%n% /;
```

### Test 4: Zero-indexed range
```gams
$set nh 50
Set i / i0*i%nh% /;
```

### Test 5: Multi-character variable name
```gams
$set npoints 100
Set pts / pt1*pt%npoints% /;
```
