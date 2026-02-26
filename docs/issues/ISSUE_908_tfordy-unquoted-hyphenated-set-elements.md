# tfordy: Unquoted Hyphenated Set Elements in Parameter Assignments

**GitHub Issue**: [#908](https://github.com/jeffreyhorn/nlp2mcp/issues/908)
**Model**: `tfordy` (Timber Forest Sector — Dynamic)
**Pipeline status**: `path_syntax_error` (13 compilation errors)
**Blocking since**: Sprint 21 Day 7 (after dotted column header fix)

## Summary

After the Day 7 dotted column header fix (PR #905), tfordy remains at `path_syntax_error` with 13 compilation errors. The set elements `period-1` through `period-9` are correctly quoted in set definitions (`'period-1'`) but are emitted unquoted in parameter assignment LHS positions (`avl(period-1,t) = 1`). GAMS interprets `period-1` as arithmetic (`period` minus `1`), causing $120 (unknown identifier) and $171 (domain violation) errors.

## Root Cause

The emitter's `_quote_assignment_index()` function in `src/emit/original_symbols.py` does not quote set elements containing hyphens when they appear as parameter assignment indices.

**Set definition (correct — quotes present):**
```gams
te /'period-1', 'period-2', ... 'period-12'/
t(te) /'period-1', 'period-2', ... 'period-9'/
```

**Parameter assignment (incorrect — quotes missing):**
```gams
avl(period-1,t) = 1;  * GAMS reads this as: avl(period - 1, t) = 1
avl(period-2,t) = 1;  * GAMS reads this as: avl(period - 2, t) = 1
...
avl(period-9,t) = 1;
```

**Should be:**
```gams
avl('period-1',t) = 1;
avl('period-2',t) = 1;
...
avl('period-9',t) = 1;
```

## Reproduction

```bash
# 1. Check emitted MCP for unquoted hyphens:
grep "period-" data/gamslib/mcp/tfordy_mcp.gms

# 2. Run through GAMS:
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams \
  data/gamslib/mcp/tfordy_mcp.gms o=/tmp/tfordy_mcp.lst

# 3. Error count:
grep -c '^\*\*\*\* ' /tmp/tfordy_mcp.lst  # 33 (13 unique + duplicates)
```

## Error Details

| Error Code | Count | Description |
|---|---|---|
| $120 | 9 | Unknown identifier (`period` is not a declared symbol) |
| $171 | 9 | Domain violation for set (arithmetic result not in domain) |
| $340 | 9 | Label with same name exists (GAMS hint: forgot to quote?) |

All 9 errors correspond to the 9 `avl(period-N,t) = 1;` assignments (N=1..9).

## Fix Location

**File**: `src/emit/original_symbols.py`
**Function**: `_quote_assignment_index()` (around line 181)

The function should detect set element labels containing hyphens (or other special characters that require quoting) and wrap them in single quotes. The fix should apply to any set element that:
1. Contains a hyphen (`-`)
2. Contains characters that are not valid GAMS identifiers (letters, digits, underscore)
3. Starts with a digit

A simple heuristic: if a set element label matches `[a-zA-Z_]\w*-\w+` (identifier-hyphen-identifier pattern), it should be quoted.

## Related Issues

- Issue #886 — tfordy compound table headers and hyphenated elements (compound headers RESOLVED by PR #905; hyphenated quoting still open)
