# Ajax: Table Parsing Creates Invalid Domain Elements

**GitHub Issue:** [#673](https://github.com/jeffreyhorn/nlp2mcp/issues/673)

**Issue:** The ajax model's table data is incorrectly parsed, creating invalid domain elements that cause GAMS Error 170 (domain violation).

**Status:** Fixed  
**Severity:** High - Model fails to compile  
**Affected Models:** ajax  
**Date:** 2026-02-10  
**Fixed:** 2026-02-11

---

## Problem Summary

The table parser incorrectly interprets column headers containing hyphens. The original table has columns like `machine-1`, `machine-2`, etc., but the parsed data keys contain truncated elements like `'-1'`, `'-2'`.

GAMS Error 170: Domain violation for element

---

## Root Cause

The issue was in the preprocessor's handling of table column headers with hyphens.

When parsing a table like:
```gams
Table prate(g,m) 'production rate (tons per hour)'
                  machine-1  machine-2   machine-3
   20-bond-wt            53         52          49
```

The grammar structure is:
```
table_block: "Table"i ID "(" table_domain_list ")" (STRING | DESCRIPTION)? table_content+ SEMI
```

The `(STRING | DESCRIPTION)?` is meant for table descriptions (like `'production rate'`).

**Previous behavior (Issue #665):** Column headers with hyphens were NOT quoted because the DESCRIPTION terminal was expected to match them (e.g., `machine-1  machine-2` as a single multi-word description).

**The bug:** When a table already has a STRING description on the declaration line, the DESCRIPTION terminal isn't used for column headers. Without quoting, `machine-1` was parsed as:
- Row label: `machine` 
- Value: `-1` (negative number)

This caused all column data to be misassigned.

---

## Solution

Modified `normalize_special_identifiers()` in `src/ir/preprocessor.py` to:

1. **Detect if the Table declaration line has a STRING description** (quoted text after the domain)
2. **Quote column headers only when needed:**
   - If Table HAS a STRING description: Quote column headers to prevent `machine-1` from being parsed as `machine` + `-1`
   - If Table has NO description: Don't quote column headers so the DESCRIPTION terminal can match them
3. **Always quote identifiers with `+`** (these trigger table continuation parsing)

### Code Changes

```python
# Check if the Table declaration line has a STRING description
table_has_description = bool(
    re.search(r"\)\s*['\"][^'\"]*['\"]", stripped)
)

# In column header handling:
if table_has_description or has_plus_identifier:
    # Quote all special identifiers in column headers
    processed = _quote_special_in_line(line)
    result.append(processed)
else:
    # Don't quote - let DESCRIPTION terminal match
    result.append(line)
```

---

## Verification

After the fix:
- `prate` values correctly use `('20-bond-wt', 'machine-1')` instead of `('20-bond-wt', '-1')`
- ajax model compiles and solves successfully with optimal solution
- All existing tests pass

---

## Files Modified

- `src/ir/preprocessor.py`: Updated `normalize_special_identifiers()` to conditionally quote table column headers based on whether the table declaration has a STRING description
- `tests/unit/test_special_identifiers.py`: Updated test expectations for column header quoting behavior
