# srkandw/srpchase: Undeclared scenred library symbols after $libInclude strip

**GitHub Issue:** [#978](https://github.com/jeffreyhorn/nlp2mcp/issues/978)
**Models:** srkandw (GAMSlib SEQ=353), srpchase (GAMSlib SEQ=356)
**Error category:** `internal_error`
**Error message:** `Parameter 'ScenRedParms' not declared [context: expression]`
**Status:** Fixed

## Description

Both srkandw and srpchase use `$libInclude scenred` to include the GAMS scenred (scenario reduction) library. The preprocessor correctly strips these directives (Issue #888), but the library defines parameters `ScenRedParms` and `ScenRedReport` that are referenced later in the model code. Since the library is not available to the parser, these symbols are never declared, causing parse failures.

## Root Cause

The preprocessor strips `$libInclude` directives but does not predeclare the symbols the included library would define. The scenred library defines:

1. **`ScenRedParms`** -- Parameter with string index, used to configure scenred options
2. **`ScenRedReport`** -- Parameter with string index, populated by scenred with results

## Fix

Modified `strip_unsupported_directives()` in `src/ir/preprocessor.py` to inject predeclaration statements when stripping a `$libInclude` directive that references the scenred library. On the first `$libInclude scenred` encounter, the following lines are injected:

```gams
Parameter ScenRedParms(*);
Parameter ScenRedReport(*);
```

A `scenred_predeclared` flag ensures predeclarations are only injected once, even when multiple `$libInclude scenred` directives appear (e.g., srkandw has two -- one for setup and one for execution with arguments).

### Files Changed

- `src/ir/preprocessor.py`: Inject scenred parameter predeclarations on first `$libInclude scenred`, with `scenred_predeclared` flag to prevent duplicates
- `tests/unit/ir/test_preprocessor.py`: Updated existing tests for new predeclaration lines; added 2 new tests:
  - `test_scenred_predeclare_only_once`: Verifies predeclarations injected only once for multiple `$libInclude scenred`
  - `test_libinclude_non_scenred_no_predeclare`: Verifies non-scenred `$libInclude` does not inject predeclarations

## Verification

- Both srkandw and srpchase parse successfully (`parse_model_file` completes without error)
- All 3925 tests pass (2 new tests added)
- mypy, ruff, and black checks pass

## Related Issues

- [#888](https://github.com/jeffreyhorn/nlp2mcp/issues/888) -- clearlak: `$libInclude scenred` stripping (fixed)
- [#894](https://github.com/jeffreyhorn/nlp2mcp/issues/894) -- srkandw: original `$libInclude` issue
- [#895](https://github.com/jeffreyhorn/nlp2mcp/issues/895) -- srpchase: `$libInclude`/`File`/`putClose` issue
- [#975](https://github.com/jeffreyhorn/nlp2mcp/issues/975) -- srkandw: quoted set element in sum domain (fixed)
- [#976](https://github.com/jeffreyhorn/nlp2mcp/issues/976) -- srpchase: set assignment with IndexOffset (fixed)
