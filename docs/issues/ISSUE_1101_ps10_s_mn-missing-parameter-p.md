# ps10_s_mn: Missing Parameter `p(i)` in MCP Output ($140)

**GitHub Issue:** [#1101](https://github.com/jeffreyhorn/nlp2mcp/issues/1101)
**Model:** ps10_s_mn (GAMSlib SEQ=369)
**Status:** OPEN
**Error Category:** Compilation — $140 Unknown symbol
**Severity:** Medium — model translates but GAMS compilation fails (3 errors)
**Sprint:** 22 Day 12

---

## Problem Summary

After resolving the empty parameter declaration issue (#917), the ps10_s_mn MCP still fails to compile because the parameter `p(i)` is referenced in stationarity equations but never declared or assigned. The parameter `p(i)` is a loop-local variable assigned inside the solve loop as `p(i) = pt(i,t)`.

---

## Error Details

### Primary error: $140 Unknown symbol `p` (line 124)

```gams
stat_b(i).. ((-1) * p(i)) + nu_rev(i) - piL_b(i) =E= 0;
****                  $140
```

`p(i)` also appears in:
- Line 125: `stat_w(i).. ((-1) * (p(i) * (-1))) - lam_pc(i) - ...`
- Line 138: `obj.. util =E= sum(i, p(i) * (b(i) - w(i)));`

### Cascading: 2 errors

- **$257 (line 181)**: Solve statement not checked
- **$141 (line 184)**: `Util.l` has no value

---

## Root Cause

In the original `ps10_s_mn.gms`, `p(i)` is assigned inside the solve loop:

```gams
loop(t,
   p(i) = pt(i,t);              ← p(i) set from random data pt(i,t)
   solve SB_lic maximizing Util using nlp;
   Util_lic(t) = Util.l;
   ...
);
```

The KKT transformation extracts the inner NLP model `SB_lic` and builds stationarity conditions that reference `p(i)` (since `p(i)` appears in the objective and constraints). However, the emitter does not declare `p(i)` as a parameter or emit the assignment `p(i) = pt(i,t)` because:

1. `p(i)` is declared as a `Parameter` in the original source but has no static values and its only assignment is inside the loop body
2. Issue #917 fix correctly removed the empty declaration for `p(i)` (it had no values and no expressions), but now `p(i)` is neither declared nor assigned
3. The loop body assignment `p(i) = pt(i,t)` references `t` which is the loop index — for a single-solve MCP, a representative value of `t` must be chosen

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/ps10_s_mn.gms -o /tmp/ps10_s_mn_mcp.gms --skip-convexity-check
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/ps10_s_mn_mcp.gms lo=2 o=/tmp/ps10_s_mn_mcp.lst
grep '^\*\*\*\*' /tmp/ps10_s_mn_mcp.lst
```

---

## Original GAMS Context

```gams
Sets i /0*9/, t /1*1000/;
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

For multi-solve loop models where the KKT inner model references loop-assigned parameters:

1. **Detect loop-body parameter assignments** that feed into the solved model (e.g., `p(i) = pt(i,t)`)
2. **Emit the parameter declaration** with the loop-independent domain (e.g., `p(i)`)
3. **Emit an initialization** using the first loop iteration value: `p(i) = pt(i,'1');` — or alternatively, emit the loop statement itself so GAMS can execute it (but this requires choosing a single iteration)

A simpler alternative: declare `p(i)` and initialize with `pt(i,'1')` (first element of `t`).

---

## Related Issues

- #917: Empty parameter declarations removed (prerequisite fix)
- #944: ps5_s_mn multi-solve pattern (same family of models)

---

## Impact

1 primary compilation error. Model cannot compile or solve. The same issue affects ps5_s_mn identically.
