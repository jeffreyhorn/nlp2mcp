# Plan: Fix twocge Compilation Errors (#906)

**Goal:** Fix `ord(JPN)` compilation errors in twocge stationarity equations
so the model compiles and reaches PATH solver.

**Estimated effort:** 2-3 hours
**Models unblocked:** twocge

---

## Current State (Sprint 24)

Two of the three original issues are RESOLVED by prior fixes:
- **USA SAM data**: ✅ FIXED — 60 values (30 JPN + 30 USA) correctly captured
- **Post-solve code ordering**: ✅ FIXED — percentage-change assignments no
  longer emitted before solve

**Remaining:** 4 compilation errors (Error 140/154/198/651) from `ord(JPN)`
in stationarity equations.

---

## Problem: `ord(JPN)` in Stationarity

### Affected Equations

Four stationarity equations contain `ord(JPN) <> ord(JPN)`:
- `stat_e(i,r)`: `sum(rr, 1$(ord(JPN) <> ord(JPN)) * nu_eqw(i,r,rr))`
- `stat_m(i,r)`: `sum(rr, (-1)$(ord(JPN) <> ord(JPN)) * nu_eqw(i,r,rr))`
- `stat_pwe(i,r)`: `sum(rr, 1$(ord(JPN) <> ord(JPN)) * nu_eqpw(i,r,rr))`
- `stat_pwm(i,r)`: `sum(rr, (-1)$(ord(JPN) <> ord(JPN)) * nu_eqpw(i,r,rr))`

### GAMS Errors

- **Error 651**: `ord` can only be referenced with a 1-dimensional set
  (`JPN` is an element, not a set)
- **Error 140**: Unknown symbol
- **Error 154**: Set for 'ord' is not controlled
- **Error 198**: Set used in 'ord' is not ordered

### Root Cause

The original trade equations use `$(ord(r) <> ord(rr))`:

```gams
eqpw(i,r,rr).. (pWe(i,r) - pWm(i,rr))$(ord(r) <> ord(rr)) =e= 0;
eqw(i,r,rr)..  (E(i,r) - M(i,rr))$(ord(r) <> ord(rr)) =e= 0;
```

The equation body is `DollarConditional(expr, Binary(<>, Call(ord, r), Call(ord, rr)))`.

When the stationarity builder processes `∂eqw/∂e(i,r)`, the Jacobian term
carries the condition `$(ord(r) <> ord(rr))`. During `_replace_indices_in_expr`,
the symbolic `r` gets replaced with the concrete element `JPN` (from element-
to-set mapping). But `ord(JPN)` is invalid GAMS — `ord()` requires a set
variable, not a concrete element.

### Where the Substitution Happens

