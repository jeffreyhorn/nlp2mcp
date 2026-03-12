# tricp: smax Emission Dimension Mismatch in Variable Bounds

**GitHub Issue:** [#1056](https://github.com/jeffreyhorn/nlp2mcp/issues/1056)
**Status:** FIXED
**Severity:** High — path_syntax_error, model fails to compile
**Date:** 2026-03-11
**Fixed:** 2026-03-12
**Affected Models:** tricp

---

## Problem Summary

The tricp model's generated MCP file incorrectly emits `smax(i, kp, fx(i,kp))` instead of `smax((i,kp), fx(i,kp))` in variable bound expressions. GAMS expects `smax` to take exactly two arguments: a domain and an expression. The emitter is splitting the tuple domain `(i,kp)` into separate arguments, causing GAMS error $148 (dimension mismatch) and $8 (')' expected).

---

## Error Details

GAMS compilation errors:
```
x.up(n,k) = myScale * smax(i, kp, fx(i,kp));
                                  $148,8,409
****   8  ')' expected
**** 148  Dimension different - The symbol is referenced with more/less indices as declared
**** 409  Unrecognizable item

comp_up_x(n,k).. myScale * smax(i, kp, fx(i,kp)) - x(n,k) =G= 0;
                                       $148,8,37,409
```

---

## Root Cause

The parser stores `smax((i,kp), fx(i,kp))` as `Call("smax", (SymbolRef("i"), SymbolRef("kp"), body_expr))` — domain indices are flattened into the args tuple. The generic `Call` handler in `expr_to_gams()` joins all args with commas: `smax(i, kp, fx(i,kp))`. For multi-index domains, GAMS requires tuple parentheses: `smax((i,kp), fx(i,kp))`.

---

## Fix

**File:** `src/emit/expr_to_gams.py` — `expr_to_gams()` Call handler (~line 578)

Added special handling for `smax`/`smin` Call nodes: collect leading `SymbolRef` args as domain indices, wrap multiple indices in tuple parentheses, and separate from the body expression.

```python
if func in ("smax", "smin") and len(args) >= 2:
    # Collect leading SymbolRef args as domain indices
    domain_indices = []
    for arg in args:
        if isinstance(arg, SymbolRef):
            domain_indices.append(arg.name)
        else:
            break
    if domain_indices:
        remaining = args[len(domain_indices):]
        if len(domain_indices) == 1:
            idx_str = domain_indices[0]
        else:
            idx_str = "(" + ",".join(domain_indices) + ")"
        body_str = expr_to_gams(remaining[-1], ...)
        return f"{func}({idx_str}, {body_str})"
```

---

## Verification

After fix:
```
x.up(n,k) = myScale * smax((i,kp), fx(i,kp));     # multi-index: tuple parens
x.l(n,k) = myScale * uniform(0, smax(i, fx(i,k))); # single-index: no extra parens
comp_up_x(n,k).. myScale * smax((i,kp), fx(i,kp)) - x(n,k) =G= 0;
```

- No $148/$8 compilation errors
- Model compiles and reaches the solver
- Remaining errors (760 unmatched variables) are a separate issue (#1062)
- Quality gate: 4141 tests pass, typecheck/lint/format clean

---

## Related

- #1062 tricp: Unmatched variables slp/sln (separate issue — MCP matching)
- #933 tricp: Translation timeout (resolved)
