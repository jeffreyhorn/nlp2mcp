# Documentation Link Strategy Research

**Date:** 2025-11-12  
**Unknown:** 4.2 (Medium Priority)  
**Owner:** UX Team  
**Status:** ✅ RESOLVED

---

## Assumption

Error messages should link to relevant documentation sections to help users self-serve fixes.

---

## Research Questions

1. What documentation structure: single page or per-error pages?
2. Should links be to web docs or local docs?
3. What error categories need documentation: syntax, convexity, solver, other?
4. How to maintain doc links in code without hardcoding URLs?
5. Should we use short links (docs.nlp2mcp.dev/errors/E001)?

---

## Investigation

### Documentation Structure Options

#### Option A: Single-Page Documentation
**Approach:** One `docs/errors/README.md` with all errors, use anchor links

**Pros:**
- Simplest to maintain
- Single source of truth
- Works well in GitHub
- Fast to search (Ctrl+F)

**Cons:**
- Can become long and unwieldy
- Harder to navigate for specific errors
- No per-error SEO

**Example:**
```markdown
# Error Documentation

## E001: Undefined Variable
[Details...]

## E002: Nonlinear Equality Warning
[Details...]

## W001: Nonconvex Pattern Detected
[Details...]
```

**Link format:** `https://github.com/user/repo/docs/errors/README.md#e001-undefined-variable`

#### Option B: Per-Error Pages
**Approach:** Separate file for each error code

**Pros:**
- Well-organized
- Better SEO
- Easy to link directly
- Scalable

**Cons:**
- More files to maintain
- Need index page
- More complex

**Example:**
```
docs/errors/
  index.md
  E001-undefined-variable.md
  E002-nonlinear-equality.md
  W001-nonconvex-pattern.md
```

**Link format:** `https://docs.nlp2mcp.dev/errors/E001`

#### Option C: Hybrid Approach
**Approach:** Category pages with anchor links

**Pros:**
- Balanced organization
- Grouped by type
- Manageable file count

**Cons:**
- Medium complexity
- Need to decide categories

**Example:**
```
docs/errors/
  index.md
  syntax-errors.md       # E001-E099
  validation-errors.md   # E100-E199
  convexity-warnings.md  # W001-W099
  solver-errors.md       # E200-E299
```

---

## Decision

✅ **Sprint 6: Use Option A (Single-Page with Anchor Links)**

### Rationale

1. **Simplicity:** Fastest to implement for Sprint 6
2. **Maintainability:** Single file easier to keep up-to-date
3. **GitHub Integration:** Works perfectly in GitHub repo
4. **Deferred Complexity:** Can migrate to Option B/C in Sprint 7+ if needed
5. **Sprint 6 Scope:** Limited number of errors (≤10), single page sufficient

### Future Migration Path

- Sprint 6: Single-page (`docs/errors/README.md`)
- Sprint 7: If >20 errors, migrate to Option C (category pages)
- Sprint 8+: If >50 errors, migrate to Option B (per-error pages)

---

## Link Management Strategy

### URL Format

**Base URL:** `https://docs.nlp2mcp.dev/errors/`  
**Anchor Format:** `#{error-code}-{short-description}`

**Examples:**
- `https://docs.nlp2mcp.dev/errors/#E001-undefined-variable`
- `https://docs.nlp2mcp.dev/errors/#W001-nonconvex-equality`
- `https://docs.nlp2mcp.dev/errors/#E101-syntax-error`

### Error Code Scheme

**Format:** `{Level}{Category}{Number}`

**Levels:**
- `E` = Error (blocking, prevents conversion)
- `W` = Warning (non-blocking, user should review)
- `I` = Info (non-blocking, informational only)

**Categories:**
- `0xx` = Syntax errors (parsing failures)
- `1xx` = Validation errors (semantic issues)
- `2xx` = Solver errors (PATH/CPLEX issues)
- `3xx` = Convexity warnings
- `9xx` = Internal errors (bugs in nlp2mcp)

**Sprint 6 Error Codes:**
- `E001` - Undefined variable
- `E002` - Undefined equation
- `E003` - Type mismatch
- `E101` - Syntax error (general)
- `W301` - Nonlinear equality (potentially nonconvex)
- `W302` - Trigonometric function (potentially nonconvex)
- `W303` - Bilinear term (potentially nonconvex)
- `W304` - Division/quotient (potentially nonconvex)
- `W305` - Odd-power polynomial (potentially nonconvex)

### Link Storage in Code

**Approach:** Central error registry with metadata

**Implementation:**
```python
# src/utils/error_codes.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class ErrorInfo:
    code: str
    level: str  # "Error", "Warning", "Info"
    title: str
    doc_anchor: str
    
    def doc_url(self) -> str:
        """Generate documentation URL"""
        return f"https://docs.nlp2mcp.dev/errors/#{self.doc_anchor}"

# Error registry
ERROR_REGISTRY = {
    "E001": ErrorInfo(
        code="E001",
        level="Error",
        title="Undefined variable",
        doc_anchor="e001-undefined-variable"
    ),
    "W301": ErrorInfo(
        code="W301",
        level="Warning",
        title="Nonlinear equality may be nonconvex",
        doc_anchor="w301-nonlinear-equality"
    ),
    # ... more errors
}

def get_error_info(code: str) -> Optional[ErrorInfo]:
    """Get error metadata by code"""
    return ERROR_REGISTRY.get(code)
```

