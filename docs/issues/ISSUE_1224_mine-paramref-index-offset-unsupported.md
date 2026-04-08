# mine: Parameter-Valued Index Offsets Unsupported

**GitHub Issue:** [#1224](https://github.com/jeffreyhorn/nlp2mcp/issues/1224)
**Status:** OPEN — Translation failure (unsupported offset expression)
**Severity:** Medium — Translation aborts with internal error
**Date:** 2026-04-07
**Last Updated:** 2026-04-07
**Affected Models:** mine

---

## Problem Summary

The mine model (GAMSlib SEQ=39, "Opencast Mining") uses parameter-valued index
offsets in equation `pr`: `x(l, i+li(k), j+lj(k))` where `li(k)` and `lj(k)`
are parameters that provide the offset amount. The AD engine and index mapping
code only support constant integer offsets (e.g., `i+1`, `t-2`) and fail with
"Complex offset expressions not yet supported: ParamRef(li(k))".

---

## Root Cause

The equation `pr` uses parameter-dependent offsets:

```gams
Set k 'neighbors' / ne, se, sw, nw /;
Parameter
   li(k) 'lead for i' / (se,sw) 1 /
   lj(k) 'lead for j' / ("ne",se) 1 /;

pr(k,l+1,i,j)$c(l,i,j).. x(l,i+li(k),j+lj(k)) =g= x(l+1,i,j);
```

The offset `i+li(k)` is not a constant — it depends on the value of parameter
`li` at index `k`. For `k=se`, `li(se)=1` so the offset is `i+1`; for `k=ne`,
`li(ne)=0` so the offset is `i+0` (i.e., just `i`). The grammar parses this
as `IndexOffset(base="i", offset=ParamRef("li", ("k",)))`, but the AD engine
expects `offset` to be a `Const` (integer literal).

Additionally, the equation condition `$c(l,i,j)` references a 3-dimensional
subset `c` that has no concrete members at compile time (dynamically computed),
causing a separate warning about unevaluable set membership.

---

## Reproduction

```bash
# Translate — fails with internal error
.venv/bin/python -m src.cli data/gamslib/raw/mine.gms -o /tmp/mine_mcp.gms --quiet

# Error output:
# Error: Unexpected error - Complex offset expressions not yet supported: ParamRef(li(k))
```

---

## Error Details

```
Error: Unexpected error - Complex offset expressions not yet supported: ParamRef(li(k))
```

Also emits warning:
```
Failed to evaluate condition SetMembershipTest(c, (SymbolRef(l), SymbolRef(i), SymbolRef(j)))
with indices ('nw', '1', '1', '1'): Set membership for 'c' cannot be evaluated statically
because the set has no concrete members at compile time.
```

---

## Potential Fix Approaches

1. **Enumerate parameter-valued offsets**: For each value of `k`, evaluate
   `li(k)` and `lj(k)` at parse time and expand the equation into separate
   instances with constant offsets. E.g., for `k=se`: `x(l, i+1, j+1)`,
   for `k=ne`: `x(l, i+0, j+1)`, etc. This requires the parameter values
   to be known at IR build time.

2. **Support ParamRef offsets in IndexOffset**: Extend `IndexOffset.offset`
   to accept `Expr` (not just `Const`) and propagate through AD and
   stationarity building. This is a significant architectural change.

3. **Partial support with concrete expansion**: If the parameter has known
   concrete values and the set is small, expand each `(k, offset_value)`
   combination into separate equation instances with constant offsets.
   Handles mine's case (4 neighbors) without general ParamRef offset support.

---

## Files Involved

- `src/ir/ast.py` — `IndexOffset` definition (offset field type)
- `src/ad/constraint_jacobian.py` — Offset expression validation
- `src/ir/parser.py` — Index offset parsing
- `data/gamslib/raw/mine.gms` — Original model (80 lines)
