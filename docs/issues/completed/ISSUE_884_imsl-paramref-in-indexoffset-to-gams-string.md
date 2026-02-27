# imsl: ParamRef Not Handled in IndexOffset._offset_expr_to_string()

**GitHub Issue:** [#884](https://github.com/jeffreyhorn/nlp2mcp/issues/884)
**Status:** RESOLVED
**Severity:** Medium — Model parses but translation fails
**Date:** 2026-02-25
**Affected Models:** imsl
**Sprint:** 21 (Day 4 blocker)

---

## Problem Summary

The `imsl.gms` model parses successfully (Sprint 21 Day 4 lead/lag fix) but fails during translation (emitter stage). The `IndexOffset._offset_expr_to_string()` method does not handle `ParamRef` nodes, raising `NotImplementedError` when trying to serialize an offset expression that references a scalar parameter.

---

## Error Details

```
NotImplementedError: Unsupported offset expression type 'ParamRef' in IndexOffset: ParamRef(k)
```

### Full Traceback

```
File "src/emit/original_symbols.py", line 1276, in emit_computed_parameter_assignments
    idx.to_gams_string()
File "src/ir/ast.py", line 501, in to_gams_string
    offset_str = self._offset_expr_to_string(self.offset)
File "src/ir/ast.py", line 343, in _offset_expr_to_string
    args_str = ",".join(self._offset_expr_to_string(arg) for arg in expr.args)
File "src/ir/ast.py", line 364, in _offset_expr_to_string
    right_str = self._offset_expr_to_string(expr.right, parent_op=expr.op, is_right=True)
File "src/ir/ast.py", line 391, in _offset_expr_to_string
    raise NotImplementedError(
        "Unsupported offset expression type 'ParamRef' in IndexOffset: ParamRef(k)"
    )
```

---

## Root Cause

GAMS source line 40 of `imsl.gms`:

```gams
w(m+floor((ord(n)-1)/k),n)$(ord(m) = 1) = 1 - mod(ord(n)-1,k)/k;
```

Here `k` is a scalar parameter (declared at line 29). It appears inside the index offset expression `m+floor((ord(n)-1)/k)`. The parser correctly creates:

```
IndexOffset(
    base='m',
    offset=Call('floor', (
        Binary('/',
            Binary('-', Call('ord', (SymbolRef('n'),)), Const(1.0)),
            ParamRef(k)
        )
    )),
    circular=False
)
```

The `_offset_expr_to_string()` method in `src/ir/ast.py` handles `Const`, `SymbolRef`, `Call`, `Unary`, and `Binary` expression types, but has no case for `ParamRef`. When the emitter calls `to_gams_string()` on this `IndexOffset`, the recursive descent hits `ParamRef(k)` with no handler.

---

## Reproduction

```python
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
from src.emit.gams_emitter import emit_gams
m = parse_model_file('data/gamslib/raw/imsl.gms')
result = emit_gams(m)  # raises NotImplementedError
```

---

## Fix

Add a `ParamRef` handler to `_offset_expr_to_string()` in `src/ir/ast.py`, between the existing `SymbolRef` handler (line 340) and the `Call` handler (line 342):

```python
elif isinstance(expr, ParamRef):
    if expr.indices:
        idx_str = ",".join(
            self._offset_expr_to_string(i) if not isinstance(i, str) else i
            for i in expr.indices
        )
        return f"{expr.name}({idx_str})"
    return expr.name
```

This produces `k` for scalar `ParamRef(k)` and `p(i,j)` for indexed `ParamRef(p, ('i','j'))`.

Expected emitted output for line 40:
```gams
w(m+floor((ord(n)-1)/k),n) = 1 - mod(ord(n)-1,k)/k;
```

**Estimated effort:** 30min–1h (handler + unit test)

---

## GAMS Source Context

```gams
Scalar
   k     'n / m'
   deltn 'data increments'
   deltm 'approximation increment';

k = (card(n) - 1) / (card(m) - 1);

w(m+floor((ord(n)-1)/k),n)$(ord(m) = 1) = 1 - mod(ord(n)-1,k)/k;
w(m+1,n)$w(m,n) = 1 - w(m,n);
```

---

## Resolution

This issue was already fixed in commit b94ab2ba (PR #883 review comments), which added `ParamRef` and `VarRef` handlers to `IndexOffset._offset_expr_to_string()`. The imsl model now parses and translates successfully (`python -m src.cli data/gamslib/raw/imsl.gms` produces MCP output without errors).

## Related Issues

- Sprint 21 Day 4 PR #883: Lead/lag in parameter assignment LHS (parsing fix)
- The `$(ord(m) = 1)` dollar condition on the parameter assignment is a separate concern (whether dollar conditions on computed parameter assignments are preserved in the emitter)
