# Put Statement Format Specifier Analysis

**Date:** February 6, 2026
**Task:** Sprint 18 Prep Task 6
**Purpose:** Research GAMS put statement `:width:decimals` syntax and design grammar extension

---

## Executive Summary

**Key Findings:**
1. **Format specifier syntax is `:width:decimals`** - no three-part `:width:decimals:exponent` variant exists
2. **Only 3 of 4 models fail due to format specifiers** - stdcge has a different issue (missing semicolon in loop)
3. **Grammar extension is straightforward** - add `put_format` rule to `put_item`
4. **No conflict with existing colon usage** - put statement scope is clearly bounded
5. **Put statements are output-only** - safe to parse and ignore for MCP generation

**Estimated fix time:** ~2 hours (confirmed)

---

## GAMS Put Statement Format Syntax

### Full Specification

From GAMS documentation, the local item formatting syntax is:

```
item:{<>}width:decimals
```

Where:
- `item` = the output item being formatted (expression, variable, parameter, text)
- `{<>}` = optional alignment symbol (`<` left, `>` right, `<>` center)
- `width` = field width in characters (integer)
- `decimals` = number of decimal places for numeric items (integer)

### Key Points

1. **No three-part variant** - there is no `:width:decimals:exponent` syntax for scientific notation
2. **Alignment is optional** - can be omitted: `item:10:5` or `item:<10:5`
3. **Components can be omitted** - `item:10` (width only) or `item::5` (decimals only) are valid
4. **Applies to any put item** - numeric expressions, text strings, set labels
5. **Zero means variable width** - `item:0:0` produces variable width with no decimals

### Examples from GAMS Documentation

```gams
put x.l:20:10;           * width 20, 10 decimals
put 'text':15;           * text with width 15
put value:<10:5;         * left-aligned, width 10, 5 decimals
put ratio:>8:2;          * right-aligned, width 8, 2 decimals
```

---

## Model Verification

### ps5_s_mn

**Status:** ❌ Fails due to `:width:decimals`

**Parse Error:**
```
Parse error at line 145, column 13: Unexpected character: 'p'
  loop(i, put pt(i,t):10:5;);
              ^
```

**Analysis:** The error message is misleading. The actual failure is that `pt(i,t):10:5` is not recognized as a valid `put_item`. The grammar parses `pt(i,t)` as an expression, but `:10:5` following it is unexpected.

**Blocking Issue:** `:width:decimals` format specifier
**Secondary Issues:** None identified

**Failing Lines (source file):**
- Line 151: `loop(i, put pt(i,t):10:5;);`
- Line 152: `put noMHRC(t) Util_lic(t):20:10 Util_Lic2(t):20:10 Util_gap(t);`

*Note: Parse error reports line 145 due to preprocessing (comment removal shifts line numbers).*

---

### ps10_s

**Status:** ❌ Fails due to `:width:decimals`

**Parse Error:**
```
Parse error at line 59, column 24: Unexpected character: ':'
  loop(i, put i.tl x.l(i):20:10 w.l(i):20:10 b.l(i):20:10 p(i):20:10 theta(i):20:10/;);
                         ^
```

**Analysis:** The colon after `x.l(i)` starts the format specifier `:20:10`, which is not recognized.

**Blocking Issue:** `:width:decimals` format specifier
**Secondary Issues:** None identified

**Failing Lines (source file):**
- Line 63: `loop(i, put i.tl x.l(i):20:10 w.l(i):20:10 b.l(i):20:10 p(i):20:10 theta(i):20:10/;);`
- Line 64: `put "Util" Util.l:20:10;`
- Line 68: `loop(i, put i.tl licd.m(i):20:10; put /;);`

*Note: Parse error reports line 59 due to preprocessing (comment removal shifts line numbers).*

---

### ps10_s_mn

**Status:** ❌ Fails due to `:width:decimals`

