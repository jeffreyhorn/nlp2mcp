# Set Range Syntax Fixtures

This directory contains test fixtures for GAMS set range syntax and set declarations.

## Purpose

These fixtures test the parser's ability to handle various GAMS set declaration syntaxes including:
- Numeric ranges: `Set i / 1*6 /`
- Alpha ranges: `Set s / s1*s10 /`
- Prefix ranges: `Set plants / p1*p100 /`
- Macro ranges: `Set i / 1*%n% /`
- Explicit elements: `Set i / i1, i2, i3 /`
- Indexed sets (subsets): `Set active(i)`
- Multi-dimensional sets: `Set pairs(i,j)`
- Tuple notation: `Set ij(i,j) / i1.j1, i2.j1 /`

## Fixtures

### Created (8/8)

1. **range_numeric.gms** - Numeric range notation
   - Tests: `Set i / 1*6 /`
   - Expands to: 1, 2, 3, 4, 5, 6
   
2. **range_alpha.gms** - Alphabetic prefix with numeric range
   - Tests: `Set s / s1*s10 /`
   - Expands to: s1, s2, ..., s10
   
3. **range_prefix.gms** - Custom prefix range
   - Tests: `Set plants / p1*p100 /`
   - Expands to: p1, p2, ..., p100
   
4. **range_with_macro.gms** - Range with macro expansion
   - Tests: `Set i / 1*%n% /` where `%n%` = 8
   - Expands to: 1, 2, ..., 8
   
5. **explicit_elements.gms** - Explicit comma-separated elements
   - Tests: `Set i / i1, i2, i3 /`
   - No expansion, explicit list
   
6. **indexed_set.gms** - Indexed set (subset)
   - Tests: `Set active(i) / 1, 3, 5 /`
   - Subset of parent set i
   
7. **multi_dim_set.gms** - Multi-dimensional set (2D)
   - Tests: `Set pairs(i,j) / 1.1, 2.1, 3.2 /`
   - 2D set with tuple elements
   
8. **set_tuple.gms** - Set tuple notation
   - Tests: `Set ij(i,j) / i1.j1, i2.j1, i3.j2 /`
   - Tuple notation with dot syntax

## Expected Results

See `expected_results.yaml` for detailed expected parsing behavior for each fixture.

## Usage

```bash
# Run set range fixture tests (when implemented)
pytest tests/unit/gams/test_parser.py -v -k set_range
```

## Implementation Notes

**Sprint 7 Status:**
- Range expansion (`*` notation) fully implemented
- Multi-dimensional sets supported in IR
- Tuple notation (`.` syntax) supported

**Range Expansion Algorithm:**
- `1*6` → ["1", "2", "3", "4", "5", "6"]
- `s1*s10` → ["s1", "s2", ..., "s10"]
- Prefix extracted, numeric range expanded
- Results stored in SetDef.members

## Coverage Matrix

| Syntax Type | Fixture | Parse | Expand | Cardinality | Notes |
|-------------|---------|-------|--------|-------------|-------|
| Numeric range | range_numeric | ✓ | ✓ | 6 | 1*6 |
| Alpha range | range_alpha | ✓ | ✓ | 10 | s1*s10 |
| Prefix range | range_prefix | ✓ | ✓ | 100 | p1*p100 |
| Macro range | range_with_macro | ✓ | ✓ | 8 | 1*%n% |
| Explicit | explicit_elements | ✓ | N/A | 3 | i1,i2,i3 |
| Indexed | indexed_set | ✓ | N/A | 3 | active(i) |
| Multi-dim | multi_dim_set | ✓ | N/A | 3 | pairs(i,j) |
| Tuple | set_tuple | ✓ | N/A | 3 | i1.j1 |

## Edge Cases

**Tested:**
- Large ranges (p1*p100) - 100 elements
- Macro expansion in ranges
- Multi-dimensional indexing
- Subset relationships

**Not Yet Tested:**
- Empty ranges (1*0)
- Invalid ranges (6*1 reversed)
- Non-numeric prefixes
- Special characters in set names

## Status

- **Created:** Sprint 7 Day 0
- **Fixtures:** 8/8 ✅ COMPLETE (Day 5)
- **Tests:** Partial (set range expansion working)
