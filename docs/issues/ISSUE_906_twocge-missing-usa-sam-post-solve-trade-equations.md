# twocge: Missing USA SAM Data, Post-Solve Code Before Solve, Missing Trade Equations

**GitHub Issue**: [#906](https://github.com/jeffreyhorn/nlp2mcp/issues/906)
**Model**: `twocge` (Two-Country General Equilibrium)
**Pipeline status**: `path_solve_terminated` (28 execution errors)
**Blocking since**: Sprint 21 Day 7 (after dotted column header fix)

## Summary

After the Day 7 dotted column header fix, twocge upgraded from `path_syntax_error` to `path_solve_terminated`. The SAM table now captures 50 values for JPN, but the USA continuation section (lines 48–73 in original) is missing entirely. This causes all derived parameters for USA to be zero, leading to 26 division-by-zero errors and 2 power-domain errors at runtime. Additionally, two trade equations (`eqpw`, `eqw`) are missing from the emitted MCP, and post-solve calibration code is placed before the solve statement.

## Root Cause Analysis

### 1. Missing USA SAM Continuation Data (Primary)

The original `twocge.gms` has a continuation table for SAM:
```gams
Table SAM(u,v,r)  social accounting matrix (in value terms)
         BRD.JPN MLK.JPN CAP.JPN LAB.JPN IDT.JPN
  BRD       40      30
  ...
  +     BRD.USA MLK.USA CAP.USA LAB.USA IDT.USA
  BRD       30      20
  ...
```

The `+` continuation section with USA columns is not captured by the parser. The emitted MCP only has 50 JPN values:
```
SAM(u,v,r) /BRD.BRD.JPN 40, BRD.MLK.JPN 30, ... GOV.LAB.JPN 0/
```

All USA-indexed parameters (`F0`, `X0`, `Xp0`, `Xg0`, `Xv0`, `E0`, `M0`, `Sp0`, `Sg0`, `Td0`, `Tz0`, `FF`, `Sf`) are zero for USA, causing division by zero in calibration formulas like:
```gams
beta(h,j,r) = F0(h,j,r) / sum(k, F0(k,j,r));  * 0/0 for r=USA
```

### 2. Post-Solve Calibration Before Solve

Lines 306–331 in the emitted MCP contain post-solve percentage-change calculations:
```gams
dY(j,r) = (y.l(j,r) / Y0(j,r) - 1) * 100;
dF(h,j,r) = (f.l(h,j,r) / F0(h,j,r) - 1) * 100;
```

These reference `.l` values that are only meaningful after a solve, but they appear before the solve statement (line 630). In the original model, these appear after the solve.

### 3. Missing Trade Equations (`eqpw`, `eqw`)

The original model defines two trade equilibrium equations:
```gams
eqpw(i,r,rr)..  (pWe(i,r) - pWm(i,rr))$(ord(r) <> ord(rr)) =e= 0;
eqw(i,r,rr)..   (E(i,r) - M(i,rr))$(ord(r) <> ord(rr)) =e= 0;
```

These cross-country trade equations are not present in the emitted MCP. They use a third index `rr` with `ord(r) <> ord(rr)` conditioning, which may not be handled by the KKT derivation.

## Reproduction

```bash
# 1. Check SAM data captured (only JPN, no USA):
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
m = parse_model_file('data/gamslib/raw/twocge.gms')
sam = m.params['sam']
print(f'SAM values: {len(sam.values)}')  # 50 (should be ~100)
usa_keys = [k for k in sam.values if 'USA' in str(k)]
print(f'USA keys: {len(usa_keys)}')  # 0 (should be ~50)
"

# 2. Run MCP through GAMS:
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams \
  data/gamslib/mcp/twocge_mcp.gms o=/tmp/twocge_mcp.lst

# 3. Count errors:
grep -c '^\*\*\*\* ' /tmp/twocge_mcp.lst  # 32 (28 exec + 4 meta)
```

## Error Details

| Error Type | Count | Lines | Cause |
|---|---|---|---|
| Division by zero | 26 | 117–131, 306–331 | USA parameters all zero |
| rPower domain (x=0, y<0) | 2 | 134–135 | `E0(i,r)**phi` with E0=0, phi<0 |
| SOLVE aborted | 1 | 630 | Cascaded from above |

## Fix Strategy

1. **Table continuation parsing** (Issue #901 partially addressed this): Investigate why the `+` continuation section for USA columns is not captured. The dotted column header merge works for the first section but the continuation parser may not re-invoke it.
2. **Post-solve code ordering**: The emitter should place post-solve parameter assignments after the solve statement, not before.
3. **Trade equations with cross-index conditioning**: Investigate whether `eqpw(i,r,rr)` with `$(ord(r) <> ord(rr))` is handled by KKT derivation. These may need special support for multi-region equilibrium conditions.

## Related Issues

- Issue #901 — twocge dotted table column headers (RESOLVED by Day 7 dotted column header fix)
