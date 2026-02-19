# IndexOffset End-to-End Pipeline Audit

**Date:** 2026-02-19
**Branch:** `planning/sprint20-task2`
**Auditor:** Sprint 20 Prep Task 2

---

## Executive Summary

Of the 8 IndexOffset-blocked models, **5 now translate successfully** (launch, mine,
ampl, robert, pak) — meaning Sprint 19 AD work unblocked them further than expected.
The remaining **3 models** (sparta, tabora, otpop) are still blocked in the **translation pipeline** due to
two distinct `IndexOffset.to_gams_string()` gaps that surface at different stages (emit vs. stationarity/index replacement):

1. **sparta / tabora**: `Unary("-", Call(ord, ...))` — unary minus over a complex
   `Call()` operand inside an `IndexOffset` offset. The `to_gams_string()` method
   handles `Unary("-", SymbolRef)` and `Unary("-", Const)` but not `Unary("-", Call)`.
2. **otpop**: `Binary(-, Call(card, ...), Call(ord, ...))` — a binary arithmetic
   expression inside an `IndexOffset` offset. `to_gams_string()` has no `Binary` case
   and raises `NotImplementedError("Complex offset expressions not yet supported")`.

The xfail test (`test_diff_sum_over_t_with_lead`) is a **cleanup item**, not a
critical-path blocker for any of the 8 models.

The emit layer (`_format_mixed_indices`) **fully supports** circular lead/lag (++ / --)
via `idx.to_gams_string()` — the gap is in `IndexOffset.to_gams_string()` itself.

**Revised effort estimate: ~3h** (down from ~4h original estimate).

---

## Per-Model Status Table

| Model   | Pre-Sprint19 Status     | Current Stage  | Error / Token                                           | Remaining Work                                              | Est. Hours |
|---------|------------------------|----------------|---------------------------------------------------------|-------------------------------------------------------------|------------|
| launch  | parse=success, solve=failure | ✅ **translate success** | —                                               | None — translate now works; solve failure is PATH issue     | 0h         |
| mine    | parse=failure          | ✅ **translate success** | —                                               | None — now parses and translates successfully               | 0h         |
| ampl    | parse=success, translate=not_tested | ✅ **translate success** | —                                    | None — translate now works                                  | 0h         |
| robert  | parse=success, solve=failure | ✅ **translate success** | —                                           | None — translate now works; solve failure is PATH issue     | 0h         |
| pak     | parse=success, solve=failure | ✅ **translate success** | —                                           | None — translate now works; solve failure is PATH issue     | 0h         |
| sparta  | parse=failure          | ❌ **emit failure**      | `NotImplementedError: Unary minus with complex operand not supported: Call(ord, (SymbolRef(l)))` | Extend `IndexOffset.to_gams_string()` for `Unary("-", Call(...))` | 1h |
| tabora  | parse=failure          | ❌ **emit failure**      | `NotImplementedError: Unary minus with complex operand not supported: Call(ord, (SymbolRef(a)))` | Same fix as sparta                                          | 0.5h (shared fix) |
| otpop   | parse=failure          | ❌ **stationarity/index-replacement failure** | `NotImplementedError: Complex offset expressions not yet supported: Binary(-, Call(card, (SymbolRef(t))), Call(ord, (SymbolRef(t))))` | Extend `IndexOffset.to_gams_string()` for `Binary(op, Call, Call)` offset expressions | 1h |

**Notes on "translate success" models:**
- `launch`, `robert`, `pak` previously showed `solve=failure` in the status file. These
  are PATH solver infeasibility issues unrelated to IndexOffset — the MCP translation
  itself succeeds.
- `mine` previously showed `parse=failure` (pre-Sprint 19 grammar gap now fixed).
- `ampl` previously showed `translate=not_tested` (cascading failure now resolved).

---

## Failure Analysis

### sparta and tabora: `Unary("-", Call(...))` in IndexOffset offset

**GAMS source patterns:**
- `sparta.gms:57`: `x(t-(ord(l)-1), ...)` — lag by `ord(l)-1`, which is `-(ord(l)-1)`
- `tabora.gms`: similar pattern with `ord(a)`

