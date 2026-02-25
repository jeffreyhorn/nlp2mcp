# camcge: Stationarity Equations Missing Subset Conditioning

**GitHub Issue:** [#871](https://github.com/jeffreyhorn/nlp2mcp/issues/871)
**Status:** OPEN
**Severity:** High — Model compiles but PATH solver aborts with 5 execution errors (division by zero)
**Date:** 2026-02-24
**Affected Models:** camcge

---

## Problem Summary

The camcge MCP model compiles without syntax errors (after Issue #860 fixes), but the PATH
solver aborts with 5 execution errors due to division by zero in stationarity equations.
The root cause is that stationarity equations are generated over the full domain `i` (all 11
sectors) when the original constraint equations are only defined over a subset `it(i)` (9
traded sectors). Non-traded sectors (`services`, `publiques`) have zero-valued parameters
(`e0=0`, `m0=0`) that appear in denominators of the differentiated expressions.

---

## Detailed Error Analysis

### Error 1: `stat_e(services)` — line 431

**Original equation:** `edemand(it).. e(it)/e0(it) =e= ...`
- Only defined over `it` (traded sectors)
- Contains `e0(it)` in denominator → differentiation produces `1/e0(i)` term

**Stationarity equation (emitted):**
```
stat_e(i).. sum(it, ...) + sum(it, 1 / e0(i) ** 1 * nu_edemand(it)) + ... =E= 0;
```

**Problem:** `e0(services) = 0` → division by zero when evaluating `stat_e(services)`.
The `e0(i)` reference should be `e0(it)` or the entire sum should be conditioned on `it(i)`.

### Error 2: `stat_k(*)` — line 441 (all 10 non-publiques sectors)

**Original equation:** `activity(i).. xd(i) =e= ad(i) * prod(lc$wdist(i,lc), l(i,lc)**alphl(lc,i)) * k(i)**(1 - sum(lc, alphl(lc,i)))`
- Differentiation with respect to `k` produces `... * (1 - sum(lc, alphl(lc,i))) / k(i)` term

**Stationarity equation (emitted):**
```
stat_k(i).. ((-1) * (ad(i) * prod(lc$(wdist(i,lc)), l(i,lc) ** alphl(lc,i)) * k(i) ** (1 - sum(lc, alphl(lc,i))) * (1 - sum(lc, alphl(lc,i))) / k(i))) * nu_activity(i) + ... =E= 0;
```

**Problem:** `k(i)` is initialized at 0 for some sectors → division by zero in `1/k(i)`.
This is a Jacobian evaluation issue — the `nu_activity(i)` Jacobian has `k` in denominator.

### Error 3: `stat_pd(services)` — line 447

**Original equations:** `esupply(it)` and `costmin(it)` — both defined over `it` only.
- Differentiation produces terms with `pd(it)` and `pm(it)` in denominators.

**Problem:** The stationarity equation `stat_pd(i)` evaluates these terms for all `i`,
but `services` and `publiques` have parameters that cause division by zero.

### Error 4: `stat_pm(services)` — line 450

Same pattern as `stat_pd` — `costmin(it)` derivative terms with `pm` in denominator.

---

## Root Cause

The stationarity equation builder (`src/kkt/stationarity.py`) does not propagate equation
domain restrictions from the original constraints to the stationarity equations. When an
original constraint like `edemand(it)` is only defined over the `it` subset, the KKT
derivative terms from that constraint should only contribute to stationarity equations
where the variable's domain intersects with `it`.

Currently, the builder:
1. Differentiates each constraint with respect to each variable
2. Sums the Lagrangian contributions across all constraints
3. Emits the stationarity equation over the variable's full domain

It does NOT condition the Lagrangian terms on the original constraint's domain subset.

This is the same class of issue as sambal's Bug 1 (Issue #862) — domain conditioning from
original equations (whether via subset domains or dollar conditions) is not propagated to
stationarity equations.

---

## Reproduction

```bash
# Generate MCP
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
from src.kkt.builder import build_kkt_system
from src.emit.emit_gams import emit_mcp_gams
ir = parse_file('data/gamslib/raw/camcge.gms')
kkt = build_kkt_system(ir)
code = emit_mcp_gams(kkt)
with open('/tmp/camcge_test.gms', 'w') as f: f.write(code)
"

# Run in GAMS
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/camcge_test.gms o=/tmp/camcge_test.lst

# Check errors
grep 'division by zero\|Evaluation error' /tmp/camcge_test.lst
```

Expected: 0 execution errors, PATH solves successfully.
Actual: 5 execution errors (division by zero), SOLVE aborted.

---

## Proposed Fix

### Option A: Emit domain-conditioned stationarity equations

When building stationarity equations, detect the domain of each contributing constraint:
- If `edemand(it)` contributes `∂edemand/∂e`, only include that term when `i ∈ it`
- Emit: `stat_e(i).. sum(it, ...)$it(i) + ... =E= 0`

This requires propagating the equation's domain filter through the AD differentiation and
into the stationarity term collection.

### Option B: Condition the full stationarity equation on the intersection of domains

For each stationarity equation `stat_v(i)`, if all contributing terms require subset `it(i)`,
condition the entire equation: `stat_e(i)$it(i)..`

### Option C: Fix variable initialization to avoid zero-valued denominators

Initialize variables like `e`, `k`, `pd`, `pm` with small non-zero values at problematic
domain points. This is a workaround, not a proper fix, as the stationarity equations are
mathematically wrong for non-traded sectors.

**Recommended:** Option A — it's the mathematically correct approach and addresses the root
cause. This is the same infrastructure needed for sambal's Bug 1 (Issue #862).

---

## Effort Estimate

~6-8h — requires changes to the AD → stationarity pipeline to propagate equation domain
conditioning. This overlaps significantly with the sambal Issue #862 Bug 1 fix.

---

## Files Likely Affected

| File | Change |
|------|--------|
| `src/kkt/stationarity.py` | Propagate equation domain conditioning to stationarity terms |
| `src/kkt/derivative_rules.py` | Preserve domain info through AD differentiation |
| `src/emit/emit_gams.py` | Emit domain-conditioned stationarity equations |

---

## Related Issues

- **Issue #862** (sambal): Same class of issue — dollar condition from sum not propagated
- **Issue #764** (mexss): Accounting variable stationarity conditioning
- **Issue #826** (decomp): Empty stationarity equation from domain issues
