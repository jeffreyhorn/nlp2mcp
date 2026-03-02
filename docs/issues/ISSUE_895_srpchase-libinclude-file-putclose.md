# srpchase: `$libInclude`, `File` declaration, and `putClose`

**GitHub Issue:** [#895](https://github.com/jeffreyhorn/nlp2mcp/issues/895)
**Model:** srpchase (GAMSlib SEQ=356, "Scenario Tree Construction Example")
**Error category:** `internal_error` (previously `lexer_invalid_char`)
**Error message:** `Parameter 'ancestor' not declared` at line 39
**Status:** PARTIALLY RESOLVED — `$libInclude`, hybrid `File`, and `putClose` with content are now stripped; remaining error is a parser bug with set assignment IndexOffset (#976)

## Description

The model uses three unsupported GAMS features: (1) `$libInclude scenred` directive, (2) hybrid `File` declaration (`File ID STRING / path /;`), and (3) `putClose` with content arguments spanning multiple lines.

## Fix

Three changes, all in `src/ir/preprocessor.py` `strip_unsupported_directives()`:

1. **`$libInclude` stripping** — already implemented in Sprint 21 Day 11 (issue #888). Handles both `$libInclude` and `$     libInclude` (with spaces).

2. **Hybrid `File` declaration stripping** — strips `File` declarations that the grammar cannot parse (the hybrid form `File ID STRING / path /;`). Simple forms like `File sol / path /;` and `File ID STRING;` are preserved because the grammar handles them.

3. **`putClose` with content stripping** — strips `putClose` statements with content arguments (the grammar only supports `putclose ID? ;`). Multi-line statements are tracked with an `in_put_statement` flag until a `;` is found. Also strips `puttl` statements (not in grammar at all).

After the fix, srpchase advances from `lexer_invalid_char` (the `/` in the hybrid `File` declaration at line 69) to `internal_error`:
```
ParserSemanticError: Parameter 'ancestor' not declared [context: expression] (line 39, column 1)
```

This remaining error is a parser bug: `ancestor` is declared in-model as `Set ancestor(n,n)` (line 26), but the assignment `ancestor(n,n-card(leaf))$stage(n,'t3') = yes;` at line 39 uses an arithmetic index offset `n-card(leaf)` on the LHS. The parser's `_handle_assign()` detects the `IndexOffset`, skips the set assignment path, and falls through to the parameter check which fails. See [#976](https://github.com/jeffreyhorn/nlp2mcp/issues/976) for the specific bug.

Additionally, the model references undeclared scenred library symbols (`ScenRedParms`, `tree_con`) from the stripped `$libInclude scenred` directive.

## Related Issues

- [#976](https://github.com/jeffreyhorn/nlp2mcp/issues/976) — srpchase: set assignment with IndexOffset on LHS (current blocker)
- [#888](https://github.com/jeffreyhorn/nlp2mcp/issues/888) — clearlak: `$libInclude scenred` (primary fix)
- [#894](https://github.com/jeffreyhorn/nlp2mcp/issues/894) — srkandw: `$ libInclude scenred` (space after `$`)
- [#897](https://github.com/jeffreyhorn/nlp2mcp/issues/897) — feasopt1: `File` declaration + `.infeas` attribute

## Verification

- 8 unit tests added for selective File/putClose stripping (4 strip, 4 preserve)
- No regressions (ps10_s.gms `File sol / path /;` still parsed by grammar)
- All tests pass (3905 passed)