**IR representation:**  
The parser produces `IndexOffset(base='t', offset=Unary("-", Call(ord, (SymbolRef(l)))), circular=False)`.

**Current `to_gams_string()` behaviour:**  
Handles `Unary("-", SymbolRef)` and `Unary("-", Const)` but not `Unary("-", Call(...))`.
The `else` branch raises:
```
NotImplementedError: Unary minus with complex operand not supported: Call(ord, (SymbolRef(l)))
```

**Fix required:**  
Extend the `Unary("-", ...)` branch in `IndexOffset.to_gams_string()` (src/ir/ast.py:384)
to handle the case where the inner operand is a `Call(...)`. The emitted string would be
`t-(ord(l)-1)` — i.e., fall back to a generic arithmetic expression. This requires either:
- Calling `expr_to_gams()` on the offset expression, or
- Adding a `Call` case that delegates to a string-formatted sub-expression.

**Risk:** Medium — requires careful handling of operator precedence and parenthesization.

---

### otpop: `Binary(-, Call, Call)` in IndexOffset offset

**GAMS source pattern:**
- `otpop.gms:101`: `p(t + (card(t) - ord(t)))` — lead by `card(t)-ord(t)` elements

**IR representation:**  
`IndexOffset(base='t', offset=Binary(-, Call(card, (SymbolRef(t))), Call(ord, (SymbolRef(t)))), circular=False)`

**Current `to_gams_string()` behaviour:**  
The `else` branch catches this and raises:
```
NotImplementedError: Complex offset expressions not yet supported: Binary(-, Call(card, (SymbolRef(t))), Call(ord, (SymbolRef(t))))
```

**Note:** This fails at the AD/stationarity stage (`src/kkt/stationarity.py:962`), not
the emit stage — `indices_as_strings()` is called during index replacement, earlier than
`_format_mixed_indices`.

**Fix required:**  
Extend `IndexOffset.to_gams_string()` to handle `Binary(op, Call, Call)` by delegating
offset serialization to a recursive expression-to-string helper. The emitted string would
be `t+(card(t)-ord(t))`.

**Risk:** Medium-High — `ord()` and `card()` offsets are runtime-dynamic (set-dependent),
so the MCP translation may produce index expressions that are correct syntactically but
semantically depend on set ordering. Need to verify GAMS PATH solver accepts such indexing.

---

## xfail Test Assessment

**Test:** `tests/unit/ad/test_index_offset_ad.py::TestDifferentiateWithIndexOffset::test_diff_sum_over_t_with_lead`

**What it tests:** When differentiating `sum(t, x(t+1))` w.r.t. `x(t1+1)`, the sum
should collapse to `1` (only the `t=t1` term contributes). Currently, `_sum_should_collapse()`
and `_is_concrete_instance_of()` expect `str` wrt-indices, not `IndexOffset`.

**Status:** `xfail strict=True` — currently passes as expected-failure.

**Affects which of the 8 models?** None directly. The xfail is triggered when
differentiating equations that contain `Sum(domain, VarRef(x, IndexOffset(...)))` with
respect to an `IndexOffset` wrt-index. For the 3 failing models (sparta, tabora, otpop),
the failures occur _before_ AD reaches sum-collapse (sparta/tabora fail at emit, otpop
fails at stationarity index replacement).

**Recommendation:** **Cleanup item, not critical path.** Fix after sparta/tabora/otpop
are unblocked. If left as xfail, it means sum-collapse doesn't fire for lead/lag
equations — differentiation still works correctly (returns a sum of zero terms rather
than a collapsed constant), just not as efficiently.

**Priority:** Low — schedule in Sprint 20 alongside the `to_gams_string()` fixes, but
not a blocker.

---

## Emit Layer: Circular Lead/Lag Assessment

**Question:** Does `_format_mixed_indices()` correctly handle circular lead/lag (`++`/`--`)?

**Answer:** **Yes, fully supported.**

`_format_mixed_indices()` (src/emit/expr_to_gams.py:223) delegates directly to
`idx.to_gams_string()` for any `IndexOffset` it encounters. The `to_gams_string()` method
in `IndexOffset` handles all circular cases:

