# Issue: Tuple Notation in Table Row Labels

**GitHub Issue:** [#363](https://github.com/jeffreyhorn/nlp2mcp/issues/363)  
**Status:** Open  
**Priority:** MEDIUM  
**Complexity:** MEDIUM (3-4h)  
**Impact:** 1 Tier 2 model (chenery)  
**Sprint:** Sprint 14+

---

## Problem Description

GAMS tables support tuple notation in row labels, where multiple set elements are listed in parentheses and then combined with a common suffix using dot notation.

**Syntax:** `(elem1,elem2,elem3).suffix` expands to three rows:
- `elem1.suffix`
- `elem2.suffix`  
- `elem3.suffix`

**Current Status:** Parser treats `(` at start of row label as unexpected character.

---

## Affected Models

### chenery.gms (line 57)

**GAMS Syntax:**
```gams
Table ddat(lmh,*,i) 'demand parameters'
                            light-ind  food+agr  heavy-ind  services
   (low,medium,high).ynot        100      230         220       450
   medium.p-elas                -.674     -.246      -.587     -.352
   high  .p-elas               -1        -1         -1        -1    ;
```

**Semantics:**
The row `(low,medium,high).ynot` expands to:
- `low.ynot`
- `medium.ynot`
- `high.ynot`

All three rows get the same values: `100, 230, 220, 450`.

**Error:**
```
Error: Parse error at line 57, column 1: Unexpected character: '('
   (low,medium,high).ynot        100      230         220       450
   ^
```

**Blocker:** Tuple notation `(low,medium,high).suffix` not supported in row labels.

---

## Root Cause Analysis

### Current Grammar

**Table row labels:**
```lark
table_row: table_row_label table_value*
table_row_label: ID ("." ID)*       -> dotted_label
```

**Issue:** Row labels must start with `ID`. Tuple notation `(ID,ID,...).ID` starts with `(`.

---

## Implementation Requirements

### Feature: Tuple Row Labels

**Grammar Extension:**
```lark
table_row_label: dotted_label                    -> simple_label
               | "(" id_list ")" "." ID          -> tuple_label

dotted_label: ID ("." ID)*
id_list: ID ("," ID)*
```

**Semantics:**
- `(a,b,c).suffix` → expand to 3 rows: `a.suffix`, `b.suffix`, `c.suffix`
- Each expanded row gets the same data values
- Multiple levels: `(a,b).x.y` → `a.x.y`, `b.x.y`

**Parser Implementation:**
```python
def _handle_tuple_label(self, node):
    """
    Handle tuple row label: (elem1,elem2,...).suffix
    
    Returns list of expanded label strings.
    """
    id_list_node = node.children[0]  # id_list
    suffix = _token_text(node.children[1])  # ID after dot
    
    # Extract elements from tuple
    elements = [_token_text(child) for child in id_list_node.children if isinstance(child, Token)]
    
    # Expand to multiple labels
    expanded_labels = [f"{elem}.{suffix}" for elem in elements]
    
    return expanded_labels
```

**Data Replication:**
When a row has a tuple label, the same data values are replicated for each expanded label.

Example:
```gams
(low,medium,high).ynot  100  230  220  450
```
Results in three rows:
```
low.ynot     100  230  220  450
medium.ynot  100  230  220  450
high.ynot    100  230  220  450
```

---

## Implementation Options

### Option A: Grammar + Parser Expansion (RECOMMENDED)

**Approach:** Parse tuple labels and expand them to multiple rows during table processing.

**Steps:**
1. Extend grammar to recognize `(id_list).suffix` syntax
2. Parser detects tuple labels and expands them
3. Replicate data values for each expanded row
4. Store each expanded row separately in table data

**Pros:**
- Semantically correct representation
- Preserves expansion structure
- Handles arbitrary tuple sizes

**Cons:**
- More complex parser logic
- Need to handle data replication

**Effort:** 3-4h
- Grammar: 30 min
- Parser expansion logic: 1.5h
- Data replication: 1h
- Testing: 1h

---

### Option B: Preprocessor Expansion

**Approach:** Expand tuple labels in preprocessor before parsing.

**Implementation:**
```python
def expand_tuple_row_labels(source: str) -> str:
    """
    Expand tuple row labels in tables.
    
    (a,b,c).suffix  100  200  300
    →
    a.suffix  100  200  300
    b.suffix  100  200  300
    c.suffix  100  200  300
    """
    import re
    
    # Pattern: (id,id,...).id followed by values
    pattern = r'^\s*\(([^)]+)\)\.(\w+)(.*)$'
    
    lines = source.split('\n')
    result = []
    
    for line in lines:
        match = re.match(pattern, line)
        if match:
            # Extract tuple elements, suffix, and values
            elements = [e.strip() for e in match.group(1).split(',')]
            suffix = match.group(2)
            values = match.group(3)
            
            # Expand to multiple lines
            for elem in elements:
                result.append(f"   {elem}.{suffix}{values}")
        else:
            result.append(line)
    
    return '\n'.join(result)
```

**Pros:**
- Simpler implementation
- No grammar changes needed

**Cons:**
- Loses tuple structure information
- Harder to detect preprocessing errors
- Assumes uniform indentation

**Effort:** 2h

---

## Recommendation

**Option A: Grammar + Parser Expansion** (3-4h)

**Rationale:**
1. **Semantic correctness**: Preserves tuple structure in AST
2. **Robustness**: Handles variations in formatting/indentation
3. **Moderate impact**: Unlocks chenery.gms (1 model)
4. **Clean implementation**: Proper grammar + parser approach

**Implementation Plan:**
1. Grammar extension: `tuple_label` rule (30 min)
2. Parser: Detect and expand tuple labels (1.5h)
3. Data replication logic (1h)
4. Unit tests + integration test (1h)

---

## Testing Requirements

### Unit Tests

**Basic Tuple Label:**
```gams
Set lmh / low, medium, high /;
Set i / a, b /;

Table data(lmh,i)
             a    b
(low,medium).x  1    2
high.x          3    4;
```
Expected:
- `low.x`: [1, 2]
- `medium.x`: [1, 2]
- `high.x`: [3, 4]

**Tuple with Three Elements:**
```gams
(a,b,c).suffix  100  200  300
```
Expected expansion:
- `a.suffix`: [100, 200, 300]
- `b.suffix`: [100, 200, 300]
- `c.suffix`: [100, 200, 300]

**Mixed Tuple and Regular Labels:**
```gams
Table data(i,j)
           col1  col2
(a,b).x      1     2
c.x          3     4
d.y          5     6;
```

**chenery.gms Pattern:**
```gams
Table ddat(lmh,*,i) 'demand parameters'
                            light-ind  food+agr  heavy-ind  services
   (low,medium,high).ynot        100      230         220       450
   medium.p-elas                -.674     -.246      -.587     -.352
   high.p-elas                  -1        -1         -1        -1;
```

### Integration Tests

- chenery.gms: Should parse table at line 55-60 after implementing tuple labels

---

## Expected Impact

**Parse Rate Improvement:**
- Current: 5/18 (27%)
- After fix: 6/18 (33%)
- Improvement: +1 model (chenery.gms)

**Note:** chenery.gms may have additional blockers after this table. This fix addresses the immediate blocker at line 57.

---

## Edge Cases

**Multiple Tuple Labels:**
```gams
(a,b).x   1  2
(c,d).y   3  4
```
Each tuple is independent.

**Nested Dots:**
```gams
(a,b).x.y.z  1  2
```
Suffix can be multi-level dotted identifier.

**Empty Tuple (Invalid):**
```gams
().suffix  1  2
```
Should raise parse error.

**Single Element (Valid but Unusual):**
```gams
(a).suffix  1  2
```
Equivalent to `a.suffix  1  2`.

---

## References

- GAMS Documentation: Table Statement, Set Notation
- Failing model: `tests/fixtures/tier2_candidates/chenery.gms` (line 57)
- Grammar: `src/gams/gams_grammar.lark` (table_row_label rule)
- Parser: `src/ir/parser.py` (_handle_table_block method)
- Related: Issue #356 (Tuple notation in sets) - similar expansion logic
