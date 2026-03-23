# fawley: Empty mbal Equation — SetMembershipTest Condition Evaluation Failure

**GitHub Issue:** [#1133](https://github.com/jeffreyhorn/nlp2mcp/issues/1133)
**Status:** OPEN
**Severity:** High — GAMS aborts SOLVE with EXECERROR=1
**Date:** 2026-03-22
**Affected Models:** fawley (and potentially any model with 2D set membership conditions)

---

## Problem Summary

The fawley model (`data/gamslib/raw/fawley.gms`) translates to MCP, but GAMS aborts
the SOLVE with `EXECERROR = 1` due to:

```
MCP pair mbal.nu_mbal has empty equation but associated variable is NOT fixed
```

Some instances of `mbal(c)` become empty equations (0 = 0) because the translator
cannot evaluate `SetMembershipTest` conditions used by the `pbal` equation, causing
the KKT system to include incorrect equation instances.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/fawley.gms -o /tmp/fawley_mcp.gms
gams /tmp/fawley_mcp.gms lo=2
# Expected: "MCP pair mbal.nu_mbal has empty equation but associated variable is NOT fixed"
# SOLVE ABORTED, EXECERROR = 1
```

---

## Root Cause

### The pbal Equation's 2D Set Condition

The `pbal` equation (line 237 of fawley.gms) has a 2D set membership condition:

```gams
pbal(cfq,m)$cfm(cfq,m).. q(cfq,m) =e= sum(c$bposs(cfq,c), char(c,m)*bq(c,cfq));
```

The condition `$cfm(cfq,m)` is a 2-dimensional `SetMembershipTest`. The set `cfm` is
computed at runtime:

```gams
cfm(cf,m) = sum((l,s)$specs(cf,l,s), ms(m,s));
cfm(cf,"weight") = yes;
```

### Condition Evaluation Failure

The translator's condition evaluator (`src/ir/condition_eval.py`, line ~310) raises:

```
Unsupported expression type SetMembershipTest in condition
```

when trying to evaluate `cfm(cfq,m)` at translate time. The fallback behavior
(`src/ad/index_mapping.py`, lines ~393-403) includes ALL instances instead of
filtering by the condition. This means equation instances that should be excluded
(where `cfm(cfq,m)` is false) are included in the KKT system.

### Cascade to mbal

The `mbal` equation is unconditional:

```gams
mbal(c).. u(c)$cr(c) + sum(p, ap(c,p)*z(p)) + sum(tr, at(c,tr)*trans(tr)) + import(c)$ci(c)
    =e= sum(cfq$bposs(cfq,c), bq(c,cfq)) + invent(c) + sum((cfr,r), recipes(cfr,c,r)*rb(cfr,r));
```

For commodities not in any blending or recipe relationship, `mbal(c)` evaluates to
`0 =E= 0` (empty equation). The MCP pairs `mbal.nu_mbal` but `nu_mbal(c)` is not
fixed to zero for these empty instances, causing the GAMS runtime error.

### Key Sets

- `cfm(cf,m)`: 2D set — quality-blended products × measures (runtime computed)
- `cfq(cf)`: Quality-blended products (subset of cf; `cfq = not cfr`)
- `cfr(cf)`: Recipe-blended products (computed from `recipes` data)
- `bposs(cf,c)`: Blending possibilities (explicit data)

---

## Suggested Fix

Two complementary approaches:

### Approach 1: Support SetMembershipTest in condition_eval.py

Add support for evaluating `SetMembershipTest` conditions in
`src/ir/condition_eval.py`. When the referenced set has been computed (via
assignment), look up whether the tuple `(cfq_val, m_val)` is a member. This
requires tracking runtime-computed set memberships in the IR.

### Approach 2: Fix empty MCP equation handling

In the MCP emitter, detect equations that evaluate to `0 =E= 0` (empty equations)
and either:
- Skip them from the MCP pairing
- Fix the associated multiplier variable to zero (`nu_mbal.fx(c) = 0`)

This is a safety net that would help with any future condition evaluation failures.

---

## Verification Plan

```bash
python -m src.cli data/gamslib/raw/fawley.gms -o /tmp/fawley_mcp.gms
gams /tmp/fawley_mcp.gms lo=2
# Should: No "empty equation" error, SOLVE proceeds
```

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/ir/condition_eval.py` ~line 310 | `SetMembershipTest` not supported |
| `src/ad/index_mapping.py` ~lines 393-403 | Fallback includes all instances on condition failure |
| `src/emit/emit_gams.py` | MCP equation pairing — could detect/skip empty equations |
| `src/kkt/stationarity.py` | KKT assembly — could skip equations with unresolvable conditions |
