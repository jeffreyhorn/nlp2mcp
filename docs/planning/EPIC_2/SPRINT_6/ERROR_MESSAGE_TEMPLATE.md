# Error Message Template

**Date:** 2025-11-12  
**Status:** ✅ DESIGN COMPLETE - Ready for Sprint 6 Implementation  
**Purpose:** Define structured error message format for nlp2mcp UX improvements  
**Sprint:** Sprint 6 Component 4 (UX Improvements Iteration 1)

## Overview

This document specifies the error message template for nlp2mcp to provide clear, actionable feedback to users when parsing or validation errors occur. The template improves upon basic error messages by providing context, explanation, and suggested actions.

## Template Structure

All error messages follow this structure:

```
{Error Level}: {Brief Description} (line {line}, column {col})

{Source Context - up to 3 lines with caret pointer}

{Detailed Explanation}

{Suggested Action or Workaround}

{Documentation Link (optional)}
```

### Components

1. **Error Level**: `Error` or `Warning`
   - `Error`: Prevents compilation/conversion, must be fixed
   - `Warning`: Does not prevent compilation but may indicate problems

2. **Brief Description**: One-line summary of the issue
   - Clear, specific problem statement
   - Includes the problematic construct or feature name

3. **Location**: `(line {line}, column {col})`
   - Exact position in source file
   - Line numbers are 1-indexed
   - Column numbers are 1-indexed (character position)

4. **Source Context**: Visual display of problematic code
   - Shows up to 3 lines (1 before, error line, 1 after)
   - Format: `{lineno:>4} | {code}`
   - Caret pointer (`^^^` or `~~~`) under problematic tokens
   - Helps user locate exact issue without opening file

5. **Detailed Explanation**: Why this is an error
   - What the user tried to do
   - Why nlp2mcp doesn't support it
   - Technical context if helpful

6. **Suggested Action**: How to fix it
   - Concrete steps to resolve the error
   - Workarounds if available
   - Alternative approaches

7. **Documentation Link** (optional): Where to learn more
   - Relative path to documentation
   - Section anchor if applicable
   - Example: `See: docs/GAMS_SUBSET.md#unsupported-features`

## Error Categories

### Category 1: Parse Errors

Syntax errors, unsupported GAMS features, malformed constructs.

**Characteristics:**
- Always `Error` level (fatal)
- Usually have source context
- Need specific workarounds
- Link to GAMS_SUBSET.md

### Category 2: Semantic Errors

Valid syntax but incorrect semantics (undefined variables, type mismatches).

**Characteristics:**
- Always `Error` level (fatal)
- Have source context
- Explanations focus on model structure
- May link to user guide or examples

### Category 3: Convexity Warnings

Non-convex problems that may not solve correctly with MCP.

**Characteristics:**
- Always `Warning` level (non-fatal)
- Have source context
- Educational explanations
- Link to CONVEXITY.md
- Suggest alternative solvers

### Category 4: Feature Limitations

Supported but limited features (e.g., table syntax, indexed sets).

**Characteristics:**
- Usually `Warning` level
- Have source context
- Explain current limitations
- May suggest manual workarounds

## Examples

### Example 1: Unsupported Equation Type (Parse Error)

```
Error: Unsupported equation type '=n=' (line 15, column 20)

  15 | constraint.. x + y =n= 0;
                            ^^^

nlp2mcp currently only supports:
  =e= (equality)
  =l= (less than or equal)
  =g= (greater than or equal)

The '=n=' operator (non-binding) is not supported for MCP reformulation.

Action: Convert to one of the supported equation types.
See: docs/GAMS_SUBSET.md#equation-types
```

**Rationale:**
- Clear identification of unsupported operator
- Shows exact location with caret
- Lists what IS supported (helpful context)
- Explains why it's not supported
- Directs to documentation

### Example 2: Conditional Compilation (Parse Error)

```
Error: Unsupported construct '$if' (line 42, column 5)

  42 | $if defined(DEBUG) Display x.l;
          ^^

nlp2mcp does not support conditional compilation directives.
Conditional logic ($if, $ife, $set, etc.) is evaluated at GAMS compile-time
and is not available during NLP→MCP conversion.

Action: Remove conditional directives or refactor model to avoid them.
Workaround: Create separate .gms files for different configurations.
See: docs/GAMS_SUBSET.md#unsupported-features
```

