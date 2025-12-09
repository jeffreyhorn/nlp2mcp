# Parser: `file` Statement Not Supported

## GitHub Issue
- **Issue #:** 434
- **URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/434

## Summary
The parser does not support the GAMS `file` statement for file I/O operations.

## Affected Model
- **inscribedsquare.gms** (Tier 2) - Inscribed Square Problem

## Error
```
Error: Parse error at line 84, column 6: Unexpected character: 'f'
  file f / '%gams.scrdir%gnuplot.in' /;
       ^
```

## Root Cause
The grammar does not include a rule for `file` statements. GAMS uses `file` to declare file handles for output operations.

## GAMS Code Pattern
```gams
file f / '%gams.scrdir%gnuplot.in' /;
if( %gnuplot% and
 (m.modelstat = %modelStat.optimal% or
  m.modelstat = %modelStat.locallyOptimal% or
  m.modelstat = %modelStat.feasibleSolution%),
  f.nd=6;
  f.nw=0;
  ...
);
```

The `file` statement declares a file handle `f` with a path, used for writing output (typically for plotting or reporting).

## Suggested Fix
Option 1 (Skip/Ignore): Add `file` to the list of ignored directives since file I/O is not relevant for NLP model extraction.

Option 2 (Parse but don't process): Add a grammar rule that parses the file statement but doesn't create IR nodes:
```lark
file_stmt: "file"i ID "/" STRING "/" SEMI
```

## Complexity
Low - can be handled by ignoring or adding a simple skip rule.

## Test Case
```gams
file f / 'output.txt' /;
```

Expected: Statement is parsed (or skipped) without error.

## Notes
The `file` statement is typically used for post-solve reporting and visualization, which is outside the scope of NLP model extraction. Ignoring it is the simplest solution.
