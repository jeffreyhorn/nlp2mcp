# Abel MCP: nu_stateq Declared Over Full (n,k) Domain Despite stateq Conditional Restricting to ku

**GitHub Issue:** [#760](https://github.com/jeffreyhorn/nlp2mcp/issues/760)
**Status:** FIXED (sprint19-day6-issue759-760-abel-domain-fix)
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

## Fix

**File:** `src/emit/emit_gams.py`

Added a new block (block 3) after the existing inequality multiplier `.fx` section that handles
equality multipliers whose equation has lead/lag restrictions.

The fix detects lead/lag `IndexOffset` nodes in the equation body using
`_collect_lead_lag_restrictions()` (imported from `src.emit.equations`), infers the active
domain condition via `_build_domain_condition()`, and emits a `.fx` statement to fix the
out-of-domain multiplier instances to zero.

```python
# 3. Fix equality multipliers (nu_*) whose equation has lead/lag restrictions.
for eq_name in sorted(kkt.model_ir.equalities):
    ...
    inferred_cond = _build_domain_condition(lead_offsets, lag_offsets)
    ...
    fx_lines.append(f"{mult_name}.fx({domain_str})$(not ({inferred_cond})) = 0;")
```

### Result

```gams
* Before fix:
Variable nu_stateq(n,k)   -- declared over full (n,k), terminal k unmatched

* After fix:
nu_stateq.fx(n,k)$(not (ord(k) <= card(k) - 1)) = 0;
```

This fixes the terminal-period `nu_stateq` instances to zero, eliminating the unmatched free
variable error.

---

## Generated MCP (Fixed)

```gams
* Multiplier still declared over full domain (avoids subset remapping issues):
Variable nu_stateq(n,k)

* Terminal-period multiplier instances fixed to zero:
nu_stateq.fx(n,k)$(not (ord(k) <= card(k) - 1)) = 0;
```

---

## Solve Result (After Both Fixes)

```
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      1 Optimal
```

---

## Related Issues

- **ISSUE_670**: Cross-indexed sums (Error 149) — prior blocker now fixed
- **ISSUE_759**: Companion issue — `stat_u` domain not restricted to match `u`'s effective domain
  (fixed in same branch)
- `qabel.gms` has the same structure and will benefit from the same fix
