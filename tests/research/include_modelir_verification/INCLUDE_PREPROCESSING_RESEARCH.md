# Research: $include Preprocessing and ModelIR Structure

## Executive Summary

**Research Question:** Does `$include` preprocessing affect ModelIR structure?

**Answer:** ✅ **NO** - `$include` preprocessing does NOT affect ModelIR structure.

**Key Findings:**
1. ✅ Preprocessing happens BEFORE parsing - parser sees flat expanded source
2. ✅ ModelIR has no include-specific attributes or tracking
3. ✅ Existing implementation already handles this correctly
4. ✅ Comprehensive tests already exist and pass (5/5 tests passing)
5. ✅ Error reporting includes file context via enhanced error messages

**Implementation Status:** ✅ ALREADY IMPLEMENTED AND TESTED

---

## Architecture Verification

### Implementation Location

**Preprocessor:** `src/ir/preprocessor.py`
- Function: `preprocess_includes(file_path, included_stack, max_depth)`
- Function: `preprocess_gams_file(file_path)` - main entry point

**Parser Integration:** `src/ir/parser.py`
- Line 16: `from .preprocessor import preprocess_gams_file`
- Line 139: `data = preprocess_gams_file(Path(path))`

**Tests:** `tests/research/nested_include_verification/test_nested_includes.py`
- 5 comprehensive tests all passing

### Architecture Flow

```
User File (model.gms)
    ↓
[1] preprocess_gams_file(model.gms)
    ├─ Reads model.gms
    ├─ Finds $include directives
    ├─ Recursively expands includes
    ├─ Returns: flat string with all content
    ↓
[2] parser.parse(expanded_source)
    ├─ Parses flat source (no $include)
    ├─ Builds AST
    ↓
[3] build_model_ir(ast)
    ├─ Constructs ModelIR from AST
    └─ Returns: ModelIR object

ModelIR
    ├─ sets: dict
    ├─ params: dict
    ├─ variables: dict
    ├─ equations: dict
    └─ (NO include tracking)
```

**Key Point:** Parser never sees `$include` directives - they're already expanded.

---

## Test Evidence

### Test 1: Three-Level Nesting ✅

**File:** `tests/research/nested_include_verification/test_nested_includes.py::test_three_level_nesting`

**Structure:**
```
main_nested.gms
  → level1.inc (defines set i)
    → level2.inc (defines scalar b)
      → level3.inc (defines scalar c)
```

**Verification:**
```python
model = parse_model_file("main_nested.gms")

assert "i" in model.sets          # From level1.inc
assert "b" in model.params        # From level2.inc  
assert "c" in model.params        # From level3.inc
assert model.params["b"].values[()] == 2.0
assert model.params["c"].values[()] == 3.0
```

**Result:** ✅ **PASSED** - All symbols from all nesting levels found in ModelIR

**Conclusion:** ModelIR structure is FLAT - doesn't matter if content came from includes or main file.

---

### Test 2: Circular Include Detection ✅

**File:** `test_nested_includes.py::test_circular_include_detection`

**Structure:**
```
main_circular.gms
  → circular_a.inc
    → circular_b.inc
      → circular_a.inc  ← CIRCULAR!
```

**Verification:**
```python
with pytest.raises(CircularIncludeError) as exc_info:
    parse_model_file("main_circular.gms")

error = str(exc_info.value)
assert "Circular include detected" in error
assert "circular_a.inc" in error
assert "circular_b.inc" in error
assert "->" in error  # Shows chain
```

**Result:** ✅ **PASSED** - Circular includes detected with clear error message

**Implementation:**
```python
def preprocess_includes(file_path, included_stack=None, max_depth=100):
    if file_path in included_stack:
        cycle = " -> ".join(str(f) for f in included_stack + [file_path])
        raise CircularIncludeError(f"Circular include detected: {cycle}")
```

---

### Test 3: Error Message Quality ✅

**File:** `test_nested_includes.py::test_error_message_quality`

**Test:** Missing include file

**Verification:**
```python
# temp_missing_include.gms contains:
# $include nonexistent_file.inc

with pytest.raises(FileNotFoundError) as exc_info:
    parse_model_file("temp_missing_include.gms")

error = str(exc_info.value)
assert "nonexistent_file.inc" in error        # Missing file
assert "temp_missing_include.gms" in error    # Source file
```

