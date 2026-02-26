# srpchase: `$libInclude`, `File` declaration, and `putClose`

**GitHub Issue:** [#895](https://github.com/jeffreyhorn/nlp2mcp/issues/895)
**Model:** srpchase (GAMSlib SEQ=356, "Scenario Tree Construction Example")
**Error category:** `lexer_invalid_char`
**Error message:** `Unexpected character: '/'` at line 69, column 34

## Description

The model uses three unsupported GAMS features: (1) `$libInclude scenred` directive, (2) `File` declaration for output files, and (3) `putClose` for writing to files.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/srpchase.gms')
"
```

## Relevant Code (lines 64–74)

```gams
* Initialize ScenRed
$set srprefix srpchase
$libInclude scenred

File fopts 'Scenred option file' / 'sr2%srprefix%.opt' /;
putClose fopts 'order           1'
             / 'section   epsilon'
             / ' 2           0.05'
             / ' 3           0.05'
             / 'end';
```

## Root Cause

1. `$libInclude scenred` — not handled by preprocessor (same as clearlak, srkandw)
2. `File fopts 'description' / 'filename' /;` — the `File` declaration for GAMS put-file I/O is not in the grammar
3. `putClose fopts '...' / '...' / '...';` — the `putClose` statement with `/` as line separator is not supported
4. The `/` in the `File` declaration is the immediate blocker (lexer error at line 69, column 34)

## Related Issues (duplicate cluster: `$libInclude`)

This issue shares the `$libInclude` root cause with:
- [#888](https://github.com/jeffreyhorn/nlp2mcp/issues/888) — clearlak: `$libInclude scenred` (primary issue)
- [#894](https://github.com/jeffreyhorn/nlp2mcp/issues/894) — srkandw: `$ libInclude scenred` (space after `$`)

**Primary fix:** Fixing #888 should also resolve the `$libInclude` portion of this issue. This issue has additional blockers: `File` declaration and `putClose` statement support.

The `File` declaration blocker is also shared with:
- [#897](https://github.com/jeffreyhorn/nlp2mcp/issues/897) — feasopt1: `File` declaration + `.infeas` attribute

## Fix Approach

1. Add `$libInclude` to `strip_unsupported_directives()` in the preprocessor — shared with #888, #894
2. Add `File` declaration to the grammar (or strip it in preprocessor) — shared with #897
3. Add `putClose` / `put` statement support to the grammar (or strip in preprocessor)
4. The put-file I/O subsystem is tangential to MCP translation; stripping may be preferable
