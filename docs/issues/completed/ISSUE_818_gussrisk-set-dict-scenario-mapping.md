# gussrisk: `Set dict` Scenario Mapping Syntax Not Supported

**GitHub Issue:** [#818](https://github.com/jeffreyhorn/nlp2mcp/issues/818)
**Model:** `gussrisk` (GAMSlib)
**Blocking Stage:** Parse (lexer_invalid_char at line 85/115, 74%)
**Severity:** Medium — blocks full parse of gussrisk
**Date:** 2026-02-21
**Status:** FIXED

---

## Problem Summary

The grammar does not support the GAMS `Set dict` (dictionary set) syntax used for scenario/GUSS mapping. This involves triple-dotted tuple notation (`name.attribute.''`) where set elements are paired with solver attributes via dot-separated segments including empty strings.

---

## Root Cause

1. **Triple-dotted set tuples**: `set_member` rules only supported 2-element dotted pairs (`a.b`). GUSS dictionary sets use 3-element dotted tuples (`a.b.c`, `a.b.''`).
2. **`solve ... scenario dict` syntax**: The solve statement grammar didn't support the optional `scenario ID` suffix.

---

## Fix Applied

### Grammar (`src/gams/gams_grammar.lark`)

1. Added `set_triple` alternatives for 3-segment dotted set tuples (all combinations of SET_ELEMENT_ID and STRING for each segment):
   ```
   | SET_ELEMENT_ID "." SET_ELEMENT_ID "." SET_ELEMENT_ID -> set_triple
   | SET_ELEMENT_ID "." SET_ELEMENT_ID "." STRING          -> set_triple
   | ... (8 total combinations)
   ```

2. Added `"scenario"i ID` as optional suffix to solve statement alternatives:
   ```
   | "Solve"i ID obj_sense ID "using"i solver_type "scenario"i ID SEMI -> solve
   | "Solve"i ID "using"i solver_type obj_sense ID "scenario"i ID SEMI -> solve
   ```

### Parser (`src/ir/parser.py`)

- Added `set_triple` handler in `_expand_set_members`: joins 3 segments with dots (e.g., `rap.param.riskaver`)
- The `_handle_solve` method already handles extra children gracefully (scenario dict name ignored in IR)

### Tests

- `tests/unit/test_issue_818.py::TestTripleDottedSetTuples` — triple-dotted tuples with IDs and strings
- `tests/unit/test_issue_818.py::TestSolveScenario` — solve with scenario dict in both word orders

### Verification

gussrisk now fully parses:
```bash
python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/gussrisk.gms'); print('OK')"
```

---

## Impact

- Unblocks: gussrisk full parse
- Related: Any model using GUSS (Gather-Update-Solve-Scatter) scenario solving with dictionary sets