**Parse Error:**
```
Parse error at line 141, column 13: Unexpected character: 'p'
  loop(i, put pt(i,t):10:5;);
              ^
```

**Analysis:** Same issue as ps5_s_mn - format specifier not recognized.

**Blocking Issue:** `:width:decimals` format specifier
**Secondary Issues:** None identified

**Failing Lines (source file):**
- Line 147: `loop(i, put pt(i,t):10:5;);`
- Line 148: `put noMHRC(t) Util_lic(t):20:10 Util_Lic2(t):20:10 Util_gap(t);`

*Note: Parse error reports line 141 due to preprocessing (comment removal shifts line numbers).*

---

### stdcge

**Status:** ⚠️ Fails due to **different issue** (not `:width:decimals`)

**Parse Error:**
```
Parse error at line 362, column 17: Unexpected character: ')'
  loop(j, put j.tl);
                  ^
```

**Analysis:** This model does NOT use `:width:decimals` format specifiers. The failure is because `put` statements inside loops require a semicolon before the closing `)`, but this code has:
```gams
loop(j, put j.tl);
```

The grammar expects `put_stmt` which requires SEMI, but here the put is followed directly by `);`.

**Blocking Issue:** Missing `put_stmt_nosemi` variant for loop context
**Secondary Issues:** None - the `:width:decimals` fix will NOT help this model

**Failing Lines (source file):**
- Line 385: `loop(j, put j.tl);`
- Line 388: `put h.tl;` (inside loop without semicolon before loop end)
- Line 397: `loop(j, put j.tl);`
- Line 400: `put h.tl;`

*Note: Parse error reports line 362 due to preprocessing (comment removal shifts line numbers).*

---

## Model Summary

| Model | Blocks on `:width:decimals`? | Secondary Issues | Fix Will Help? |
|-------|------------------------------|------------------|----------------|
| ps5_s_mn | ✅ Yes | None | ✅ Yes |
| ps10_s | ✅ Yes | None | ✅ Yes |
| ps10_s_mn | ✅ Yes | None | ✅ Yes |
| stdcge | ❌ No | Missing `put_stmt_nosemi` | ❌ No (separate fix needed) |

**Conclusion:** The `:width:decimals` fix will unblock **3 models**, not 4. stdcge requires a separate fix (adding `put_stmt_nosemi` variant).

---

## Grammar Extension Design

### Current Grammar

```lark
put_stmt: "put"i put_items? SEMI
        | "put"i put_items "/" SEMI

put_items: put_item (","? put_item)*

put_item: STRING
        | "/" -> put_newline
        | expr
```

### Proposed Grammar Extension

```lark
put_stmt: "put"i put_items? SEMI
        | "put"i put_items "/" SEMI

put_items: put_item (","? put_item)*

// Extended put_item to support format specifiers
// Format: item:width:decimals or item:<width:decimals (with alignment)
put_item: STRING put_format?
        | "/" -> put_newline
        | expr put_format?

// Format specifier: :width or :width:decimals
// Optional alignment prefix: < (left), > (right), <> (center)
put_format: ":" PUT_ALIGN? NUMBER (":" NUMBER)?

PUT_ALIGN: "<>" | "<" | ">"
```

### Alternative Design (Simpler)

If alignment is rarely used, a simpler approach:

```lark
put_item: STRING (":" NUMBER (":" NUMBER)?)?
        | "/" -> put_newline
        | expr (":" NUMBER (":" NUMBER)?)?
```

This handles `:width` and `:width:decimals` but not alignment prefixes.

### AST/IR Impact

**None** - Put statements are parsed and ignored for MCP generation. The format specifiers don't need to be preserved in the IR. The grammar change only affects parsing, not semantics.

### Potential Conflicts

**Colon usage in existing grammar:**
1. `option_format` rule: `ID ":" NUMBER (":" NUMBER)*` - e.g., `option decimals:8`
2. No conflict - put_item scope is clearly bounded within put_stmt

