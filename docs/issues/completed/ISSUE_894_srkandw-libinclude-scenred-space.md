# srkandw: `$ libInclude scenred` (space after $)

**GitHub Issue:** [#894](https://github.com/jeffreyhorn/nlp2mcp/issues/894)
**Model:** srkandw (GAMSlib SEQ=353, "Stochastic Programming Scenario Reduction")
**Error category:** `internal_error` (previously `lexer_invalid_char`)
**Error message:** `Unknown set or alias 'time-2' referenced in sum indices` at line 61
**Status:** FIXED — All blockers resolved. Model parses, generates MCP, solves optimally (MODEL STATUS 1).

## Description

The model uses `$     libInclude scenred kandw scen_red n tree prob na sprob dem` — a `$libInclude` directive with spaces between `$` and `libInclude`. This loads the GAMS scenario reduction library which defines symbols like `ScenRedParms`, `ScenRedReport`, `sprob`, etc.

## Current State

The `$libInclude` directive (including the space-separated form `$     libInclude`) is already stripped by the preprocessor (added in Sprint 21 Day 11, issue #888). The model now advances past the original `lexer_invalid_char` error to a `ParserSemanticError`:

```
ParserSemanticError: Unknown set or alias 'time-2' referenced in sum indices
[context: conditional assignment] [domain: ('n',)] (line 61, column 10)
```

This error occurs because the parser does not recognize quoted string set elements in sum domain positions. The element `'time-2'` is a locally-declared member of set `t` (line 21: `t 'time periods' / time-1, time-2 /`), used as a fixed index in `sum(tn('time-2',n), 1)`. The parser incorrectly tries to resolve `'time-2'` as a set/alias name instead of treating it as an element literal. See [#975](https://github.com/jeffreyhorn/nlp2mcp/issues/975) for the specific bug.

The model also uses `sum{...}` with curly braces (line 136), which is an additional potential blocker, and references undeclared scenred library symbols (`ScenRedParms`, `ScenRedReport`) at lines 126-150.

## Root Cause

1. ~~`$libInclude` not handled by preprocessor~~ — FIXED (Sprint 21 Day 11)
2. Quoted set element `'time-2'` in sum domain not recognized as element literal — see [#975](https://github.com/jeffreyhorn/nlp2mcp/issues/975)
3. Undeclared scenred library symbols (`ScenRedParms`, `ScenRedReport`) — NOT FIXABLE without library support
4. `sum{...}` curly-brace syntax (line 136) — partially supported (#355)

## Related Issues

- [#975](https://github.com/jeffreyhorn/nlp2mcp/issues/975) — srkandw: quoted set element in sum domain (current blocker)
- [#888](https://github.com/jeffreyhorn/nlp2mcp/issues/888) — clearlak: `$libInclude scenred` (primary fix)
- [#895](https://github.com/jeffreyhorn/nlp2mcp/issues/895) — srpchase: `$libInclude` + `File`/`putClose`