In `_replace_indices_in_expr` (stationarity.py), the `Call("ord", ...)` handler
(added in Sprint 24 Day 8 for #1178) remaps concrete elements to equation-domain
set names. But this handler only fires for the equation domain indices — `r` and
`rr` are from the CONSTRAINT domain, not the stationarity equation domain (`i`,
`r`). The `rr` index is NOT in the stationarity equation domain.

Specifically:
- Stationarity equation domain: `stat_e(i, r)` — indices `i`, `r`
- Constraint domain: `eqw(i, r, rr)` — indices `i`, `r`, `rr`
- The `sum(rr, ...)` wraps the multiplier term and binds `rr`
- Inside the sum, `ord(r)` should stay as `ord(r)` (it's in the stationarity domain)
- `ord(rr)` should stay as `ord(rr)` (it's bound by the enclosing sum)
- But `_replace_indices_in_expr` maps `r` → `JPN` and `rr` → `JPN` (concrete elements)

The existing ord() handler checks:
1. If the argument is a concrete element → map to equation domain
2. If the argument is a set/alias → check subset relationships

For `r`: it's in the stationarity domain `(i, r)` so it should stay as `r`.
But the `element_to_set` mapping has `JPN → r`, suggesting `r` was already
substituted to `JPN` BEFORE reaching the ord() handler.

The substitution `r → JPN` happens in `_substitute_sum_indices` during AD
sum collapse, or in `_replace_indices_in_expr`'s VarRef/ParamRef handling.
The ord() handler then tries to reverse-map `JPN` back to `r`, which should
work for `ord(r)` but fails for `ord(rr)` because `rr` is also mapped to `JPN`
and the handler picks the wrong domain variable.

### Key Insight

Both `r` and `rr` map to `JPN` (same element). The ord() handler maps `JPN`
back to the equation domain, but there's only one `r` in the domain —
`rr` is a sum variable, not an equation domain variable. The handler can't
distinguish between `r` (domain) and `rr` (sum-bound) when both map to
the same concrete element.

---

## Fix Approach

### Option A: Preserve ord() arguments during index substitution (~2h)

**Principle:** Don't substitute SymbolRef arguments inside `Call("ord", ...)`
and `Call("card", ...)` when the argument is a set/alias name that's bound
by the enclosing sum or the equation domain.

**Implementation:**

1. In `_replace_indices_in_expr`, the `Call("ord", ...)` handler already
   checks `bound_index_names` (from ChainMap) and `is_set_or_alias`. The
   issue is that the `ord(r)` and `ord(rr)` arguments arrive as
   `SymbolRef("JPN")` instead of `SymbolRef("r")` — the substitution
   happened upstream.

2. The fix should be in the **upstream substitution** — prevent
   `_substitute_sum_indices` from replacing `SymbolRef` inside `Call("ord")`
   and `Call("card")`. This was partially done in Sprint 24 Day 8 (the
   `card/ord` special case in `_apply_index_substitution`), but the
   existing handler only skips SymbolRef DIRECTLY inside `Call("card"/
   "ord")`, not SymbolRef inside nested expressions like
   `Binary(<>, Call(ord, SymbolRef(r)), Call(ord, SymbolRef(rr)))`.

3. Check: does the `_apply_index_substitution` `Call("card"/"ord")` handler
   from #1178 handle this case? It should — the `SymbolRef("r")` is
   directly inside `Call("ord", SymbolRef("r"))`.

4. If the upstream handler works correctly, the issue is that the
   substitution happens AFTER `_apply_index_substitution` — perhaps in
   `_replace_indices_in_expr` itself.

**Investigation needed:** Trace exactly WHERE `r` → `JPN` substitution
happens for the `ord(r)` argument. Add debug logging to
`_replace_indices_in_expr` for the twocge model and check:
- Does `ord(r)` arrive at `_replace_indices_in_expr` with `SymbolRef("r")`
  or `SymbolRef("JPN")`?
- If `SymbolRef("JPN")`, which upstream step substituted it?

### Option B: Fix ord() handler to recognize sum-bound elements (~1h)

If the substitution is in `_replace_indices_in_expr` itself (not upstream),
fix the `ord()` handler to also recognize names bound by enclosing `Sum`
nodes (via ChainMap detection) and map them to the correct sum variable
instead of the equation domain.

---

## Reproduction

**Prerequisite:** GAMSlib raw sources must be downloaded into `data/gamslib/raw/`
(run `python scripts/gamslib/download_models.py`).

```bash
.venv/bin/python -m src.cli data/gamslib/raw/twocge.gms -o /tmp/twocge_mcp.gms --quiet
gams /tmp/twocge_mcp.gms lo=0

# Errors:
# stat_e(i,r).. ... sum(rr, 1$(ord(JPN) <> ord(JPN)) * nu_eqw(i,r,rr)) ...
#                                  $140,198,651,154,198,651,154
```

## Files to Modify

| File | Change |
|------|--------|
| `src/kkt/stationarity.py` | `_replace_indices_in_expr` ord() handler |
| `src/ad/derivative_rules.py` | Possibly `_apply_index_substitution` card/ord handler |

## Risk Assessment

**Medium risk:** The ord() handler is shared by all models. Changes must
not break the otpop fix (#1178) or the himmel16 alias protection.

## Verification

1. twocge compiles (no Error 651)
2. otpop still compiles (regression check)
3. himmel16 still solves correctly (regression check)
4. `make test` passes
