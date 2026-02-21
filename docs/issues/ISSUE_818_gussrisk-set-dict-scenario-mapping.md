# gussrisk: `Set dict` Scenario Mapping Syntax Not Supported

**GitHub Issue:** [#818](https://github.com/jeffreyhorn/nlp2mcp/issues/818)
**Model:** `gussrisk` (GAMSlib)
**Blocking Stage:** Parse (lexer_invalid_char at line 85/115, 74%)
**Severity:** Medium — blocks full parse of gussrisk
**Date:** 2026-02-21

---

## Problem Summary

The grammar does not support the GAMS `Set dict` (dictionary set) syntax used for scenario/GUSS mapping. This involves triple-dotted tuple notation (`name.attribute.''`) where set elements are paired with solver attributes via dot-separated segments including empty strings.

---

## Reproduction

### Failing GAMS Pattern (gussrisk.gms, lines 85–92)

```gams
Set dict / rapscenarios.scenario. ''
           rap         .param   .riskaver
           invest      .level   .stockoutput
           obj         .level   .objlevel
           investav    .marginal.investavshadow /;

solve evportfol using nlp maximizing obj scenario dict;
```

### Error Output

```
Error: Parse error at line 85, column 33: Unexpected character: '.'
  Set dict / rapscenarios.scenario. '',
                                  ^
```

### Smoke Test Command

```bash
python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/gussrisk.gms')"
```

---

## Root Cause

The set data grammar (`set_member` rules) does not support:

1. Triple-dotted tuples: `name.attribute.value` (3 segments joined by dots)
2. Empty string as a segment: `scenario. ''` (dot followed by quoted empty string)
3. The `solve ... scenario dict` statement syntax (scenario-based solving)

The existing `set_tuple` rule only supports 2-element dotted pairs (e.g., `a.b`). The triple-dot form `a.b.c` and `a.b.''` are not matched.

---

## Suggested Fix

1. Extend `set_tuple` or `set_member` rules to support 3+ segment dotted tuples
2. Allow empty STRING (`''`) as a valid segment in dotted notation
3. Add `scenario` keyword support in `solve` statement
4. Consider using `dotted_label` (which already supports N-segment dots) for set data

### Files to Modify

- `src/gams/gams_grammar.lark` — extend set_member for multi-segment tuples; add `scenario` to solve_stmt
- `src/ir/parser.py` — handle multi-segment set tuples in set data processing
- May also need preprocessor changes if dot-after-dot patterns are tokenized incorrectly

---

## Impact

- Blocks: gussrisk full parse
- Related: Any model using GUSS (Gather-Update-Solve-Scatter) scenario solving with dictionary sets
- Note: gussrisk also uses inline scalar data `/ 500 /` which was fixed in Sprint 20 Day 8
