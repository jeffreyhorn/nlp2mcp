# maxmin: smin() Argument Count Mismatch — Expects 2 Arguments, Got 3

**GitHub Issue:** [#939](https://github.com/jeffreyhorn/nlp2mcp/issues/939)
**Status:** OPEN
**Severity:** Medium — Model parses but cannot be translated (smin arity error)
**Date:** 2026-02-26
**Affected Models:** maxmin
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `maxmin.gms` model (GAMSlib SEQ=206, "Max Min Location of Points in Unit Square") parses successfully but fails during KKT translation because the symbolic differentiation engine encounters an `smin()` call with 3 arguments, but expects exactly 2.

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 206 |
| Solve Type | NLP |
| Convexity | likely_convex |
| Reference Objective | 0.3528 |
| Parse Status | success |
| Translate Status | failure — `internal_error` |

---

## Error Message

```
Error: Invalid model - smin() expects 2 arguments, got 3
```

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/maxmin.gms -o /tmp/maxmin_mcp.gms
# Or:
python scripts/gamslib/run_full_test.py --model maxmin --only-translate --verbose
```

---

## Root Cause

In GAMS, `smin` (scalar minimum) has the syntax `smin(index, expression)` where `index` is a set domain and `expression` is the body to minimize over. However, the maxmin model likely uses a nested or multi-index `smin` call that the IR parser represents with 3 arguments instead of the expected 2 (domain + body).

The error is raised in `src/ad/derivative_rules.py:1345`:
```python
raise ValueError(f"smin() expects 2 arguments, got {len(expr.args)}")
```

This suggests either:
1. The parser is including the domain index as a separate argument (should be part of the smin expression structure, not a plain argument)
2. The model uses a nested smin pattern not handled by the current AST representation
3. The smin call has a compound domain `(i,j)` that gets expanded into separate arguments

---

## Possible Fixes

| Approach | Impact | Effort |
|----------|--------|--------|
| Debug the smin AST representation — check how multi-index domains are stored | High — would fix this specific model | Low-Medium |
| Update derivative rule to handle 3+ argument smin (domain expansion) | High | Low |
| Inspect the parsed IR to understand what 3 arguments are being passed | Diagnostic | Low |

### Diagnostic Step

```python
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
m = parse_model_file('data/gamslib/raw/maxmin.gms')
# Inspect equations for smin usage
for name, eq in m.equations.items():
    print(f"{name}: {eq.lhs} =E= {eq.rhs}")
```

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/ad/derivative_rules.py:1340-1350` | smin differentiation rule with arity check |
| `src/ir/parser.py` | How smin expressions are parsed and stored in AST |
| `src/gams/gams_grammar.lark` | Grammar rule for `smin_expr` |
| `data/gamslib/raw/maxmin.gms` | Original model to inspect smin usage |

---

## Related Issues

- None directly — this is a unique argument count mismatch for smin
