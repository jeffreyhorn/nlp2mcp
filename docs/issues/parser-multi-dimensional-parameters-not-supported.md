# Parser Limitation: Multi-Dimensional Parameter Data Not Supported

## Status
**Open** - Parser limitation  
**Priority**: High  
**Component**: Parser (src/ir/parser.py)  
**Discovered**: 2025-11-06 during Sprint 5 Prep Task 8

## Description

The GAMS parser does not support multi-dimensional parameter data declarations. Standard GAMS syntax allows parameters indexed by multiple sets with data specified using dotted notation (e.g., `task1.res2 5.0`), but the parser rejects this.

## Current Behavior

When parsing a GAMS file with 2D parameter data, the parser fails with:

```
Error: Invalid model - Parameter 'usage' data for multi-dimensional domains is not supported [context: expression] (line X, column Y)
```

## Expected Behavior

The parser should accept and correctly parse multi-dimensional parameter data declarations like:

```gams
Parameters
    usage(tasks, resources) / 
        task1.res1 2.0,
        task1.res2 3.0,
        task2.res1 1.5,
        task2.res2 4.0
    /
;
```

## Reproduction

### Minimal Test Case

Create a file `test_2d_param.gms`:

```gams
Sets
    i /i1, i2/
    j /j1, j2/
;

Parameters
    a(i, j) /
        i1.j1 1.0,
        i1.j2 2.0,
        i2.j1 3.0,
        i2.j2 4.0
    /
;

Variables
    x
    obj
;

Equations
    objdef
;

objdef.. obj =e= sum((i,j), a(i,j) * x);

Model test /all/;
Solve test using NLP minimizing obj;
```

Run:
```bash
nlp2mcp test_2d_param.gms -o output.gms
```

**Result**: Parser error for multi-dimensional parameter data.

### Working Workaround

**Option 1**: Use 1D parameters only

```gams
Sets
    i /i1, i2, i3/
;

Parameters
    a(i) / i1 1.0, i2 2.0, i3 3.0 /
;
```

**Option 2**: Use separate parameter assignment statements (if supported)

```gams
Parameters
    usage(tasks, resources)
;

usage('task1', 'res1') = 2.0;
usage('task1', 'res2') = 3.0;
usage('task2', 'res1') = 1.5;
usage('task2', 'res2') = 4.0;
```

**Option 3**: Use Table statements (may have similar limitations)

```gams
Table usage(tasks, resources)
           res1  res2
    task1  2.0   3.0
    task2  1.5   4.0
;
```

## Impact

**High Impact:**
- **Model Expressiveness**: Severely limits ability to represent realistic problems
- **Resource Allocation**: Cannot model multi-dimensional resource usage matrices
- **Network Flow**: Cannot represent arc-node incidence or cost matrices  
- **Production Planning**: Cannot model product-resource consumption rates
- **User Experience**: Forces unnatural model formulations

**Workaround Available**: Yes, but restructures the problem unnaturally

## Examples of Affected Problem Types

### 1. Resource Allocation
```gams
Parameters
    usage(tasks, resources) "Resource consumption per task"
;
```
**Cannot specify**: How much of each resource each task uses.

### 2. Transportation Problem
```gams
Parameters
    cost(sources, destinations) "Shipping cost"
;
```
**Cannot specify**: Transportation costs between locations.

### 3. Network Flow
```gams
Parameters
    capacity(nodes, nodes) "Arc capacity"
    cost(nodes, nodes) "Arc cost"
;
```
**Cannot specify**: Network topology and costs.

### 4. Production Planning
```gams
Parameters
    yield(products, resources) "Resource yield per product"
;
```
**Cannot specify**: How resources convert to products.

## Technical Details

### Current Parser Behavior

The parser appears to handle 1D parameter data correctly:

```gams
Parameters
    a(i) / i1 1.0, i2 2.0 /
;
```

But fails on 2D data with dotted notation:

