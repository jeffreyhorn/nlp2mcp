# Feedtray: Dynamic Set `yes$` Assignments Emitted as Arithmetic

**GitHub Issue:** [#861](https://github.com/jeffreyhorn/nlp2mcp/issues/861)
**Status:** RESOLVED
**Severity:** Medium — Model translates but GAMS compilation fails (path_syntax_error)
**Date:** 2026-02-24
**Resolved:** 2026-02-24
**Affected Models:** feedtray

---

## Problem Summary

The feedtray model parses and translates to MCP, but the emitted GAMS code fails compilation
with 4 errors. The root cause is that dynamic set membership assignments using `yes$`
syntax are emitted as arithmetic parameter assignments using `1$`, creating type mismatches
in downstream expressions.

---

## Resolution

Added `_restore_yes_keyword()` function in `emit_set_assignments` to detect when the
parser converted `yes` to `Const(1.0)` and restore it to `SymbolRef('yes')` before
GAMS emission. Two patterns are handled:

1. `DollarConditional(Const(1.0), cond)` → `DollarConditional(SymbolRef('yes'), cond)`
   - Emits: `yes$(cond)` instead of `1$(cond)`
2. `Binary(-, Const(1.0), rhs)` → `Binary(-, SymbolRef('yes'), rhs)`
   - Emits: `yes - rhs` instead of `1 - rhs`

### Result

- feedtray: Error 133 (incompatible operands) completely eliminated
- Remaining errors are about discrete variable `yf` in MCP (Error 65) which is a
  fundamental MCP limitation (no binary/integer variables), not related to this issue
- All 3744 tests pass

---

## Files Changed

| File | Change |
|------|--------|
| `src/emit/original_symbols.py` | Added `_restore_yes_keyword()`, called from `emit_set_assignments()` |
