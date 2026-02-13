# Table Parsing Issues Analysis (ISSUE_392, ISSUE_399)

**Date:** 2026-02-13
**Task:** Sprint 19 Prep Task 7
**Purpose:** Analyze the two table parsing issues to understand root causes and produce fix plans

---

## Executive Summary

Both ISSUE_392 (table continuation in `like`) and ISSUE_399 (table description as header in `robert`) share a **common root cause**: the grammar's optional description `(STRING | DESCRIPTION)?` in the `table_block` rule is not being matched by the Lark parser. Instead, the STRING description token is consumed as a `table_row`'s row label via the `dotted_label: (ID | STRING)` path.

This causes the entire table (all column headers and data rows) to collapse into a single `table_row` node with the description as its row label and all other tokens as values. The continuation handling code in the semantic handler is structurally sound but never exercises correctly because the grammar doesn't produce the expected parse tree.

**Key finding:** Both issues require a **grammar fix** — the `(STRING | DESCRIPTION)?` optional must be consumed before `table_content+` matching begins. The semantic handler's continuation logic and column-matching code are correct in principle and need only minor adjustments after the grammar fix.

**Revised effort estimate:** 3-5h total for both fixes combined (shared root cause), down from 4-8h estimated separately.

---

## Shared Root Cause: Grammar Ambiguity

### The Grammar Rule

```lark
table_block: "Table"i ID "(" table_domain_list ")" (STRING | DESCRIPTION)? table_content+ SEMI
```

Where `table_content` leads to `table_row`, and:

```lark
table_row: table_row_label table_value*
table_row_label: dotted_label -> simple_label
dotted_label: (ID | STRING) ("." (ID | STRING | range_expr))*
```

### The Problem

The `dotted_label` rule accepts `STRING` tokens. When Lark's Earley parser encounters `'expected profits'` or `'systolic blood pressure data'` after the closing `)`, it has two valid parse paths:

1. **Intended:** Match as `(STRING)?` (the optional table description)
2. **Actual:** Match as `table_content -> table_row -> simple_label -> dotted_label -> STRING`

Both paths are grammatically valid. Lark's Earley parser can represent this as an ambiguous parse, but with the default settings (without `ambiguity="explicit"`), it returns a single tree chosen according to internal rule-order and longest-match heuristics, which in this case results in the `STRING` being matched as part of `table_content` (path 2) rather than as the optional description.

### Parse Tree Evidence

**robert model** (`Table c(p,t) 'expected profits'`):
```
table_block (7 children):
  [0] Token(TABLE): 'Table'
  [1] Token(ID): 'c'
  [2] Token(LPAR): '('
  [3] Tree: table_domain_list (p, t)
  [4] Token(RPAR): ')'
  [5] table_content -> table_row (16 children)
        row_label: "'expected profits'" (STRING)
        table_value: 1, 2, 3, low, 25, 20, 10, medium, 50, 50, 50, high, 75, 80, 100
  [6] Token(SEMI): ';'
```

Note: There is no STRING or DESCRIPTION child at the `table_block` level — the grammar's optional `(STRING | DESCRIPTION)?` is not matched at all. Instead, the STRING token is embedded inside the first `table_content -> table_row` structure as its row label. All 4 rows (column headers + 3 data rows) collapse into a single `table_row` with the description as row label.

**like model** (`Table data(*,i) 'systolic blood pressure data'`):
```
table_block:
  [5] table_content -> table_row (48 children)
        row_label: "'systolic blood pressure data'" (STRING)
        [all data from first section as table_values]
  [6] table_content -> table_continuation (51 children)
        [continuation data: 16-31 column headers + pressure + frequency values]
  [7] Token(SEMI): ';'
```

The first section collapses into one row; the continuation is correctly parsed as `table_continuation` but its column headers and data share the wrong structure.

---

## ISSUE_392: Table Continuation (`like` model)

### Model and Table

**File:** `data/gamslib/raw/like.gms` (lines 19-26)