**Rationale:**
- Identifies the specific directive
- Explains compile-time vs conversion-time distinction
- Provides concrete workaround
- Links to comprehensive documentation

### Example 3: Nonlinear Equality Warning (Convexity)

```
Warning: Non-convex problem detected (model.gms)

Nonlinear equality in equation 'circle_constraint' (line 18)

  18 | circle_constraint.. x**2 + y**2 =e= 4;
                          ^^^^^^^^^^^^^^^

Nonlinear equalities (=e=) with nonlinear expressions typically define 
non-convex feasible sets. The KKT-based MCP reformulation may produce 
an unsolvable system or find only local solutions.

Recommendation: 
  - Use NLP solver (CONOPT, IPOPT) instead of PATH
  - Or reformulate as inequality if possible: x**2 + y**2 =l= 4

See: docs/CONVEXITY.md for more information
```

**Rationale:**
- Clearly labeled as warning (won't stop compilation)
- Educational explanation of why this is problematic
- Multiple solution options
- Links to deeper explanation

### Example 4: Undefined Variable (Semantic Error)

```
Error: Undefined variable 'z' (line 24, column 15)

  23 | Equation objdef;
  24 | objdef.. obj =e= x + y + z;
                               ^

Variable 'z' is used in equation 'objdef' but was never declared.

Action: Add variable declaration before use:
  Variables x, y, z;

Or check for typos in variable name.
```

**Rationale:**
- Clear problem statement
- Shows context including previous line
- Specific fix with example code
- Suggests alternative cause (typo)

### Example 5: Loop Construct (Parse Error)

```
Error: Unsupported construct 'loop' (line 56, column 1)

  56 | loop(i, solve m using nlp minimizing obj;);
       ^^^^

nlp2mcp does not support loop constructs or multi-solve models.
Only single-solve NLP models can be converted to MCP.

Action: Remove loop and generate separate .gms files for each scenario.
Workaround: Use GAMS scripting to generate multiple model variants.
See: docs/GAMS_SUBSET.md#unsupported-features
```

**Rationale:**
- Identifies unsupported control flow
- Explains fundamental limitation (single-solve only)
- Provides practical workaround
- Links to documentation

### Example 6: Table Statement with Complex Indexing (Warning)

```
Warning: Complex table statement may require manual verification (line 30)

  30 | Table data(i,j)
       ^^^^^

Table statement parsed successfully, but complex indexing or sparse data
patterns may not be fully validated. Verify that table data correctly
populates parameters in the generated MCP model.

Recommendation: Check .lst file after PATH solve to ensure data loaded correctly.
```

**Rationale:**
- Warning doesn't block compilation
- Explains limitation in current implementation
- Gives user action to verify correctness
- Honest about what the tool can/cannot guarantee

### Example 7: Min/Max with Nested Different Operations (Parse Error)

```
Error: Differentiation not yet implemented for function 'max' (line 12)

Nested min/max with different operations detected

  12 | obj_eq.. obj =e= min(x, max(y, z));
                               ^^^

nlp2mcp supports nested min/max only for same-operation nesting:
  - min(a, min(b, c))  ✓ Supported (flattens to min(a,b,c))
  - max(a, max(b, c))  ✓ Supported (flattens to max(a,b,c))
  - min(a, max(b, c))  ✗ Not supported (mixed operations)

Action: Reformulate to avoid mixed nesting:
  - Option 1: Use auxiliary variable for inner max
      Variables aux_max;
      aux_eq.. aux_max =e= max(y, z);
      obj_eq.. obj =e= min(x, aux_max);
  
  - Option 2: Manually reformulate using epigraph form

See: docs/planning/EPIC_2/SPRINT_6/NESTED_MINMAX_DESIGN.md
```

**Rationale:**
- Identifies specific function causing the error
- Clearly explains what IS and ISN'T supported with examples
- Provides two concrete workarounds with code
- Links to design doc for advanced users

### Example 8: Missing Solve Statement (Semantic Error)

```
Error: No solve statement found (model.gms)

A valid GAMS model must include a solve statement:
  solve {model_name} using nlp minimizing|maximizing {objective_var};

Example:
  Model mymodel /all/;
  Solve mymodel using nlp minimizing obj;

Action: Add a solve statement at the end of your model file.
See: docs/GAMS_SUBSET.md#model-structure
```

**Rationale:**
- Clear problem statement (no source context needed - file-level issue)
- Shows required syntax
- Provides complete example
- Links to documentation on model structure

## Implementation Guidelines

### For Parser Errors

**Location:** `src/ir/parser.py`

```python
from src.utils.error_formatter import FormattedError, ErrorContext

def _handle_unsupported_construct(self, token: Token) -> None:
    """Handle unsupported GAMS construct."""
    error = FormattedError(
        level="Error",
        title=f"Unsupported construct '{token.value}'",
        context=ErrorContext(
            filename=self.filename,
            line=token.line,
            column=token.column,
            source_lines=self._get_source_lines(token.line)
        ),
        explanation=(
            f"nlp2mcp does not support {token.value} constructs.\n"
            "Only single-solve NLP models can be converted to MCP."
        ),
        action=(
            f"Remove {token.value} or refactor model to avoid it.\n"
            "See: docs/GAMS_SUBSET.md#unsupported-features"
        ),
        doc_link="docs/GAMS_SUBSET.md#unsupported-features"
    )
    raise ParseError(error.format())
```

### For Convexity Warnings

**Location:** `src/convexity/checker.py`

```python
from src.utils.error_formatter import FormattedError, ErrorContext

def check_nonlinear_equality(self, eq_name: str, eq_def: EquationDef) -> None:
    """Check for non-convex nonlinear equalities."""
    if self._is_nonlinear_equality(eq_def):
        warning = FormattedError(
            level="Warning",
            title="Non-convex problem detected",
            context=ErrorContext(
                filename=self.model_ir.filename,
                line=eq_def.line,
                column=eq_def.column,
                source_lines=self._get_source_lines(eq_def.line)
            ),
            explanation=(
                f"Nonlinear equality in equation '{eq_name}'\n\n"
                "Nonlinear equalities typically define non-convex feasible sets.\n"
                "KKT-based MCP reformulation may not be solvable."
            ),
            action=(
                "Recommendation:\n"
                "  - Use NLP solver (CONOPT, IPOPT) instead of PATH\n"
                "  - Or reformulate as inequality if possible"
            ),
            doc_link="docs/CONVEXITY.md"
        )
        self.warnings.append(warning.format())
```

### For CLI Display

**Location:** `src/cli.py`

```python
def main():
    try:
        # ... parsing and conversion ...
    except ParseError as e:
        # Error already formatted by parser
        print(str(e), file=sys.stderr)
        sys.exit(1)
    
    # Display warnings if any
    if warnings:
        print("\n⚠️  Warnings:\n", file=sys.stderr)
        for warning in warnings:
            print(warning, file=sys.stderr)
            print()  # blank line between warnings
```

## Design Decisions

### Decision 1: Column Numbers

**Choice:** Include column numbers in error messages

**Rationale:**
- Many editors support jumping to line:column
- More precise than line-only
- Helps with long lines
- Standard practice in modern compilers (Rust, TypeScript)

**Alternative:** Line-only (simpler but less precise)

### Decision 2: Caret Pointer Style

**Choice:** Use `^^^` for multi-character tokens, `^` for single character

**Rationale:**
- Visual clarity
- Works well in monospace terminal output
- Standard in many compilers (Python, Rust)

**Alternative:** `~~~` (squiggly underline) - also acceptable

### Decision 3: Context Lines

**Choice:** Show up to 3 lines (1 before, error line, 1 after)

**Rationale:**
- Balance between context and brevity
- Fits in terminal window without scrolling
- Enough context to understand issue

**Alternative:** Show more lines (5-7) - too verbose for terminal

### Decision 4: Documentation Links

**Choice:** Use relative paths from project root

**Rationale:**
- Works in both repo and installed package
- User can navigate from project directory
- Avoids external URL dependencies

**Alternative:** Absolute URLs - fragile, requires hosting

### Decision 5: Error vs Warning

**Choice:** Strict classification - errors are fatal, warnings are not

**Rationale:**
- Clear distinction
- User knows if they can proceed
- Aligns with compiler conventions

**Alternative:** Multiple warning levels - adds complexity

## Testing Strategy

### Unit Tests

```python
# tests/unit/utils/test_error_formatter.py

def test_format_error_with_context():
    """Test error formatting with source context."""
    error = FormattedError(
        level="Error",
        title="Test error",
        context=ErrorContext(
            filename="test.gms",
            line=10,
            column=5,
            source_lines=["line 9", "line 10", "line 11"]
        ),
        explanation="This is a test explanation.",
        action="Take this action to fix it.",
        doc_link="docs/TEST.md"
    )
    
    output = error.format()
    
    assert "Error: Test error (line 10, column 5)" in output
    assert "  10 | line 10" in output
    assert "     ^" in output
    assert "This is a test explanation" in output
    assert "Take this action to fix it" in output
    assert "See: docs/TEST.md" in output


def test_format_error_without_context():
    """Test error formatting without source context."""
    error = FormattedError(
        level="Warning",
        title="Test warning",
        context=None,
        explanation="Warning explanation.",
        action="Suggested action."
    )
    
    output = error.format()
    
    assert "Warning: Test warning" in output
    assert "line" not in output  # No location
    assert "Warning explanation" in output
    assert "Suggested action" in output
```

### Integration Tests

Test with real GAMS files that trigger errors:

1. `tests/fixtures/error_messages/unsupported_equation_type.gms` - =n= operator
2. `tests/fixtures/error_messages/conditional_compile.gms` - $if directive
3. `tests/fixtures/error_messages/loop_construct.gms` - loop statement
4. `tests/fixtures/error_messages/undefined_variable.gms` - missing declaration

Verify formatted output matches examples.

## Migration Plan

### Phase 1: Add Formatter (Sprint 6)

1. Create `src/utils/error_formatter.py`
2. Add unit tests
3. No changes to existing error paths yet

### Phase 2: Integrate in Parser (Sprint 6)

1. Update `src/ir/parser.py` to use formatter for new errors
2. Keep existing error messages unchanged initially
3. Gradually migrate existing errors

### Phase 3: Add Convexity Warnings (Sprint 6 or 7)

1. Update `src/convexity/checker.py`
2. Format existing warnings
3. Add new warnings as needed

### Phase 4: Full Migration (Sprint 7+)

1. Migrate all remaining error messages
2. Remove old formatting code
3. Update tests

## Future Enhancements

### Enhancement 1: Color Output

Add color support for terminal output:
- Red for errors
- Yellow for warnings
- Bold for titles
- Gray for context

**Implementation:** Use `colorama` library for cross-platform support

### Enhancement 2: JSON Output Mode

Add `--json` flag for machine-readable errors:

```json
{
  "level": "error",
  "title": "Unsupported equation type '=n='",
  "location": {"line": 15, "column": 20, "file": "model.gms"},
  "explanation": "nlp2mcp currently only supports...",
  "action": "Convert to one of the supported equation types.",
  "doc_link": "docs/GAMS_SUBSET.md#equation-types"
}
```

**Use case:** Integration with IDEs, automated testing

### Enhancement 3: Error Codes

Assign unique error codes (e.g., E001, E002, W001):
- Easier to search documentation
- Can filter specific error types
- Machine-readable

**Example:** `Error E042: Unsupported construct 'loop'`

### Enhancement 4: Quick Fix Suggestions

For common errors, provide automated fixes:

```
Error: Missing semicolon (line 10, column 25)

Quick fix available:
  nlp2mcp --fix model.gms
```

**Use case:** Simple syntax errors that are easy to auto-correct

## References

- **Rust Compiler Errors**: https://doc.rust-lang.org/book/appendix-05-error-messages.html
  - Inspiration for format and helpful messages

- **Elm Compiler Errors**: https://elm-lang.org/news/compiler-errors-for-humans
  - Focus on beginner-friendly explanations

- **TypeScript Errors**: https://www.typescriptlang.org/docs/handbook/intro.html
  - Column numbers, context, documentation links

- **GAMS Documentation**: https://www.gams.com/latest/docs/
  - Reference for GAMS constructs and limitations

## Appendix: Template Checklist

When creating a new error message, ensure it includes:

- [ ] Error level (Error or Warning)
- [ ] Brief, specific title
- [ ] Location (line, column) if applicable
- [ ] Source context (3 lines with caret) if applicable
- [ ] Clear explanation of what went wrong
- [ ] Actionable suggestion for fixing
- [ ] Documentation link if available
- [ ] Tested with real example
- [ ] No jargon unless explained
- [ ] Helpful tone, not condescending

---

**Document Status:** ✅ COMPLETE  
**Next Step:** Implement `src/utils/error_formatter.py` prototype  
**Approval:** Ready for Sprint 6 implementation
