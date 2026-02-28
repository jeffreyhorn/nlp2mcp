# ps3_s: Objective Mismatch — Non-Convex 3-Type Principal-Agent Model

**GitHub Issue:** [#960](https://github.com/jeffreyhorn/nlp2mcp/issues/960)
**Status:** OPEN
**Model:** ps3_s (GAMSlib SEQ=367)
**Error category:** `objective_mismatch`
**MCP objective:** 1.056
**NLP objective:** 1.162
**Relative difference:** 9.1%

## Description

ps3_s (Parts Supply Problem with 3 Types, Second-Best) is a non-convex NLP (maximization) modeling adverse selection with 3 supplier types. The generated MCP solves to Optimal but converges to a different KKT point, with a significant 9.1% objective mismatch.

The larger mismatch compared to ps2_s (0.5%) is expected: with 3 types, the IC constraint space grows from 2×2 to 3×3, creating more local optima.

## Root Cause

### Non-Convexity with Multiple KKT Points

Same fundamental cause as ps2_s: the revenue function `b(i) =E= x(i)**0.5` is non-convex, and the IC constraint `ic(i,j)` with `Alias(i,j)` creates a 3×3 combinatorial structure. The model also has lead/lag constraints (`licd`, `licu`) that add further structure.

Model structure:
```gams
Set i / 0*2 /;
Alias(i,j);

ic(i,j)..   w(i) - theta(i)*x(i) =g= w(j) - theta(i)*x(j);
licd(i)..   w(i) - theta(i)*x(i) =g= w(i+1) - theta(i)*x(i+1);
licu(i)..   w(i) - theta(i)*x(i) =g= w(i-1) - theta(i)*x(i-1);

solve SB3 maximizing Util using nlp;
```

The single solve statement means no warm-start benefit — the MCP solver must find the right KKT point from default initialization.

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/ps3_s.gms -o /tmp/ps3_s_mcp.gms

# Solve MCP (finds obj = 1.056)
gams /tmp/ps3_s_mcp.gms lo=2

# Solve original NLP (finds obj = 1.162)
gams data/gamslib/raw/ps3_s.gms lo=2

# Compare: MCP 1.056 vs NLP 1.162 (9.1% mismatch)
```

## Recommended Fix

Same as ps2_s: improved initialization heuristics or multi-start MCP solving. The 3-type case is a good test case for any initialization strategy since the mismatch is more pronounced.

## Related Issues

- ps2_s, ps2_f_s: 2-type variants (0.5% mismatch)
- ps3_s_gic: 3-type variant with generalized IC (same 9.1% mismatch)
- ps3_s_scp: 3-type variant with SCP (2.3% mismatch)
- ps3_s_mn: 3-type variant with monotone non-decreasing (2.2% mismatch)
- ps10_s: 10-type variant (27.4% mismatch)
- #942, #943: Previously blocking .fx emission issues (RESOLVED)

## Estimated Effort

See ps2_s — same fix applies across all models in this family.