```gams
Table data(*,i) 'systolic blood pressure data'
                 1   2   3   4   5   6   7   8   9  10  11  12  13  14  15
   pressure     95 105 110 115 120 125 130 135 140 145 150 155 160 165 170
   frequency     1   1   4   4  15  15  15  13  21  12  17   4  20   8  17

   +            16  17  18  19  20  21  22  23  24  25  26  27  28  29  30  31
   pressure    175 180 185 190 195 200 205 210 215 220 225 230 235 240 245 260
   frequency     8   6   6   7   4   3   3   8   1   6   0   5   1   7   1   2;
```

### Expected Parse

- **Dimensions:** 2 rows (pressure, frequency) x 31 columns (1-31)
- **Total values:** 62
- **Description:** `'systolic blood pressure data'` (should be skipped)
- **Continuation:** `+` marker on line 24 introduces columns 16-31

### Actual Parse (Current)

- The description `'systolic blood pressure data'` becomes the row label
- All tokens from columns 1-15 and both data rows collapse into a single `table_row`
- The `+` continuation section is parsed as `table_continuation` (correct grammar match)
- **Result:** 4 of 62 values captured (93.5% data loss)
- **Generated MCP:** `data(*,i) /'1'.'systolic blood pressure data' 2.0, ...`

### Root Cause

Primary: Grammar ambiguity (shared root cause — see above). The STRING description is consumed as the row label instead of the optional description.

Secondary: The continuation handling heuristic at `src/ir/parser.py:1832-1837` may need verification for numeric column headers:

```python
if len(merged_lines) == 1:
    is_column_header_continuation = True
else:
    is_column_header_continuation = (
        all_identifier_tokens and not has_number_tokens
    )
```

For the `like` table, once the primary grammar fix is applied, the table will be correctly parsed with separate column header and data rows. The `+` continuation introduces a new set of column headers (`16 17 18 ... 31`). When the continuation is processed, the `len(merged_lines) == 1` branch may apply if the continuation is treated as a fresh section, which would correctly classify it as a column header continuation (the `len == 1` case always returns `True`). However, this depends on how the continuation merging interacts with the corrected parse tree structure and needs verification during implementation.

**Note:** This secondary concern cannot be fully evaluated until the primary grammar fix is in place, since the current grammar produces a malformed parse tree. The `len(merged_lines) == 1` branch may handle this case correctly.

### Fix Plan

1. **Grammar fix** (shared with ISSUE_399): Ensure `(STRING | DESCRIPTION)?` is consumed before `table_content+`
2. **Heuristic fix:** Improve the continuation classification logic:
   - Option A: If the continuation appears after a blank line (or after data rows have been seen), treat it as a new column header section regardless of token types
   - Option B: Check if the PLUS token is the first token on a line that doesn't have a preceding row label — if so, it's a column header continuation
   - Option C: Track the "section" state: after seeing row labels, a `+` line always starts a new column section with new headers followed by data rows re-using the same row labels
3. **Test strategy:** Unit test with `like` table; validate 62 values captured correctly

### Data Recovery

| Metric | Before Fix | After Fix |
|--------|-----------|-----------|
| Values captured | 4 / 62 | 62 / 62 (expected) |
| Data loss | 93.5% | 0% |
| GAMS compilation | Error 170 | Pass (expected) |

---

## ISSUE_399: Table Description as Header (`robert` model)

### Model and Table

**File:** `data/gamslib/raw/robert.gms` (lines 27-32)

```gams
Table c(p,t) 'expected profits'
              1    2    3
   low       25   20   10
   medium    50   50   50
   high      75   80  100;
```

### Expected Parse

- **Dimensions:** 3 rows (low, medium, high) x 3 columns (1, 2, 3)
- **Total values:** 9
- **Description:** `'expected profits'` (should be skipped)

### Actual Parse (Current)

- `'expected profits'` becomes the row label of a single `table_row`
- All tokens (1, 2, 3, low, 25, 20, 10, medium, 50, 50, 50, high, 75, 80, 100) are table_values
- The semantic handler reconstructs this as: row `'expected profits'` with values matched by column position
- **Result:** 4 of 9 values captured (55% data loss)
- **Generated MCP:** `c(p,t) /'1'.'expected profits' 2.0, low.'expected profits' 25.0, ...`

### Root Cause

Primary: Grammar ambiguity (shared root cause — see above). Identical to ISSUE_392.

