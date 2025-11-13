# Parser Line/Column Tracking Research

**Date:** 2025-11-12  
**Unknown:** 4.1 (High Priority)  
**Owner:** UX Team  
**Status:** ✅ RESOLVED

---

## Assumption

The GAMS parser can be enhanced to track line/column positions and include them in error messages for improved user experience.

---

## Research Questions

1. Does current parser infrastructure store line/column metadata?
2. How to propagate position info from lexer to parser to error handler?
3. Should we use existing Python parser libraries that track positions?
4. What about errors in normalized IR (after parsing) - can we still cite lines?
5. How to format error messages with position info?

---

## Investigation

### Current Parser Implementation

**Parser:** `src/ir/parser.py` uses Lark parser library

**Finding:** Lark provides built-in position tracking via the `meta` attribute on parse tree nodes.

#### Lark Meta Attribute

From Lark documentation, every parse tree node has a `meta` attribute with:
- `meta.line` - Line number (1-indexed)
- `meta.column` - Column number (0-indexed  
- `meta.start_pos` - Absolute character position in input
- `meta.end_pos` - End position
- `meta.end_line` - Ending line number
- `meta.end_column` - Ending column number

**Example:**
```python
from lark import Lark, Tree

parser = Lark(grammar, propagate_positions=True)
tree = parser.parse(source_code)

# Access position info
for node in tree.iter_subtrees():
    if hasattr(node, 'meta'):
        print(f"Line {node.meta.line}, Col {node.meta.column}")
```

### Verification Test

**Test Input:**
```gams
Variables x, y;
Equations badEq;
badEq.. x * y * z =e= 10;  # Error: z not declared
```

**Current Error (without position):**
```
Error: Undefined variable 'z' in equation 'badEq'
```

**Desired Error (with position):**
```
Error: Undefined variable 'z' in equation 'badEq'
  File: model.gms, Line 3, Column 15
  
  3 | badEq.. x * y * z =e= 10;
                      ^
  
  This variable is used but not declared.
  Fix: Add 'z' to the Variables section
  Docs: https://docs.nlp2mcp.dev/errors/E001-undefined-variable
```

---

## Decision

✅ **Use Lark's built-in `meta` attribute for position tracking**

### Implementation Strategy

1. **Enable position propagation in parser**
   ```python
   # src/ir/parser.py
   parser = Lark(
       grammar,
       propagate_positions=True,  # Enable position tracking
       maybe_placeholders=False
   )
   ```

2. **Store position metadata on IR nodes**
   ```python
   @dataclass
   class IRNode:
       name: str
       # ... other fields ...
       source_location: Optional[SourceLocation] = None
   
   @dataclass
   class SourceLocation:
       filename: str
       line: int  # 1-indexed
       column: int  # 1-indexed (convert from Lark's 0-indexed)
       end_line: int
       end_column: int
   ```

3. **Extract position during AST transformation**
   ```python
   def transform_node(tree_node):
       ir_node = IRNode(...)
       
       if hasattr(tree_node, 'meta'):
           ir_node.source_location = SourceLocation(
               filename=current_file,
               line=tree_node.meta.line,
               column=tree_node.meta.column + 1,  # Convert to 1-indexed
               end_line=tree_node.meta.end_line,
               end_column=tree_node.meta.end_column + 1
           )
       
       return ir_node
   ```

4. **Use position in error messages**
   ```python
   def format_error(error_msg: str, location: SourceLocation, source_lines: List[str]):
       line_content = source_lines[location.line - 1]
       caret = ' ' * (location.column - 1) + '^'
       
       return f"""Error: {error_msg}
     File: {location.filename}, Line {location.line}, Column {location.column}
     
     {location.line} | {line_content}
       {caret}
   """
   ```

---

## Answers to Research Questions

### Q1: Does current parser store line/column metadata?
**A:** Yes, Lark provides `meta` attribute with full position information when `propagate_positions=True` is enabled.

### Q2: How to propagate position from lexer to parser to error handler?
**A:** 
1. Lark lexer/parser automatically tracks positions
2. Store `meta` data on IR nodes during AST transformation
3. Pass `SourceLocation` to error formatter when creating error messages

### Q3: Should we use existing libraries?
**A:** Yes, Lark's built-in position tracking is sufficient. No additional libraries needed.

### Q4: Can we cite lines for errors in normalized IR?
**A:** Yes, if we store `SourceLocation` on IR nodes during transformation. This allows tracing back to original source even after normalization.

### Q5: How to format error messages with position info?
**A:** Use the structured error format from Task 6 (error_formatter.py) enhanced with:
- File/line/column header
- Source line display with caret pointer
- Suggestion and documentation link

---

## Implementation Requirements for Sprint 6

### Day 4 (Convexity CLI Integration)
When Unknown 4.1 resolution is applied:

1. **Enable position tracking**
   - Modify `src/ir/parser.py` to use `propagate_positions=True`
   - Verify no performance regression (position tracking is lightweight)

2. **Add SourceLocation to IR nodes**
   - Add `source_location: Optional[SourceLocation]` field to relevant IR node types
   - Extract `meta` during AST → IR transformation

3. **Update error formatter**
   - Enhance `src/utils/error_formatter.py` to accept `SourceLocation`
   - Add source line extraction and caret formatting
   - Test with sample errors

4. **Integration testing**
   - Test parser errors (syntax errors)
   - Test validation errors (undefined variables, type mismatches)
   - Test convexity warnings (nonlinear equality detection)

### Estimated Implementation Time: 3-4 hours on Day 4

---

## Risks and Mitigations

### Risk 1: Performance impact of position tracking
**Impact:** Low  
**Mitigation:** Lark's position tracking is lightweight (minimal overhead). Can be disabled with flag if needed.

### Risk 2: Position info lost during IR transformations
**Impact:** Medium  
**Mitigation:** Explicitly propagate `SourceLocation` through all transformation stages. Add validation to ensure critical nodes have positions.

### Risk 3: Multi-file support complexity
**Impact:** Low  
**Mitigation:** `SourceLocation` includes filename field. Support for `$include` can be added later.

---

## Test Cases

### Test 1: Undefined Variable Error
```gams
Variables x;
Equations eq1;
eq1.. x + y =e= 5;  # y not declared
```

**Expected Output:**
```
Error E001: Undefined variable 'y'
  File: test.gms, Line 3, Column 11
  
  3 | eq1.. x + y =e= 5;
                ^
  
  Fix: Add 'y' to the Variables section
  Docs: https://docs.nlp2mcp.dev/errors/E001
```

### Test 2: Syntax Error
```gams
Variables x;
Equations eq1;
eq1.. x ** =e= 5;  # Missing operand
```

**Expected Output:**
```
Error: Unexpected token '='
  File: test.gms, Line 3, Column 12
  
  3 | eq1.. x ** =e= 5;
                 ^
```

### Test 3: Convexity Warning
```gams
Variables x, y;
Equations circle;
circle.. sqr(x) + sqr(y) =e= 4;  # Nonlinear equality
```

**Expected Output:**
```
Warning W001: Nonlinear equality constraint may be nonconvex
  File: test.gms, Line 3, Column 10
  
  3 | circle.. sqr(x) + sqr(y) =e= 4;
               ^~~~~~~~~~~~~~~~~~~~~^
  
  Consider: Replace with inequality: sqr(x) + sqr(y) <= 4
  Docs: https://docs.nlp2mcp.dev/errors/W001-nonconvex-equality
```

---

## Deliverable

This research document confirms:

✅ **Lark's `meta` attribute provides all needed position information**  
✅ **Implementation strategy defined and feasible**  
✅ **Integration points identified for Day 4**  
✅ **Test cases defined for validation**  
✅ **Risks assessed and mitigated**

**Ready for Day 4 implementation:** Yes

---

## References

- Lark Parser Documentation: https://lark-parser.readthedocs.io/en/latest/
- Lark Meta Attribute: https://lark-parser.readthedocs.io/en/latest/visitors.html#tree
- Task 6 Error Formatter: `src/utils/error_formatter.py`
- KNOWN_UNKNOWNS.md: Unknown 4.1 (lines 1259-1319)
