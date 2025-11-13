# Min/Max Flattening Feature

**Status:** Production (Sprint 6 Day 2)  
**Module:** `src/ad/minmax_flattener.py`  
**Integration:** Automatic in `src/ad/ad_core.py`

---

## Overview

The min/max flattening transformation automatically simplifies nested min/max operations in GAMS models before they are converted to Mixed Complementarity Problems (MCP). This optimization reduces the number of auxiliary variables and complementarity conditions, improving both model clarity and solver performance.

## Problem

GAMS models often contain nested min/max operations:

```
min(min(x, y), z)
max(max(a, b), c)
min(x, max(y, min(z, w)))
```

Without flattening, each nested min/max creates additional auxiliary variables and complementarity conditions in the MCP reformulation, increasing problem complexity unnecessarily.

## Solution

Since min and max are associative operations, nested structures of the same type can be safely flattened:

```
min(min(x, y), z)  →  min(x, y, z)
max(max(a, b), c)  →  max(a, b, c)
```

**Important:** Mixed nesting (e.g., `min(max(x, y), z)`) is **NOT** flattened, as this would change the semantics.

## Mathematical Foundation

See `docs/research/nested_minmax_semantics.md` for complete mathematical proofs. Key results:

**Theorem 1 (Associativity):** For any real numbers x, y, z:
- min(min(x, y), z) = min(x, y, z)
- max(max(x, y), z) = max(x, y, z)

**Theorem 2 (N-ary Generalization):** Extends to arbitrary depth by induction.

**Theorem 3 (Subdifferential Equivalence):** The subdifferentials of nested and flattened forms are identical at all points, ensuring equivalent KKT conditions.

## Usage

### Automatic Integration

Flattening is automatically applied when calling `differentiate()`:

```python
from src.ad import differentiate
from src.ir.ast import Call, VarRef

# Expression with nested min
expr = Call("min", (
    Call("min", (VarRef("x"), VarRef("y"))),
    VarRef("z")
))

# Automatically flattened before differentiation
derivative = differentiate(expr, "x")
# Flattened form used: min(x, y, z)
```

### Direct API

For manual flattening of AST expressions:

```python
from src.ad.minmax_flattener import flatten_all_minmax
from src.ir.ast import Call, VarRef

nested = Call("min", (
    Call("min", (VarRef("x"), VarRef("y"))),
    VarRef("z")
))

flattened = flatten_all_minmax(nested)
# Result: Call("min", (VarRef("x"), VarRef("y"), VarRef("z")))
```

### Detection API

To analyze nesting patterns without transformation:

```python
from src.ad.minmax_flattener import detect_minmax_nesting, NestingType

expr = Call("min", (Call("min", (VarRef("x"), VarRef("y"))), VarRef("z")))

nesting_type = detect_minmax_nesting(expr)
# Returns: NestingType.SAME_TYPE_NESTING

# For detailed analysis:
from src.ad.minmax_flattener import analyze_nesting

info = analyze_nesting(expr)
# info.nesting_type: SAME_TYPE_NESTING
# info.outer_func: "min"
# info.depth: 2
# info.total_args: 3
```

## Examples

### Example 1: Simple Nested Min

**Before:**
```gams
z =E= min(min(x, y), w);
```

**After Flattening:**
```gams
z =E= min(x, y, w);
```

**MCP Impact:**
- Before: 2 min operations → 2 auxiliary variables, 4 complementarity conditions
- After: 1 min operation → 1 auxiliary variable, 3 complementarity conditions
- **Reduction:** 1 fewer variable, 1 fewer condition

### Example 2: Deep Nesting

**Before:**
```gams
result =E= min(min(min(a, b), c), d);
```

**After Flattening:**
```gams
result =E= min(a, b, c, d);
```

**MCP Impact:**
- Before: 3 min operations → 3 auxiliary variables, 6 complementarity conditions
- After: 1 min operation → 1 auxiliary variable, 4 complementarity conditions
- **Reduction:** 2 fewer variables, 2 fewer conditions

### Example 3: Mixed Nesting (NOT Flattened)

**Before:**
```gams
z =E= min(max(x, y), w);
```

**After Flattening:**
```gams
z =E= min(max(x, y), w);  * UNCHANGED
```

**Rationale:** This is semantically different from any flat form. The inner max must be evaluated first, and only then can the outer min be computed.

### Example 4: Complex Expression

**Before:**
```gams
obj.. total =E= cost + 10 * min(min(x, y), z);
```

**After Flattening:**
```gams
obj.. total =E= cost + 10 * min(x, y, z);
```

**Benefits:**
- Simpler AST structure
- Fewer variables in MCP reformulation
- Clearer intent for readers

## Nesting Types

The flattener classifies nesting patterns into three types:

### 1. NO_NESTING
Already flat or not a min/max operation:
```
min(x, y, z)      # Already flat
exp(x)            # Not min/max
5.0               # Constant
```