There is no secondary issue for ISSUE_399. Once the grammar correctly consumes the description, the table will parse as 4 rows: column headers (`1 2 3`) followed by 3 data rows (`low`, `medium`, `high`). The existing semantic handler's column-position matching should handle this correctly.

### Fix Plan

1. **Grammar fix** (shared with ISSUE_392): Same fix resolves both issues
2. **No additional handler changes needed** for this issue
3. **Test strategy:** Unit test with `robert` table; validate 9 values captured correctly

### Data Recovery

| Metric | Before Fix | After Fix |
|--------|-----------|-----------|
| Values captured | 4 / 9 | 9 / 9 (expected) |
| Data loss | 55% | 0% |
| GAMS compilation | Error 170 | Depends on ISSUE_670 (cross-indexed sums) |

**Note:** The `robert` model has a secondary blocker (ISSUE_670: cross-indexed sums in KKT stationarity equations) that will prevent full compilation even after the table parsing fix. However, the table data will be correctly captured.

---

## Proposed Grammar Fix

### Option 1: Dedicated Description Terminal (Recommended)

Add a higher-priority terminal specifically for table descriptions that matches quoted strings after the closing parenthesis:

```lark
table_block: "Table"i ID "(" table_domain_list ")" TABLE_DESC? table_content+ SEMI

TABLE_DESC: STRING
```

However, this may not resolve the Earley ambiguity since `TABLE_DESC` and `dotted_label`'s `STRING` would still overlap.

### Option 2: Restructure table_row to Exclude STRING as First Token

Modify `dotted_label` to not accept `STRING` as the first element when used as a table row label:

```lark
table_row_label: dotted_label -> simple_label
               | ...
dotted_label: ID ("." (ID | STRING | range_expr))*  // Remove STRING from first position
```

But this would break Issue #665, our open bug about supporting quoted row labels like `'20-bond-wt'` in `table_row_label` parsing (see `docs/issues/` for full context).

### Option 3: Use Semantic Disambiguation in the Handler (Recommended)

Keep the grammar as-is but add logic at the start of `_handle_table_block` to detect and correct the description misparse. Since the grammar ambiguity causes the STRING to be consumed as part of the first `table_row` (not as a direct child of `table_block`), the fix must check the first `table_row`'s row label:

```python
# After extracting table_contents (list of table_row and table_continuation nodes):
# Check if the first table_row's row label is a STRING — if so, it's a
# misparse of the description (the grammar's (STRING|DESCRIPTION)? was not matched)
description = None
if table_rows:
    first_row = table_rows[0]
    first_label = first_row.children[0]
    if (isinstance(first_label, Tree) and first_label.data == "simple_label"):
        dotted = first_label.children[0]
        first_tok = dotted.children[0]
        if isinstance(first_tok, Token) and first_tok.type == "STRING":
            # This is a description misparse — extract as description
            # and reinterpret remaining table_values as column headers + data
            description = _token_text(first_tok)
            # Reparse: the table_values of this row ARE the actual column
            # headers and data rows (grouped by line number)
```

Note: There is no need to check for a STRING/DESCRIPTION token as a direct child of `table_block` — as demonstrated in the parse tree evidence above, the grammar ambiguity means the STRING is always consumed inside the first `table_row`, never as a standalone child at the `table_block` level.

### Option 4: Grammar Priority Annotation

Use Lark's priority system to prefer the `(STRING)?` match over `table_row -> dotted_label -> STRING`:

```lark
table_block.2: "Table"i ID "(" table_domain_list ")" STRING table_content+ SEMI
table_block.1: "Table"i ID "(" table_domain_list ")" DESCRIPTION table_content+ SEMI
table_block.0: "Table"i ID "(" table_domain_list ")" table_content+ SEMI
```

This splits the rule into three priority-ordered alternatives. However, this approach has a fundamental limitation: the ambiguity occurs *within* the expansion of `table_content` (specifically, whether `STRING` is matched by `dotted_label` inside `table_row`), not *between* different `table_block` alternatives. Rule-level priorities choose between alternative expansions of the same rule, but they don't resolve ambiguities that arise within a shared sub-rule. This option would need to be restructured to actually prevent the `dotted_label` path from capturing the STRING when a description is present — which brings us back to the grammar restructuring challenges of Option 2.