```gams
Parameters
    a(i, j) / i1.j1 1.0, i1.j2 2.0 /
;
```

### Grammar Requirements

The grammar needs to support:

1. **Multi-level identifiers**: `identifier.identifier` (and potentially deeper nesting)
2. **Tuple syntax**: `(i1, j1)` as an alternative to dotted notation
3. **Sparse data**: Not all combinations need values (sparse matrix)

### Suggested Implementation

1. **Lexer**: Recognize dotted identifiers in parameter data context
   ```
   param_index: IDENTIFIER ("." IDENTIFIER)*
   ```

2. **Parser Rule**: 
   ```
   param_data: param_index NUMBER
             | "(" identifier_list ")" NUMBER
   ```

3. **AST Structure**: Store multi-dimensional parameter data as nested dictionaries or tuples:
   ```python
   {
       "usage": {
           ("task1", "res1"): 2.0,
           ("task1", "res2"): 3.0,
           ("task2", "res1"): 1.5,
       }
   }
   ```

4. **Normalization**: Convert dotted notation to tuple form:
   ```python
   "task1.res1" -> ("task1", "res1")
   ```

### Edge Cases to Handle

1. **Dimension Mismatch**:
   ```gams
   Parameters a(i, j) / i1 1.0 /;  # Wrong: only 1 index
   ```

2. **Invalid Index**:
   ```gams
   Parameters a(i, j) / i1.j1 1.0, i1.k1 2.0 /;  # k1 not in j
   ```

3. **Sparse vs Dense**: GAMS uses sparse representation (unspecified = 0)

4. **Higher Dimensions**: Should support 3D, 4D, etc.:
   ```gams
   Parameters a(i, j, k) / i1.j1.k1 1.0 /;
   ```

## Related Issues

- Table parsing support (may have similar multi-dimensional challenges)
- Parameter validation and domain checking

## Suggested Fix Priority

**High Priority:**
- Critical for realistic problem modeling
- Blocks many common optimization problem types
- No good workaround that preserves model structure
- Required for production use

## Testing Requirements

When implementing, add tests for:

1. **2D Parameters**:
   ```gams
   Parameters a(i, j) / i1.j1 1.0, i1.j2 2.0 /;
   ```

2. **3D Parameters**:
   ```gams
   Parameters a(i, j, k) / i1.j1.k1 1.0 /;
   ```

3. **Sparse Data**:
   ```gams
   Parameters a(i, j) / i1.j1 1.0, i3.j2 5.0 /;  # Not all combinations
   ```

4. **Mixed Notation** (if supported):
   ```gams
   Parameters a(i, j) / (i1,j1) 1.0, i2.j2 2.0 /;
   ```

5. **Error Cases**:
   - Dimension mismatch: `a(i,j) / i1 1.0 /`
   - Invalid index: `a(i,j) / i1.k1 1.0 /` where k1 not in j
   - Duplicate entries: `a(i,j) / i1.j1 1.0, i1.j1 2.0 /`

6. **Integration Tests**:
   - Resource allocation problem with usage matrix
   - Transportation problem with cost matrix
   - Network flow with capacity matrix

## Alternative Syntax Considerations

GAMS supports multiple syntaxes for multi-dimensional data:

1. **Dotted notation** (most common):
   ```gams
   a(i,j) / i1.j1 1.0, i1.j2 2.0 /
   ```

2. **Tuple notation**:
   ```gams
   a(i,j) / (i1,j1) 1.0, (i1,j2) 2.0 /
   ```

3. **Table notation**:
   ```gams
   Table a(i,j)
          j1   j2
   i1    1.0  2.0
   i2    3.0  4.0
   ;
   ```

The parser should ideally support all three, with dotted notation as the primary focus since it's most common.

## References

- **GAMS Documentation**: Data entry for multi-dimensional parameters
- **Sprint 5 Prep Task 8**: Limitation discovered when attempting to create realistic resource allocation models
- **Common Pattern**: Used in transportation, assignment, network flow, and resource allocation problems
