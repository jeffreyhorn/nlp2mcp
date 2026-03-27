# camshape: MCP Pairing Error — stat_rdiff.rdiff Unmatched Equation

**GitHub Issue:** [#1160](https://github.com/jeffreyhorn/nlp2mcp/issues/1160)
**Status:** FIXED
**Severity:** High — MCP solve aborted (EXECERROR)
**Date:** 2026-03-26
**Affected Models:** camshape

---

## Problem Summary

After fixing the GAMS $141 compilation error (PR #1159), camshape now compiles but fails at solve time with "MCP pair stat_rdiff.rdiff has unmatched equation". This means the stationarity equation `stat_rdiff` and the variable `rdiff` have mismatched dimensions in the MCP model.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/camshape.gms -o /tmp/camshape_mcp.gms --skip-convexity-check
gams /tmp/camshape_mcp.gms lo=2
```

**GAMS output:**
```
**** MCP pair stat_rdiff.rdiff has unmatched equation
**** SOLVE from line 291 ABORTED, EXECERROR = 1
```

---

## Root Cause Analysis

The `rdiff` variable in camshape is declared over the full domain `i`:

```gams
Variable rdiff(i);
```

However, `rdiff` only has bounds assigned via a subset restriction:

```gams
rdiff.lo(i(j+1)) = -alpha*d_theta;
rdiff.up(i(j+1)) =  alpha*d_theta;
```

The `i(j+1)` subset means `rdiff` only has active instances for `i` values where `j+1` exists (i.e., all but the first element, since `j` is an alias of `i` and `j+1` is a lead operation).

The stationarity equation `stat_rdiff(i)` is generated for the full domain `i` (100 elements), but the MCP pairing expects the equation and variable to have the same number of active instances. Since `rdiff` is only active for 99 elements (due to the `j+1` subset), there's a dimension mismatch.

### Key Details

1. **Variable domain:** `rdiff(i)` — full domain, 100 elements
2. **Active instances:** Only 99 (those where `i(j+1)` is valid)
3. **Stationarity equation:** `stat_rdiff(i)` — 100 elements (full domain)
4. **MCP pairing:** `stat_rdiff.rdiff` — 100 vs 99 → unmatched

---

## Expected Behavior

The stationarity equation `stat_rdiff` should either:
1. Be conditioned to match the same subset as `rdiff`'s active instances (skip the first element), OR
2. The MCP pairing should use the subset domain `i(j+1)` for both the equation and variable

---

## Affected Files

- `src/kkt/assemble.py` — MCP pairing logic
- `src/kkt/stationarity.py` — Stationarity equation domain computation
- `src/emit/emit_gams.py` — MCP model block emission

---

## Fix Approach

1. Detect when a variable's bounds are only set for a subset of its declared domain
2. Propagate the effective domain (subset) to the stationarity equation
3. Condition the MCP pairing to use the subset domain
4. Alternatively, fix the variable instances to exclude elements without bounds

**Effort estimate:** 3-4 hours

---

## Investigation (2026-03-26)

After PR #1161 (moving stationarity conditions to body), the `stat_rdiff.rdiff` pairing error persists but for a different reason than originally diagnosed.

**Updated root cause:** The actual equation/variable count mismatch (601 eq vs 603 var, 2 projected) comes from multiplier `.fx` lines fixing excluded instances of conditional constraint multipliers (`nu_eqrdiff`, `lam_convexity`, etc.). These `.fx` reduce the variable count without correspondingly reducing equation count.

The `rdiff` variable itself has no KKT-level bounds because `rdiff.lo(i(j))` and `rdiff.up(i(j))` use `SubsetIndex(i(j))` which the KKT pipeline skips: `"Variable 'rdiff' lo_expr_map key (SubsetIndex(i(j)),) contains IndexOffset/SubsetIndex; only plain-string domain indices are supported in KKT pipeline. Skipping."` This means no `comp_lo_rdiff`/`comp_up_rdiff` equations are generated.

**Fix applied:** Added section 1b in the emitter's `.fx` generation that checks equality constraints referencing conditioned primal variables for lead/lag conditions. When `eqrdiff(i)$((j(i)) and (ord(i) <= card(i) - 1))` has a lead/lag condition `ord(i) <= card(i) - 1` that excludes terminal instances, the emitter now generates `rdiff.fx(i)$(not (ord(i) <= card(i) - 1)) = 0` to fix `rdiff(i100)`.

Combined with PR #1161's stationarity condition-to-body approach, the MCP pairing mismatch is fully resolved:
- `stat_rdiff(i)` — 100 instances (unconditional, body handles condition via DollarConditional)
- `rdiff(i)` — 100 instances, with `rdiff(i100)` fixed to 0
- Both `stat_rdiff` and `rdiff` have 99 active + 1 fixed instances → balanced

**Result:** camshape MCP compiles with 0 errors and no unmatched equation pairing. MODEL STATUS 5 (Locally Infeasible) — the remaining infeasibility is from alias differentiation issues (tracked in parent issue #1111), not the MCP pairing.
