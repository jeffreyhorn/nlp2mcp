# Worst: Expression-Based Variable Bounds Not Emitted

**GitHub Issue:** [#873](https://github.com/jeffreyhorn/nlp2mcp/issues/873)
**Status:** FIXED
**Severity:** High — Model translates but GAMS compilation fails (path_syntax_error)
**Date:** 2026-02-25
**Affected Models:** worst
**Fixed:** 2026-02-25

---

## Problem Summary

The worst model translates to MCP but the emitted GAMS code fails compilation with 4 errors.
Variables `r(t)` and `q(t)` have expression-based `.lo`/`.up` bounds in the original model
(e.g., `r.lo(t) = tdata(t,"rmin")`), but the emitter only outputs `.l` initialization that
references those bounds. Since the bounds themselves are never emitted, GAMS raises $141
"Symbol declared but no values assigned" on `r.lo(t)` and `q.lo(t)`.

---

## Fix Applied

### 1. VariableDef (src/ir/symbols.py)
Added 6 new expression-based bound fields mirroring `l_expr`/`l_expr_map`:
- `lo_expr` / `lo_expr_map` — expression-based lower bounds
- `up_expr` / `up_expr_map` — expression-based upper bounds
- `fx_expr` / `fx_expr_map` — expression-based fixed bounds

### 2. Parser (src/ir/parser.py)
In `_handle_variable_attribute_assignment()`, when `_extract_constant()` fails for
`.lo`/`.up`/`.fx` bounds, the expression is now stored in the corresponding `*_expr`
or `*_expr_map` field instead of being silently discarded.

Also extended `_extract_constant()` to handle simple binary arithmetic between literal
constants (e.g., `1/0.99` → `1.0101...`), so bounds like `1/0.99` are stored as numeric
values. A new helper `_is_literal_const()` ensures only literal Const/Unary(-, Const)
operands trigger this evaluation — parameter-based expressions (e.g., `(xmin+xmax)/2`)
remain as expressions.

### 3. Emitter (src/emit/emit_gams.py)
Added a "Variable Bounds" emission section before `.l` initialization that emits
`var.lo(idx) = expr;`, `var.up(idx) = expr;`, and `var.fx(idx) = expr;` for all
expression-based bounds.

### 4. Test fixture update (tests/e2e/test_gamslib_match.py)
Updated alkyl MCP solve reference from -1.894 to -1.765 — the correct value now that
upper bound complementarity constraints are properly included in the MCP.

---

## Verification

- worst model: $141 errors resolved (remaining $483 is a separate MCP mapping issue)
- alkyl model: Solves correctly with new objective -1.765
- All 3,783 tests pass (3,722 unit/integration + 61 e2e)
