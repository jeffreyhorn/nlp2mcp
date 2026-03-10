# imsl: Post-solve parameter assignments emitted before MCP solve statement

**GitHub Issue:** [#1036](https://github.com/jeffreyhorn/nlp2mcp/issues/1036)
**Status:** OPEN
**Severity:** Medium — causes GAMS compilation Error 116 ("Label is unknown")
**Date:** 2026-03-10
**Affected Models:** imsl (SEQ=59), potentially any model with post-solve reporting parameters

---

## Problem Summary

The imsl model has parameter assignments that depend on solution values (marginals `.m`) which only exist after a solve statement. In the original GAMS file, these assignments appear after `solve dual using lp maximizing tdual;` (lines 113–116). However, the MCP emitter places **all** parameter assignments before the MCP equations and solve statement, causing GAMS Error 116 ("Label is unknown") because `drep(n,"dev")` references a value that hasn't been computed yet.

---

## Root Cause

The emitter (`src/emit/original_symbols.py`) emits all parameter computed assignments in the "Original Model Declarations" section, which appears before the MCP equations and solve statement. It does not distinguish between:

1. **Pre-solve assignments** — parameter computations needed to set up the model (e.g., `t(n) = (ord(n) - 1) / (card(n) - 1)`)
2. **Post-solve assignments** — reporting parameters that use solution values (e.g., `drep(n,"dev") = sum(m, -ddual.m(m)*w(m,n)) - y(n)`)

The parser stores both kinds in `param.expressions` without recording their position relative to solve statements.

---

## Triggering GAMS Code

From `imsl.gms` lines 109–116 (after the second solve):

```gams
solve dual using lp maximizing tdual;

Parameter
   drep(n,*) 'dual solution report'
   dualdev   'sum of absolute deviations from dual solution';

drep(n,"t")  = t(n);
drep(n,"y")  = y(n);
drep(n,"dev")= sum(m, -ddual.m(m)*w(m,n)) - y(n);   $ uses .m from solve
dualdev      = sum(n, abs(drep(n,"dev")));            $ references "dev" label
```

The emitter outputs `dualdev = sum(n, abs(drep(n,"dev")));` before any solve, but `drep(n,"dev")` hasn't been assigned yet, so GAMS raises Error 116.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/imsl.gms -o /tmp/imsl_mcp.gms
gams /tmp/imsl_mcp.gms
# imsl_mcp.gms(57) Error 116: Label is unknown
```

Generated MCP line 57:
```gams
dualdev = sum(n, abs(drep(n,"dev")));   $ "dev" label not yet assigned
```

---

## Proposed Fix

### Option A: Filter out post-solve parameters

During parsing, track which parameter assignments reference solution attributes (`.l`, `.m`, `.lo`, `.up`). These post-solve reporting parameters should be excluded from the MCP output entirely, since they are not part of the optimization model — they are reporting/display computations.

### Option B: Emit post-solve assignments after the MCP solve

Move parameter assignments that reference solution attributes to a post-solve section in the MCP output, after `Solve mcp_model using MCP;`. This preserves the reporting logic but requires the emitter to partition assignments into pre-solve and post-solve groups.

### Option C: (Minimal) Exclude parameters not referenced in any equation

Parameters that don't appear in any equation definition are purely for reporting. These could be excluded from the MCP output entirely without affecting the optimization model.

---

## Affected Files

| File | Change |
|------|--------|
| `src/ir/parser.py` | Track assignment position relative to solve statements |
| `src/emit/original_symbols.py` | Partition parameter assignments into pre/post-solve |

---

## Context

- LP models are valid MCP targets (KKT conditions are well-defined)
- This issue also affects any model with post-solve reporting parameters that reference `.l` or `.m` values
- The parameters `prep(n,*)`, `drep(n,*)`, `primaldev`, `dualdev` are all post-solve reporting — none appear in the model equations
