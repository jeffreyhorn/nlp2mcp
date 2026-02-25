# Worst: Expression-Based Variable Bounds Not Emitted

**GitHub Issue:** [#873](https://github.com/jeffreyhorn/nlp2mcp/issues/873)
**Status:** OPEN
**Severity:** High — Model translates but GAMS compilation fails (path_syntax_error)
**Date:** 2026-02-25
**Affected Models:** worst

---

## Problem Summary

The worst model translates to MCP but the emitted GAMS code fails compilation with 4 errors.
Variables `r(t)` and `q(t)` have expression-based `.lo`/`.up` bounds in the original model
(e.g., `r.lo(t) = tdata(t,"rmin")`), but the emitter only outputs `.l` initialization that
references those bounds. Since the bounds themselves are never emitted, GAMS raises $141
"Symbol declared but no values assigned" on `r.lo(t)` and `q.lo(t)`.

---

## Error Details

**GAMS $141 errors (4 total):**

```
  79  r.l(t) = (r.lo(t) + r.up(t)) / 2;
****               $141
  81  q.l(t) = (q.lo(t) + q.up(t)) / 2;
****               $141
```

The `.l` expressions reference `.lo` and `.up` which were never assigned.

Additionally, $257 (solve not checked) and a post-solve $141 on `pval.l` are cascading errors.

---

## Root Cause

Two separate bugs prevent expression-based bounds from reaching the emitted MCP code:

### Bug 1: Parser discards expression-based `.lo`/`.up`/`.fx` bounds

In `src/ir/parser.py`, `_handle_variable_attribute_assignment()` calls `_extract_constant()`
to get a numeric value for the bound. When the RHS is an expression (like `tdata(t,"rmin")`),
`_extract_constant()` returns `None`. For `.l` assignments, the parser stores the expression
in `l_expr_map`. But for `.lo`, `.up`, and `.fx` bounds, the parser simply returns without
storing:

```python
# Current code (simplified):
if bound_kind == "l":
    var_def.l_expr_map[key] = expr  # stored!
else:
    return  # .lo/.up/.fx expression silently discarded!
```

The `VariableDef` dataclass has `lo_map`/`up_map`/`fx_map` for numeric bounds but has no
expression-based storage for `.lo`/`.up`/`.fx` (unlike `.l` which has both `l`/`l_map` and
`l_expr`/`l_expr_map`).

### Bug 2: Emitter has no code to emit `.lo`/`.up`/`.fx` bound assignments

Even if the parser stored expression-based bounds, `src/emit/emit_gams.py` only uses
`lo_map`/`up_map` to initialize `.l` values via clamping expressions. It never emits
standalone bound assignment statements like `r.lo(t) = tdata(t,"rmin");`.

---

## Reproduction Steps

```bash
python -m src.cli data/gamslib/raw/worst.gms -o /tmp/worst_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/worst_mcp.gms action=c
# Expect: 4 errors ($141 on r.lo, q.lo, $257, pval.l)
```

---

## Original GAMS Code

```gams
Positive Variable
    r(t)     'risk free rate'
    q(t)     'volatility';

r.lo(t) = tdata(t,"rmin");    * expression-based lower bound
r.up(t) = tdata(t,"rmax");    * expression-based upper bound
q.lo(t) = tdata(t,"qmin");    * expression-based lower bound
q.up(t) = tdata(t,"qmax");    * expression-based upper bound

r.l(t) = (r.lo(t) + r.up(t))/2;
q.l(t) = (q.lo(t) + q.up(t))/2;
```

---

## Suggested Fix

1. **VariableDef**: Add `lo_expr`/`lo_expr_map`, `up_expr`/`up_expr_map`, and
   `fx_expr`/`fx_expr_map` fields (mirroring `l_expr`/`l_expr_map`).

2. **Parser**: In `_handle_variable_attribute_assignment()`, when `_extract_constant()`
   returns `None` for `.lo`/`.up`/`.fx`, store the expression in the new expr_map fields
   instead of discarding.

3. **Emitter**: Add a "Variable Bounds" section before the `.l` initialization section that
   emits `var.lo(idx) = expr;` and `var.up(idx) = expr;` for all expression-based bounds.

**Effort estimate:** ~3-4h

---

## Files That Need Changes

| File | Change |
|------|--------|
| `src/ir/model_ir.py` | Add `lo_expr`/`lo_expr_map`/`up_expr`/`up_expr_map`/`fx_expr`/`fx_expr_map` to `VariableDef` |
| `src/ir/parser.py` | Store expression-based bounds in new fields instead of discarding |
| `src/emit/emit_gams.py` | Emit `.lo`/`.up`/`.fx` bound assignments before `.l` initialization |

---

## Related Issues

- **Issue #863** (resolved): worst table data not emitted for f0/pdata (fixed in this branch)
