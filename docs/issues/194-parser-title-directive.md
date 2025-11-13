# Issue #194: Parser does not support GAMS $title directive

**Issue URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/194  
**Status:** Open  
**Priority:** Medium  
**Labels:** bug, enhancement  
**Created:** 2025-11-13  
**Milestone:** Sprint 7 (proposed)

## Problem Description

The GAMS parser currently does not support the `$title` compiler directive, which is commonly used in GAMS models to provide a descriptive title. This prevents parsing of many otherwise valid GAMS models, including several test fixtures created for convexity detection testing.

## Error Observed

When attempting to parse a GAMS file containing `$title`, the parser fails with:

```
lark.exceptions.UnexpectedCharacters: No terminal matches '$' in the current parser context, at line 1 col 1

$title Convex Quadratic Program - Convex
^
```

## Impact

**Severity:** Medium  
**Scope:** Parser/Frontend

### Current Impact
- **Test Coverage:** Unable to test 10 out of 13 convexity test fixtures
  - Working: `convex_lp.gms`, `convex_with_nonlinear_ineq.gms`, `nonconvex_trig.gms`
  - Blocked: `convex_qp.gms`, `nonconvex_circle.gms`, `nonconvex_bilinear.gms`, `nonconvex_quotient.gms`, `nonconvex_odd_power.gms`, and 5 others
- **User Experience:** Users must manually remove `$title` directives from their GAMS files before conversion
- **GAMSLib Integration:** Many GAMSLib models use `$title`, limiting our ability to benchmark against real-world models

### Sprint 6 Workaround
For Sprint 6 Day 3 (Convexity Heuristics), we worked around this by:
- Using only the 3 fixtures without `$title` directives
- All 18 unit tests pass with these 3 fixtures
- Documented limitation in CHANGELOG.md (commit e71cb9a)
- See PR #193 review comments for details

## Example GAMS Files Affected

```gams
$title Convex Quadratic Program - Convex

Variables x, y, obj;
Equations objdef;

objdef.. obj =e= x**2 + y**2;

x.lo = -10; x.up = 10;
y.lo = -10; y.up = 10;

Model m /all/;
Solve m using nlp minimizing obj;
```

## GAMS $title Directive Specification

From GAMS documentation:
- **Syntax:** `$title text`
- **Purpose:** Sets the title for the model, displayed in GAMS output and listings
- **Scope:** Single-line directive, ignored by GAMS compiler (documentation only)
- **Common Usage:** First line of many GAMS model files
- **Related Directives:** Similar to `$ontext`/`$offtext` (comment blocks)

## Proposed Solution

### Option 1: Lexer-Level Filtering (Recommended)
Strip `$title` lines during preprocessing before parsing:

```python
def preprocess_gams_source(source: str) -> str:
    """Remove unsupported compiler directives before parsing."""
    lines = source.split('\n')
    filtered = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('$title'):
            # Replace with comment to preserve line numbers
            filtered.append(f"* [Stripped: {line}]")
        else:
            filtered.append(line)
    return '\n'.join(filtered)
```

**Pros:**
- Simple implementation (~10 lines)
- Preserves line numbers for error reporting
- Can be extended to other unsupported directives
- Zero impact on grammar complexity

**Cons:**
- Loses $title information (but we don't use it anyway)

### Option 2: Grammar Extension
Add `$title` support to Lark grammar:

```lark
compiler_directive: "$title" /[^\n]*/
```

**Pros:**
- More complete GAMS compatibility
- Could preserve title for future use

**Cons:**
- Requires grammar changes
- Need to handle in AST
- More complex for minimal benefit

## Recommended Approach

**Option 1 (Lexer-Level Filtering)** is recommended because:
1. **Simplicity:** Minimal code changes, no grammar modifications
2. **Extensibility:** Can easily add support for other unsupported directives (`$ontext`, `$offtext`, `$include`, etc.)
3. **Line Preservation:** Maintains line numbers for accurate error reporting
4. **Low Risk:** Isolated change, easy to test and verify

## Implementation Checklist

- [ ] Add `preprocess_gams_source()` function to `src/ir/parser.py`
- [ ] Call preprocessing in `parse_gams_file()` before Lark parsing
- [ ] Add unit tests for $title directive handling
- [ ] Update parser to handle other common directives: `$ontext`/`$offtext`, `$set`, `$include`
- [ ] Test with all 13 convexity fixtures
- [ ] Update documentation in `docs/parser.md`

## Test Cases

```python
def test_title_directive_removed():
    source = """$title Test Model
Variables x;
Equations eq;
eq.. x =e= 5;
"""
    model_ir = parse_gams_file(source)
    assert model_ir is not None  # Should parse successfully

def test_title_with_special_chars():
    source = "$title Model: x² + y² ≤ 10\n"
    preprocessed = preprocess_gams_source(source)
    assert '$title' not in preprocessed
```

## Acceptance Criteria

1. Parser successfully handles GAMS files with `$title` directive
2. All 13 convexity test fixtures parse without errors
3. Line numbers in error messages remain accurate
4. Zero regressions in existing tests (1149 tests continue passing)
5. Documentation updated with supported directives list

## Related Issues

- **PR #193:** Sprint 6 Day 3 convexity heuristics (worked around with 3/13 fixtures)
- **Future:** GAMSLib integration will require broader directive support
- **Related Files:**
  - `tests/fixtures/convexity/*.gms` - 10 blocked fixtures
  - `src/ir/parser.py` - Parser implementation
  - `src/ir/gams.lark` - Grammar definition

## Files Affected by This Issue

**Test Fixtures (blocked):**
1. `tests/fixtures/convexity/convex_qp.gms`
2. `tests/fixtures/convexity/convex_exponential.gms`
3. `tests/fixtures/convexity/convex_log_barrier.gms`
4. `tests/fixtures/convexity/convex_inequality.gms`
5. `tests/fixtures/convexity/nonconvex_circle.gms`
6. `tests/fixtures/convexity/nonconvex_trig_eq.gms`
7. `tests/fixtures/convexity/nonconvex_bilinear.gms`
8. `tests/fixtures/convexity/nonconvex_quotient.gms`
9. `tests/fixtures/convexity/nonconvex_odd_power.gms`
10. `tests/fixtures/convexity/mixed_convex_nonconvex.gms`

**Implementation Files (to modify):**
- `src/ir/parser.py` - Add preprocessing
- `tests/unit/ir/test_parser.py` - Add $title tests

## Priority Justification

**Medium Priority** because:
- **Not Blocking:** Workarounds exist (remove $title manually, or use fixtures without it)
- **Test Impact:** Limited to 10/13 convexity fixtures, which test functionality not critical features
- **User Impact:** Minor inconvenience for users with $title in their models
- **Future Need:** Will become more important for GAMSLib integration

**Should Address In:**
- Sprint 7 (if time available)
- Before GAMSLib benchmark work
- As part of broader directive support effort

## Estimated Effort

**2-3 hours total:**
- 1 hour: Implement `preprocess_gams_source()` function
- 1 hour: Add comprehensive tests for $title and edge cases
- 30 min: Update documentation and verify all 13 fixtures parse
- 30 min: Code review and integration

## Notes

- This issue was discovered during Sprint 6 Day 3 (Convexity Heuristics)
- Documented in PR #193 review comments (commit e71cb9a)
- Current workaround is acceptable for Sprint 6 goals
- Should be bundled with support for other common directives ($ontext, $offtext, $set)
