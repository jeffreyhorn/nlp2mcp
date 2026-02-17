# Abel MCP: nu_stateq Declared Over Full (n,k) Domain Despite stateq Conditional Restricting to ku

**GitHub Issue:** [#760](https://github.com/jeffreyhorn/nlp2mcp/issues/760)
**Status:** OPEN
**Severity:** High — MCP generates but GAMS aborts with EXECERROR = 3
**Date:** 2026-02-16
**Affected Models:** abel, qabel (same structure)

---

## Problem Summary

The abel model (`data/gamslib/raw/abel.gms`) generates an MCP file without Error 149
(after the ISSUE_670 Day 5 fix), but GAMS aborts during the solve with:

```
**** Unmatched free variables = 2
     nu_stateq(consumpt,1965-iv)
     nu_stateq(invest,1965-iv)
**** SOLVE from line 122 ABORTED, EXECERROR = 3
```

---

## Original Model Structure

```gams
Set
   k   'horizon'  / 1964-i, 1964-ii, 1964-iii, 1964-iv, 1965-i, 1965-ii, 1965-iii, 1965-iv /
   ku(k) 'control horizon'   -- all k except terminal: 1964-i .. 1965-iii
   n   'states'   / consumpt, invest /;

* stateq is conditionally defined — only for k in ku:
stateq(n,k)$(ord(k) <= card(k) - 1).. x(n,k+1) =e= sum(np, a(n,np)*x(np,k))
    + sum(m, b(n,m)*u(m,k)) + c(n);
```

The equation `stateq(n,k)` is conditional and only generates rows for `k ∈ ku`. The multiplier
`nu_stateq(n,k)` is therefore declared over a larger domain than the equation it multiplies.

---

## Root Cause

The multiplier declaration uses the full declared domain of `stateq` (i.e., `(n,k)`) without
accounting for the `$(ord(k) <= card(k) - 1)` conditional. GAMS generates `stateq` equations
only for `k ∈ ku`, but `nu_stateq(n,1965-iv)` exists as a free variable with no matching
equation — GAMS reports it as an unmatched free variable.

---

## Reproduction

```bash
# Generate MCP (requires ISSUE_670 Day 5 fix in place)
python -m src.cli data/gamslib/raw/abel.gms -o /tmp/abel_mcp.gms

# Run GAMS:
gams /tmp/abel_mcp.gms lo=2

# Expected errors in abel_mcp.lst:
# **** Unmatched free variables = 2
#      nu_stateq(consumpt,1965-iv)
#      nu_stateq(invest,1965-iv)
# **** SOLVE from line 122 ABORTED, EXECERROR = 3
```

---

## Generated MCP (Relevant Sections)

```gams
* Multiplier declared over full domain:
Variable nu_stateq(n,k)   -- should be nu_stateq(n,ku) to match stateq conditional

* Equation with conditional (restricts to ku):
stateq(n,k)$(ord(k) <= card(k) - 1).. x(n,k+1) =E= sum(np, a(n,np)*x(np,k))
    + sum(m, b(n,m)*u(m,k)) + c(n);

* MCP model pairing (mismatch):
Model mcp_model /
    stateq.nu_stateq  -- stateq over ku, nu_stateq over full k: terminal k unmatched
/;
```

---

## Suggested Fix

When a constraint is conditionally defined (e.g., `stateq(n,k)$(ord(k) <= card(k) - 1)`),
the corresponding multiplier should be declared with the same conditional domain restriction.

Options:
- Declare `nu_stateq(n,ku)` using the named subset `ku` (if the conditional maps to a known subset); or
- Apply the same `$(ord(k) <= card(k) - 1)` conditional when declaring the multiplier and in
  the MCP model statement pairing.

The subset `ku(k)` is already defined in the original model and represents `ord(k) <= card(k) - 1`.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/kkt/stationarity.py` or `src/kkt/complementarity.py` | Multiplier declaration domain generation |
| `src/emit/model.py` | MCP model statement emission |
| `src/emit/emit_gams.py` | Variable declaration emission |
| `data/gamslib/raw/abel.gms` | Original model with `ku(k)` subset and `stateq` conditional |

---

## Related Issues

- **ISSUE_670**: Cross-indexed sums (Error 149) — prior blocker now fixed
- **ISSUE_759**: Companion issue — `stat_u` domain not restricted to match `u`'s effective domain
- `qabel.gms` has the same structure and will have the same issue
