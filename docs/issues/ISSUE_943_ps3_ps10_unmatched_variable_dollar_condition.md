# ps3_s / ps3_s_mn / ps10_s: Unmatched Variable from Dollar-Conditioned Complementarity Equation

**GitHub Issue:** [#943](https://github.com/jeffreyhorn/nlp2mcp/issues/943)
**Status:** OPEN
**Models:** ps3_s, ps3_s_mn, ps10_s (GAMSlib)
**Error category:** `gams_error` (EXECERROR = 1 or 2)
**Runtime error:** `Unmatched variable not free or fixed`

## Description

These three models share the same root cause: the generated MCP declares a complementarity pair like `comp_licd.lam_licd`, but the equation `comp_licd(i)` has a dollar condition `$(ord(i) <= card(i) - 1)` that excludes the last index. The multiplier variable `lam_licd(i)` is declared over the full domain, so the last instance (e.g., `lam_licd(2)` or `lam_licd(9)`) has no matching equation. GAMS requires unmatched MCP variables to be either free or fixed.

### Affected Models

| Model | Set Size | Unmatched Variables | EXECERROR |
|-------|----------|---------------------|-----------|
| ps3_s | 3 (0, 1, 2) | lam_licd(2) | 1 |
| ps3_s_mn | 3 (0, 1, 2) | lam_licd(2), lam_mn(2) | 2 |
| ps10_s | 10 (0-9) | lam_licd(9) | 1 |

## Reproduction

```bash
# Translate and solve:
python -m src.cli data/gamslib/raw/ps3_s.gms -o /tmp/ps3_s_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/ps3_s_mcp.gms lo=2

# Expected error:
# **** Unmatched variable not free or fixed
#      lam_licd(2)
```

## Root Cause

The original NLP constraint enforces a "limited incentive compatibility decrease" condition on consecutive elements:

```gams
* Original: w(i) - theta(i)*x(i) >= w(i+1) - theta(i)*x(i+1) for i < N
licd(i)$(ord(i) <= card(i) - 1).. w(i) - theta(i)*x(i) =g= w(i+1) - theta(i)*x(i+1);
```

This constraint only applies for `i = 0, 1, ..., N-2` (comparing consecutive elements). The last element `i = N-1` has no "next" element, so the constraint doesn't apply.

The KKT builder creates the complementarity equation `comp_licd(i)` and multiplier `lam_licd(i)` over the full domain `i`, preserving the dollar condition on the equation:

```gams
comp_licd(i)$(ord(i) <= card(i) - 1).. w(i) - theta(i) * x(i) - (w(i+1) - theta(i) * x(i+1)) =G= 0;
```

But the multiplier `lam_licd(i)` is declared for ALL `i`, and the MCP pairing `comp_licd.lam_licd` doesn't account for the domain mismatch.

For ps3_s_mn, the same pattern occurs twice: `comp_licd` and `comp_mn` both exclude the last index, creating two unmatched variables.

## Emitted MCP — Offending Pairing

```gams
Positive Variable lam_licd(i);  * declared for i = 0, 1, 2

comp_licd(i)$(ord(i) <= card(i) - 1).. ...  * only defined for i = 0, 1

Model mcp_model /
    comp_licd.lam_licd,    * tries to pair ALL i, but lam_licd(2) has no equation
/;
```

## Fix Approach

**Option A: Fix unmatched multiplier variables to 0.** Add `.fx` statements for instances where the equation doesn't exist:
```gams
lam_licd.fx(i)$(ord(i) > card(i) - 1) = 0;
```

The emitter should detect when a complementarity equation has a dollar condition that excludes some domain instances and fix the corresponding multiplier variables to 0 for those instances.

**Option B: Restrict multiplier domain.** Use a subset for the multiplier variable:
```gams
Set i_licd(i);
i_licd(i) = yes$(ord(i) <= card(i) - 1);
Positive Variable lam_licd(i_licd);
```

Option A is simpler and doesn't require modifying the variable declaration.

**Implementation:** In the emitter (`emit_gams.py`), when emitting complementarity pairs, check if the equation has a dollar condition. If so, emit `.fx` for the multiplier on the complement of that condition.

**Estimated effort:** 1-2h (detect dollar-conditioned equations and fix complement instances)

## Related Issues

- #826: Decomp empty stationarity equation (similar pattern — variable not fixed for empty equation)
- #904: power() non-integer exponent (primary blocker now fixed; this is the secondary blocker)
