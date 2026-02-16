# Differentiation fails for `sameas()` function (lop)

**GitHub Issue:** [#733](https://github.com/jeffreyhorn/nlp2mcp/issues/733)
**Status:** Fixed
**Severity:** Medium -- Blocks MCP translation of lop model (after Issue #732 fix)
**Discovered:** 2026-02-15 (Sprint 19, after Issue #732 fixed domain mismatch)
**Fixed:** 2026-02-15 (Sprint 19)
**Affected Models:** lop, and potentially asyncloop, cesam, circpack, gqapsdp, popdynm, sddp, sroute (8 gamslib models use `sameas`)

---

## Problem Summary

The lop model fails during differentiation with:

```
Error: Invalid model - Differentiation not yet implemented for function 'sameas'.
```

After Issue #732 fixed the domain mismatch, the pipeline advances to the differentiation stage where `sameas(s,s1)` in the `balance` equation is not recognized by the derivative rule engine.

---

## Root Cause

`sameas`, `card`, and `ord` are GAMS set operations that are constant with respect to decision variables. They had no entry in `src/ad/derivative_rules.py`, causing the differentiation engine to raise an error.

- `sameas(a,b)` = Kronecker delta (0 or 1 based on set element identity)
- `card(s)` = cardinality of set s
- `ord(s)` = ordinal position of set element

Since none of these depend on decision variables, their derivatives are always 0.

---

## Fix

Added `sameas`, `card`, and `ord` as zero-derivative functions in `_diff_call()` in `src/ad/derivative_rules.py`:

```python
elif func in ("sameas", "card", "ord"):
    return Const(0.0)
```

Also updated the error message's supported functions list to include the new functions.

---

## Additional Context

- The `balance` equation containing `sameas` belongs to model `sp` (LP), not an NLP model
- After this fix, lop advances past differentiation but the full KKT assembly takes a long time due to the model's size (many indexed variables across multiple models)
- The fix also benefits other gamslib models that use `card` or `ord` in equations
