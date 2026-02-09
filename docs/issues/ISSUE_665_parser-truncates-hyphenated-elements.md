# Issue #665: Parser truncates set element names containing hyphens in Table data

**GitHub Issue:** [#665](https://github.com/jeffreyhorn/nlp2mcp/issues/665)
**Status:** Open
**Priority:** Medium
**Category:** Parser Bug

## Summary

The GAMS parser truncates set element names that contain hyphens when parsing Table data. For example, `20-bond-wt` becomes `20` in the parsed parameter data, but is correctly parsed as `20-` in the set declaration (though still missing `bond-wt`).

## Reproduction

**Model:** `data/gamslib/raw/ajax.gms`

### Original GAMS source

```gams
Set
   m 'machines at mills' / machine-1,  machine-2,  machine-3              /
   g 'paper grades'      / 20-bond-wt, 25-bond-wt, c-bond-ext, tissue-wrp /;

Table dempr(g,*) 'demand and prices'
                  demand  price
   20-bond-wt      30000     77
   25-bond-wt      20000     81
   c-bond-ext      12000     99
   tissue-wrp       8000    105;
```

### Parsed IR (actual behavior)

```python
from src.ir.parser import parse_model_file
ir = parse_model_file('data/gamslib/raw/ajax.gms')

# Set g members - note truncation to '20-' instead of '20-bond-wt'
print(ir.sets['g'].members)
# Output: ['20-', '25-', 'c-bond-ext', 'tissue-wrp']

# Parameter dempr values - note '20' instead of '20-' or '20-bond-wt'
for k, v in list(ir.params['dempr'].values.items())[:4]:
    print(f'{k!r} = {v}')
# Output:
#   ('20', 'demand') = 30000.0
#   ('20', 'price') = 77.0
#   ('25', 'demand') = 20000.0
#   ('25', 'price') = 81.0
```

### Expected behavior

```python
# Set g members should be:
['20-bond-wt', '25-bond-wt', 'c-bond-ext', 'tissue-wrp']

# Parameter dempr keys should be:
('20-bond-wt', 'demand') = 30000.0
('20-bond-wt', 'price') = 77.0
('25-bond-wt', 'demand') = 20000.0
# etc.
```

## Impact

1. **Set/Parameter mismatch**: Set `g` has element `'20-'` but parameter `dempr` references element `20` - these don't match, causing GAMS compilation errors
2. **Full name lost**: The complete element name `20-bond-wt` is lost entirely
3. **Quoted elements preserved**: Elements like `c-bond-ext` that get quoted by the parser are handled correctly (as `'c-bond-ext'`)

## Generated MCP file shows the issue

```gams
Sets
    g /'20-', '25-', 'c-bond-ext', 'tissue-wrp'/
;

Parameters
    dempr(g,wc_dempr_d2) /20.demand 30000.0, 20.price 77.0, ...
                          'c-bond-ext'.demand 12000.0, .../
```

Note: `'20-'` in the set but `20` in the parameter data.

## Root Cause Analysis

The parser appears to be treating `-` as a token separator in Table row labels, splitting `20-bond-wt` into separate tokens. Two separate issues:

1. **Set declaration parsing**: Parses `20-bond-wt` as `20-` (partial truncation)
2. **Table row label parsing**: Parses `20-bond-wt` as `20` (complete truncation of hyphenated parts)

### Likely location in code

The issue is likely in `src/ir/parser.py` in the grammar rules for:
- Set element lists (the `/.../ ` blocks)
- Table row labels

The grammar may need to be updated to treat hyphenated identifiers as a single token rather than as separate tokens joined by operators.

## Workaround

Users can quote element names in the source GAMS file:
```gams
Set
   g 'paper grades' / '20-bond-wt', '25-bond-wt', 'c-bond-ext', 'tissue-wrp' /;
```

However, this requires modifying the source model, which is not ideal.

## Related

- Discovered during PR #664 review (set element quoting)
- Similar issue may affect other models with hyphenated element names
- The emission code now correctly quotes elements with `-`, but the parsing issue means the full element name is never captured

## Files to investigate

- `src/ir/parser.py` - Main parser
- `src/ir/grammar.lark` (if exists) - Grammar definition
- Tests in `tests/parser/` - Add regression tests

## Test case to add

```python
def test_parse_hyphenated_set_elements():
    """Verify hyphenated set elements are parsed completely."""
    gams_code = '''
    Set g / 20-bond-wt, 25-bond-wt, c-bond-ext /;
    Parameter dempr(g,*) / 20-bond-wt.demand 30000, 25-bond-wt.price 81 /;
    '''
    ir = parse_gams_string(gams_code)
    assert ir.sets['g'].members == ['20-bond-wt', '25-bond-wt', 'c-bond-ext']
    assert ('20-bond-wt', 'demand') in ir.params['dempr'].values
```
