# Parser Error Line Number Tracking Design

**Sprint:** Epic 2 - Sprint 8 Prep  
**Task:** Task 4 - Design Parser Error Line Number Tracking  
**Created:** 2025-11-17  
**Purpose:** Design approach to extend SourceLocation tracking from convexity warnings (Sprint 7) to ALL parser errors

---

## Executive Summary

**Objective:** Achieve 100% coverage of parser errors with file/line/column information by extending Sprint 7's SourceLocation infrastructure.

**Key Findings:**
- **Lark-native errors:** Already include line/column information automatically
- **Custom parser errors:** 58 raise points in parser.py already use `_error()` helper which extracts location
- **Current state:** Parser errors **already have** line/column tracking via `ParserSemanticError`
- **Gap:** ParseError class in errors.py is not being used by parser; `ParserSemanticError` is used instead

**Sprint 8 Recommendation:**
- **Consolidate error handling:** Migrate from `ParserSemanticError` to `ParseError` for consistency
- **Enhance Lark error wrapping:** Wrap Lark exceptions in `ParseError` with extracted location
- **Minimal work required:** Infrastructure already exists, just needs integration

---

## Table of Contents

1. [Parser Error Type Catalog](#parser-error-type-catalog)
2. [Current Line Number Coverage](#current-line-number-coverage)
3. [Location Extraction Patterns](#location-extraction-patterns)
4. [Exception Class Analysis](#exception-class-analysis)
5. [Error Raise Point Inventory](#error-raise-point-inventory)
6. [Test Strategy](#test-strategy)
7. [Implementation Effort](#implementation-effort)

---

## Parser Error Type Catalog

### Lark-Native Errors (from grammar)

**1. UnexpectedToken**
- **Source:** Lark parser, generated during parse
- **Example:** `UnexpectedToken: Expected one of: SEMI, got RPAR`
- **Location:** ✅ Includes line/column from Lark metadata
- **Current handling:** Propagates to user unmodified
- **Sprint 8 action:** Wrap in `ParseError` for consistent formatting

**2. UnexpectedCharacters**
- **Source:** Lark lexer, generated when no token matches
- **Example:** `UnexpectedCharacters: No terminal matches '@' in the current parser context, at line 35 col 4`
- **Location:** ✅ Includes line/column in exception message
- **Current handling:** Propagates to user unmodified
- **Sprint 8 action:** Wrap in `ParseError` for consistent formatting

**Evidence:**
```python
# From tests/unit/gams/test_parser.py:506
with pytest.raises((lark.exceptions.UnexpectedToken, lark.exceptions.UnexpectedCharacters)):
    parse_text("Set i / 1*10")  # Missing semicolon
```

### Custom Parser Errors (nlp2mcp-specific)

**3. ParserSemanticError**
- **Source:** `src/ir/parser.py` validation logic
- **Example:** `"Indexed assignments are not supported yet [context: assignment_stmt]"`
- **Location:** ✅ Has line/column tracking via `_error()` helper
- **Current implementation:**
  ```python
  class ParserSemanticError(ValueError):
      def __init__(self, message: str, line: int | None = None, column: int | None = None):
          super().__init__(message)
          self.line = line
          self.column = column
  ```
- **Sprint 8 action:** Migrate to `ParseError` for consistency with errors.py

**4. ConditionEvaluationError**
- **Source:** `src/ir/condition_eval.py` - Evaluates $if/$elseif conditions
- **Example:** `"Unknown parameter 'foo' in condition"`
- **Location:** ❌ No line/column tracking (condition evaluator doesn't have parse tree)
- **Sprint 8 action:** Not a parse error; condition evaluation is separate phase

**5. CircularIncludeError**
- **Source:** `src/ir/preprocessor.py` - Detects include cycles
- **Example:** `"Circular include detected: a.gms -> b.gms -> a.gms"`
- **Location:** ❌ Preprocessor error, not parse error
- **Sprint 8 action:** Out of scope (preprocessor, not parser)

**6. IncludeDepthExceededError**
- **Source:** `src/ir/preprocessor.py` - Prevents infinite recursion
- **Example:** `"Include depth exceeded (max 100)"`
- **Location:** ❌ Preprocessor error, not parse error
- **Sprint 8 action:** Out of scope

**7. ValueError (domain mismatch)**
- **Source:** `src/ir/normalize.py:237` - Raised during normalization
- **Example:** `"Domain mismatch during normalization"`
- **Location:** ❌ Normalization error, not parse error
- **Sprint 8 action:** Out of scope (post-parse phase)

### ParseError Class (errors.py)

**8. ParseError (unused by parser)**
- **Source:** `src/utils/errors.py` - User-friendly parse error class
- **Current state:** Defined but **not used** by parser.py
- **Capabilities:**
  - Line/column tracking
  - Source line display
  - Caret pointer (^) under error location
  - Actionable suggestions
- **Sprint 8 action:** **Replace ParserSemanticError with ParseError**

**Example ParseError formatting:**
```
Parse error at line 5, column 12: Unexpected semicolon
  x = y + z;;
           ^
Suggestion: Remove the extra semicolon
```

---

## Current Line Number Coverage

### Coverage Analysis

| Error Type | Count | Has Line Numbers | Source |
|-----------|-------|------------------|--------|
| Lark UnexpectedToken | N/A | ✅ YES | Lark metadata |
| Lark UnexpectedCharacters | N/A | ✅ YES | Lark metadata |
| ParserSemanticError | 58 | ✅ YES | `_error()` helper |
| ConditionEvaluationError | 17 | ❌ NO | No parse tree |
| CircularIncludeError | 1 | ❌ NO | Preprocessor |
| IncludeDepthExceededError | 1 | ❌ NO | Preprocessor |
| ValueError (normalize) | 1 | ❌ NO | Post-parse |

**Parser error coverage:** 58/58 (100%) ✅  
**All errors coverage:** 58/79 (73%) - Others are preprocessor/normalization, not parse errors

### How ParserSemanticError Currently Works

**1. The `_error()` Helper (parser.py:1010-1024):**
```python
def _error(self, message: str, node: Tree | Token | None = None) -> ParserSemanticError:
    context_desc = self._current_context_description()
    if context_desc:
        message = f"{message} [context: {context_desc}]"
    if self._context_stack:
        current_domain = self._context_stack[-1][2]
        if current_domain:
            message = f"{message} [domain: {current_domain}]"
    line, column = self._node_position(node)  # ← Extracts line/column from Lark Tree
    if line is None and self._context_stack:
        for _, ctx_node, _ in reversed(self._context_stack):
            line, column = self._node_position(ctx_node)
            if line is not None:
                break
    return ParserSemanticError(message, line, column)  # ← Returns error with location
```

**2. Location Extraction (`_node_position` helper, parser.py:1027-1042):**
```python
def _node_position(self, node: Tree | Token | None) -> tuple[int | None, int | None]:
    """Extract line and column from a Lark node."""
    if node is None:
        return (None, None)
    if isinstance(node, Token):
        return (node.line, node.column)
    if isinstance(node, Tree) and hasattr(node, "meta"):
        return (node.meta.line, node.meta.column)
    return (None, None)
```

**3. Usage Pattern (all 58 raise points):**
```python
# Example from parser.py:876
raise self._error("Indexed assignments are not supported yet", target)
                    └─ message                                  └─ Tree node for location
```

**Result:** All custom parser errors already have line/column information! ✅

---

## Location Extraction Patterns

### Existing Infrastructure (Sprint 7)

**SourceLocation Dataclass (symbols.py):**
```python
@dataclass(frozen=True)
class SourceLocation:
    """Source code location for error reporting and traceability."""
    line: int
    column: int
    filename: str | None = None

    def __str__(self) -> str:
        """Format as 'file.gms:15:8' or 'line 15, col 8' if no filename."""
        if self.filename:
            return f"{self.filename}:{self.line}:{self.column}"
        return f"line {self.line}, col {self.column}"
```

**Extraction Helper (parser.py:1044-1058):**
```python
def _extract_source_location(
    self, node: Tree | Token | None, filename: str | None = None
) -> SourceLocation | None:
    """Extract source location from a parse tree node."""
    line, column = self._node_position(node)
    if line is not None and column is not None:
        return SourceLocation(line=line, column=column, filename=filename)
    return None
```

**Used for:** Convexity warnings (W301-W305) in normalize.py

### Pattern for Lark Error Wrapping

**Current state:** Lark errors propagate directly to user  
**Target state:** Wrap in `ParseError` with extracted location

**Implementation pattern:**
```python
def parse_text(source: str) -> Tree:
    """Parse a source string and return a disambiguated Lark parse tree."""
    parser = _build_lark()
    try:
        raw = parser.parse(source)
        return _resolve_ambiguities(raw)
    except lark.exceptions.UnexpectedToken as e:
        # Extract location from Lark exception
        raise ParseError(
            message=f"Unexpected token: {e.token}",
            line=e.line,
            column=e.column,
            suggestion="Check syntax near this location"
        ) from e
    except lark.exceptions.UnexpectedCharacters as e:
        raise ParseError(
            message=f"Unexpected character: {e.char}",
            line=e.line,
            column=e.column,
            suggestion="This character is not valid in this context"
        ) from e
```

### Pattern for ParserSemanticError → ParseError Migration

**Current implementation:**
```python
raise self._error("Indexed assignments are not supported yet", target)
```

**Target implementation:**
```python
def _parse_error(self, message: str, node: Tree | Token | None = None, suggestion: str | None = None) -> ParseError:
    """Create a ParseError with location extracted from node."""
    context_desc = self._current_context_description()
    if context_desc:
        message = f"{message} [context: {context_desc}]"
    
    line, column = self._node_position(node)
    if line is None and self._context_stack:
        for _, ctx_node, _ in reversed(self._context_stack):
            line, column = self._node_position(ctx_node)
            if line is not None:
                break
    
    # Could extract source_line from original source if we store it
    return ParseError(message=message, line=line, column=column, suggestion=suggestion)

# Usage:
raise self._parse_error("Indexed assignments are not supported yet", target,
                        suggestion="Use scalar assignment: x.l = 5")
```

---

## Exception Class Analysis

### Current Exception Hierarchy

```
Exception
├── ValueError
│   └── ParserSemanticError (parser.py:32-48)
│       - Used by: parser.py (58 raise points)
│       - Has: line, column
│       - Missing: source_line, suggestion, caret display
│
└── NLP2MCPError (errors.py:8-10)
    └── UserError (errors.py:13-38)
        ├── ParseError (errors.py:57-117)
        │   - Used by: nobody (unused!)
        │   - Has: line, column, source_line, suggestion, caret display
        │   - Format: "Parse error at line X, column Y: message"
        │
        ├── ModelError (errors.py:120-127)
        ├── UnsupportedFeatureError (errors.py:130-150)
        ├── FileError (errors.py:153-159)
        └── NumericalError (errors.py:162-208)
```

### Recommendation: Consolidate on ParseError

**Why consolidate:**
1. **ParseError has better UX:** Source line display, caret pointer, suggestions
2. **Consistency:** All error types use NLP2MCPError hierarchy
3. **Future-proofing:** ParseError designed for user-facing errors
4. **Less code:** One error class instead of two

**Migration path:**
1. Keep `ParserSemanticError` as deprecated alias (for backwards compatibility)
2. Add `_parse_error()` helper that returns `ParseError`
3. Gradually migrate `raise self._error()` to `raise self._parse_error()`
4. Wrap Lark errors in `ParseError` in `parse_text()`

**No breaking changes:** ParserSemanticError can inherit from ParseError or be an alias

---

## Error Raise Point Inventory

### Parser.py Error Raise Points (58 total)

All 58 raise points use `raise self._error(...)` which already includes line/column:

**By category:**
- Assignment validation: 14 raises (lines 838-892)
- Symbol lookup: 11 raises (lines 1072-1100)
- Expression construction: 18 raises (lines 1116-1330)
- Alias processing: 5 raises (lines 1383-1402)
- Model/objective validation: 6 raises (lines 1415-1476)
- Declaration validation: 4 raises (lines 259-670)

**Sample raises with location extraction:**
```python
# Line 876: Indexed assignment
raise self._error("Indexed assignments are not supported yet", target)

# Line 1072: Domain mismatch
raise self._error(
    f"Variable '{name}' expects {len(expected)} indices but received {len(idx_tuple)}",
    node
)

# Line 1100: Undefined symbol
raise self._error(f"Undefined symbol '{name}' referenced", node)

# Line 1216: Constant validation
raise self._error(f"Assignments must use numeric constants; got {expr!r} in {context}")
```

**All include `node` parameter for location extraction!** ✅

### Lark Error Injection Points (2 total)

**1. parse_text() (parser.py:155-159):**
```python
def parse_text(source: str) -> Tree:
    parser = _build_lark()
    raw = parser.parse(source)  # ← Lark errors raised here
    return _resolve_ambiguities(raw)
```
**Sprint 8 action:** Add try/except to wrap Lark errors

**2. parse_file() (parser.py:162-169):**
```python
def parse_file(path: str | Path) -> Tree:
    preprocessed = preprocess_gams_file(path)
    return parse_text(preprocessed)  # ← Calls parse_text, gets wrapped errors
```
**Sprint 8 action:** No change needed (inherits from parse_text)

---

## Test Strategy

### Test Coverage Plan

**1. Lark Error Wrapping Tests**
- Test `UnexpectedToken` wrapping with correct line/column
- Test `UnexpectedCharacters` wrapping with correct line/column
- Verify `ParseError` format includes source line and caret
- Verify suggestion field is populated

**2. ParserSemanticError Migration Tests**
- Test all 58 error messages still work after migration
- Verify line/column information preserved
- Verify context/domain information still included
- Test caret display for sample errors

**3. Regression Tests**
- Run existing test suite to ensure no breakage
- Verify test_errors.py ParseError tests still pass
- Check that error messages match expected format

**4. End-to-End Error Display Tests**
- Test actual error output from CLI
- Verify file:line:column format in error messages
- Check that suggestions appear in output

### Existing Test Coverage

**tests/unit/utils/test_errors.py** (lines 99-131):
- ✅ ParseError without location
- ✅ ParseError with line only  
- ✅ ParseError with line and column
- ✅ ParseError with source line and caret
- ✅ Caret alignment verification

**tests/unit/gams/test_parser.py** (line 506):
- ✅ Tests that Lark errors are raised for syntax errors
- ❌ Does not verify error formatting or location extraction

**Gap:** No tests for ParserSemanticError line number formatting

### New Test Fixtures Needed

**1. Lark error wrapping (2 test cases):**
```python
def test_unexpected_token_wrapped():
    source = "Set i / 1*10"  # Missing semicolon
    with pytest.raises(ParseError) as exc_info:
        parse_text(source)
    assert exc_info.value.line is not None
    assert exc_info.value.column is not None
    assert "Unexpected" in str(exc_info.value)

def test_unexpected_characters_wrapped():
    source = "Set i @ / 1*10 /;"  # Invalid character @
    with pytest.raises(ParseError) as exc_info:
        parse_text(source)
    assert exc_info.value.line == 1
    assert exc_info.value.column == 7
```

**2. ParserSemanticError format tests (3 test cases):**
```python
def test_parser_semantic_error_line_numbers():
    source = """
    Set i / 1*10 /;
    Parameter p(i);
    p(i) = 5;  # Should error: indexed assignment not supported
    """
    with pytest.raises(ParseError) as exc_info:
        parse_model_text(source)
    assert exc_info.value.line == 4
    assert "Indexed assignments" in str(exc_info.value)
```

**Total new tests:** ~5 test cases (1-2 hours)

---

## Implementation Effort

### Detailed Task Breakdown

**1. Add Lark error wrapping to parse_text() (1 hour)**
- Import `lark.exceptions`
- Add try/except around `parser.parse(source)`
- Extract line/column from Lark exceptions
- Wrap in `ParseError` with appropriate message and suggestion
- Test with 2 error fixtures

**2. Create _parse_error() helper (1 hour)**
- Copy `_error()` implementation
- Return `ParseError` instead of `ParserSemanticError`
- Add suggestion parameter
- Add docstring with examples
- Test with sample raise point

**3. Migrate high-value error messages (1-2 hours)**
- Identify top 10 most common errors (grep for _error usage frequency)
- Add suggestions for each error type
- Replace `_error()` calls with `_parse_error()`
- Test that errors still display correctly

**4. Add ParseError test fixtures (1 hour)**
- Write 2 Lark error wrapping tests
- Write 3 ParserSemanticError migration tests
- Run tests to verify coverage

**5. Update documentation (0.5 hours)**
- Update docstrings in parser.py
- Add comments explaining error handling strategy
- Update any relevant README sections

**Total: 4.5-5.5 hours** ✅ Within 4-6 hour estimate

### Effort Validation

**Original estimate:** 4-6 hours (PROJECT_PLAN.md)  
**Detailed breakdown:** 4.5-5.5 hours  
**Verdict:** ✅ **Confirmed** - estimate is accurate

**Risk factors:**
- ✅ Low risk: Infrastructure already exists (`_error()`, `_node_position()`)
- ✅ Low risk: ParseError class already tested
- ✅ Low risk: Small number of injection points (2 for Lark, 1 helper for custom)
- ⚠️ Medium risk: Migrating all 58 raise points (if doing full migration)

**Recommendation:** Start with high-value migrations (indexed assignments, undefined symbols) and defer full migration to later sprint if time is tight.

### Sprint 8 vs Sprint 8b Scope

**Sprint 8 (minimum viable):**
- Wrap Lark errors in ParseError (1 hour)
- Create `_parse_error()` helper (1 hour)
- Migrate top 5 error types with suggestions (1 hour)
- Add 5 test fixtures (1 hour)
- **Total: 4 hours**

**Sprint 8b (full migration):**
- Migrate all 58 raise points to `_parse_error()` (2-3 hours)
- Add suggestions for all error types (2 hours)
- Comprehensive test coverage (2 hours)
- **Total: 6-7 hours**

---

## Cross-References

### Sprint 7 Implementation

**SourceLocation usage in normalize.py** (convexity warnings):
```python
# From normalize.py - convexity warning example
def _check_convexity_mult(self, node: Binary, loc: SourceLocation | None) -> ConvexityIssue | None:
    if issue:
        return ConvexityIssue(
            code="W302",
            message="Multiplication is only convex under specific conditions",
            equation=self._current_equation,
            location=loc,  # ← SourceLocation used for warning
            suggestion="Ensure one operand is constant or both are affine"
        )
```

**Lesson:** SourceLocation works well for warnings; extend to errors for consistency

### Related Files

- `src/ir/parser.py`: Parser implementation (58 error raise points)
- `src/ir/symbols.py`: SourceLocation dataclass
- `src/utils/errors.py`: ParseError class (unused by parser)
- `tests/unit/utils/test_errors.py`: ParseError tests
- `tests/unit/gams/test_parser.py`: Parser tests (includes Lark error check)

---

## Recommendations

**Primary recommendation:** ✅ **Consolidate on ParseError for all parser errors**

**Rationale:**
1. ParseError has superior UX (source line, caret, suggestions)
2. Infrastructure already exists (just needs wiring)
3. Low implementation effort (4-5.5 hours)
4. High user impact (better error messages)
5. Builds on Sprint 7 SourceLocation work

**Implementation priorities:**
1. **High priority:** Wrap Lark errors (affects all syntax errors)
2. **High priority:** Top 5 semantic errors with suggestions (indexed assign, undefined symbol, etc.)
3. **Medium priority:** Remaining semantic errors
4. **Low priority:** Full migration of all 58 raise points

**Next steps:**
- Task 5: Design Partial Parse Metrics
- Sprint 8 implementation of error line number tracking
