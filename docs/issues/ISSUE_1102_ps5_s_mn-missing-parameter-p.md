# ps5_s_mn: Missing Parameter `p(i)` in MCP Output ($140)

**GitHub Issue:** [#1102](https://github.com/jeffreyhorn/nlp2mcp/issues/1102)
**Model:** ps5_s_mn (GAMSlib SEQ=368)
**Status:** OPEN
**Error Category:** Compilation — $140 Unknown symbol
**Severity:** Medium — model translates but GAMS compilation fails (3 errors)
**Sprint:** 22 Day 12

---

## Problem Summary

After resolving the empty parameter declaration issue (#917), the ps5_s_mn MCP still fails to compile because the parameter `p(i)` is referenced in stationarity equations but never declared or assigned. This is the same root cause as the ps10_s_mn issue — `p(i)` is a loop-local variable assigned inside the solve loop.

---

## Error Details

### Primary error: $140 Unknown symbol `p` (line 119)

```gams
stat_b(i).. ((-1) * p(i)) + nu_rev(i) - piL_b(i) =E= 0;
****                  $140
```

`p(i)` also appears in:
- Line 120: `stat_w(i).. ((-1) * (p(i) * (-1))) - lam_pc(i) - ...`
- Line 133: `obj.. util =E= sum(i, p(i) * (b(i) - w(i)));`

### Cascading: 2 errors

- **$257 (line 176)**: Solve statement not checked
- **$141 (line 179)**: `Util.l` has no value

---

## Root Cause

Identical to the ps10_s_mn issue. In the original `ps5_s_mn.gms`, `p(i)` is assigned inside the solve loop:

```gams
loop(t,
   p(i) = pt(i,t);
   solve SB_lic maximizing Util using nlp;
   ...
);
```

The KKT transformation references `p(i)` in stationarity equations and the objective, but the parameter is neither declared nor initialized in the MCP output because its only assignment is loop-local.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/ps5_s_mn.gms -o /tmp/ps5_s_mn_mcp.gms --skip-convexity-check
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/ps5_s_mn_mcp.gms lo=2 o=/tmp/ps5_s_mn_mcp.lst
grep '^\*\*\*\*' /tmp/ps5_s_mn_mcp.lst
```

---

## Original GAMS Context

```gams
Sets i /0*4/, t /1*1000/;
Parameters theta(i), pt(i,t), p(i);

theta(i) = ord(i)/card(i);
loop(t,
   pt(i,t) = uniform(0,1);
);

* Inner NLP model references p(i):
Equations obj, rev(i), pc(i), licd(i);
obj..  util =e= sum(i, p(i)*(b(i) - w(i)));
rev(i).. p(i)*sqrt(x(i)) =e= b(i);
```

---

## Suggested Fix

Same as ps10_s_mn: detect loop-body parameter assignments that feed into the solved model and emit initialization using a representative loop iteration value (e.g., `p(i) = pt(i,'1');`).

---

## Related Issues

- #917: Empty parameter declarations removed (prerequisite fix)
- ps10_s_mn: Identical root cause (same model family)

---

## Impact

1 primary compilation error. Model cannot compile or solve.
