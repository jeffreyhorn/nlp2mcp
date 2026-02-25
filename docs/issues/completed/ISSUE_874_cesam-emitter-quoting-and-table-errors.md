# Cesam: Emitter Missing Quotes on Set Elements + Table Comment Data Leak

**GitHub Issue:** [#874](https://github.com/jeffreyhorn/nlp2mcp/issues/874)
**Status:** FIXED
**Severity:** High — Model translates but GAMS compilation fails (57 errors)
**Date:** 2026-02-25
**Affected Models:** cesam
**Fixed:** 2026-02-25

---

## Problem Summary

The cesam model translates to MCP but the emitted GAMS code fails with 57 compilation errors.
Four distinct emitter bugs produce cascading failures.

---

## Fix Applied

### Bug 1: Missing quotes on `sameas()` element literals (src/ir/parser.py)
In the parser, when a quoted string literal is encountered as a `sameas()` argument, the
SymbolRef was created without preserving quotes. Fixed by wrapping the name in quotes:
`SymbolRef(f'"{name}"')` instead of `SymbolRef(name)`. This preserves quotes through the
AST so the emitter outputs `sameas(ii,"ROW")` correctly.

### Bug 2: Missing quotes on numeric set element indices (src/emit/original_symbols.py)
Added `_quote_assignment_index()` helper function that quotes numeric-looking indices
in executable assignments (parameter and subset value assignments). Applied in both
`emit_computed_parameter_assignments()` and `emit_subset_value_assignments()`.

### Bug 3: Table comment data leak (src/ir/preprocessor.py)
Comment lines (starting with `*`) within Table data blocks were leaking through the
preprocessor. Fixed by adding comment line stripping inside `normalize_table_continuations()`:
when inside a table block, lines starting with `*` are replaced with empty lines (preserving
line numbering). A global approach was tried first but reverted because it stripped
`* Stripped:` marker lines created by earlier preprocessing steps.

### Bug 4: Quoted set variable in `.l` initialization (src/emit/emit_gams.py)
When emitting `.l` expressions with indexed access, the emitter was quoting set variable
names as string literals. Fixed by passing `domain_vars` (frozenset of string indices)
to `expr_to_gams()` so set variable names aren't quoted.

---

## Verification

- All 4 bugs resolved in cesam MCP emission
- All 3,783 tests pass (3,722 unit/integration + 61 e2e)
