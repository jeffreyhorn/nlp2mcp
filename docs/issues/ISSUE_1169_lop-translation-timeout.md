# lop: Translation timeout during MCP generation

**GitHub Issue:** [#1169](https://github.com/jeffreyhorn/nlp2mcp/issues/1169)
**Model:** lop (GAMSlib SEQ=192, "Line Optimization")
**Error category:** `translation_timeout`
**Affected stage:** KKT/stationarity builder (symbolic differentiation)

## Description

The lop model parses successfully (12 equations, 9 variables, 18 sets) but the MCP translation pipeline hangs indefinitely during the KKT assembly / symbolic differentiation stage. The model `evaldt` is solved using LP (`solve evaldt maximizing obj using lp`) with 3 equations: `dtllimit`, `sumbound`, `defobjdtlop`.

Note: lop contains multiple solve statements using both LP and MIP. The last solve (`solve evaldt maximizing obj using lp`) is the one selected for translation.

## Reproduction

```bash
# Parse succeeds:
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
model = parse_model_file('data/gamslib/raw/lop.gms')
print('Parse OK:', len(model.equations), 'equations,', len(model.variables), 'variables')
"

# Translation hangs (no output after 2+ minutes):
python -m src.cli data/gamslib/raw/lop.gms -o /tmp/lop_mcp.gms --skip-convexity-check
```

## Root Cause

Likely the same class of issue as the LP timeout models (#926–#933) identified in the Sprint 23 issue fix opportunities list (item L2). The symbolic differentiation in the AD pipeline takes too long on certain LP model structures, possibly due to:

1. Large/complex sum expressions that create combinatorial blowup during differentiation
2. Multi-dimensional indexed equations with many domain combinations
3. Missing LP-specific fast path for symbolic differentiation

## Fix Approach

This is part of the broader LP timeout family (L2 in ISSUE_FIX_OPPORTUNITIES.md). Potential fixes:

1. Add a translation timeout mechanism so the CLI doesn't hang indefinitely
2. Implement LP-specific fast path for symbolic differentiation (LP Jacobians are constant, so differentiation should be trivial)
3. Profile the specific bottleneck in lop's differentiation to identify the exact expression causing blowup

## Related Issues

- #926–#933: Translation timeouts (LP/NLP) — same class of issue
- L2 in Sprint 23 ISSUE_FIX_OPPORTUNITIES.md

---

## Current Status (2026-03-29)

**Current blocker: Translation timeout (>300s).** LP fast path (PR #1172, basic simplification) implemented but differentiation itself is the bottleneck. Despite the model being LP with only 3 equations in the solved model `evaldt`, the expression structure creates too many variable/equation instance combinations. Needs coefficient extraction with sum-bound index handling, or a sparsity-aware Jacobian.

Parse: ~46s | Translate: TIMEOUT | Compile: N/A | Solve: N/A
