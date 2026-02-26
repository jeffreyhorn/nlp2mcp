# tforss: NA Propagation from Uninitialized rho, KKT Derivation Bugs, Unmatched Variable

**GitHub Issue**: [#907](https://github.com/jeffreyhorn/nlp2mcp/issues/907)
**Model**: `tforss` (Timber Forest Sector — Static Steady-State)
**Pipeline status**: `path_solve_terminated` (153 execution errors)
**Blocking since**: Sprint 21 Day 7 (after dotted column header fix)

## Summary

After the Day 7 dotted column header fix, tforss upgraded from `path_syntax_error` to `path_solve_terminated`. The model now has 153 execution errors: 100 "coefficient in variable is NA" errors, 52 "RHS value NA" errors, and 1 "unmatched variable not free or fixed" error. The root causes are: (1) `rho` is initialized to `na` because the original model sets it via a loop before solving, which the emitter doesn't reproduce; (2) KKT stationarity equations have incorrect structure; (3) variable `x(sawnwood)` is unmatched in the MCP.

## Root Cause Analysis

### 1. NA Propagation from Uninitialized `rho` (Primary — 152 errors)

The emitted MCP declares:
```gams
rho /na/
```

The original model initializes `rho` inside a loop:
```gams
loop(rhoset,
   rho = rhoval(rhoset);
   solve tforss using nlp ...
);
```

Since the emitter captures only the initial scalar value (`na`) and doesn't emit the loop that sets `rho` before solving, every equation referencing `rho` produces NA coefficients:
```gams
stat_h(m).. ... (rho / (1 - (1 + rho) ** ((-1) * life) ...  * rho=na → NA
stat_v(s,k,at).. ... (mup * (1 + rho) ** age(at)) ...  * rho=na → NA
ainvc.. phik =E= rho / (1 - (1 + rho) ** ((-1) * life)) ...  * rho=na → NA
aplnt.. phip =E= mup * sum((s,k,at), v(s,k,at) * (1 + rho) ** age(at));  * rho=na → NA
```

### 2. KKT Stationarity Bugs

The stationarity equations may have incorrect structure beyond the NA issue:

- **`stat_x(s,cl)`**: For each `(s,cl)` pair, the stationarity should reference only the multiplier for the specific subset element's constraint. If the original model uses `loop(rhoset, ...)` with different solve calls, the KKT derivation may conflate conditions from different loop iterations.

- **`stat_r(k,s)`**: Similar concern — the `sum(subset, multiplier)` structure may be incorrect where only the matching multiplier for a specific index should appear.

### 3. Unmatched Variable `x(sawnwood)`

GAMS reports:
```
**** Unmatched variable not free or fixed
     x(sawnwood)
```

Variable `x(sawnwood)` appears in the MCP but has no matching complementarity equation. This could be because:
- The variable should be fixed but isn't
- The corresponding equation was lost during KKT derivation
- The sawnwood index is in a subset that should be conditioned out

## Reproduction

```bash
# 1. Check rho initialization:
grep -n "rho" data/gamslib/mcp/tforss_mcp.gms | head -10
# Shows: rho /na/

# 2. Run MCP through GAMS:
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams \
  data/gamslib/mcp/tforss_mcp.gms o=/tmp/tforss_mcp.lst

# 3. Error summary:
grep '^\*\*\*\* ' /tmp/tforss_mcp.lst | sort | uniq -c | sort -rn
# 100 coefficient NA, 52 RHS NA, 1 unmatched variable
```

## Error Details

| Error Type | Count | Cause |
|---|---|---|
| Matrix error - coefficient is NA | 100 | `rho = na` propagates through equations |
| RHS value NA | 52 | `rho = na` in equation RHS |
| Unmatched variable not free or fixed | 1 | `x(sawnwood)` has no complementarity pair |

## Fix Strategy

1. **Loop-before-solve pattern**: The emitter needs to handle the common GAMS pattern where a parameter is set inside a loop before each solve. For MCP translation, the emitter should use the first (or a representative) value of `rho` from `rhoval` (e.g., `rho = 0.03`) rather than `na`. Alternatively, detect that `rho` is set by a loop and emit the assignment.

2. **KKT stationarity audit**: Review the stationarity equations for `stat_x`, `stat_r`, and `stat_v` to ensure they correctly reflect the partial derivatives with proper conditioning.

3. **Unmatched `x(sawnwood)`**: Investigate whether `sawnwood` should be excluded from the MCP variable set (e.g., it may be a fixed variable in the original model) or whether a complementarity equation is missing.

## Related Issues

- Issue #886 — tfordy/tforss compound table headers and hyphenated elements (PARTIALLY RESOLVED — table headers fixed in Day 7)