**Resolution:** The put_format rule only applies within put_item context, which is only matched inside put_stmt. No ambiguity with other colon usages.

---

## Additional Fix Needed: `put_stmt_nosemi`

For stdcge, we need a variant that doesn't require SEMI for use in `exec_stmt_final`:

```lark
// Add to exec_stmt_final for loop context
?exec_stmt_final: assignment_nosemi
                | assignment_stmt
                | display_stmt_nosemi
                | abort_stmt_nosemi
                | option_stmt
                | solve_stmt
                | put_stmt
                | put_stmt_nosemi    // NEW
                | putclose_stmt
                | execute_stmt
                | SEMI

// Put statement without trailing semicolon (for loop final position)
put_stmt_nosemi: "put"i put_items
               | "put"i put_items "/"
```

This is a **separate fix** from the `:width:decimals` work and should be tracked independently.

---

## Verification of Known Unknowns

### Unknown 3.1: Is the `:width:decimals` syntax the only put statement format specifier?

**Status:** ✅ VERIFIED

**Finding:** Yes, `:width:decimals` is the only format specifier syntax. There is NO `:width:decimals:exponent` variant. The full syntax is:
- `item:width` (width only)
- `item:width:decimals` (width and decimals)
- `item:{<|>|<>}width:decimals` (with optional alignment prefix)

Scientific notation is controlled by global file settings (`.nr=2`), not per-item format specifiers.

### Unknown 3.2: Do the 4 target put-statement models have secondary blocking issues?

**Status:** ✅ VERIFIED

**Finding:** 
- **ps5_s_mn, ps10_s, ps10_s_mn:** No secondary issues. The `:width:decimals` fix will allow these 3 models to parse.
- **stdcge:** Does NOT use `:width:decimals`. It has a DIFFERENT blocking issue: `put_stmt` requires SEMI but stdcge uses `put` at end of loop without semicolon. Requires separate `put_stmt_nosemi` fix.

**Conclusion:** Fix will unblock **3 models**, not 4. stdcge needs a separate grammar fix.

### Unknown 3.3: Will the grammar extension conflict with existing colon usage in GAMS?

**Status:** ✅ VERIFIED

**Finding:** No conflict. The colon in format specifiers is only matched within `put_item` context, which is nested inside `put_stmt`. The only other colon usage in the grammar is `option_format` rule (`ID ":" NUMBER`), which is in a completely different statement context. Lark's context-sensitive parsing ensures no ambiguity.

### Unknown 3.4: Are put statements semantically significant for MCP generation?

**Status:** ✅ VERIFIED

**Finding:** Put statements are output-only with no side effects on the mathematical model. They are used for:
- Writing results to CSV files
- Generating reports after solve
- Debugging output

They can be safely parsed and ignored for MCP generation. The emitter does not need to include put statements in MCP output.

---

## Estimated Fix Time

| Fix | Estimated Time | Models Unblocked |
|-----|----------------|------------------|
| `:width:decimals` grammar extension | 1.5 hours | 3 (ps5_s_mn, ps10_s, ps10_s_mn) |
| `put_stmt_nosemi` for loop context | 0.5 hours | 1 (stdcge) |
| **Total** | **2 hours** | **4 models** |

The original ~2 hour estimate is accurate, but requires two separate grammar changes.

---

## Recommendations

1. **Sprint 18 should include both fixes:**
   - `:width:decimals` format specifier support
   - `put_stmt_nosemi` for loop final position

2. **Track as single "put statement enhancement" work item** since both are small changes

3. **Test cases needed:**
   - Parse `put x.l:20:10;`
   - Parse `put "text":15;`
   - Parse `loop(i, put i.tl);` (without trailing semicolon)
   - Parse all 4 target models

---

## Document History

- February 6, 2026: Initial creation (Task 6 of Sprint 18 Prep)
