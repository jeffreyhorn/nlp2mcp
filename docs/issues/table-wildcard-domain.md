# Issue: Table Wildcard Domain Support

**GitHub Issue:** [#354](https://github.com/jeffreyhorn/nlp2mcp/issues/354)  
**Status:** Open  
**Priority:** MEDIUM (Stretch Goal)  
**Complexity:** HARD (5h)  
**Impact:** 3 Tier 2 models (least, like, bearing)  
**Sprint:** Sprint 13+

---

## Problem Description

GAMS allows wildcard `*` in table domain specifications to indicate that dimension names should be inferred from the table data. Our parser currently only supports explicit domain specifications, causing parse failures when encountering wildcard domains.

---

## Examples

### Pattern 1: Second Dimension Wildcard (least.gms)

**GAMS Syntax:**
```gams
Table dat(i,*) 'basic data'
       y       z
  a    1.5     2.3
  b    4.2     5.1;
```

**Meaning:** 
- First dimension: explicit set `i` (rows: a, b)
- Second dimension: inferred from column headers (y, z)

**Error:**
```
Error: Parse error at line 1, column 13: Unexpected character: '*'
  Table dat(i,*) 'basic data'
              ^
```

---

### Pattern 2: First Dimension Wildcard (like.gms)

**GAMS Syntax:**
```gams
Table data(*,i) 'systolic blood pressure data'
         x1      x2      x3
  y1     100     120     140
  y2     110     130     150;
```

**Meaning:**
- First dimension: inferred from row headers (y1, y2)
- Second dimension: explicit set `i` (columns: x1, x2, x3)

**Error:**
```
Error: Parse error at line 1, column 12: Unexpected character: '*'
  Table data(*,i) 'pressure data'
             ^
```

---

### Pattern 3: Both Dimensions Wildcard (bearing.gms)

**GAMS Syntax:**
```gams
Table oil_constants(*,*) 'various oil grades'
           visc    dens    temp
  oil1     0.5     0.9     100
  oil2     0.7     0.85    120;
```

**Meaning:**
- Both dimensions inferred from data (rows: oil1, oil2; cols: visc, dens, temp)

**Error:**
```
Error: Parse error at line 1, column 21: Unexpected character: '*'
  Table oil_constants(*,*) 'oil properties'
                      ^
```

---

## Implementation Requirements

### 1. Grammar Extension

**Current Rule:**
```lark
table_block: "Table"i ID "(" id_list ")" STRING? table_row+ SEMI
```

**Proposed Rule:**
```lark
table_block: "Table"i ID "(" table_domain_list ")" STRING? table_row+ SEMI

table_domain_list: table_domain ("," table_domain)*
table_domain: ID          -> explicit_domain
            | "*"         -> wildcard_domain
```

**Effort:** 30 minutes

---

### 2. AST Changes

**Current Structure:**
```python
@dataclass
class TableDef:
    name: str
    domains: tuple[str, ...]  # Explicit domain names only
    data: dict[tuple[str, ...], float]
```

**Proposed Structure:**
```python
@dataclass
class TableDomain:
    name: str | None  # None for wildcard
    is_wildcard: bool

@dataclass
class TableDef:
    name: str
    domains: tuple[TableDomain, ...]
    inferred_domains: tuple[str, ...] | None  # Filled after parsing table data
    data: dict[tuple[str, ...], float]
```

**Effort:** 1 hour

---

### 3. Domain Inference Logic

**Algorithm:**
```python
def infer_table_domains(table: TableDef, table_rows: list[TableRow]) -> tuple[str, ...]:
    """
    For each wildcard dimension, infer domain names from table data.
    
    Row wildcard (*,i): Extract row labels from first column
    Column wildcard (i,*): Extract column labels from header row
    Both wildcards (*,*): Extract both row and column labels
    """
    inferred = []
    
    for idx, domain in enumerate(table.domains):
        if domain.is_wildcard:
            if idx == 0:  # Row dimension
                # Extract unique values from first column of data rows
                row_labels = [row.label for row in table_rows if row.label]
                inferred.append(row_labels)
            elif idx == 1:  # Column dimension
                # Extract column headers from first row
                col_labels = table_rows[0].columns if table_rows else []
                inferred.append(col_labels)
        else:
            inferred.append(domain.name)
    
    return tuple(inferred)
```

**Effort:** 2 hours

---

### 4. Validation

**Checks:**
- All row labels consistent across data rows (for row wildcards)
- All column headers present in first row (for column wildcards)
- Inferred domains don't conflict with existing sets
- Data dimensions match inferred domain cardinality

**Effort:** 1 hour

---

### 5. Testing

**Unit Tests:**
```python
def test_table_wildcard_second_dimension():
    """Test i,* pattern (least.gms)"""
    
def test_table_wildcard_first_dimension():
    """Test *,i pattern (like.gms)"""
    
def test_table_wildcard_both_dimensions():
    """Test *,* pattern (bearing.gms)"""
    
def test_table_mixed_explicit_wildcard():
    """Test i,j,* pattern (3+ dimensions)"""
    
def test_table_wildcard_validation_errors():
    """Test inconsistent row/column labels"""
```

**Integration Tests:**
- Parse least.gms, like.gms, bearing.gms successfully
- Verify inferred domains match expected values
- Check data indexing works with inferred domains

**Effort:** 1 hour

---

## Total Effort Estimate

| Task | Effort |
|------|--------|
| Grammar extension | 0.5h |
| AST changes | 1h |
| Domain inference logic | 2h |
| Validation | 1h |
| Testing | 1h |
| **TOTAL** | **5.5h** |

---

## Risks and Challenges

### Risk 1: Ambiguous Table Syntax
If table data rows don't have consistent structure, inference may fail.

**Mitigation:** Strict validation with clear error messages.

---

### Risk 2: Multi-dimensional Tables (3+)
GAMS supports tables with >2 dimensions using different syntax.

**Mitigation:** Start with 2D tables (all current Tier 2 models). Extend later if needed.

---

### Risk 3: Wildcard + Complex Table Features
Wildcards combined with table slicing, aggregation, or other advanced features.

**Mitigation:** Implement basic wildcard support first. Document limitations.

---

## Affected Models

| Model | Lines | Pattern | Error Location | Status |
|-------|-------|---------|----------------|--------|
| least | 40 | `(i,*)` | line 16, col 13 | Blocked |
| like | 49 | `(*,i)` | line 19, col 12 | Blocked |
| bearing | 125 | `(*,*)` | line 68, col 21 | Blocked |

**Parse Rate Impact:** +30% Tier 2 (2/10 models → 5/10 models)

---

## Recommendation

**Defer to Sprint 13+** as stretch goal.

**Rationale:**
- 5h effort is at budget limit for a single blocker
- Lower priority than newline_as_separator (also 3 models but simpler)
- All 3 affected models are not critical path for MCP functionality

**Sprint 13 Plan:**
1. If newline_as_separator and other quick wins complete ahead of schedule
2. Implement table wildcard support as Day 9 stretch goal
3. Otherwise, defer to Sprint 14

---

## References

- Failing models: `tests/fixtures/tier2_candidates/{least,like,bearing}.gms`
- Grammar: `src/gams/gams_grammar.lark` (line 38)
- Parser: `src/ir/parser.py` (table parsing section)
- Blocker analysis: `docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_ANALYSIS.md` (lines 192-252)
- GAMS Documentation: Table statements with wildcard domains
