# Ajax: Table Parsing Creates Invalid Domain Elements

**GitHub Issue:** [#673](https://github.com/jeffreyhorn/nlp2mcp/issues/673)

**Issue:** The ajax model's table data is incorrectly parsed, creating invalid domain elements that cause GAMS Error 170 (domain violation).

**Status:** Open  
**Severity:** High - Model fails to compile  
**Affected Models:** ajax  
**Date:** 2026-02-10

---

## Problem Summary

The table parser incorrectly interprets column headers containing hyphens. The original table has columns like `machine-1`, `machine-2`, etc., but the parsed data keys contain truncated elements like `'-1'`, `'-2'`.

GAMS Error 170: Domain violation for element

---

## Reproduction

### Test Case: ajax.gms

```bash
# Translate the model
nlp2mcp data/gamslib/raw/ajax.gms -o data/gamslib/mcp/ajax_mcp.gms

# Run GAMS
cd data/gamslib/mcp && gams ajax_mcp.gms lo=2

# Check errors
grep "170" ajax_mcp.lst
```

**Error Output:**
```
**** 170  Domain violation for element
```

### Original Table Structure

From ajax.gms:
```gams
Set
   m 'machines at mills' / machine-1,  machine-2,  machine-3 /
   g 'paper grades'      / 20-bond-wt, 25-bond-wt, c-bond-ext, tissue-wrp /;

Table prate(g,m) 'production rate (tons per hour)'
                  machine-1  machine-2   machine-3
   20-bond-wt            53         52          49
   25-bond-wt            51         49          44
```

### Generated MCP (Wrong)

```gams
Sets
    m /'machine-1', 'machine-2', 'machine-3'/
    g /'20-bond-wt', '25-bond-wt', 'c-bond-ext', 'tissue-wrp'/
;

Parameters
    prate(g,m) /'20-bond-wt'.'-1' 53.0, '20-bond-wt'.'-2' 52.0, ...
```

The data keys use `'-1'`, `'-2'`, `'-3'` which are NOT in the set `m`.

### Expected MCP (Correct)

```gams
Parameters
    prate(g,m) /'20-bond-wt'.'machine-1' 53.0, '20-bond-wt'.'machine-2' 52.0, ...
```

---

## Technical Details

### Root Cause

The table parser appears to be splitting hyphenated column headers incorrectly, or there's an issue with how column headers are matched to data values.

Looking at the parsed data:
- Column headers: `machine-1`, `machine-2`, `machine-3`
- But data keys contain: `-1`, `-2`, `-3`

This suggests the parser is extracting a suffix instead of the full column header name.

### Key Files to Investigate

- `src/ir/parser.py`: `_handle_table_block()` function
- Look for how column headers are extracted and matched to values
- Check handling of hyphenated identifiers

---

## Proposed Solution

1. **Debug table parsing**: Add logging to see what column headers are extracted
2. **Check column header extraction**: Ensure full identifiers are preserved
3. **Verify matching logic**: Ensure data values are matched to correct columns

---

## Workaround

Currently none. The ajax model cannot be translated correctly.

---

## Related Models

Similar table parsing issues may affect other models with hyphenated column headers.

---

## References

- GAMS Table Syntax Documentation
- Sprint 18 analysis of domain violation errors
