# Issue: Advanced Table Syntax

**GitHub Issue:** [#359](https://github.com/jeffreyhorn/nlp2mcp/issues/359)  
**Status:** Open  
**Priority:** HIGH  
**Complexity:** HIGH (8-12h)  
**Impact:** 4 Tier 2 models (bearing, chem, chenery, like)  
**Sprint:** Sprint 13+

---

## Problem Description

GAMS tables support advanced syntax features that are not yet parsed:

1. **Multi-dimensional wildcards**: `Table data(*,*)` - infer dimensions from data
2. **Nested dot notation in row labels**: `low.a.subst` - 3-level hierarchical indexing
3. **Table continuation markers**: `+` at line end to extend columns
4. **Complex row/column alignment**: Sparse data with irregular structure

---

## Affected Models

### 1. bearing.gms (line 144)

**GAMS Syntax:**
```gams
Table oil_constants(*,*)
                    oil1    oil2    oil3
viscosity_40         75     100     150
viscosity_100        10      13      18
pour_point          -15     -10      -5
```

**Error:**
```
Error: Parse error at line 144, column 44: Unexpected character: '['
```

**Blocker:** Multi-dimensional wildcard `(*,*)` not supported in table domain.

---

### 2. chenery.gms (line 36)

**GAMS Syntax:**
```gams
Table pdat(lmh,*,sde,i) 'production data'
                    light-ind  food+agr  heavy-ind  services
   low.a.subst
   low.a.distr           .915      .944      2.60     .80
   low.a.effic          3.83      3.24       4.0     1.8
   low.b.subst
   low.b.distr           .276     1.034      2.60     .77
   medium.a.subst        .11       .29        .2      .05
```

**Error:**
```
Error: Parse error at line 36, column 4: Unexpected character: '.'
```

**Blocker:** Nested dot notation in row labels (`low.a.subst` = 3 levels: `low`, `a`, `subst`).

---

### 3. chem.gms (line 28)

**GAMS Syntax:**
```gams
Table io(i,j)  'input-output coefficients'
           z       x       y       w       v
    z             0.2     0.4     0.5     0.4
    x                     0.3     0.1
    y                             0.2     0.1
    w
    v
```

**Error:**
```
Error: Parse error at line 28, column 1: Unexpected character: 'N'
```

**Blocker:** Table with sparse data and complex alignment (empty cells, rows with no data).

---

### 4. like.gms (line 24)

**GAMS Syntax:**
```gams
Table data(i,j)  'extended table'
       col1  col2  col3  +
       col4  col5  col6
row1     1     2     3
       4     5     6
row2     7     8     9
       10    11    12
```

**Error:**
```
Error: Parse error at line 24, column 1: Unexpected character: '+'
```

**Blocker:** Table continuation marker `+` to extend column headers across multiple lines.

---

## Root Cause Analysis

### 1. Multi-dimensional Wildcards `(*,*)`

**Current Grammar:**
```lark
table_block: "Table"i ID "(" table_domain_list ")" STRING? table_row+ SEMI
table_domain: ID          -> explicit_domain
            | "*"         -> wildcard_domain
```

**Issue:** Only supports single wildcard `*`, not tuple wildcards `(*,*)` or `(*,*,*)`.

**Solution:** Extend grammar to parse wildcard tuples:
```lark
table_domain: ID                    -> explicit_domain
            | "*"                   -> wildcard_domain
            | "(" wildcard_tuple ")" -> wildcard_tuple_domain
wildcard_tuple: "*" ("," "*")+
```

---

### 2. Nested Dot Notation in Row Labels

**Current Grammar:**
```lark
table_row: ID numeric_values+
```

**Issue:** Row labels are parsed as single `ID`, but `low.a.subst` contains dots which break tokenization.

**Solution:** Allow dotted identifiers in table rows:
```lark
table_row: table_row_label numeric_values+
table_row_label: ID ("." ID)*
```

**Parser:** Expand dotted labels into hierarchical tuples:
- `low.a.subst` → tuple `(low, a, subst)`
- `medium.b.distr` → tuple `(medium, b, distr)`

---

### 3. Table Continuation Markers `+`

**Current Grammar:**
```lark
table_block: "Table"i ID "(" table_domain_list ")" STRING? table_row+ SEMI
```

**Issue:** Header is assumed to be single line. No support for `+` continuation.

**Solution:** Parse multi-line headers with `+` marker:
```lark
table_header: table_header_line ("+" table_header_line)*
table_header_line: ID+
```

**Preprocessor Alternative:** Normalize `+` continuation by joining lines before parsing.

---

### 4. Sparse Table Alignment

**Current Grammar:**
```lark
table_row: ID numeric_values+
numeric_values: NUMBER | "."
```

**Issue:** Empty rows (no data after row label) cause parse failures.

**Solution:** Make data optional:
```lark
table_row: ID numeric_values*
```

Allow empty cells (consecutive whitespace):
- Preprocessor: Insert placeholder `.` for missing values
- Parser: Handle variable-length rows

---

## Implementation Options

### Option A: Grammar Extensions (RECOMMENDED)

**Approach:** Extend grammar to natively support all advanced table features.

**Pros:**
- Clean separation of concerns
- Preserves semantic structure
- Future-proof for more complex tables

**Cons:**
- Requires multiple grammar changes
- Parser logic updates for dot notation expansion

**Effort:** 8-12h
- Wildcard tuples: 2h
- Nested dot notation: 4h
- Continuation markers: 2h
- Sparse alignment: 2h
- Testing: 2h

---

### Option B: Preprocessor Normalization

**Approach:** Normalize tables to simpler syntax before parsing.

**Transformations:**
- `(*,*)` → `(d1,d2)` with inferred dimension names
- `low.a.subst` → quoted string `'low.a.subst'`
- Join `+` continuation lines
- Fill empty cells with `.`

**Pros:**
- No grammar changes needed
- Faster implementation

**Cons:**
- Loses semantic information (can't distinguish tuple from quoted string)
- May break roundtrip (parse → regenerate → compare)

**Effort:** 4-6h

---

### Option C: Hybrid Approach

**Approach:** Preprocessor for simple cases, grammar for semantic features.

- Preprocessor: Handle `+` continuation, fill sparse cells
- Grammar: Parse wildcard tuples, nested dot notation

**Effort:** 6-8h

---

## Recommendation

**Option A: Grammar Extensions** (8-12h)

**Rationale:**
1. **High impact**: Unlocks 4 models (22% of Tier 2)
2. **Foundational**: Tables are core GAMS syntax used in many models
3. **Semantic preservation**: Nested dot notation represents hierarchical data structure
4. **Extensibility**: Sets foundation for more advanced table features

**Implementation Priority:**
1. Nested dot notation (chenery.gms) - 4h
2. Multi-dimensional wildcards (bearing.gms) - 2h
3. Sparse alignment (chem.gms) - 2h
4. Continuation markers (like.gms) - 2h

---

## Testing Requirements

### Unit Tests (per feature)

**Nested Dot Notation:**
```gams
Table data(i,j,k)
       col1  col2
a.b.c    1     2
a.b.d    3     4
x.y.z    5     6
```

**Wildcard Tuples:**
```gams
Table data(*,*)
     col1  col2
row1   1     2
row2   3     4
```

**Continuation Markers:**
```gams
Table data(i,j)
       col1  col2  +
       col3  col4
row1     1     2     3     4
```

**Sparse Tables:**
```gams
Table data(i,j)
       col1  col2
row1     1     2
row2
row3     .     5
```

### Integration Tests

- bearing.gms: Multi-dimensional wildcards
- chenery.gms: Nested dot notation
- chem.gms: Sparse alignment
- like.gms: Continuation markers

---

## References

- GAMS Documentation: Table Statement
- Failing models: `tests/fixtures/tier2_candidates/{bearing,chenery,chem,like}.gms`
- Current table grammar: `src/gams/gams_grammar.lark` (table_block rule)
- Table parser: `src/ir/parser.py` (_handle_table_block method)
