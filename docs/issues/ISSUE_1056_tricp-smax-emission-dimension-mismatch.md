# tricp: smax Emission Dimension Mismatch in Variable Bounds

**GitHub Issue:** [#1056](https://github.com/jeffreyhorn/nlp2mcp/issues/1056)
**Status:** OPEN
**Severity:** High — path_syntax_error, model fails to compile
**Date:** 2026-03-11
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

Both the variable bound assignment (`x.up`) and the corresponding upper bound complementarity equation (`comp_up_x`) contain the same incorrect `smax` syntax.

---

## Root Cause

In the original GAMS model:
```gams
x.up(n,k) = myScale*smax((i,kp),fx(i,kp));
```

The `smax` function takes a **tuple domain** `(i,kp)` as its first argument. The correct GAMS syntax is `smax((i,kp), fx(i,kp))` — note the double parentheses creating a tuple.

The emitter is serializing the domain as `smax(i, kp, fx(i,kp))` — flattening the tuple into separate arguments. GAMS interprets this as `smax(i, kp)` with `fx(i,kp)` as a dangling expression, causing the parse errors.

This is a bug in the expression emitter's handling of `smax`/`smin` multi-index domains. The domain tuple must be wrapped in an extra set of parentheses.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/tricp.gms -o /tmp/tricp_mcp.gms
gams /tmp/tricp_mcp.gms lo=2
# Error $148,$8 at x.up and comp_up_x lines
```

---

## Proposed Fix

In the GAMS expression emitter, when serializing `smax`/`smin` expressions with multi-index domains, wrap the domain in parentheses:

**Current (incorrect):**
```
smax(i, kp, fx(i,kp))
```

**Correct:**
```
smax((i,kp), fx(i,kp))
```

The fix is likely in `src/kkt/emitter.py` or `src/ir/gams_writer.py` — wherever `smax_expr`/`smin_expr` AST nodes are serialized. When the domain has more than one index, the indices must be grouped in parentheses.

---

## Related

- #933 tricp translation timeout (different issue — about translation time, now resolved by timeout increase)
- This is a pre-existing issue on main; re-translation with current code exposes the bug
