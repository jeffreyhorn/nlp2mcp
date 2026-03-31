# danwolfe: Parse Error — GAMS Async Grid Computing Functions

**GitHub Issue:** [#955](https://github.com/jeffreyhorn/nlp2mcp/issues/955)
**Status:** FIXED
**Model:** danwolfe (GAMSlib, Dantzig-Wolfe decomposition)

## Problem

Parser failed at line 219 due to unrecognized GAMS async grid computing functions (`handlecollect`, `handledelete`, `sleep`) and unsupported `display$func(...)` syntax.

## Fix

1. Added `handlecollect`, `handledelete`, `handlestatus`, `handlesubmit`, `sleep` to FUNCNAME in grammar
2. Added `DOLLAR func_call` alternative to display_stmt and display_stmt_nosemi grammar rules for `display$func(...)` pattern
3. `repeat...until` already supported from prior sprint
4. `timeelapsed` handled as regular GAMS identifier (auto-populated at runtime)

**Result:** danwolfe now parses successfully (5 variables, 8 equations). All 4,358 tests pass.
