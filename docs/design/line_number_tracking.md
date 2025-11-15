# Line Number Tracking Design

**Created:** November 15, 2025  
**Purpose:** Enable convexity warnings and error messages with line number citations  
**Status:** Design Complete - Ready for Sprint 7 Implementation

---

## Executive Summary

This document designs a metadata tracking system to propagate source code location information (line numbers, columns, file paths) through the entire compilation pipeline: **Parser → IR → Normalization → Convexity Detection → Warning Output**.

**Key Design Decisions:**
- **Lark metadata support:** Confirmed via `tree.meta.line` and `tree.meta.column`
- **IR metadata:** Optional `SourceLocation` dataclass attached to IR nodes
- **Normalization:** Metadata preserved through transformations
- **Warning format:** `"W301 in equation 'eq' (file.gms:15:8): message"`

**Implementation Effort:** 3-4 hours (Medium priority for Sprint 7)

---

## Table of Contents

1. [Background and Motivation](#background-and-motivation)
2. [Lark Parser Metadata Support](#lark-parser-metadata-support)
3. [IR Metadata Structure Design](#ir-metadata-structure-design)
4. [Parser Metadata Extraction](#parser-metadata-extraction)
5. [Normalization Metadata Preservation](#normalization-metadata-preservation)
6. [Convexity Detection Usage](#convexity-detection-usage)
7. [Warning Formatter Updates](#warning-formatter-updates)
8. [Edge Case Handling](#edge-case-handling)
9. [Implementation Plan](#implementation-plan)
10. [Testing Strategy](#testing-strategy)
11. [Future Enhancements](#future-enhancements)

---

## Background and Motivation

### Current State (Sprint 6)

Convexity warnings lack source location information:

```
W301: Nonlinear equality constraint detected
   Equation: circle_eq
   Docs: https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors/W301.md
```

**Problem:** Users cannot easily locate the problematic equation in their source code.

### Desired State (Sprint 7)

Warnings with line number citations:

```
W301: Nonlinear equality constraint detected
   Equation: circle_eq (nonconvex_circle.gms:15:8)
   Expression: x**2 + y**2 =e= 4
   Docs: https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors/W301.md
```

**Benefits:**
- Users can jump directly to the problem line in their editor
- Better debugging experience (IDE integration potential)
- Consistent with compiler error message conventions

---

## Lark Parser Metadata Support

### Lark Metadata API

Lark automatically attaches metadata to all `Tree` nodes when parsing:

```python
from lark import Tree

tree = parser.parse(source_code)
tree.meta.line       # int: Line number (1-indexed)
tree.meta.column     # int: Column number (0-indexed)
tree.meta.end_line   # int: Ending line number
tree.meta.end_column # int: Ending column number
```

**Verification:** Lark documentation confirms this feature is available in all parser modes (Earley, LALR).

### Example: Extracting Metadata

```python
def extract_equation_location(eq_tree: Tree) -> tuple[int, int]:
    """Extract line and column from equation parse tree node."""
    if hasattr(eq_tree, 'meta'):
        return (eq_tree.meta.line, eq_tree.meta.column)
    return (None, None)
```

**Testing:** Create a simple test case to verify metadata extraction:

```python
# Test case (can be added to tests/unit/test_parser.py)
def test_lark_metadata_extraction():
    source = """
Set i /1*10/;
Equation eq;
eq.. x**2 + y**2 =e= 4;
"""
    tree = parse_source(source)
    # Find equation definition node
    eq_node = find_node(tree, "equation_def")
    assert eq_node.meta.line == 3  # "Equation eq;" on line 3
    assert eq_node.meta.column >= 0
```

**Conclusion:** ✅ Lark provides full metadata support out-of-the-box.

---

## IR Metadata Structure Design

### SourceLocation Dataclass

Add a new dataclass to `src/ir/symbols.py`:

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SourceLocation:
    """Source code location for error reporting and debugging.
    
    Attributes:
        line: Line number (1-indexed, matches editor conventions)
        column: Column number (1-indexed for user display, converted from Lark's 0-indexed)
        end_line: Optional ending line for multi-line constructs
        end_column: Optional ending column
        source_file: Path to source file (relative to project root or absolute)
    """
    line: int
    column: int
    end_line: int | None = None
    end_column: int | None = None
    source_file: Path | None = None
    
    def __str__(self) -> str:
        """Format as 'file.gms:line:column' for display."""
        file_str = self.source_file.name if self.source_file else "<unknown>"
        return f"{file_str}:{self.line}:{self.column}"
    
    @classmethod
    def from_lark_meta(cls, meta, source_file: Path | None = None) -> "SourceLocation":
        """Create SourceLocation from Lark parse tree metadata.
        
        Args:
            meta: Lark tree.meta object with line, column, end_line, end_column
            source_file: Optional path to source file
            
        Returns:
            SourceLocation with 1-indexed column (Lark uses 0-indexed)
        """
        return cls(
            line=meta.line,
            column=meta.column + 1,  # Convert to 1-indexed for user display
            end_line=meta.end_line if hasattr(meta, 'end_line') else None,
            end_column=meta.end_column + 1 if hasattr(meta, 'end_column') else None,
            source_file=source_file
        )
```

### IR Node Updates

Update IR dataclasses to include optional metadata:

```python
@dataclass
class EquationDef:
    name: str
    domain: tuple[str, ...]
    relation: Rel
    lhs_rhs: tuple
    loc: SourceLocation | None = None  # NEW: Source location metadata
```

**Design Rationale:**
- `loc` is optional (`None` for programmatically generated nodes)
- Field name `loc` is concise (vs `source_location` or `metadata`)
- Defaults to `None` to maintain backward compatibility

**All IR nodes that should track location:**
- `EquationDef` (primary use case for convexity warnings)
- `VariableDef` (for variable-related warnings)
- `ParameterDef` (for parameter warnings)
- `SetDef` (for set-related errors)
- AST expression nodes (`Binary`, `Unary`, `Call`, etc.) - optional, lower priority

---

## Parser Metadata Extraction

### Modify Parser to Extract Metadata

In `src/ir/parser.py`, update the `_TreeToModelIR` transformer:

```python
class _TreeToModelIR:
    """Transform Lark parse tree to ModelIR, preserving source locations."""
    
    def __init__(self, source_file: Path | None = None):
        self.source_file = source_file
        self.sets = {}
        self.aliases = {}
        # ... existing fields ...
    
    def _extract_location(self, tree: Tree) -> SourceLocation | None:
        """Extract source location from Lark tree node."""
        if hasattr(tree, 'meta'):
            return SourceLocation.from_lark_meta(tree.meta, self.source_file)
        return None
    
    def _process_equation_def(self, node: Tree) -> None:
        """Process equation definition, extracting location metadata."""
        # Existing equation parsing logic...
        name = _token_text(node.children[0])
        domain = _id_list(node.children[1]) if len(node.children) > 2 else ()
        # ... parse relation and expressions ...
        
        # NEW: Extract source location from equation definition node
        loc = self._extract_location(node)
        
        eq_def = EquationDef(
            name=name,
            domain=domain,
            relation=relation,
            lhs_rhs=(lhs_expr, rhs_expr),
            loc=loc  # Attach metadata
        )
        self.equations[name] = eq_def
```

### Update parse_file Function

```python
def parse_file(filepath: Path) -> ModelIR:
    """Parse a GAMS file and return ModelIR with source locations."""
    tree = _parse_file(filepath)
    transformer = _TreeToModelIR(source_file=filepath)  # Pass filepath
    transformer.transform(tree)
    return transformer.to_model_ir()
```

**Testing:**

```python
def test_parser_extracts_source_locations():
    """Verify parser attaches source locations to IR nodes."""
    source_file = Path("test.gms")
    # Create test file with equation on line 5
    model_ir = parse_file(source_file)
    
    eq = model_ir.equations["test_eq"]
    assert eq.loc is not None
    assert eq.loc.line == 5
    assert eq.loc.column > 0
    assert eq.loc.source_file == source_file
```

---

## Normalization Metadata Preservation

### Challenge

Normalization transforms IR (e.g., expanding sums, substituting parameters). We must preserve source locations through these transformations.

### Strategy: Metadata Inheritance

**Rule:** When creating a new IR node from an existing node, inherit the source location.

### Example: Sum Expansion

```python
# In src/normalization/expand.py

def expand_sum(sum_expr: Sum, parent_loc: SourceLocation | None) -> Expr:
    """Expand sum expression, preserving source location."""
    # ... expansion logic ...
    
    expanded_expr = Binary(
        op="+",
        left=term1,
        right=term2,
        loc=parent_loc  # Inherit location from sum expression
    )
    return expanded_expr
```

### Normalization of Equations

```python
def normalize_equation(eq: EquationDef) -> EquationDef:
    """Normalize equation expressions, preserving metadata."""
    normalized_lhs = normalize_expr(eq.lhs_rhs[0], parent_loc=eq.loc)
    normalized_rhs = normalize_expr(eq.lhs_rhs[1], parent_loc=eq.loc)
    
    return EquationDef(
        name=eq.name,
        domain=eq.domain,
        relation=eq.relation,
        lhs_rhs=(normalized_lhs, normalized_rhs),
        loc=eq.loc  # Preserve original location
    )
```

**Design Principle:** Source location always refers to the **original source code location**, even for derived expressions.

### Edge Case: Expressions Without Source Location

For programmatically generated expressions (e.g., slack variables, auxiliary constraints), `loc=None` is acceptable:

```python
slack_eq = EquationDef(
    name="_slack_eq",
    domain=(),
    relation=Rel.EQ,
    lhs_rhs=(slack_var, zero_expr),
    loc=None  # No source location for generated equations
)
```

**Testing:**

```python
def test_normalization_preserves_source_location():
    """Verify normalization keeps source locations intact."""
    eq = EquationDef(
        name="test",
        domain=(),
        relation=Rel.EQ,
        lhs_rhs=(sum_expr, const_expr),
        loc=SourceLocation(line=10, column=5, source_file=Path("test.gms"))
    )
    
    normalized_eq = normalize_equation(eq)
    
    assert normalized_eq.loc is not None
    assert normalized_eq.loc.line == 10
    assert normalized_eq.loc.source_file == Path("test.gms")
```

---

## Convexity Detection Usage

### Access Source Location in Convexity Checkers

In `src/diagnostics/convexity/patterns.py`:

```python
from src.ir.symbols import EquationDef, SourceLocation

def detect_nonlinear_equality(eq: EquationDef) -> list[ConvexityWarning]:
    """Detect nonlinear equality constraints."""
    warnings = []
    
    if eq.relation == Rel.EQ and is_nonlinear(eq.lhs_rhs):
        warning = ConvexityWarning(
            code="W301",
            message="Nonlinear equality constraint detected",
            equation_name=eq.name,
            equation_loc=eq.loc,  # NEW: Include source location
            suggestion="Consider reformulating as two inequalities"
        )
        warnings.append(warning)
    
    return warnings
```

### ConvexityWarning Structure

Update `src/diagnostics/convexity/__init__.py`:

```python
@dataclass
class ConvexityWarning:
    code: str  # "W301", "W302", etc.
    message: str
    equation_name: str
    equation_loc: SourceLocation | None = None  # NEW: Source location
    suggestion: str | None = None
    docs_url: str | None = None
```

**Testing:**

```python
def test_convexity_warning_includes_location():
    """Verify convexity warnings include source locations."""
    eq = create_nonlinear_eq_with_location(line=15, column=8)
    warnings = detect_nonlinear_equality(eq)
    
    assert len(warnings) == 1
    assert warnings[0].equation_loc is not None
    assert warnings[0].equation_loc.line == 15
    assert warnings[0].equation_loc.column == 8
```

---

## Warning Formatter Updates

### Current Warning Format

```python
def format_warning(warning: ConvexityWarning) -> str:
    return f"{warning.code}: {warning.message}\n" \
           f"   Equation: {warning.equation_name}\n" \
           f"   Docs: {warning.docs_url}"
```

### Updated Warning Format

```python
def format_warning(warning: ConvexityWarning) -> str:
    """Format convexity warning with optional source location."""
    # Build equation line with optional location
    eq_line = f"   Equation: {warning.equation_name}"
    if warning.equation_loc:
        eq_line += f" ({warning.equation_loc})"  # Uses SourceLocation.__str__()
    
    output = f"{warning.code}: {warning.message}\n{eq_line}\n"
    
    if warning.suggestion:
        output += f"   Suggestion: {warning.suggestion}\n"
    
    if warning.docs_url:
        output += f"   Docs: {warning.docs_url}\n"
    
    return output
```

### Example Output

```
W301: Nonlinear equality constraint detected
   Equation: circle_eq (nonconvex_circle.gms:15:8)
   Suggestion: Consider reformulating as two inequalities
   Docs: https://github.com/jeffreyhorn/nlp2mcp/blob/main/docs/errors/W301.md
```

**Testing:**

```python
def test_warning_formatter_with_location():
    """Verify warning formatter displays source locations."""
    warning = ConvexityWarning(
        code="W301",
        message="Nonlinear equality",
        equation_name="circle_eq",
        equation_loc=SourceLocation(line=15, column=8, source_file=Path("test.gms")),
        docs_url="https://example.com/W301"
    )
    
    output = format_warning(warning)
    
    assert "circle_eq (test.gms:15:8)" in output
    assert "W301" in output
```

### CLI Integration

In `src/cli.py`:

```python
def main():
    # ... existing conversion logic ...
    
    # Display warnings with source locations
    for warning in convexity_warnings:
        print(format_warning(warning), file=sys.stderr)
```

**No changes needed** - warnings automatically include locations when available.

---

## Edge Case Handling

### 1. Generated/Synthetic Equations

**Scenario:** Normalization or KKT generation creates auxiliary equations not present in source.

**Solution:** `loc=None` for generated equations. Warning formatter handles gracefully:

```python
eq_line = f"   Equation: {warning.equation_name}"
if warning.equation_loc:
    eq_line += f" ({warning.equation_loc})"
# If loc=None, just shows equation name without location
```

**Example Output:**
```
W301: Nonlinear equality constraint detected
   Equation: _generated_slack_eq
   Docs: https://example.com/W301
```

### 2. Multi-Line Equations

**Scenario:** Equation definition spans multiple lines:

```gams
eq.. x**2 + y**2
     + z**2
     =e= 10;
```

**Solution:** Use `line` (start line) and optionally `end_line`:

```python
loc = SourceLocation(line=15, column=5, end_line=17, end_column=14)
# Display: "test.gms:15:5" (start position)
```

**Rationale:** Users can jump to the start of the equation. IDEs can highlight the full range if `end_line` is provided (future enhancement).

### 3. Included Files

**Scenario:** Equation defined in an included file:

```gams
$include "equations.gms"
```

**Solution:** `source_file` field tracks the actual file:

```python
loc = SourceLocation(line=10, column=5, source_file=Path("equations.gms"))
# Display: "equations.gms:10:5"
```

**Implementation:** Parser must track current file context when processing `$include` directives.

### 4. Preprocessor Macro Expansion

**Scenario:** Equation generated from macro:

```gams
$set eqname myeq
Equation %eqname%;
%eqname%.. x =e= 5;
```

**Solution:** Line number refers to the **expanded** source line (after preprocessing):

```python
# After preprocessing: "Equation myeq; myeq.. x =e= 5;" on line 3
loc = SourceLocation(line=3, column=16, source_file=Path("test.gms"))
```

**Rationale:** Users see the preprocessed code. Future enhancement could track macro origins.

### 5. Expressions Without Source Location

**Scenario:** AST nodes created during normalization (e.g., intermediate Binary nodes).

**Solution:** Inherit parent equation's location or use `loc=None`:

```python
# Prefer inheriting from parent
normalized_expr = Binary(op="+", left=a, right=b, loc=parent_eq.loc)

# Acceptable if no parent context
normalized_expr = Binary(op="+", left=a, right=b, loc=None)
```

### 6. Equation Instances (Indexed Equations)

**Scenario:** Indexed equation `eq(i)` generates multiple instances.

**Question:** Should each instance have a different location?

**Solution:** All instances share the **same** source location (the equation definition line):

```python
# eq(i).. x(i) =e= 0; defined on line 10
# All instances eq("i1"), eq("i2"), ... have loc.line=10
```

**Rationale:** The source code has one equation definition. Instance expansion happens during normalization.

---

## Implementation Plan

### Sprint 7 Implementation (3-4 hours)

**Phase 1: IR Structure (1 hour)**
1. Add `SourceLocation` dataclass to `src/ir/symbols.py`
2. Add `loc: SourceLocation | None = None` to `EquationDef`, `VariableDef`, `ParameterDef`
3. Run `make typecheck` to verify no type errors

**Phase 2: Parser Integration (1-1.5 hours)**
1. Update `_TreeToModelIR` constructor to accept `source_file` parameter
2. Add `_extract_location()` helper method
3. Update equation/variable/parameter parsing to extract metadata
4. Update `parse_file()` to pass source file path
5. Add unit tests for metadata extraction

**Phase 3: Normalization Preservation (0.5 hour)**
1. Update `normalize_equation()` to preserve `loc` field
2. Update expression normalization to inherit parent location
3. Add unit test for metadata preservation

**Phase 4: Convexity Integration (0.5 hour)**
1. Update `ConvexityWarning` dataclass to include `equation_loc`
2. Update pattern detectors to pass `eq.loc` to warnings
3. Update warning formatter to display locations
4. Add integration test (E2E with source file)

**Phase 5: Testing & Documentation (0.5 hour)**
1. Add 5-6 unit tests covering metadata extraction, preservation, formatting
2. Add 1-2 integration tests with real GAMS files
3. Update this design doc with any implementation notes

### Testing Checklist

- [ ] `test_lark_metadata_extraction()` - Verify Lark provides line/column
- [ ] `test_parser_extracts_source_locations()` - Verify parser attaches metadata
- [ ] `test_normalization_preserves_source_location()` - Verify metadata survives normalization
- [ ] `test_convexity_warning_includes_location()` - Verify warnings have locations
- [ ] `test_warning_formatter_with_location()` - Verify formatter displays locations
- [ ] `test_warning_formatter_without_location()` - Verify graceful handling of `loc=None`
- [ ] `test_e2e_warning_with_line_number()` - End-to-end test with real file

### Quality Checks

```bash
make typecheck  # Verify type annotations
make lint       # Verify code style
make format     # Auto-format code
make test       # Run all tests (including new tests)
```

**All must pass before committing.**

---

## Testing Strategy

### Unit Tests

**File:** `tests/unit/test_line_tracking.py` (new file)

```python
import pytest
from pathlib import Path
from src.ir.symbols import SourceLocation, EquationDef, Rel
from src.ir.parser import parse_source, parse_file
from src.diagnostics.convexity import detect_nonlinear_equality, format_warning

def test_source_location_creation():
    """Test SourceLocation dataclass."""
    loc = SourceLocation(line=10, column=5, source_file=Path("test.gms"))
    assert loc.line == 10
    assert loc.column == 5
    assert str(loc) == "test.gms:10:5"

def test_source_location_from_lark_meta():
    """Test converting Lark metadata to SourceLocation."""
    # Mock Lark meta object
    class MockMeta:
        line = 10
        column = 4  # 0-indexed
        end_line = 10
        end_column = 20
    
    loc = SourceLocation.from_lark_meta(MockMeta(), Path("test.gms"))
    assert loc.line == 10
    assert loc.column == 5  # Converted to 1-indexed
    assert loc.end_line == 10
    assert loc.end_column == 21

def test_parser_extracts_metadata():
    """Test parser extracts source locations from equations."""
    source = """
Set i /1*10/;
Variable x;
Equation test_eq;
test_eq.. x**2 =e= 4;
"""
    # Create temp file
    test_file = Path("/tmp/test_metadata.gms")
    test_file.write_text(source)
    
    model_ir = parse_file(test_file)
    eq = model_ir.equations.get("test_eq")
    
    assert eq is not None
    assert eq.loc is not None
    assert eq.loc.line == 5  # "test_eq.. x**2 =e= 4;" on line 5
    assert eq.loc.source_file == test_file
    
    test_file.unlink()  # Clean up

def test_warning_formatter_with_location():
    """Test warning formatter displays source locations."""
    from src.diagnostics.convexity import ConvexityWarning, format_warning
    
    warning = ConvexityWarning(
        code="W301",
        message="Nonlinear equality constraint detected",
        equation_name="circle_eq",
        equation_loc=SourceLocation(line=15, column=8, source_file=Path("test.gms")),
        docs_url="https://example.com/W301"
    )
    
    output = format_warning(warning)
    
    assert "W301" in output
    assert "circle_eq (test.gms:15:8)" in output
    assert "https://example.com/W301" in output

def test_warning_formatter_without_location():
    """Test warning formatter handles missing source location gracefully."""
    from src.diagnostics.convexity import ConvexityWarning, format_warning
    
    warning = ConvexityWarning(
        code="W301",
        message="Nonlinear equality constraint detected",
        equation_name="generated_eq",
        equation_loc=None,  # No location
        docs_url="https://example.com/W301"
    )
    
    output = format_warning(warning)
    
    assert "W301" in output
    assert "generated_eq" in output
    assert "generated_eq (" not in output  # No location shown
```

### Integration Tests

**File:** `tests/integration/test_convexity_line_numbers.py` (new file)

```python
import pytest
from pathlib import Path
from src.cli import convert_gams_to_mcp
from src.diagnostics.convexity import get_convexity_warnings

def test_e2e_convexity_warning_with_line_number(tmp_path):
    """End-to-end test: convexity warning includes line number."""
    # Create test GAMS file
    test_file = tmp_path / "nonconvex.gms"
    test_file.write_text("""
Set i /1*10/;
Variable x, y;
Equation circle_eq;
circle_eq.. x**2 + y**2 =e= 4;
Solve mymodel using nlp;
""")
    
    # Convert and get warnings
    model_ir, warnings = convert_gams_to_mcp(test_file)
    
    # Verify warning includes line number
    assert len(warnings) > 0
    w = warnings[0]
    assert w.code == "W301"
    assert w.equation_name == "circle_eq"
    assert w.equation_loc is not None
    assert w.equation_loc.line == 5  # "circle_eq.. x**2 + y**2 =e= 4;" on line 5
    assert w.equation_loc.source_file == test_file
```

---

## Future Enhancements

### 1. Expression-Level Source Locations

**Current:** Only equations track source locations.

**Future:** Track source locations for individual expressions (Binary, Unary, Call nodes).

**Benefit:** Highlight the exact subexpression causing a warning:

```
W302: Product of variables detected (bilinear term)
   Equation: bilinear_eq (test.gms:10:15)
   Expression: x * y (at column 20-25)
```

**Effort:** 2-3 hours (requires updating all AST node dataclasses).

### 2. Source Range Highlighting

**Current:** Display single line:column position.

**Future:** Display full range with `end_line` and `end_column`:

```
W301: Nonlinear equality constraint detected
   Equation: circle_eq (test.gms:10:5-12:20)
   Expression: x**2 + y**2
               + z**2
               =e= 4
```

**Benefit:** IDE integration (highlight full construct).

**Effort:** 1 hour (update formatter to use `end_line`/`end_column`).

### 3. Macro Origin Tracking

**Current:** Line numbers refer to post-preprocessing source.

**Future:** Track original macro definition location:

```
W301: Nonlinear equality constraint detected
   Equation: myeq (test.gms:15:8)
   Expanded from: %eqname% (test.gms:5:10)
```

**Benefit:** Better debugging of macro-heavy code.

**Effort:** 4-6 hours (requires preprocessor to track macro expansions).

### 4. Interactive Error Navigation

**Current:** Text-based warning output.

**Future:** IDE integration (VS Code extension, language server protocol).

**Benefit:** Click on warning to jump to source line.

**Effort:** 10+ hours (requires IDE extension development).

---

## Conclusion

This design provides a **complete, minimal, and implementable** solution for line number tracking in convexity warnings.

**Key Achievements:**
- ✅ Lark metadata support confirmed (tree.meta.line, tree.meta.column)
- ✅ IR metadata structure designed (SourceLocation dataclass)
- ✅ Normalization preservation strategy defined (inherit parent location)
- ✅ Warning formatter updated (display "file.gms:line:column")
- ✅ Edge cases handled (generated nodes, multi-line, includes)
- ✅ Implementation plan created (3-4 hours, Sprint 7 ready)

**Implementation Effort:** 3-4 hours (Medium priority for Sprint 7)

**Testing:** 7 unit tests + 1 integration test

**Backward Compatibility:** 100% (loc=None for existing code)

**Next Steps:** Implement in Sprint 7 following the 5-phase plan above.
