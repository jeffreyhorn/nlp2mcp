# ISSUE #1772 — emfl: preprocessor does not support $eval (%new% reaches the lexer)

**GitHub:** [#1772](https://github.com/jeffreyhorn/nlp2mcp/issues/1772) · **Status:** 🔴 **OPEN** — filed Sprint 40 Day 4 (2026-10-20), routed, not fixed in place

**Route:** P3 parse (Sprint 40 P3 routing note) · **Model:** `emfl` (NLP-gated, `likely_convex`, admitted by rule Sprint 40 Day 3) · **Measured at:** `de0a7186`

## Fingerprint (reproduced)

`parse: failure`, `lexer_invalid_char`:

```
Parse error at line 36, column 46: Unexpected character: '%'
  n  'total number of new facilities'    / n1*n%new%  /
```

The compile-time variable `%new%` is never expanded, because it is defined by **`$eval`**, which the preprocessor does not handle:

```gams
$if not set N1  $set N1    5
$if not set N2  $set N2    5
$if not set N   $eval new  %N1%*%N2%
```

`%old%`, `%N1%` and `%N2%` (from `$set`) expand. `%new%` is left literal and reaches the lexer.

## Fix surface

`src/ir/preprocessor.py`: support `$eval <name> <expr>` (and `$evalGlobal`/`$evalLocal`). Evaluate the arithmetic expression after `%…%` substitution, then define `<name>` the way `$set` does. Unknown-function or non-numeric results should fail loudly, never stay literal.

**Reach in the corpus:** `$eval` also appears in `gqapsdp`, `spbenders4` and `springchain`. None of them is a convex candidate today.

**Not fixed in place.**