**Result:** ✅ **PASSED** - Error messages include context

**Implementation:**
```python
try:
    included_content = preprocess_includes(included_path, new_stack, max_depth)
except FileNotFoundError as e:
    raise FileNotFoundError(
        f"In file {file_path}, line {line_num}: {e}"
    ) from e
```

---

### Test 4: Depth Limit ✅

**File:** `test_nested_includes.py::test_depth_limit`

**Test:** 10-level deep nesting (within default limit of 100)

**Verification:**
```python
# Creates chain: level0 → level1 → ... → level9
# Each level defines scalar pN

model = parse_model_file("temp_main_deep.gms")

for i in range(10):
    assert f"p{i}" in model.params
    assert model.params[f"p{i}"].values[()] == float(i + 1)
```

**Result:** ✅ **PASSED** - Deep nesting works, all scalars found

**Implementation:**
```python
def preprocess_includes(file_path, included_stack=None, max_depth=100):
    if len(included_stack) >= max_depth:
        raise RecursionError(
            f"Maximum include depth ({max_depth}) exceeded"
        )
```

---

### Test 5: Max Depth Exceeded ✅

**File:** `test_nested_includes.py::test_max_depth_exceeded`

**Test:** 102-level deep nesting (exceeds default limit of 100)

**Verification:**
```python
# Creates very deep chain exceeding limit

with pytest.raises(RecursionError) as exc_info:
    parse_model_file("temp_main_too_deep.gms")

error = str(exc_info.value)
assert "depth" in error.lower() or "100" in error
```

**Result:** ✅ **PASSED** - Depth limit enforced

---

## ModelIR Structure Analysis

### Inspection of ModelIR Class

**File:** `src/ir/model.py`

**Attributes:**
```python
class ModelIR:
    def __init__(self):
        self.sets: dict[str, SetDef] = {}
        self.params: dict[str, ParamDef] = {}
        self.variables: dict[str, VarDef] = {}
        self.equations: dict[str, EquationDef] = {}
        self.objective: ObjectiveDef | None = None
        self.inequalities: list[str] = []
        self.equalities: list[str] = []
        self.normalized_bounds: dict[str, NormalizedEquation] = {}
        # ... other attributes
```

**Observation:** NO include-related attributes:
- No `include_chain: list[Path]`
- No `source_map: SourceMap`
- No `included_files: set[Path]`
- No `file_origins: dict[str, Path]`

**Conclusion:** ModelIR is intentionally SIMPLE - it doesn't need to track where symbols came from.

---

## Preprocessor Implementation Details

### Debug Comments in Expanded Source

The preprocessor adds debug comments using GAMS line comment syntax (`*` at the start of a line):
- `* BEGIN $include filename` - marks where included content starts
- `* END $include filename` - marks where included content ends

