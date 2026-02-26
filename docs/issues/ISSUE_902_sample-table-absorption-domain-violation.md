# sample: Table Data Absorption Bug Produces Domain Violation

**GitHub Issue:** [#902](https://github.com/jeffreyhorn/nlp2mcp/issues/902)
**Model:** sample (GAMSlib)
**Error category:** `path_syntax_error`
**GAMS error:** `$170` — Domain violation for element
**Subcategory:** B (Domain violation in emitted parameter data)

## Description

The `sample` model defines a table `data(h,*)` with numeric row labels (`1`, `2`, `3`, `4`) and data values starting before the first column header position. The Issue #863 absorption logic in the parser incorrectly treats the first data value (`400000`) as a split-off row label segment, producing the corrupted row label `1.400000` instead of `1`. When emitted, `'1.400000'` is not a member of set `h = /'1', '2', '3', '4'/`, triggering 4 instances of `$170`.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
m = parse_model_file('data/gamslib/raw/sample.gms')
data_param = m.params['data']
for k, v in sorted(data_param.values.items()):
    if '1' in str(k):
        print(f'  {k}: {v}')
"
```

Expected: keys starting with `('1', ...)` — e.g., `('1', 'pop'): 400000.0`
Actual: keys starting with `('1.400000', ...)` — e.g., `('1.400000', 'pop'): 25.0`

## GAMS Source Context (lines 16–23)

```gams
Table data(h,*)
          pop   a   b  cost
   1   400000  25   1     1
   2   300000  25   4     1
   3   200000  25  16     1
   4   100000  25  64     1;
```

Column layout:
| Token | Column Position |
|-------|----------------|
| `pop` (header) | 10 |
| `a` (header) | 16 |
| `1` (row label) | 3 |
| `400000` (first data value) | 7 |

The data value `400000` at column 7 is to the left of the first column header `pop` at column 10.

## Root Cause

In `src/ir/parser.py`, lines ~2485–2511, the Issue #863 absorption logic:

1. Computes `min_col_header_col = 10` (position of first column header `pop`)
2. For each data row, scans for NUMBER tokens positioned to the left of column 10
3. Any such NUMBER token is absorbed into the row label with a dot separator

For row 1: token `400000` at column 7 < `min_col_header_col` (10), so it's treated as a label segment. Row label becomes `1.400000`.

**The bug:** The absorption logic was designed for Issue #863 where dotted labels like `9000011.jun.1` get split by the Earley parser into separate tokens. But it doesn't distinguish between:
- **True dotted-label segments** (e.g., `.1` from `9000011.jun.1`) — immediately adjacent to the row label
- **Legitimate data values** (e.g., `400000`) — separated from the row label by whitespace, positioned in the data area

**Data corruption for row 1:**
| What happens | `pop` | `a` | `b` | `cost` |
|---|---|---|---|---|
| Expected | 400000 | 25 | 1 | 1 |
| Actual | 25 | 0 | 1 | 1 |

The `400000` is consumed as a label segment, values shift left, and `a` gets zero-filled.

## Fix Approach

Add a column-gap guard to the absorption logic. Only absorb a NUMBER token if it is immediately adjacent to the preceding row label token (within 1–2 columns):

```python
# Before absorbing, check column adjacency:
if tok_col <= row_label_end_col + 2:
    absorbed.append((tok, val_str))
# else: legitimate data value, do not absorb
```

Alternative: only absorb NUMBER tokens whose string representation starts with `.` (from tokenization of `.N` patterns), which directly matches the Issue #863 pattern.

**Estimated effort:** 1h (parser fix + tests)

## Related Issues

- Subcategory B affects 5 models total in PATH_SYNTAX_ERROR_CATALOG
- Issue #863 introduced the absorption logic that causes this bug
- [#827](https://github.com/jeffreyhorn/nlp2mcp/issues/827) — gtm: domain violation from zero-fill (related pattern)
