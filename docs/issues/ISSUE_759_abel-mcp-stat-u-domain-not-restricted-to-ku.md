# Abel MCP: stat_u Generated Over Full Domain But u Only Active at ku Subset

**GitHub Issue:** [#759](https://github.com/jeffreyhorn/nlp2mcp/issues/759)
**Status:** OPEN
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

## Generated MCP (Relevant Sections)

```gams
* Equation declared over full domain:
Equations
    stat_u(m,k)      -- should be stat_u(m,ku) to match u's effective domain

* stat_u equation body (zero at terminal period):
stat_u(m,k).. sum(n, ((-1) * b(n,m)) * nu_stateq(n,k)) =E= 0;

* MCP model pairing:
Model mcp_model /
    stat_u.u,       -- stat_u(m,k) paired with u(m,k): terminal k unmatched
/;
```

---

## Suggested Fix

In `src/kkt/stationarity.py`, detect variable instances with zero Jacobian contributions (i.e.,
no constraints reference those instances). Add a conditional to restrict the stationarity equation
to the effective domain:

```gams
stat_u(m,k)$(ku(k)).. sum(n, ...) =E= 0;
```

Or restrict the `stat_u` equation domain at generation time by examining which variable instances
actually appear in constraints (examining the Jacobian contributions built by
`_add_indexed_jacobian_terms()`).

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/kkt/stationarity.py` | `build_stationarity_equations()` — stationarity domain generation; `_add_indexed_jacobian_terms()` — detect zero-Jacobian instances |
| `data/gamslib/raw/abel.gms` | Original model with `ku(k)` subset |

---

## Related Issues

- **ISSUE_670**: Cross-indexed sums (Error 149) — prior blocker now fixed
- **ISSUE_760**: Companion issue — `nu_stateq` domain not restricted to match `stateq` conditional
- `qabel.gms` has the same structure and will have the same issue
