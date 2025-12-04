# Semantic: Undefined Symbol Validation Incorrectly Fails

**GitHub Issue:** [#416](https://github.com/jeffreyhorn/nlp2mcp/issues/416)  
**Status:** Completed  
**Priority:** Medium  
**Component:** Parser (Grammar)  
**Tier 2 Candidate:** pool.gms  
**Branch:** fix-issue-409-pool-include-file  

## Problem Statement

The parser is failing semantic validation claiming that symbols are undefined, even though they are properly declared in included files. This is preventing pool.gms from being fully processed.

## Current Behavior

**Validation Error:**
```
Error: Parse error at line 119, column 7: Undefined symbol 'cost' referenced [context: equation 'obj' LHS]
  obj.. cost =e=
        ^

Suggestion: Declare 'cost' as a variable, parameter, or set before using it
```

**Context from poolmod.inc (line 62, which becomes line 119 after include expansion):**
```gams
obj.. cost =e=
  sum(qy_dom(comp,pool,pro), cprice(comp)*q(comp,pool)*y(pool,pro))
 - sum(y_dom(pool,pro), pprice(pro)*y(pool, pro))
 + sum(z_dom(comp,pro), (cprice(comp)-pprice(pro))*z(comp,pro));
```

**Variable Declaration in poolmod.inc (line 38-41):**
```gams
variables  q(comp_, pool_) pool quality from pooling raw materials
           y(pool_, pro_)  flow from pool to product
           z(comp_, pro_)  direct flow of rawmaterials to product
           cost            total cost
```

The variable `cost` IS properly declared on line 41, but the semantic validator claims it's undefined when used in the equation on line 62.

## Analysis

This is NOT a parsing error - all the syntax has been successfully parsed! The error occurs during semantic validation, specifically when checking if symbols are declared before use.

### Possible Root Causes

1. **Include file processing issue:** The variables declared in poolmod.inc might not be properly registered in the symbol table before equations are validated.

2. **Multi-line variable declaration:** The declaration uses GAMS's multi-line syntax where subsequent lines don't repeat the `variables` keyword. The parser might not be handling this correctly.

3. **Declaration order:** Variables might be declared after they're used in equations in the expanded file, causing forward reference issues.

4. **Inline descriptions:** The inline descriptions (text after variable names) might be interfering with symbol extraction.

## Expected Behavior

The parser should:
1. Successfully parse all variable declarations from poolmod.inc
2. Register all declared symbols (q, y, z, cost) in the symbol table
3. Allow equations to reference these properly declared variables
4. Complete semantic validation without undefined symbol errors

## Investigation Needed

1. **Check if variables are being registered:** Add debug logging to see if `cost`, `q`, `y`, `z` are added to `model.variables`

2. **Check declaration parsing:** Verify that multi-line variable declarations are correctly parsed:
   ```gams
   variables x(i,j) description
            y(k)   another description
            z      scalar variable;
   ```

3. **Check include file ordering:** Ensure declarations from include files are processed before statements that reference them

4. **Review validation logic:** The semantic validation might be checking references before all declarations are processed

## Workaround

None currently - this blocks completion of pool.gms semantic processing.

## Impact

**Severity:** Medium

This is a **semantic validation issue**, not a syntax parsing issue. All the GAMS syntax features needed for pool.gms have been successfully implemented:
- ✅ Range notation
- ✅ Wildcard domains  
- ✅ Conditional sums
- ✅ Option statements with flexible separators
- ✅ Solve statements in loops
- ✅ Dollar-conditioned assignments

The **parser can now handle all GAMS syntax in pool.gms**. The remaining issue is in the semantic analysis phase where symbol resolution and validation occur.

## Possible Solutions

### Option 1: Two-Pass Validation
Separate parsing from validation:
- Pass 1: Parse entire file and collect all declarations
- Pass 2: Validate references against collected declarations

### Option 2: Forward References
Allow forward references and resolve them at the end:
- Collect undefined references during parsing
- Resolve against final symbol table after all declarations are processed

### Option 3: Relax Validation
Make undefined symbol checks warnings instead of errors:
- Allow the parse to complete
- Report undefined symbols as warnings for user review

### Option 4: Include File Pre-processing
Process include files completely before main file:
- Parse poolmod.inc first, register all symbols
- Then parse pool.gms with those symbols already available

## Testing Strategy

1. **Verify declaration parsing:**
   ```gams
   variables x, y(i), z(i,j);
   equation test;
   test.. x =e= sum(i, y(i));
   ```

2. **Test multi-line declarations:**
   ```gams
   variables x description one
            y description two
            z description three;
   ```

3. **Test include file symbols:**
   ```gams
   * file: included.gms
   variables x, y;
   
   * file: main.gms
   $include included.gms
   equation test;
   test.. x =e= y;
   ```

## Related Issues

- Issue #409: Pool.gms missing include file (completed)
- Issue #412: Conditional sum syntax (completed)
- Issue #413: Option statement multiple assignments (completed)
- Issue #414: Solve statement in loops (completed)
- Issue #415: Dollar-conditioned assignments (completed)

All **syntax parsing issues** for pool.gms have been resolved. This is now a **semantic validation issue**.

## References

- GAMS Documentation: [Variable Declarations](https://www.gams.com/latest/docs/UG_VariableDeclaration.html)

---

## Resolution

**Resolved:** Sprint 12 Day 5 (2024)  
**Commits:** 
- `497b8ff` - Sprint 12 Day 5: Implement inline_descriptions blocker
- `5d6728c` - Fix var_single grammar: support both inline descriptions and newline-separated variables

### Root Cause

The issue was **not** a semantic validation problem as initially suspected. It was a **grammar parsing issue** with variable declarations that have unquoted inline descriptions.

In `poolmod.inc` line 41:
```gams
variables  q(comp_, pool_) pool quality from pooling raw materials
           y(pool_, pro_)  flow from pool to product
           z(comp_, pro_)  direct flow of rawmaterials to product
           cost            total cost
```

The parser was incorrectly treating the unquoted description words (e.g., "total cost") as separate variable declarations, causing:
1. Variables with descriptions to not be registered correctly
2. Description words to be interpreted as undefined variable references

### Solution Implemented

Modified the grammar to properly handle inline descriptions using a two-pattern approach:

1. **Grammar Changes** (`src/gams/gams_grammar.lark`):
   - Split `var_decl` into two patterns:
     - `var_single`: For single variable declarations that may have inline descriptions
     - `var_list`: For comma-separated lists (no inline descriptions to avoid ambiguity)
   - Used NEWLINE-delimited lists: `var_decl_list: var_decl (NEWLINE var_decl)*`
   - Made semicolons optional in declaration blocks

2. **Parser Updates** (`src/ir/parser.py`):
   - Added `_process_var_decl` helper method to handle both var_single and var_list patterns
   - Updated `_handle_variables_block` to process var_decl_list structure
   - Properly extract and handle desc_text (3+ word descriptions) and STRING descriptions

### Test Results

All tests passing after fix:
- **Unit tests**: 1,709 passed
- **Integration tests**: 246 passed (5 skipped)
- **E2E tests**: 42 passed
- **Quality gates**: typecheck ✓, lint ✓, format ✓

### Impact

- ✅ Variables with inline descriptions now parse correctly
- ✅ poolmod.inc variables (q, y, z, cost) all registered properly
- ✅ pool.gms progresses past this blocker

### Remaining Issues

While issue #416 is resolved, pool.gms still has parsing issues:
- **Issue #417**: Sets and parameters with inline descriptions have similar problems
- The same grammar pattern needs to be applied to set_decl and param_decl

### Lessons Learned

1. **Inline descriptions are grammar issues, not semantic issues**: The problem was in tokenization/parsing, not symbol resolution
2. **desc_text pattern is greedy**: Multi-word unquoted descriptions can consume subsequent declarations if not carefully bounded
3. **NEWLINE as delimiter**: Explicitly using NEWLINE tokens in grammar rules (even when globally ignored) provides better structure
4. **Two-pattern approach**: Separating single declarations (with descriptions) from lists (without descriptions) resolves ambiguity
- File: `tests/fixtures/tier2_candidates/poolmod.inc` (lines 38-41: variable declarations, line 62: equation using cost)
- GAMS Library: pool.gms is model 237 in GAMSLib

## Notes

**IMPORTANT:** This issue represents a different category of problem than previous issues. All prior issues (#409-#415) were about **parsing GAMS syntax**. This issue is about **semantic validation** - verifying that the parsed syntax is semantically correct (e.g., variables are declared before use).

The fact that we're now hitting semantic validation errors means **the parser successfully handles all GAMS syntax in pool.gms**! This is a major milestone. The remaining work is improving the semantic analysis to properly handle:
- Symbol table management across include files
- Multi-line declarations
- Forward references
- Declaration ordering

This may be lower priority than other parsing tasks, as the syntax parsing is now complete for pool.gms.
