# Table Data: Negative Number with Space Between Minus and Digits

**GitHub Issue:** [#704](https://github.com/jeffreyhorn/nlp2mcp/issues/704)

**Issue:** The table data parser cannot handle negative numbers where a space separates the minus sign from the digits, e.g., `- 0.0013`. This is valid GAMS table data syntax.

**Status:** Fixed
**Severity:** Low — Confirmed in 1 model (ganges), may affect others
**Discovered:** 2026-02-13 (Sprint 19 Day 1, after Subcategory G grammar fix advanced ganges past its original set element description error)
**Affected Models:** ganges (confirmed)

---

## Problem Summary

In GAMS table data, negative values can be written with a space between the minus sign and the number: `- 0.0013`. The table data parser treats the minus sign and the number as separate tokens, failing to recognize this as a single negative value.

---

## Reproduction

**Model:** `ganges` (`data/gamslib/raw/ganges.gms`)

**Failing line (152):**
```gams
Table rate(*,i) 'various tax and margin rates              (unitless)'
                 agricult  cons-good  cap-good  int-good  pub-infr  service
   dep-prof       0.0729     0.2369    0.4319    0.1921    0.7191    0.3166
   dep-lab        0.0106     0.0832    0.0094    0.0958              0.0761
   taxrat-dom     0.0212     0.0865    0.0972    0.1212    0.1268    0.1056
   taxrat-imp     0.3134     0.1629    0.4247    0.2790    0.8461    0.6715
   taxrfd-dom   - 0.0013     0.32      0.40      0.40
```

The `- 0.0013` on the `taxrfd-dom` row has a space between `-` and `0.0013`.

**Command to reproduce:**
```bash
.venv/bin/python -c "from src.ir.parser import parse_model_file; parse_model_file('data/gamslib/raw/ganges.gms')"
```

**Error output:**
```
Error: Parse error at line 152, column 18: Unexpected character: '0'
  'taxrfd-dom'   - 0.0013     0.32      0.40      0.40
                   ^
```

The parser sees `'taxrfd-dom'` (row label), then `-` (minus), then `0.0013` but doesn't connect them as a negative number because of the intervening space.

---

## Root Cause

The table data parsing in `gams_grammar.lark` uses the `table_content` rule which expects table row data to contain `NUMBER` tokens (which include an optional leading `-` but without intervening whitespace) or `table_value` alternatives. The `- 0.0013` pattern is two tokens (`-` and `0.0013`) rather than one negative number token.

---

## Proposed Fix

In the table data parsing rules, allow a minus sign token followed by a number as a valid negative table value:

```lark
table_value: NUMBER
           | "-" NUMBER    // space-separated negative
           | "+"           // continuation marker
```

Alternatively, handle this in the table data preprocessor or lexer by collapsing `- NUMBER` sequences in table context.

---

## Fix Details

**Fixed in:** Sprint 19 (branch `sprint19-fix-issues-703-706`)

1. Added `negative_number: MINUS NUMBER` rule to `src/gams/gams_grammar.lark` as a new `table_value` alternative.
2. Updated `src/ir/parser.py` `_handle_table_block` to combine `MINUS` + `NUMBER` tokens from `negative_number` nodes into a single synthetic `NUMBER` token (e.g., `-0.0013`), mirroring the existing `negative_special` handling for `-inf`/`-eps`. Updated both the initial table row handling and the continuation handling paths.

**Verification:** `ganges.gms` now parses past line 152 (hits a new unrelated error at line 1082).

---

## Context

This issue was exposed by the Sprint 19 Day 1 grammar fix that added `NUMBER STRING -> set_element_with_desc` support. The ganges model previously failed at its set element description (`7374 '1973-74 -- base year'`). With that fix, it now parses past the set data but fails at line 152 on the table negative number.
