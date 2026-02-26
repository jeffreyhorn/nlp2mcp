# twocge: 3-Dimensional Table with Dotted Column Headers Loses All Data

**GitHub Issue:** [#901](https://github.com/jeffreyhorn/nlp2mcp/issues/901)
**Model:** twocge (GAMSlib)
**Error category:** `path_syntax_error`
**GAMS error:** `$141` — Symbol declared but no values have been assigned
**Subcategory:** A (Missing parameter/Table data)

## Description

The `twocge` model defines a 3-dimensional table `SAM(u,v,r)` where column headers use dotted notation (e.g., `BRD.JPN`) to encode two dimensions. The parser extracts each dotted segment as a separate column header instead of merging them into compound headers. This produces 2-tuple keys instead of 3-tuple keys, causing the emitter to silently drop all table data. The emitted MCP file declares `SAM(u,v,r)` with no values, and all 14 downstream assignments that reference SAM cascade into `$141` errors.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
m = parse_model_file('data/gamslib/raw/twocge.gms')
sam = m.params['sam']
print(f'SAM domain: {sam.domain}, values: {len(sam.values)}')
# Check key arity — should be 3-tuples, but are 2-tuples:
for k in list(sam.values.keys())[:5]:
    print(f'  key={k} (len={len(k)})')
"
```

Expected: keys like `('BRD', 'BRD', 'JPN')` (3-tuples matching domain `(u,v,r)`)
Actual: keys like `('BRD', 'JPN')` (2-tuples — column header not merged)

## GAMS Source Context (lines 23–50)

```gams
Table SAM(u,v,r) 'social accounting matrix'
         BRD.JPN MLK.JPN CAP.JPN LAB.JPN IDT.JPN
   BRD        21      8
   MLK        17      9
   CAP                        80      45
   LAB                        20      55
   IDT         3      3
   TRF
   HOH                       100     100       6
   GOV                                        15
   INV                                        -2
   EXT         7     11

   +     TRF.JPN HOH.JPN GOV.JPN INV.JPN EXT.JPN
   BRD                20      19      16       8
   MLK                 4       2       7       3
   ...
```

Each column header like `BRD.JPN` encodes two dimensions: `v=BRD` and `r=JPN`. The row label provides `u`. Entry at row `BRD`, column `BRD.JPN` should produce key `('BRD', 'BRD', 'JPN')` with value `21`.

## Root Cause

In `src/ir/parser.py`, `_handle_table_block()` extracts column headers by iterating individual tokens:

```python
for token in first_line_tokens:
    if token.type in ("ID", "NUMBER", "STRING"):
        col_name = _token_text(token)
        col_headers.append((col_name, col_pos))
```

The Lark grammar's `dotted_label` rule produces separate `ID` tokens for each segment (`BRD`, `JPN`) with a `DOT` token between them. The column header loop treats each segment as a separate header instead of recognizing that consecutive tokens connected by dots form a single compound header.

**Contrast with row labels:** Row labels are correctly handled because `row_label_map` is built from the `simple_label -> dotted_label` parse tree node, which joins parts with dots (`row_label = ".".join(label_parts)`).

**Data flow:**
1. Parser produces 40 individual "column headers" instead of 20 compound ones
2. IR builder stores ~60 key-value pairs with wrong-arity 2-tuple keys
3. Emitter's `_expand_table_key()` tries to expand 2-tuple keys to match domain size 3, fails, returns `None`
4. All SAM entries silently dropped; SAM emitted with no data
5. Downstream assignments (`F0`, `X0`, `Xp0`, etc.) all reference empty SAM → cascading `$141`

## Fix Approach

Modify column header extraction in `_handle_table_block()` to reconstruct dotted labels:

1. After extracting individual tokens from the header line, detect consecutive `ID DOT ID` sequences and merge them into compound headers (e.g., `BRD.JPN`)
2. Apply the same fix in both the standard path (~line 2428) and the section-based path (~line 2356)
3. After this fix, keys are stored as `('BRD', 'BRD.JPN')`, and the existing `_expand_table_key()` in the emitter correctly splits `'BRD.JPN'` into `['BRD', 'JPN']`, producing the correct 3-tuple

**Estimated effort:** 2–3h (parser fix + tests)

## Related Issues

- Subcategory A affects 16 models total in PATH_SYNTAX_ERROR_CATALOG
- [#886](https://github.com/jeffreyhorn/nlp2mcp/issues/886) — tfordy: compound table headers (similar dotted-header pattern)
- Other Subcategory A models may have different root causes (e.g., multi-section tables, sparse data)
