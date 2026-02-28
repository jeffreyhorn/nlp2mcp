# twocge: Table `+` Continuation Sections Overwrite Earlier Data

**GitHub Issue:** [#968](https://github.com/jeffreyhorn/nlp2mcp/issues/968)
**Model:** twocge (GAMSlib)
**Error category:** `gams_error` (EXECERROR = 28)
**GAMS errors:** `division by zero` (26 instances), `rPower: FUNC DOMAIN: x**y, x=0,y<0` (2 instances)

## Description

The `twocge` model defines a 3-dimensional table `SAM(u,v,r)` with 4 `+` continuation
sections covering two regions (JPN and USA):

```gams
Table SAM(u,v,r) 'social accounting matrix'
         BRD.JPN MLK.JPN CAP.JPN LAB.JPN IDT.JPN
   BRD        21      8
   MLK        17      9
   ...

   +     TRF.JPN HOH.JPN GOV.JPN INV.JPN EXT.JPN
   BRD                20      19      16       8
   ...

   +     BRD.USA MLK.USA CAP.USA LAB.USA IDT.USA
   BRD        40       1
   MLK        17      29
   ...

   +     TRF.USA HOH.USA GOV.USA INV.USA EXT.USA
   BRD                30      20      20      13
   ...
```

The table parser (via `_merge_dotted_col_headers()`) correctly merges dotted headers
like `BRD.JPN` into compound column headers. However, when the USA continuation
sections (sections 3 and 4) are parsed, the data is stored with **JPN region keys**
instead of USA keys, overwriting the JPN values.

## Root Cause

The parser produces 50 entries, all with `.JPN` suffix. The USA data (sections 3-4)
replaces JPN data. For example:

| Key | Expected JPN value | Stored value | Source |
|-----|-------------------|-------------|--------|
| `('BRD', 'BRD.JPN')` | 21 | 40 | USA section 3 value overwrote JPN section 1 |
| `('MLK', 'BRD.JPN')` | 17 | 17 | Coincidentally same in both regions |

The correct behavior should produce ~100 entries: 50 for JPN and 50 for USA.

The bug is in `src/ir/parser.py` in the table parsing logic. The `_merge_dotted_col_headers()`
function or the `+` continuation handling in `_handle_table_block()` appears to use the
first section's column headers as a template for all sections, ignoring that later `+`
sections introduce new column headers with different region suffixes.

## Impact

All derived parameters (`F0`, `M0`, `E0`, `Xp0`, etc.) for `r=USA` are zero/unassigned
because the USA SAM data was stored under JPN keys. This causes 28 runtime execution
errors in calibration assignments (lines 117-135) and post-solve reporting (lines 306-331)
where division by zero occurs for the USA region.

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/twocge.gms -o /tmp/twocge_mcp.gms

# Verify wrong data (BRD.BRD.JPN should be 21, not 40)
grep "BRD.BRD.JPN" /tmp/twocge_mcp.gms
# Output: BRD.BRD.JPN 40  <-- wrong, this is the USA value

# Verify no USA entries
grep "USA" /tmp/twocge_mcp.gms | grep -v "^\*\|onText\|offText"
# No data entries for USA

# Verify with Python
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
ir = parse_model_file('data/gamslib/raw/twocge.gms')
sam = ir.params['SAM']
print(f'Total entries: {len(sam.values)}')  # Should be ~100, gets 50
usa = [k for k in sam.values if any('USA' in str(x) for x in k)]
print(f'USA entries: {len(usa)}')  # Should be ~50, gets 0
"

# Run through GAMS to see 28 execution errors
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/twocge_mcp.gms lo=3
grep "Exec Error" /tmp/twocge_mcp.lst
```

## Fix Approach

In `src/ir/parser.py`, fix the `+` continuation section handling in `_handle_table_block()`
to correctly parse new column headers for each `+` section rather than reusing the
first section's headers. The `_merge_dotted_col_headers()` function should be applied
independently to each `+` section's column header tokens.

**Files to modify:**
- `src/ir/parser.py` — `_handle_table_block()` and/or `_merge_dotted_col_headers()`

**Estimated effort:** 2-4h

## Related Issues

- [#901](https://github.com/jeffreyhorn/nlp2mcp/issues/901) — twocge dotted table column headers (RESOLVED — original fix)
- [#967](https://github.com/jeffreyhorn/nlp2mcp/issues/967) — twocge explicit zeros (PARTIALLY RESOLVED — zero-filtering applied but root cause is this issue)
