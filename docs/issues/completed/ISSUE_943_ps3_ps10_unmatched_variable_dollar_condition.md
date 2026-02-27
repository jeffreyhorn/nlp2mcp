# ps3_s / ps3_s_mn / ps10_s: Unmatched Variable from Dollar-Conditioned Complementarity Equation

**GitHub Issue:** [#943](https://github.com/jeffreyhorn/nlp2mcp/issues/943)
**Status:** RESOLVED
**Models:** ps3_s, ps3_s_mn, ps10_s (GAMSlib)
**Error category:** `gams_error` (EXECERROR = 1 or 2)
**Runtime error:** `Unmatched variable not free or fixed`

## Description

These three models share the same root cause: the generated MCP declares a complementarity pair like `comp_licd.lam_licd`, but the equation `comp_licd(i)` has an inferred dollar condition `$(ord(i) <= card(i) - 1)` (from lead/lag `i+1`) that excludes the last index. The multiplier variable `lam_licd(i)` is declared over the full domain, so the last instance (e.g., `lam_licd(2)` or `lam_licd(9)`) has no matching equation. GAMS requires unmatched MCP variables to be either free or fixed.

### Affected Models

| Model | Set Size | Unmatched Variables | EXECERROR | Status |
|-------|----------|---------------------|-----------|--------|
| ps3_s | 3 (0, 1, 2) | lam_licd(2) | 1 | SOLVED (Optimal) |
| ps3_s_mn | 3 (0, 1, 2) | lam_licd(2), lam_mn(2) | 2 | SOLVED (Optimal) |
| ps10_s | 10 (0-9) | lam_licd(9) | 1 | SOLVED (Optimal) |

## Root Cause

The original NLP constraint uses `i+1` (lead expression):

```gams
licd(i).. w(i) - theta(i)*x(i) =g= w(i+1) - theta(i)*x(i+1);
```

The equation emitter infers `$(ord(i) <= card(i) - 1)` from the lead/lag analysis
to exclude the terminal index. However, the `.fx` emission code (section 2) only
checked `eq_def.condition` (the explicit dollar condition from the original equation),
which was `None` — the lead/lag condition is inferred at emit time, not stored on
the equation definition.

The existing section 3 (lead/lag fix for equality equations) already handled this
pattern for `nu_*` multipliers, but the analogous logic was missing for inequality
complementarity multipliers (`lam_*`).

## Fix (RESOLVED)

Added section 2b in `src/emit/emit_gams.py` (`.fx` emission): for each inequality
complementarity equation without an explicit condition, check for lead/lag
restrictions using `_collect_lead_lag_restrictions()` + `_build_domain_condition()`.
When a lead/lag condition is inferred, emit:

```gams
lam_licd.fx(i)$(not (ord(i) <= card(i) - 1)) = 0;
```

This mirrors the existing section 3 logic for equality multipliers. All three
models now compile and solve to Optimal.

**Tests:** `tests/unit/emit/test_fx_complementarity.py::TestLeadLagComplementarityFix`

## Related Issues

- #826: Decomp empty stationarity equation (similar pattern — variable not fixed for empty equation)
- #942: Empty diagonal complementarity pairs (fixed in same PR)
- #904: power() non-integer exponent (primary blocker now fixed; this was the secondary blocker)