| Pattern | Offset | circular | Output |
|---------|--------|----------|--------|
| `i++1`  | `Const(1)` | `True` | `"i++1"` |
| `i--2`  | `Const(-2)` | `True` | `"i--2"` |
| `i++j`  | `SymbolRef("j")` | `True` | `"i++j"` |
| `i--j`  | `Unary("-", SymbolRef("j"))` | `True` | `"i--j"` |

The unit tests in `tests/unit/emit/test_expr_to_gams.py::TestIndexOffset` cover all four
patterns and all pass.

**Circular lead/lag is NOT a blocker for any of the 8 models.** sparta and tabora use
linear offsets (`t-(ord(l)-1)`), not circular (`t--`). otpop uses linear offsets too.

---

## Revised Effort Estimate

| Task | Estimate | Notes |
|------|----------|-------|
| Extend `to_gams_string()` for `Unary("-", Call(...))` (sparta, tabora) | 1h | Fix + test |
| Extend `to_gams_string()` for `Binary(op, Call, Call)` (otpop) | 1h | Fix + test; may need recursive helper |
| Verify sparta/tabora solve (PATH) | 0.5h | Run after fix and check solver output |
| Fix xfail sum-collapse (cleanup) | 0.5h | Low priority; can defer |
| **Total** | **~3h** | Down from ~4h original estimate |

**Models already unblocked:** launch, mine, ampl, robert, pak — no IndexOffset work needed.

---

## Appendix: Pipeline Run Evidence

Run date: 2026-02-19 on branch `planning/sprint20-task2`.

```
$ python -m src.cli data/gamslib/raw/launch.gms 2>&1 | tail -3
Solve mcp_model using MCP;
Scalar nlp2mcp_obj_val;
nlp2mcp_obj_val = cost.l;
# Exit code: 0

$ python -m src.cli data/gamslib/raw/mine.gms 2>&1 | tail -3
Solve mcp_model using MCP;
Scalar nlp2mcp_obj_val;
nlp2mcp_obj_val = profit.l;
# Exit code: 0

$ python -m src.cli data/gamslib/raw/ampl.gms 2>&1 | tail -3
Solve mcp_model using MCP;
Scalar nlp2mcp_obj_val;
nlp2mcp_obj_val = profit.l;
# Exit code: 0

$ python -m src.cli data/gamslib/raw/robert.gms 2>&1 | tail -3
Solve mcp_model using MCP;
Scalar nlp2mcp_obj_val;
nlp2mcp_obj_val = profit.l;
# Exit code: 0

$ python -m src.cli data/gamslib/raw/pak.gms 2>&1 | tail -3
Solve mcp_model using MCP;
Scalar nlp2mcp_obj_val;
nlp2mcp_obj_val = w.l;
# Exit code: 0

$ python -m src.cli data/gamslib/raw/sparta.gms 2>&1
# Skipping parameter 'rep': declared without domain...
Error: Unexpected error - Unary minus with complex operand not supported: Call(ord, (SymbolRef(l)))
# Exit code: 1

$ python -m src.cli data/gamslib/raw/tabora.gms 2>&1
# Skipping parameter 'rep1': declared without domain...
Error: Unexpected error - Unary minus with complex operand not supported: Call(ord, (SymbolRef(a)))
# Exit code: 1

$ python -m src.cli data/gamslib/raw/otpop.gms 2>&1 | grep "Error:"
Error: Unexpected error - Complex offset expressions not yet supported: Binary(-, Call(card, (SymbolRef(t))), Call(ord, (SymbolRef(t))))
# Exit code: 1
```

**Stack trace summary for sparta/tabora:**
```
src/emit/expr_to_gams.py:223 _format_mixed_indices
  → idx.to_gams_string()
  → src/ir/ast.py:384 IndexOffset.to_gams_string
  → NotImplementedError: Unary minus with complex operand not supported
```

**Stack trace summary for otpop:**
```
src/kkt/stationarity.py:962 _replace_indices_in_expr
  → var_ref.indices_as_strings()
  → src/ir/ast.py:389 IndexOffset.to_gams_string
  → NotImplementedError: Complex offset expressions not yet supported
```
