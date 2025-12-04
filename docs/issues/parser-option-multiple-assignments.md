# Parser: Option Statement with Multiple Assignments Not Supported

**GitHub Issue:** #413  
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/413  
**Status:** Open  
**Priority:** High  
**Component:** Parser  
**Tier 2 Candidate:** pool.gms  

## Problem Statement

The parser fails when encountering GAMS `option` statements with multiple comma-separated assignments on a single line. This is blocking pool.gms from parsing completely.

## Current Behavior

**Parse Error:**
```
Error: Parse error at line 708, column 16: Unexpected character: 'q'
  option clear = q,          clear = y,       clear = z
                 ^
```

**Failing Example from pool.gms (line 708):**
```gams
option clear = q,          clear = y,       clear = z  // start from same default point
       clear = obj,        clear = clower,  clear = cupper
       clear = pszrlt,     clear = plower,  clear = pupper
       clear = pqlower,    clear = pqupper, clear = fraction
       clear = extensions;
```

This is a multi-line option statement with multiple comma-separated assignments. Each assignment uses the form `clear = variable_name`.

## Expected Behavior

The parser should successfully parse `option` statements with:
- Multiple assignments on a single line separated by commas
- Continuation across multiple lines
- Mixed whitespace formatting
- Inline comments after the statement

## GAMS Language Specification

The GAMS `option` statement supports multiple assignments:

**Syntax:**
```gams
option option_name = value [, option_name = value]* ;
```

**Examples:**
```gams
* Single assignment
option limrow = 10;

* Multiple assignments on one line
option limrow = 10, limcol = 5;

* Multiple assignments across lines
option limrow = 10,
       limcol = 5,
       optcr = 0.01;

* The clear option specifically
option clear = x, clear = y, clear = z;
```

The `clear` option is used to reset variables to their default values before resolving.

## Technical Analysis

### Current Grammar State

The current `option_stmt` grammar rule likely expects a single assignment:

```lark
option_stmt: "option" ID "=" option_value ";"
```

### Required Changes

Need to support comma-separated list of assignments:

```lark
option_stmt: "option" option_assignment ("," option_assignment)* ";"
option_assignment: ID "=" option_value
```

Where `option_value` can be:
- Identifier (like variable names for `clear`)
- Number (like `limrow = 10`)
- String (for some options)
- Special keywords (on/off, yes/no, etc.)

### Specific Patterns to Support

1. **Simple multiple assignments:**
   ```gams
   option limrow = 10, limcol = 5;
   ```

2. **Multiple clear assignments:**
   ```gams
   option clear = x, clear = y, clear = z;
   ```

3. **Multi-line with continuation:**
   ```gams
   option clear = q,
          clear = y,
          clear = z;
   ```

4. **Mixed whitespace formatting:**
   ```gams
   option clear = q,          clear = y,       clear = z
          clear = obj,        clear = clower,  clear = cupper;
   ```

## Implementation Plan

### 1. Update Grammar (src/gams/gams_grammar.lark)

Update the `option_stmt` rule to support comma-separated assignments:

```lark
option_stmt: "option" option_assignment ("," option_assignment)* ";"
option_assignment: ID "=" option_value
option_value: ID | NUMBER | STRING | "on" | "off" | "yes" | "no"
```

### 2. Update Parser (src/ir/parser.py)

Update the `_parse_option_stmt` method to handle multiple assignments:
- Extract all option assignments from the statement
- Process each assignment individually
- Handle the special semantics of common options like `clear`, `limrow`, etc.

For the IR representation, we may want to either:
- Create separate `OptionStmt` nodes for each assignment (simplest)
- Or create a single node with a list of assignments (more compact)

### 3. Testing Strategy

**Unit Tests:**
- Single option assignment (existing behavior)
- Two assignments on one line
- Multiple assignments across lines
- Various option types (clear, limrow, limcol, etc.)
- Mixed whitespace and formatting

**Integration Tests:**
- Verify pool.gms parses successfully past line 708
- Test other GAMS library files with option statements

**Test Examples:**
```gams
* Test 1: Simple multiple
option limrow = 10, limcol = 5;

* Test 2: Multiple clear
option clear = x, clear = y;

* Test 3: Multi-line
option clear = a,
       clear = b,
       clear = c;

* Test 4: Pool.gms pattern
option clear = q,          clear = y,       clear = z
       clear = obj,        clear = clower,  clear = cupper;
```

## Acceptance Criteria

1. ✅ Grammar supports comma-separated option assignments
2. ✅ Parser correctly processes multiple assignments
3. ✅ pool.gms parses successfully past line 708
4. ✅ All existing tests continue to pass
5. ✅ New tests cover multiple assignment patterns
6. ✅ Quality gates pass (typecheck, lint, format, test)

## Related Issues

- Issue #409: Pool.gms missing include file (completed)
- Issue #412: Conditional sum syntax (completed)

This is the next blocker preventing pool.gms from parsing completely.

## References

- GAMS Documentation: [Option Statement](https://www.gams.com/latest/docs/UG_GamsCall.html#GAMSAOoptions)
- File: `tests/fixtures/tier2_candidates/pool.gms` (line 708)
- GAMS Library: pool.gms is model 237 in GAMSLib
