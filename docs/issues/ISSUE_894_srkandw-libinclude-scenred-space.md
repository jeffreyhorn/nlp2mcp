# srkandw: `$ libInclude scenred` (space after $)

**GitHub Issue:** [#894](https://github.com/jeffreyhorn/nlp2mcp/issues/894)
**Model:** srkandw (GAMSlib SEQ=353, "Stochastic Programming Scenario Reduction")
**Error category:** `internal_error` (previously `lexer_invalid_char`)
**Error message:** `Unknown set or alias 'time-2' referenced in sum indices` at line 61
**Status:** PARTIALLY RESOLVED — `$libInclude` stripping works; remaining error is semantic (undeclared library symbols)

## Description

The model uses `$     libInclude scenred kandw scen_red n tree prob na sprob dem` — a `$libInclude` directive with spaces between `$` and `libInclude`. This loads the GAMS scenario reduction library which defines symbols like `ScenRedParms`, `ScenRedReport`, `sprob`, `time-2`, etc.

## Current State

The `$libInclude` directive (including the space-separated form `$     libInclude`) is already stripped by the preprocessor (added in Sprint 21 Day 11, issue #888). The model now advances past the original `lexer_invalid_char` error to a `ParserSemanticError`:

```
ParserSemanticError: Unknown set or alias 'time-2' referenced in sum indices
[context: conditional assignment] [domain: ('n',)] (line 61, column 10)
```

This error occurs because the scenred library defines sets and parameters (`time-2`, `ScenRedParms`, `ScenRedReport`, `sprob`, etc.) that are referenced throughout the model but never declared in the model file itself. Without implementing library symbol pre-declaration or a lenient mode for undeclared symbols, this model cannot be parsed.

The model also uses `sum{...}` with curly braces (line 136), which is an additional unsupported syntax.

## Root Cause

1. ~~`$libInclude` not handled by preprocessor~~ — FIXED (Sprint 21 Day 11)
2. Scenred library symbols (`time-2`, `ScenRedParms`, `ScenRedReport`, etc.) are undeclared — NOT FIXABLE without library support
3. `sum{...}` curly-brace syntax — NOT SUPPORTED

## Related Issues

- [#888](https://github.com/jeffreyhorn/nlp2mcp/issues/888) — clearlak: `$libInclude scenred` (primary fix)
- [#895](https://github.com/jeffreyhorn/nlp2mcp/issues/895) — srpchase: `$libInclude` + `File`/`putClose`