### Recommendation

**Option 3 (semantic disambiguation)** is the safest approach:
- No grammar changes → zero regression risk for other table parsing
- Handles both STRING and DESCRIPTION descriptions
- Detects the misparse pattern and corrects it in the semantic handler
- Works with the existing parse tree structure
- Backward compatible with tables that don't have descriptions

**Option 4** is the cleanest but requires Earley parser priority testing to verify Lark honors rule-level priorities in this context. It should be evaluated as a follow-up.

---

## Implementation Plan

### Phase 1: Semantic Handler Fix (~2-3h)

1. **Detect description misparse** at the start of `_handle_table_block`:
   - Check if the first `table_row`'s row label is a STRING token
   - If so, extract it as the description and reparse the remaining `table_value` tokens by line number to reconstruct the actual column headers and data rows

2. **Reparse logic (with line info verification):**
   - First, **verify** that the `table_value` tokens (or their underlying Lark `Token` objects) retain a valid `line` attribute at this stage of parsing — Lark Token objects typically preserve line/column metadata, but this should be confirmed during implementation
   - If `token.line` is available, group the `table_value` tokens from the misparse row by `token.line`
   - The first distinct line of tokens becomes the column headers
   - Subsequent lines become data rows, with the first ID token on each line as the row label
   - This effectively reconstructs the correct parse structure from the flat token list when line information is preserved
   - **Fallback if line info is not available:** use alternative positional metadata from Lark (e.g., `column`, `end_line`) or preserve raw row segmentation earlier in the parse pipeline

3. **Handle continuation after reparse:**
   - If `table_continuation` nodes exist, process them normally using the existing continuation merging code
   - The continuation code already handles column position offsets correctly

### Phase 2: Continuation Heuristic Fix (~1-2h)

After the grammar/semantic fix, verify the continuation handling for the `like` model:

1. **Test if the heuristic correctly classifies numeric column headers as header continuation**
2. If needed, improve the heuristic at `src/ir/parser.py:1832-1837`:
   - Add a state tracker: after seeing data rows, a `+` continuation always starts a new column header section
   - Alternative: check if the continuation tokens repeat existing row labels (e.g., `pressure`, `frequency`) — if not, they're likely column headers

### Phase 3: Testing (~1h)

1. **Unit tests:**
   - Table with STRING description and no continuation (robert's `c(p,t)`)
   - Table with STRING description and `+` continuation (like's `data(*,i)`)
   - Table without description (regression test)
   - Table with DESCRIPTION (unquoted multi-word) description

2. **Model validation:**
   - Regenerate `like_mcp.gms` and verify 62 values in `data(*,i)` parameter
   - Regenerate `robert_mcp.gms` and verify 9 values in `c(p,t)` parameter
   - Run both through GAMS compilation to verify no Error 170

---

## Effort Estimate

| Task | Estimated Time | Notes |
|------|---------------|-------|
| Semantic handler fix (description misparse detection + reparse) | 2-3h | Core fix for both issues |
| Continuation heuristic verification/fix | 1-2h | May be unnecessary if current code works after grammar fix |
| Unit tests + model validation | 1h | 4+ test cases |
| **Total** | **3-5h** | Down from 4-8h (2-4h each) due to shared root cause |

**Comparison with FIX_ROADMAP estimates:**
- ISSUE_392: FIX_ROADMAP estimated 2-4h → actual likely 2-3h (includes continuation heuristic)
- ISSUE_399: FIX_ROADMAP estimated 2-4h → actual likely 1h (covered by shared fix)
- Combined: 3-5h vs. 4-8h estimated separately

---

## Impact on Sprint 19

- **Models unblocked:** 2 (like, robert — though robert also needs ISSUE_670 fix)
- **Data recovery:** 58 values for like (93.5% → 0% loss), 5 values for robert (55% → 0% loss)
- **Regression risk:** Low — semantic handler fix doesn't change grammar, only adds detection logic
- **Dependencies:** None for like; robert also depends on ISSUE_670 (cross-indexed sums)