**Usage in error messages:**
```python
from src.utils.error_codes import get_error_info

def format_validation_error(var_name: str, location: SourceLocation):
    error_info = get_error_info("E001")
    
    return f"""{error_info.level} {error_info.code}: {error_info.title} '{var_name}'
  File: {location.filename}, Line {location.line}, Column {location.column}
  
  {location.line} | ...source line...
        ^
  
  Fix: Add '{var_name}' to the Variables section
  Docs: {error_info.doc_url()}
"""
```

---

## Documentation Template

### Error Documentation Structure

Each error in `docs/errors/README.md` follows this template:

```markdown
## {CODE}: {Title}

**Level:** Error | Warning | Info  
**Category:** Syntax | Validation | Convexity | Solver

### Description

[What this error means]

### Common Causes

1. [Cause 1]
2. [Cause 2]

### How to Fix

**Quick Fix:**
[Simple one-liner fix]

**Detailed Fix:**
1. [Step 1]
2. [Step 2]

### Example

**GAMS Code (Error):**
```gams
[Code that triggers error]
```

**Error Message:**
```
[Full error message]
```

**Fixed Code:**
```gams
[Corrected code]
```

### Related

- See also: [E002](#e002-undefined-equation)
- GAMS documentation: [link]

---
```

---

## Implementation Plan for Day 4

When Unknown 4.2 resolution is applied:

### Step 1: Create Error Documentation (1h)

Create `docs/errors/README.md` with Sprint 6 errors:
- E001: Undefined variable
- W301-W305: Convexity warnings (5 patterns)
- E101: General syntax error

### Step 2: Implement Error Registry (1h)

Create `src/utils/error_codes.py` with:
- `ErrorInfo` dataclass
- `ERROR_REGISTRY` dictionary
- `get_error_info()` function
- `doc_url()` method

### Step 3: Update Error Formatter (30min)

Modify `src/utils/error_formatter.py` to:
- Accept error code parameter
- Look up error info from registry
- Include documentation URL in formatted output

### Step 4: Integration Testing (30min)

Test error messages with doc links:
- Trigger E001 (undefined variable)
- Trigger W301 (nonlinear equality)
- Verify URLs are correct
- Verify URLs resolve in browser

### Estimated Implementation Time: 3 hours on Day 4

---

## Sprint 6 Error Documentation Outline

### `docs/errors/README.md`

```markdown
# nlp2mcp Error Reference

This document describes all errors and warnings you may encounter when using nlp2mcp.

## Quick Index

**Errors (Blocking):**
- [E001: Undefined Variable](#e001-undefined-variable)
- [E002: Undefined Equation](#e002-undefined-equation)
- [E101: Syntax Error](#e101-syntax-error)

**Warnings (Non-Blocking):**
- [W301: Nonlinear Equality](#w301-nonlinear-equality)
- [W302: Trigonometric Function](#w302-trigonometric-function)
- [W303: Bilinear Term](#w303-bilinear-term)
- [W304: Division/Quotient](#w304-division-quotient)
- [W305: Odd-Power Polynomial](#w305-odd-power-polynomial)

---

## E001: Undefined Variable

**Level:** Error  
**Category:** Validation

### Description

A variable is referenced in an equation but not declared in the Variables section.

### How to Fix

Add the missing variable to the Variables declaration:

```gams
Variables x, y, z;  # Add 'z' here
Equations eq1;
eq1.. x + y + z =e= 10;
```

---

## W301: Nonlinear Equality

**Level:** Warning  
**Category:** Convexity

### Description

The equation contains a nonlinear expression with equality constraint (=e=), which may define a nonconvex feasible region.

### Common Causes

1. Circle/sphere constraints: `x^2 + y^2 = 4`
2. Hyperbola constraints: `x * y = 1`
3. Exponential equalities: `exp(x) = 5`

### How to Fix

**Option 1:** Replace with inequality if feasible region allows:
```gams
# Instead of:
circle.. sqr(x) + sqr(y) =e= 4;

# Use:
circle_ub.. sqr(x) + sqr(y) =l= 4;  # If you want points inside circle
```

**Option 2:** Accept the warning if this is intentional (PATH may still solve)

**Option 3:** Use global solver (not PATH) if convexity is critical

---

[... more errors ...]
```

---

## Test Cases

### Test 1: Error with Doc Link
```python
from src.utils.error_codes import get_error_info

error_info = get_error_info("E001")
print(error_info.doc_url())
# Output: https://docs.nlp2mcp.dev/errors/#e001-undefined-variable
```

### Test 2: Warning with Doc Link
```python
from src.diagnostics.convexity import check_convexity

warnings = check_convexity(model)
for w in warnings:
    print(f"{w.code}: {w.message}")
    print(f"Docs: {w.doc_url()}")
# Output:
# W301: Nonlinear equality may be nonconvex
# Docs: https://docs.nlp2mcp.dev/errors/#w301-nonlinear-equality
```

### Test 3: Full Error Message
```
Error E001: Undefined variable 'z'
  File: model.gms, Line 3, Column 15
  
  3 | eq1.. x + y + z =e= 10;
                    ^
  
  Fix: Add 'z' to the Variables section
  Docs: https://docs.nlp2mcp.dev/errors/#e001-undefined-variable
```

---

## Deliverable

This research document confirms:

✅ **Single-page documentation chosen for Sprint 6**  
✅ **URL format and anchor scheme defined**  
✅ **Error code scheme established (E/W/I + Category + Number)**  
✅ **Link management strategy with central registry**  
✅ **Documentation template created**  
✅ **Implementation plan defined for Day 4**

**Ready for Day 4 implementation:** Yes

---

## References

- Task 6 Error Formatter: `src/utils/error_formatter.py`
- KNOWN_UNKNOWNS.md: Unknown 4.2 (lines 1320-1394)
- GitHub Markdown Anchors: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#section-links
