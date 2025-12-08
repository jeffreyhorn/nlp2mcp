# Issue: Variables from Include Files Not Visible in Main File

**Status**: Open  
**Priority**: High  
**Component**: Parser (Include File Handling)  
**GitHub Issue**: [#418](https://github.com/jeffreyhorn/nlp2mcp/issues/418)  
**Tier 2 Candidate**: pool.gms

## Description

Variables defined in an included file (poolmod.inc) are not visible when referenced in the main file (pool.gms), causing "Undefined symbol" errors during semantic validation.

## Example

**File**: `tests/fixtures/tier2_candidates/pool.gms` (line 56)
```gams
$include poolmod.inc
```

**File**: `tests/fixtures/tier2_candidates/poolmod.inc` (lines 39-42)
```gams
variables  q(comp_, pool_) pool quality from pooling raw materials
           y(pool_, pro_)  flow from pool to product
           z(comp_, pro_)  direct flow of rawmaterials to product
           cost            total cost
```

**File**: `tests/fixtures/tier2_candidates/pool.gms` (line 119)
```gams
obj.. cost =e=
```

**Error**:
```
Error: Parse error at line 119, column 7: Undefined symbol 'cost' referenced [context: equation 'obj' LHS]
  obj.. cost =e=
        ^

Suggestion: Declare 'cost' as a variable, parameter, or set before using it
```

## Root Cause

The variable `cost` is declared in `poolmod.inc` (line 42), but when `pool.gms` references it on line 119, the parser reports it as undefined. This suggests one of the following issues:

### Hypothesis 1: Include File Not Processed First
The include file may not be fully processed before the main file continues parsing. If the parser processes declarations sequentially and doesn't complete the include file before returning to the main file, symbols from the include won't be registered.

### Hypothesis 2: Symbol Scope Issue
Variables declared in an include file may not be properly added to the global symbol table, or there may be scope isolation between the included file and the main file.

### Hypothesis 3: Line-Continuation Issue
The variable declaration in poolmod.inc uses newline-separated entries with inline descriptions:
```gams
variables  q(comp_, pool_) pool quality from pooling raw materials
           y(pool_, pro_)  flow from pool to product
           z(comp_, pro_)  direct flow of rawmaterials to product
           cost            total cost
```

While issue #416 and #417 fixed similar patterns, there may be an edge case when these declarations appear in an included file that's parsed separately.

## Investigation Needed

1. **Verify variable registration**: Check if `cost`, `q`, `y`, `z` are actually registered in the model when poolmod.inc is parsed
2. **Test include file handling**: Create minimal test case with include file containing variables
3. **Check symbol table**: Verify that symbols from included files are added to the main model's symbol table
4. **Line number tracking**: Ensure error messages correctly reference include file locations

## Impact

- **Blocks**: pool.gms from parsing completely (Tier 2 GAMS library file)
- **Severity**: High - Include files are fundamental to GAMS programs
- **Workaround**: None without modifying source files

## Test Case

Create minimal reproduction:

**File**: `test_include_vars.gms`
```gams
$include vars.inc

Equation test;
test.. x =e= 1;
```

**File**: `vars.inc`
```gams
Variable x;
```

Expected: Variable `x` from include file should be recognized in equation
Actual: TBD - need to verify behavior

## Related Issues

- Issue #416 (Completed): Variables with inline descriptions - Fixed variable parsing with desc_text
- Issue #417 (Completed): Sets and parameters with inline descriptions - Fixed similar parsing issues
- Issue #409 (Completed): Pool.gms missing include file - Fixed include file path resolution

## Notes

- pool.gms successfully includes poolmod.inc (issue #409 resolved)
- Sets and parameters from poolmod.inc ARE being registered correctly (issues #416/#417 resolved)
- Only variables from include files seem to have this issue
- The error occurs during semantic validation, not during parsing, suggesting the variables are parsed but not registered in the symbol table

## Progress

Issues resolved for pool.gms:
- ✅ Issue #409: Include file path resolution
- ✅ Issue #412: Conditional sum syntax  
- ✅ Issue #413: Option statement multiple assignments
- ✅ Issue #414: Solve statement in loops
- ✅ Issue #415: Dollar-conditioned assignments
- ✅ Issue #416: Variables with inline descriptions
- ✅ Issue #417: Sets and parameters with inline descriptions
- ❌ **Current blocker**: Variables from include files not visible

## Next Steps

1. Create GitHub issue
2. Add minimal test case to reproduce
3. Debug include file processing to understand symbol registration
4. Verify if issue is specific to variables or affects all symbol types
5. Implement fix ensuring include file symbols are properly registered
