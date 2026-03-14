# catmix: Regression — skip_lead_lag_inference Removes Essential Domain Restriction

**GitHub Issue:** [#1084](https://github.com/jeffreyhorn/nlp2mcp/issues/1084)
**Status:** OPEN
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

## Reproduction

```bash
python -m src.cli data/gamslib/raw/catmix.gms -o /tmp/catmix_mcp.gms
gams /tmp/catmix_mcp.gms lo=2
# **** MODEL STATUS      5 Locally Infeasible
# 101 INFEASIBLE (INFES)
```

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

### What the MCP Emits

**Before PR #1076 (correct):**
```gams
ode1(i)$(ord(i) <= card(i) - 1).. x1(i+1) =E= x1(i) + ...;
nu_ode1.fx(i)$(not (ord(i) <= card(i) - 1)) = 0;
```

**After PR #1076 (broken):**
```gams
ode1(i).. x1(i+1) =E= x1(i) + ...;
```

The `$(ord(i) <= card(i) - 1)` guard and multiplier fixups were removed.

### Code Location

**File:** `src/emit/equations.py:469`
```python
eq_str, aliases = emit_equation_def(eq_name, eq_def, skip_lead_lag_inference=True)
```

PR #1076 added `skip_lead_lag_inference=True` for all original equality equations to fix
whouse (where lag references in the body should NOT restrict the domain). But this is a
blanket flag that also disables inference for catmix-style equations where the lead offset
appears in the **equation head domain**, genuinely restricting which instances are generated.

### Why whouse Needed the Change

In whouse, `sb(t).. stock(t) =e= stock(t-1) + ...` — GAMS evaluates `stock(t-1)` as 0
when `t` is the first element (default .l value), so the equation IS generated for all `t`.
The old inference incorrectly added `$(ord(t) > 1)`.

### Why catmix Breaks

In catmix, `ode1(nh(i+1))..` — the `nh(i+1)` is a domain qualifier, not just a body
reference. GAMS genuinely skips instances where `i+1 ∉ nh`. The IR loses this information
(`domain=('i',), condition=None`), so lead/lag inference was the only way to reconstruct it.

---

## Suggested Fix

**Option A (Recommended):** Distinguish head-domain offsets from body-only offsets. Restore
lead/lag inference for equations whose head domain originally had lead/lag qualifiers. This
requires the IR parser to record when the equation head used `eq(set(i+1))` vs just `eq(i)`.

**Option B:** Capture the domain qualifier in the IR. Store `ode1(nh(i+1))` as having an
explicit condition equivalent to `$(ord(i) <= card(i) - 1)`. This is the most robust fix
but requires parser changes.

**Option C:** Distinguish lead vs lag. Restore inference for lead offsets (positive, like
`i+1`) while keeping `skip_lead_lag_inference` for lag offsets (negative, like `t-1`).

---

## Shared Pattern

This same root cause affects **hydro** (#1087) and **pindyck** (#1088), which also have
lag-domain equations (`flow(tt-1)..`, `tdeq(t-1)..`) that lose their domain restriction.

## Files to Modify

| File | Change |
|------|--------|
| `src/emit/equations.py:469` | Make `skip_lead_lag_inference` conditional on head-domain offset |
| `src/ir/parser.py` | (Option B) Capture head-domain offsets in EquationDef |
