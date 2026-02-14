# Translation: Table Parameter Data Incomplete in MCP Output (weapons)

**GitHub Issue:** [#713](https://github.com/jeffreyhorn/nlp2mcp/issues/713)
**Status:** Fixed
**Severity:** High — MCP output has compilation errors, solve fails
**Discovered:** 2026-02-13 (Sprint 19, after Issue #709 fix enabled weapons translation)
**Affected Models:** weapons

---

## Problem Summary

The `weapons` model parses and translates successfully, but the generated MCP file (`data/gamslib/mcp/weapons_mcp.gms`) fails to solve because the 2D table parameter `td` is not fully emitted. GAMS reports "Label is unknown" for labels like `"avail"` that exist as column headers in the original table but are missing from the translated output.

---

## Reproduction

**Model:** `weapons` (`data/gamslib/raw/weapons.gms`)

**Commands to reproduce:**
```bash
source .venv/bin/activate
python scripts/gamslib/batch_translate.py --model weapons
gams data/gamslib/mcp/weapons_mcp.gms lo=3 o=/tmp/weapons_mcp.lst
```

**GAMS error output:**
```
*** Error 116 in weapons_mcp.gms
    wa(w) = td(w,"avail");
                  $116
**** 116  Label is unknown
```

**Solve result:** `path_syntax_error` / `compilation_error`

---

## Root Cause

The original GAMS model declares a 2D table:

```gams
Table td 'target data'
            1   2   3   4   5   ... 20  avail
icbm          .05             .15 ...          200
mrbm-1    .16 .17 .15 ...                      100
...
damage     60  50  50  75 ...
target     30                 100 ...            ;
```

This table has column headers `1` through `20` plus `avail`, and row headers `icbm`, `mrbm-1`, `lr-bomber`, `f-bomber`, `mrbm-2`, `damage`, `target`. The data is then accessed as:

```gams
wa(w) = td(w,"avail");     -- weapon availability (column "avail")
tm(t) = td("target",t);    -- minimum weapons per target (row "target")
mv(t) = td("damage",t);    -- military value (row "damage")
```

The translated MCP output emits `td` as:

```gams
Parameters
    td(*,*) /'1'.'target data' 2.0, icbm.'target data' 0.05, ...
```

Only a single dimension label `'target data'` appears (which is the table's *description string*, not a data label). The actual 2D table data with all row/column combinations is not properly emitted. The translator appears to be confusing the table's description string with column header data, and is not emitting the full sparse matrix of values.

---

## Proposed Fix

Investigate how `table_block` data is stored in the IR (`ModelIR`) and how `expr_to_gams.py` / the MCP emitter reconstructs parameter data. The table's 2D data (row_label, col_label -> value) needs to be correctly stored during parsing and emitted as individual element assignments or a proper data block in the MCP output.

---

## Context

This issue was exposed by the Issue #709 fix (Prod expression support) which enabled weapons to translate successfully for the first time. The translation succeeds but the emitted GAMS code is incorrect.

---

## Fix Applied

**Root Cause:** When a table has no explicit domain (e.g., `Table td 'target data'`), the Earley parser consumes the description STRING `'target data'` as a row label in the first `table_row`, rather than recognizing it as the optional table description. This causes `_handle_table_block` to treat the description string as the only column header, mapping all data values to that single column key.

**Fix:** Added detection in `_handle_table_block` (around line 2024 in `src/ir/parser.py`) to skip the description string line when it appears on the same line as the table name and consists of a single quoted-string token. The actual column headers on the next line are then correctly used.

**Verification:**
- `td` parameter now stores 147 values with correct 2D keys (e.g., `("icbm", "avail") -> 200.0`)
- MCP output emits full sparse table data with proper `row.col` syntax
- Original GAMS Error 116 ("Label is unknown") is eliminated
- Quality gate: typecheck ✓, lint ✓, format ✓, 3312 tests pass ✓

**Note:** The weapons model now fails at solve with a different error (Error 483: MCP multiplier `lam_minw` not properly linked). This is a separate KKT system formulation issue, not related to table data emission.
