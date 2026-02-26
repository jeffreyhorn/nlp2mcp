# sarf: Translation Timeout from Combinatorial Explosion in Variable Instances

**GitHub Issue:** [#885](https://github.com/jeffreyhorn/nlp2mcp/issues/885)
**Status:** OPEN
**Severity:** Medium — Model parses but translation times out (>60s)
**Date:** 2026-02-25
**Affected Models:** sarf
**Sprint:** 21 (Day 4 blocker)

---

## Problem Summary

The `sarf.gms` model (GAMSlib SEQ=49, Farm Credit and Income Distribution) parses successfully but times out during translation. The bottleneck is the derivative computation stage where the 4-dimensional variable `task(g,t,mn,mn)` generates 369,024 instances, requiring ~452 million Jacobian entry computations.

---

## Error Details

```
Translation timeout after 60s
```

### Timing Breakdown

| Stage | Time |
|---|---|
| Parse | ~10s |
| Validate | <1s |
| Gradient computation | ~13s |
| Jacobian computation | **TIMEOUT** (>60s) |

---

## Root Cause

Three factors combine to cause the timeout:

### 1. 4-Dimensional Variable with Superset Domain

```gams
Variable task(g,t,mn,mn) 'agricultural tasks by technology (ha)';
```

The variable is declared over the full superset `mn` (31 members) for both the 3rd and 4th indices, even though equations only access it as `task(g,t,m,n)` where `m` (27 implements) and `n` (5 power sources) are subsets. This generates:

- 16 x 24 x 31 x 31 = **369,024 variable instances**
- Total equation instances: **1,226**
- Jacobian entries: 369,024 x 1,226 = **~452 million**

### 2. Unevaluable Dynamic Set Conditions

Equations use dollar conditions on **dynamic sets** that cannot be evaluated statically:

```gams
cposs(c,s)     = yes$length(c,s);
taskposs(g,t)  = sum((c,s), yes$treq(g,t,c,s));
equipposs(m,t) = yes$(sum((g,n)$taskposs(g,t), tech(g,m,n)) <> 0);
```

The condition evaluator raises `Unsupported expression type SetMembershipTest` for these, causing all instances to be included rather than the much smaller valid set.

### 3. LP Model (Not NLP)

The model is solved as `lp` (linear program), not `nlp`. Applying the NLP-to-MCP pipeline (computing symbolic KKT derivatives) to a large LP model is computationally excessive for what are only linear terms.

---

## Reproduction

```python
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
from src.emit.gams_emitter import emit_gams
m = parse_model_file('data/gamslib/raw/sarf.gms')
# Translation times out:
result = emit_gams(m)
```

---

## Possible Fixes

| Approach | Impact | Effort |
|----------|--------|--------|
| Sparsity-aware variable instance enumeration (only instances appearing in equations) | High — would reduce 369K to ~5K instances | High (architecture change) |
| Dynamic set condition evaluation support | Medium — would filter equation instances | Medium (new evaluator capability) |
| Early detection/skip for models exceeding instance threshold | Low — skip rather than timeout | Low (threshold check) |
| LP-specific fast path (skip symbolic differentiation) | High for LP models | Medium (model type dispatch) |

**Recommended near-term**: Add a variable instance threshold check (~100K) that logs a warning and either skips or uses a simplified emission path. Long-term: sparsity-aware enumeration.

**Estimated effort:** Investigation only; fix depends on chosen approach (2h–20h range)

---

## Model Structure

| Category | Details |
|----------|---------|
| Model type | LP (linear program) |
| Sets | 12 (largest: `mn` = 31, `t` = 24, `g` = 16) |
| Parameters | 32 (includes large tables: `tech(g,mn,mn)`, `yef`, `stress`) |
| Variables | 10 (critical: `task(g,t,mn,mn)`) |
| Equations | 16 |

---

## GAMS Source Context

Key variable (line 394):
```gams
Variable
   task(g,t,mn,mn)  'agricultural tasks by technology  (ha)'
   xcrop(c,s)       'cropping activities               (ha)'
   xwater(c,w)      'water application                 (ha)'
   ...
```

Key equations (lines 422–458):
```gams
tbal(g,t)$taskposs(g,t)..
   sum((c,s)$cposs(c,s), treq(g,t,c,s)*xcrop(c,s))
   =e= sum((m,n)$tech(g,m,n), task(g,t,m,n)) - ...;

equipb1(m,t)$equipposs(m,t)..
   sum((g,n)$taskposs(g,t), tech(g,m,n)*task(g,t,m,n)) =l= avail(m)*equipp(m);
```

---

## Related Issues

- Sprint 21 Day 4 PR #883: Lead/lag in parameter assignment LHS (parsing fix)
- Issue #830 (gastrans): Similar Jacobian timeout from dynamic subset conditions
