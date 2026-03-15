# catmix: Regression — skip_lead_lag_inference Removes Essential Domain Restriction

**GitHub Issue:** [#1084](https://github.com/jeffreyhorn/nlp2mcp/issues/1084)
**Status:** FIXED
**Severity:** High — model_optimal regressed to model_infeasible
**Date:** 2026-03-14
**Affected Models:** catmix
**Regressing PR:** #1076 (Sprint 22 Day 7 WS3)

---

## Problem Summary

The catmix model (GAMSlib SEQ=242, "Catalyst Mixing" COPS benchmark) regressed from
model_optimal to model_infeasible after PR #1076 introduced `skip_lead_lag_inference=True`
for original equality equations.

The equations `ode1(nh(i+1))` and `ode2(nh(i+1))` use a lead offset `i+1` in the equation
**head domain**, which restricts generation to 100 instances (i=0..99, excluding i=100).
The IR stores only `domain=('i',), condition=None`, losing the lead offset. Previously,
the emitter's lead/lag inference reconstructed the restriction from body IndexOffset nodes.
PR #1076 disabled this inference, causing all 101 instances to be generated.

---

## Root Cause

### Original GAMS

```gams
Set nh / 0*100 /;  Alias(nh,i);
Equation ode1(nh), ode2(nh);
ode1(nh(i+1)).. x1(i+1) =e= x1(i) + 0.5*h*(...);
ode2(nh(i+1)).. x2(i+1) =e= x2(i) + 0.5*h*(...);
```

`ode1(nh(i+1))` means: only generate for `i` where `i+1 ∈ nh`. This excludes `i=100`
(since `101 ∉ nh`), producing exactly 100 equations.

### Why catmix Breaks

In catmix, `ode1(nh(i+1))..` — the `nh(i+1)` is a domain qualifier, not just a body
reference. GAMS genuinely skips instances where `i+1 ∉ nh`. The IR loses this information
(`domain=('i',), condition=None`), so lead/lag inference was the only way to reconstruct it.

---

## Fix Applied

Implemented **Option A** — distinguish head-domain offsets from body-only offsets:

1. **`src/ir/symbols.py`**: Added `has_head_domain_offset: bool = False` field to
   `EquationDef` dataclass.

2. **`src/ir/parser.py`**: Added `_domain_list_has_offset()` helper that inspects the
   parse tree for `linear_lead`/`linear_lag` suffixes in domain elements (both direct
   like `i+1` and nested like `nh(i+1)`). Called in `_handle_eqn_def_domain()` to set
   the flag on `EquationDef`.

3. **`src/emit/equations.py`**: Changed the blanket `skip_lead_lag_inference=True` to
   `skip_lead_lag_inference=not eq_def.has_head_domain_offset`. Equations with head-domain
   offsets now restore lead/lag inference; equations without (like whouse's `sb(t)`) still
   skip it.

4. **`src/emit/emit_gams.py`**: Added section 3a for equality multiplier fixups — when
   an equation has `has_head_domain_offset=True` and no explicit condition, the inferred
   lead/lag condition is used to generate `.fx` fixups for the multiplier (e.g.,
   `nu_ode1.fx(i)$(not (ord(i) <= card(i) - 1)) = 0`).

### Verification

- catmix: `ode1(i)$(ord(i) <= card(i) - 1)..` guard restored, `nu_ode1.fx` fixup present
- whouse: `sb(t)..` still has NO guard (correct — GAMS evaluates stock(t-1) as 0)
- All 4173 tests pass

---

## Files Modified

| File | Change |
|------|--------|
| `src/ir/symbols.py` | Added `has_head_domain_offset` field to `EquationDef` |
| `src/ir/parser.py` | Added `_domain_list_has_offset()` helper; set flag in `_handle_eqn_def_domain()` |
| `src/emit/equations.py` | Made `skip_lead_lag_inference` conditional on `has_head_domain_offset` |
| `src/emit/emit_gams.py` | Added section 3a for head-domain-offset multiplier fixups |