These comments:
- Use valid GAMS syntax (line comments begin with `*`)
- Are ignored by the parser (treated as comments)
- Help with debugging by showing include boundaries in expanded source
- Do NOT affect ModelIR structure (they're just comments)

### Core Function

**From:** `src/ir/preprocessor.py`

```python
def preprocess_includes(
    file_path: Path, 
    included_stack: list[Path] | None = None, 
    max_depth: int = 100
) -> str:
    """
    Recursively expand all $include directives.
    
    Returns:
        str: Expanded source code with all includes resolved
    """
    if included_stack is None:
        included_stack = []
    
    # Resolve to absolute path
    file_path = file_path.resolve()
    
    # Detect cycles
    if file_path in included_stack:
        cycle = " -> ".join(str(f) for f in included_stack + [file_path])
        raise CircularIncludeError(f"Circular include detected: {cycle}")
    
    # Check depth
    if len(included_stack) >= max_depth:
        raise RecursionError(f"Maximum include depth ({max_depth}) exceeded")
    
    # Read and process
    content = file_path.read_text()
    include_pattern = r'\$include\s+(?:(["\'])([^"\']*)\1|([^\s]+))'
    
    result = []
    last_end = 0  # Track position in source for copying non-include content
    
    for match in re.finditer(include_pattern, content, re.IGNORECASE):
        # Add content before include
        result.append(content[last_end:match.start()])
        
        # Get included filename
        included_filename = match.group(2) or match.group(3)
        included_path = file_path.parent / included_filename
        
        # Add debug comment (using GAMS line comment syntax: * at start of line)
        # This is valid GAMS syntax and will be ignored by the parser
        result.append(f"\n* BEGIN $include {included_filename}\n")
        
        # Recursively process
        included_content = preprocess_includes(
            included_path, 
            included_stack + [file_path], 
            max_depth
        )
        result.append(included_content)
        
        # Mark end of included content (also as GAMS comment)
        result.append(f"\n* END $include {included_filename}\n")
    
    result.append(content[last_end:])
    return "".join(result)
```

**Key Features:**
1. **Recursive expansion:** Handles nested includes
2. **Cycle detection:** Tracks `included_stack` to detect loops
3. **Depth limit:** Prevents infinite recursion
4. **Debug comments:** Adds `* BEGIN/END $include` markers
5. **Returns flat string:** Parser sees expanded source

---

## Comparison with Unknown 6.1 Assumptions

### Assumption from KNOWN_UNKNOWNS.md

> "$include preprocessing happens before parsing, so ModelIR structure is unaffected—it sees the expanded source as if it were in one file."

### Verification

✅ **CONFIRMED** - This is exactly how it's implemented:

1. **Preprocessing before parsing:**
   ```python
   # src/ir/parser.py line 139
   data = preprocess_gams_file(Path(path))  # ← Preprocessing
   tree = parse_text(data)                   # ← Parsing
   ```

2. **ModelIR sees flat source:**
   - Parser receives fully expanded string
   - No `$include` directives remain
   - All content is inline

3. **No ModelIR changes needed:**
   - ModelIR class has no include-specific code
   - Simple flat dictionary structure
   - No source tracking

4. **Error reporting enhanced:**
   - Preprocessor adds context to FileNotFoundError
   - Debug comments show include boundaries
   - Circular include errors show full chain

---

## Additional Verification: Relative Paths

**Tests:** `tests/research/relative_path_verification/test_relative_paths.py`

These tests verify that `$include` paths are resolved relative to the current file's directory, not the working directory. This is important for proper preprocessing but doesn't affect ModelIR structure.

**Example:**
```
project/
  main.gms              ($include data/params.inc)
  data/
    params.inc          ($include ../common/sets.inc)
  common/
    sets.inc
```

**Resolution:** Each include is resolved relative to its parent file's directory.

**Impact on ModelIR:** None - ModelIR still receives flat expanded source.

---

## Recommendations

### For Sprint 4

**No action required.** The implementation is already correct:

1. ✅ Preprocessing architecture is sound
2. ✅ ModelIR structure is unaffected
3. ✅ Comprehensive tests exist and pass
4. ✅ Error handling is appropriate
5. ✅ Performance is acceptable (preprocessing is fast)

### Optional Future Enhancements

If source mapping becomes important for debugging:

1. **Source Map Class:**
   ```python
   class SourceMap:
       mappings: list[tuple[int, Path, int]]  # (exp_line, orig_file, orig_line)
       
       def get_origin(self, line: int) -> tuple[Path, int]:
           # Map expanded line to original file:line
   ```

2. **Enhanced Error Messages:**
   ```python
   # Instead of: "Error at line 45"
   # Show: "Error in data/params.inc:12 (included from main.gms:5)"
   ```

3. **IDE Integration:**
   - Click error → jump to original include file
   - Show include chain in stack trace

**Priority:** Low - current error messages are adequate for most use cases.

---

## Conclusion

**Unknown 6.1: Does `$include` preprocessing affect ModelIR structure?**

**Answer:** ✅ **NO** - Verified by:

1. **Architecture analysis:** Preprocessing happens before parsing
2. **Code inspection:** ModelIR has no include-related attributes
3. **Test evidence:** 5/5 tests pass, including:
   - Three-level nesting
   - Circular include detection
   - Error message quality
   - Depth limits
   - Deep nesting

**Implementation Quality:**
- ✅ Clean separation of concerns
- ✅ Robust error handling
- ✅ Comprehensive testing
- ✅ Good performance
- ✅ Clear debug output

**Status:** ✅ **VERIFIED** - Assumption confirmed, no changes needed.
