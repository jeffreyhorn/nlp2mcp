# srkandw: Quoted set element in sum domain not recognized

**GitHub Issue:** [#975](https://github.com/jeffreyhorn/nlp2mcp/issues/975)
**Model:** srkandw (GAMSlib SEQ=353, "Scenario Reduction - Kaut & Wallace")
**Error category:** `internal_error`
**Error message:** `Unknown set or alias 'time-2' referenced in sum indices [context: conditional assignment] [domain: ('n',)] (line 61, column 10)`

## Description

The parser fails when a quoted string set element (e.g., `'time-2'`) is used as a fixed index in a sum domain filter. In GAMS, `sum(tn('time-2',n), 1)` means "sum over all `n` where `tn('time-2',n)` is true", with `'time-2'` being a literal element of set `t`. The parser treats the quoted string as a symbol name and fails to resolve it.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/srkandw.gms')
"
```

## Relevant Code

### Set declarations (lines 18-22)

```gams
Set
   i 'raw materials' / raw-1, raw-2   /
   j 'products'      / p-1,p-2        /
   t 'time periods'  / time-1, time-2 /
   n 'nodes'         / n-0*n-12       /;
```

### Multi-dimensional set with element mapping (lines 55-59)

```gams
Set
   tn(t,n)   'time node mapping' / time-1.(n-1*n-3), time-2.(n-4*n-12)      /
   tree(n,n) / n-0.(n-1*n-3), n-1.(n-4*n-6), n-2.(n-7*n-9), n-3.(n-10*n-12) /
   sn(n)     'subset of nodes in reduced subtree'
   leaf(n)   'leaf nodes in original tree';
```

### Failing line (line 61)

```gams
leaf(n)$(sum(tn('time-2',n), 1)) = yes;
```

Here `'time-2'` is a literal element of set `t`, used as a fixed index into the 2D set `tn(t,n)`. The parser should recognize this as a set element reference, not try to resolve it as a set/alias name.

## Root Cause

The parser's sum domain resolution expects index names to be declared sets or aliases. When it encounters `tn('time-2',n)` in a sum domain, it tries to look up `'time-2'` as a set name and fails with "Unknown set or alias 'time-2'". In GAMS, quoted strings in domain positions are element literals that filter the domain — they don't need to be declared as sets.

## Additional Blockers

Even after fixing this issue, srkandw has additional blockers:

1. **Undeclared scenred library symbols**: The model uses `$libInclude scenred` (stripped by preprocessor) which defines `ScenRedParms` and `ScenRedReport` parameters. These are referenced at lines 126-134 and 139-150 but never declared locally.

2. **Curly-brace sum syntax**: Lines 141 and 178 use `sum{leaf(sn), sprob(sn)}` with curly braces. This syntax is partially supported (issue #355) but may fail with the specific `leaf(sn)` domain pattern.

## Fix Approach

Modify the parser's sum domain resolution to treat quoted strings as element literals rather than requiring them to be declared sets. When a quoted string appears in a sum domain index position, it should be treated as a fixed element filter, not a set reference.

## Related Issues

- [#894](https://github.com/jeffreyhorn/nlp2mcp/issues/894) — srkandw: original `$libInclude` issue (partially resolved)
- [#888](https://github.com/jeffreyhorn/nlp2mcp/issues/888) — clearlak: `$libInclude scenred` (fixed)
- [#355](https://github.com/jeffreyhorn/nlp2mcp/issues/355) — curly-brace sum syntax (partially implemented)