### 2. SAME_TYPE_NESTING
Safe to flatten:
```
min(min(x, y), z)           # Nested min in min
max(max(a, b), c)           # Nested max in max
min(x, min(y, z))           # Nested min anywhere
max(max(a, b), max(c, d))   # Multiple nested max
```

### 3. MIXED_NESTING
NOT safe to flatten:
```
min(max(x, y), z)   # max inside min
max(min(a, b), c)   # min inside max
```

## Performance Characteristics

### Time Complexity
- Detection: O(n) where n = number of nodes in expression
- Flattening: O(n) single-pass post-order traversal
- Overall: Linear in expression size

### Space Complexity
- O(n) for new AST construction
- Original AST remains unchanged (functional approach)

### Benchmark Results

From Sprint 6 Day 1 PATH solver comparison (`docs/demos/sprint6_day1_path_comparison.md`):

**Problem:** 3-variable quadratic with nested min constraint

| Metric | Nested Form | Flattened Form | Improvement |
|--------|-------------|----------------|-------------|
| Variables | 6 | 5 | 16.7% fewer |
| Equations | 8 | 6 | 25.0% fewer |
| Solution | (0, 0, 10) | (0, 0, 10) | Identical |
| Objective | 0.000000 | 0.000000 | Identical |

## Testing

### Unit Tests
36 comprehensive tests in `tests/unit/ad/test_minmax_flattening.py`:
- Detection of all nesting types
- Nesting analysis (depth, argument count)
- Flattening transformations
- Edge cases (deep nesting, mixed types, single args)
- Integration scenarios

### Run Tests
```bash
pytest tests/unit/ad/test_minmax_flattening.py -v
```

### Regression Tests
Full test suite verifies no regressions:
```bash
pytest tests/
```

## Implementation Details

### Algorithm

1. **Traverse AST** using visitor pattern (post-order)
2. **Detect** Call nodes with func="min" or func="max"
3. **Classify** nesting type:
   - Check if any arguments are Call nodes with same func
   - Determine SAME_TYPE_NESTING or MIXED_NESTING
4. **Flatten** if SAME_TYPE_NESTING:
   - Recursively collect all leaf arguments
   - Replace with single Call node containing flattened list
5. **Preserve** if MIXED_NESTING or NO_NESTING

### Key Functions

**`flatten_all_minmax(expr)`**
- Main entry point
- Flattens all flattenable min/max in expression
- Returns: New AST with flattened operations

**`detect_minmax_nesting(expr)`**
- Classifies nesting pattern
- Returns: NestingType enum

**`analyze_nesting(expr)`**
- Detailed nesting analysis
- Returns: NestingInfo with depth, arg count, etc.

### AST Visitor

The `MinMaxFlattener` class implements the visitor pattern:
- Handles all expression types: Const, VarRef, ParamRef, Unary, Binary, Call, Sum
- Post-order traversal: children transformed before parents
- Functional: original AST unchanged, new AST returned

## Related Documentation

- **Mathematical Proofs:** `docs/research/nested_minmax_semantics.md`
- **Testing Strategy:** `docs/research/nested_minmax_testing.md`
- **PATH Validation:** `docs/demos/sprint6_day1_path_comparison.md`
- **MCP Reformulation:** `src/kkt/reformulation.py`

## Future Enhancements

Potential improvements for future sprints:

1. **Count Optimization:** Pre-compute argument counts to avoid multiple traversals
2. **Pattern Caching:** Cache nesting analysis for repeated expressions
3. **Partial Flattening:** Flatten only some branches if beneficial
4. **Rewrite Rules:** Extend to other associative operations (e.g., addition, multiplication)

## FAQ

**Q: Why not flatten min(max(x,y),z)?**  
A: Because min(max(x,y),z) ≠ any flat form. The max must be evaluated first, then the min. Flattening would change semantics.

**Q: Does flattening affect numerical results?**  
A: No. Mathematical proofs and PATH solver validation confirm identical solutions. See `docs/research/nested_minmax_semantics.md`.

**Q: Is flattening always beneficial?**  
A: Yes for SAME_TYPE_NESTING. It strictly reduces auxiliary variables and complementarity conditions with no downsides.

**Q: Can I disable flattening?**  
A: Not currently. Flattening is always-on because it's semantically safe and always beneficial. If needed for debugging, you can modify `src/ad/ad_core.py` to comment out the flattening line.

**Q: What about indexed min/max?**  
A: Indexed variables within min/max are preserved correctly. The flattening only affects the min/max nesting structure, not the variable indexing.

## Changelog

### Sprint 6 Day 2 (Production Release)
- Production implementation with full test coverage
- Integration with AD system via `differentiate()`
- 36 unit tests covering all scenarios
- User documentation (this file)

### Sprint 6 Day 1 (Research & POC)
- Mathematical proofs of semantic safety
- POC implementation demonstrating algorithm
- PATH solver validation
- Testing strategy definition
