# srpchase: Set assignment with arithmetic index offset on LHS

**GitHub Issue:** [#976](https://github.com/jeffreyhorn/nlp2mcp/issues/976)
**Model:** srpchase (GAMSlib SEQ=356, "Scenario Tree Construction Example")
**Error category:** `internal_error`
**Error message:** `Parameter 'ancestor' not declared [context: expression] (line 39, column 1)`

## Description

The parser fails when a set assignment uses an arithmetic index offset expression on the LHS. In `ancestor(n,n-card(leaf))$stage(n,'t3') = yes;`, the second index `n-card(leaf)` is an `IndexOffset` expression. The parser's assignment handler detects the `IndexOffset`, skips the set assignment path, and falls through to the parameter check, which fails because `ancestor` is a set.

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/srpchase.gms')
"
```

## Relevant Code

### Set declaration (lines 22-27)

```gams
Set
   n             'nodes'            / n0*n%DIM% /
   t             'time periods'     / t1*t3     /
   stage(n,t)    'stage mapping'
   ancestor(n,n) 'ancestor matrix'
   leaf(n)       'leaf nodes';
```

### Failing line (lines 38-39)

```gams
* Build ancestor relations to represent the fan
ancestor(n,'n0')$stage(n,'t2')         = yes;
ancestor(n,n-card(leaf))$stage(n,'t3') = yes;
```

Line 38 works because both indices are simple (`n` and `'n0'`). Line 39 fails because the second index `n-card(leaf)` is parsed as an `IndexOffset` with a `card()` function call as the offset expression.

## Root Cause

In `src/ir/parser.py`, the `_handle_assign()` method (around line 4214) checks:

```python
has_lead_lag = any(isinstance(idx, IndexOffset) for idx in indices)
```

When `has_lead_lag` is `True`, the code skips the set assignment branch (`if symbol_name in self.model.sets and not has_lead_lag`) and falls through to the parameter assignment branch, which raises `Parameter 'ancestor' not declared` because `ancestor` is a set, not a parameter.

The assumption that `IndexOffset` indices cannot appear in set assignments is incorrect. GAMS allows set assignments with computed indices like `ancestor(n,n-card(leaf)) = yes;`.

## Additional Blockers

Even after fixing this issue, srpchase has additional blockers:

1. **Undeclared scenred library symbols**: The model uses `$libInclude scenred` (stripped by preprocessor) which defines `ScenRedParms`, `ancestor` modifications, and `tree_con`. These are referenced at lines 77-82 but some are never declared locally.

## Fix Approach

Modify the `_handle_assign()` method in `src/ir/parser.py` to allow `IndexOffset` indices in set assignments. The `has_lead_lag` flag should not prevent the set assignment path from being taken. Instead, set assignments with `IndexOffset` indices should store the assignment with the offset expression preserved (similar to how variable `.l` expressions handle `IndexOffset` keys in `l_expr_map`).

Possible implementation:
1. Remove the `and not has_lead_lag` guard from the set assignment condition
2. Handle `IndexOffset` indices in set assignments — store them as dynamic set membership operations
3. Alternatively, convert `IndexOffset` indices to expression-based set assignments

## Related Issues

- [#895](https://github.com/jeffreyhorn/nlp2mcp/issues/895) — srpchase: original `$libInclude`/`File`/`putClose` issue (partially resolved)
- [#888](https://github.com/jeffreyhorn/nlp2mcp/issues/888) — clearlak: `$libInclude scenred` (fixed)
