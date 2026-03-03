# srkandw/srpchase: Undeclared scenred library symbols after $libInclude strip

**GitHub Issue:** [#978](https://github.com/jeffreyhorn/nlp2mcp/issues/978)
**Models:** srkandw (GAMSlib SEQ=353), srpchase (GAMSlib SEQ=356)
**Error category:** `internal_error`
**Error message:** `Parameter 'ScenRedParms' not declared [context: expression]`

## Description

Both srkandw and srpchase use `$libInclude scenred` to include the GAMS scenred (scenario reduction) library. The preprocessor correctly strips these directives (Issue #888), but the library defines parameters `ScenRedParms` and `ScenRedReport` that are referenced later in the model code. Since the library is not available to the parser, these symbols are never declared, causing parse failures.

## Reproduction

```bash
# srkandw fails at line 126
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/srkandw.gms')
"

# srpchase fails at line 77
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/srpchase.gms')
"
```

## Relevant Code

### srkandw.gms

```gams
* Line 110: Library include (stripped by preprocessor)
$libInclude scenred.gms

* Lines 126-133: References to undeclared ScenRedParms
ScenRedParms('report_level') = 0;
ScenRedParms('reduction_method') = ord(method) - 1;
ScenRedParms('red_num_leaves') = ord(run);

* Line 136: Second library include with arguments (stripped)
$     libInclude scenred kandw scen_red n tree prob na sprob dem

* Lines 139, 148-150: References to undeclared ScenRedReport
display ScenRedParms, ScenRedReport, sprob, sn;
report(method,run, 'red_percentage')   = ScenRedReport('red_percentage');
report(method,run, 'reduction_method') = ScenRedReport('reduction_method');
report(method,run, 'run_time')         = ScenRedReport('run_time');
```

### srpchase.gms

```gams
* Line 67: Library include (stripped by preprocessor)
$libInclude scenred

* Lines 77-79: References to undeclared ScenRedParms
ScenRedParms('construction_method') = 2;
ScenRedParms('reduction_method'   ) = 2;
ScenRedParms('sroption'           ) = 1;

* Line 82: Second library include with arguments (stripped)
$libInclude scenred %srprefix% tree_con n ancestor prob ancestor prob price
```

## Root Cause

The preprocessor strips `$libInclude` directives (Issue #888) but does not predeclare the symbols that the included library would define. The scenred library defines at minimum:

1. **`ScenRedParms`** -- Parameter with string index, used to configure scenred options
2. **`ScenRedReport`** -- Parameter with string index, populated by scenred with results

These parameters use string indices (e.g., `ScenRedParms('report_level')`), so they should be predeclared as `Parameter ScenRedParms(*), ScenRedReport(*);` or equivalent.

## Fix Approach

When the preprocessor encounters `$libInclude scenred`, in addition to stripping the line, inject predeclaration statements for the known scenred library symbols:

```gams
Parameter ScenRedParms(*);
Parameter ScenRedReport(*);
```

This could be implemented in `strip_unsupported_directives()` in `src/ir/preprocessor.py` by detecting `scenred` in the `$libInclude` directive and appending the predeclaration lines instead of just a stripped comment.

Alternatively, a mapping of library names to their exported symbols could be maintained, making it extensible for other `$libInclude` libraries in the future.

## Additional Blockers

### srkandw (after scenred fix)

1. **Curly-brace sum with subset domain**: Line 141 uses `sum{leaf(sn), sprob(sn)}`. The grammar supports curly-brace sum syntax (Sprint 17 Day 8) and subset domain patterns, but this specific combination may need testing.

### srpchase (after scenred fix)

No additional known blockers beyond scenred symbols. The `File` and `putClose` statements at lines 69-74 are handled by the preprocessor (PR #977).

## Related Issues

- [#888](https://github.com/jeffreyhorn/nlp2mcp/issues/888) -- clearlak: `$libInclude scenred` stripping (fixed)
- [#894](https://github.com/jeffreyhorn/nlp2mcp/issues/894) -- srkandw: original `$libInclude` issue
- [#895](https://github.com/jeffreyhorn/nlp2mcp/issues/895) -- srpchase: `$libInclude`/`File`/`putClose` issue
- [#975](https://github.com/jeffreyhorn/nlp2mcp/issues/975) -- srkandw: quoted set element in sum domain (fixed)
- [#976](https://github.com/jeffreyhorn/nlp2mcp/issues/976) -- srpchase: set assignment with IndexOffset (fixed)
