# Abel MCP: stat_u Generated Over Full Domain But u Only Active at ku Subset

**GitHub Issue:** [#759](https://github.com/jeffreyhorn/nlp2mcp/issues/759)
**Status:** FIXED (sprint19-day6-issue759-760-abel-domain-fix)
**Severity:** High — MCP generates but GAMS aborts with EXECERROR = 3
**Date:** 2026-02-16
**Affected Models:** abel, qabel (same structure)

---

## Problem Summary

The abel model (`data/gamslib/raw/abel.gms`) generates an MCP file without Error 149
(after the ISSUE_670 Day 5 fix), but GAMS aborts during the solve with:

```
**** MCP pair stat_u.u has unmatched equation
     stat_u(gov-expend,1965-iv)
**** MCP pair stat_u.u has unmatched equation
     stat_u(money,1965-iv)
**** SOLVE from line 122 ABORTED, EXECERROR = 3
```

---

## Original Model Structure

```gams
Set
   k   'horizon'  / 1964-i, 1964-ii, 1964-iii, 1964-iv, 1965-i, 1965-ii, 1965-iii, 1965-iv /
   ku(k) 'control horizon'   -- all k except terminal: 1964-i .. 1965-iii
   m   'controls' / gov-expend, money /;

Variable u(m,k) 'control variable';   -- declared over full (m,k)

* u is only used in stateq at k in ku:
stateq(n,k+1).. x(n,k+1) =e= sum(np, a(n,np)*x(np,k)) + sum(m, b(n,m)*u(m,k)) + c(n);
* Implicitly stateq(n, ku) since k+1 only exists for k in ku.
```

The variable `u(m,k)` is declared over full `k` but is only used at `k ∈ ku`. The stationarity
equation `stat_u(m,k)` therefore needs to be restricted to `ku` as well.

---

## Root Cause

The stationarity builder generates `stat_u(m,k)` over the full declared domain of `u`, which is
`(m,k)`. But `u(m,k)` is only referenced in constraints at `k ∈ ku`. There are no constraints
that reference `u(m,1965-iv)`, so the Jacobian contribution at the terminal period is zero.
The stationarity equation `stat_u(m,1965-iv)` then has only zeros in it — but the MCP still
tries to pair it with `u(m,1965-iv)`, which GAMS rejects because there's no matching equation.

The specific challenges:
1. `u(m,ku)` appears directly in `criterion` with the subset index `ku`.
2. `u(m,k)` also appears in `stateq(n,k+1)` with the plain declared index `k` — but `stateq`
   itself only generates rows for `k ∈ ku` due to the lead `k+1` restriction.
3. An alias `mp` (alias for `m`) is used in `criterion` as `u(mp,ku)`.

The original `_find_variable_subset_condition` function:
- Didn't resolve aliases (`mp` treated differently from `m`)
- Didn't detect that `u(m,k)` in `stateq` is implicitly restricted to `ku` (via the lead `k+1`)
- Didn't traverse VarRef indices when collecting lead/lag restrictions (since `VarRef.children()`
  doesn't yield indices)

---

## Reproduction

```bash
# Generate MCP (requires ISSUE_670 Day 5 fix in place)
python -m src.cli data/gamslib/raw/abel.gms -o /tmp/abel_mcp.gms

# Run GAMS:
gams /tmp/abel_mcp.gms lo=2

# Expected errors in abel_mcp.lst:
# **** MCP pair stat_u.u has unmatched equation
#      stat_u(gov-expend,1965-iv)
# **** MCP pair stat_u.u has unmatched equation
#      stat_u(money,1965-iv)
# **** SOLVE from line 122 ABORTED, EXECERROR = 3
```

---

## Fix

**File:** `src/kkt/stationarity.py`

Added `_find_variable_subset_condition()` and integrated it as a fallback after
`_find_variable_access_condition()` returns `None`.

Key changes:
1. **Alias resolution**: Built an `alias_to_canonical` map from `model_ir.aliases` and resolve
   both actual and declared indices through it before comparing. This treats `u(mp,ku)` as
   equivalent to `u(m,ku)`.

2. **Lead/lag restriction detection**: Before walking each equation's expressions, collect the
   domain indices that appear inside `IndexOffset` nodes (e.g., `k` in `x(n,k+1)`). These are
   stored in `restricted_by_eq`. The key fix: `VarRef.children()` does NOT yield indices, so
   the collection function explicitly iterates `VarRef.indices`.

3. **Skip declared-index accesses in restricted equations**: When `_walk_expr` encounters
   `u(m,k)` and `k` is in `restricted_by_eq`, the plain declared-index access is treated as
   "not evidence that the full domain is needed" rather than setting `pos_subsets[pos] = None`.

4. **`_walk_expr` signature**: Updated to accept `skip_declared_at: frozenset[str]` and pass
   it through recursive calls.

### Result

```gams
* Before fix:
stat_u(m,k).. sum(n, ((-1) * b(n,m)) * nu_stateq(n,k)) =E= 0;

* After fix:
stat_u(m,k)$(ku(k)).. sum(n, ((-1) * b(n,m)) * nu_stateq(n,k)) =E= 0;
u.fx(m,k)$(not (ku(k))) = 0;
```

---

## Generated MCP (Fixed)

```gams
* Stationarity restricted to ku:
stat_u(m,k)$(ku(k)).. sum(n, ((-1) * b(n,m)) * nu_stateq(n,k)) =E= 0;

* Terminal-period u instances fixed to zero:
u.fx(m,k)$(not (ku(k))) = 0;
```

---

## Related Issues

- **ISSUE_670**: Cross-indexed sums (Error 149) — prior blocker now fixed
- **ISSUE_760**: Companion issue — `nu_stateq` domain not restricted to match `stateq` conditional
  (fixed in same branch)
- `qabel.gms` has the same structure and will benefit from the same fix
