# Robert MCP: GAMS Error 171 — Subset/Superset Index Mismatch in stat_x

**GitHub Issue:** [#766](https://github.com/jeffreyhorn/nlp2mcp/issues/766)
**Status:** OPEN
**Severity:** High — MCP generates but GAMS reports Error 171 (domain violation), aborting solve
**Date:** 2026-02-16
**Affected Models:** robert

---

## Problem Summary

The robert model (`data/gamslib/raw/robert.gms`) generates an MCP file, but GAMS reports
Error 171 (domain violation for set) when compiling the generated MCP:

```
stat_x(p,tt)$(t(tt)).. ((-1) * c(p,tt)) + sum(r, a(r,p) * nu_sb(r,tt)) + sum(t, lam_cc(t)) =E= 0;
                                           $171
**** 171  Domain violation for set
**** 2 ERROR(S)   0 WARNING(S)
**** SOLVE from line ... ABORTED
```

---

## Original Model Structure

Robert is a linear production-planning/inventory model:

```gams
Set
   tt    'long horizon'  / 1*4 /
   t(tt) 'short horizon' / 1*3 /;  * t is a SUBSET of tt

* Key equations:
cc(t)..      sum(p, x(p,t)) =l= m;          * Capacity constraint over subset t
sb(r,tt+1).. s(r,tt+1) =e= s(r,tt) - sum(p, a(r,p)*x(p,tt));  * Stock balance over full tt
pd..         profit =e= sum(t, sum(p, c(p,t)*x(p,t))           * Objective uses subset t
                           - sum(r, misc("storage-c",r)*s(r,t)));

* Variable domains:
x(p,tt)  'production and sales'   * declared over FULL tt
s(r,tt)  'opening stocks'         * declared over FULL tt

* Parameter c uses SUBSET t:
Table c(p,t) 'expected profits'   * declared over SUBSET t, not full tt
```

---

## Root Cause

`x(p,tt)` is declared over the full horizon `tt`, but used in the objective `pd` as `x(p,t)`
(using the subset `t`). When the AD differentiates `pd` w.r.t. `x(p,tt)`, it produces a
derivative that references `c(p,t)` — using `t` (subset) as the index, while the stationarity
equation `stat_x` is declared over `tt` (superset).

The sum `sum(t, lam_cc(t))` in `stat_x(p,tt)` is also problematic: `lam_cc` is the multiplier
for `cc(t)` (declared over subset `t`), and summing it with the set name `t` inside an equation
declared over `tt` causes GAMS Error 171 (domain violation — `t` is not a free index in the
context of `stat_x(p,tt)`).

**Specifically:**
1. `stat_x(p,tt)` uses `c(p,tt)` in the generated output — but `c` is declared over `(p,t)`,
   so `c(p,tt)` is a domain violation (tt contains elements not in t)
2. `sum(t, lam_cc(t))` inside `stat_x(p,tt)` — `t` is used as an iteration set, but GAMS
   may interpret this as a set name collision with the domain dimension

This is the **subset/superset index mismatch variant** of ISSUE_670 mentioned in
`docs/planning/EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md` (robert section).

---

## Generated MCP (Problem Lines)

```gams
* Multiplier declaration:
Variable lam_cc(t)    -- declared over subset t

* Stationarity equation for x (declared over tt):
stat_x(p,tt)$(t(tt)).. ((-1) * c(p,tt)) + sum(r, a(r,p) * nu_sb(r,tt))
                        + sum(t, lam_cc(t)) =E= 0;
                               ****$171 -- domain violation: c(p,tt) but c declared over (p,t)
```

The `$(t(tt))` condition correctly restricts the equation to instances where `tt ∈ t`, but:
- `c(p,tt)` still uses `tt` as index while `c` is declared over `(p,t)` → GAMS 171
- The `sum(t, ...)` may also trigger domain issues in the scope of `stat_x(p,tt)`

---

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/robert.gms -o /tmp/robert_mcp.gms

# Run GAMS:
gams /tmp/robert_mcp.gms lo=2

# Expected errors:
# stat_x(p,tt)$(t(tt)).. ... c(p,tt) ...
#                             $171
# **** 171  Domain violation for set
# **** SOLVE from line ... ABORTED
```

---

## Suggested Fix

**Option A: Index substitution in derivative expressions**

When the AD produces `c(p,tt)` from differentiating `pd` (which uses `c(p,t)`) w.r.t.
`x(p,tt)`, the index replacement should recognize that `c` is declared over `(p,t)` and
map `tt` → `t` in the parameter reference. Since `stat_x` is conditioned on `$(t(tt))`,
the correct index for `c` is `tt` restricted to `t`, which is simply `tt` with a domain
guard — GAMS allows `c(p,tt)` if `tt ∈ t`.

**Fix:** In `_replace_indices_in_expr()`, when a parameter's declared domain is a subset
of the equation's domain (e.g., `c` declared over `t` but equation over `tt`), emit the
parameter with the superset index but rely on the `$(subset(superset))` condition that
`_find_variable_subset_condition` or similar logic already generates.

**Option B: Declare lam_cc over tt instead of t**

Declare `lam_cc(tt)` (multiplier for the full tt horizon) with a `.fx(tt)$(not t(tt)) = 0`
fixing statement for terminal-period instances. This would allow `sum(t, lam_cc(t))` to
become `sum(tt, lam_cc(tt))` and avoid the domain issue.

**Option C: Use t explicitly in stat_x**

Since `stat_x(p,tt)$(t(tt))` is only generated for `tt ∈ t`, rewrite as `stat_x(p,t)` with
domain `t` instead of `tt`. Then `c(p,t)` and `sum(t, lam_cc(t))` are both valid.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/kkt/stationarity.py` | `_replace_indices_in_expr()` — subset/superset mapping |
| `src/kkt/stationarity.py` | `_find_variable_subset_condition()` — already handles subset domain restriction |
| `src/emit/emit_gams.py` | Multiplier declaration domain generation |
| `data/gamslib/raw/robert.gms` | Original model with t(tt) subset structure |

---

## Related Issues

- **ISSUE_670**: Cross-indexed sums (Error 149) — this is the subset/superset variant
  described in the ISSUE_670 design doc (robert section)
- **ISSUE_759**: stat_u domain restriction — similar subset detection mechanism
- The fix for this issue may generalize to other models where parameter domains use
  subset indices while variable domains use the superset
