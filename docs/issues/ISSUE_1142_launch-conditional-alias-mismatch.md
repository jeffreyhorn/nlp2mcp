# launch: Conditional Alias Gradient Mismatch

**GitHub Issue:** [#1142](https://github.com/jeffreyhorn/nlp2mcp/issues/1142)
**Status:** OPEN
**Severity:** Medium — objective mismatch (17.4%)
**Date:** 2026-03-23
**Parent Issue:** #1111 (Alias-Aware Differentiation)
**Affected Models:** launch

---

## Problem Summary

The launch model (Expendable Launch Vehicle Design) uses aliases with
conditional sums of the form `sum(ss$ge(ss,s), ...)` where `ss` is an
alias of `s`. The conditional restricts the alias to a subset of the
set elements, creating a triangular summation pattern.

| Model | NLP Objective | MCP Objective | Rel Diff |
|-------|--------------|--------------|----------|
| launch | 2257.8 | 2731.7 | 17.4% |

**Note:** There is also an existing issue #945 for launch relating to
per-instance stationarity dimension mismatch, which may interact with
the alias gradient issue.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/launch.gms -o /tmp/launch_mcp.gms
gams /tmp/launch_mcp.gms lo=2
# Objective: ~2732, expected: ~2258
```

---

## Root Cause Analysis

The launch model uses:

```gams
Alias(s, ss);
```

With conditional summation patterns like:

```gams
sum(ss$(ord(ss) >= ord(s)), x(ss) * param(s,ss))
```

This creates a triangular structure where for each stage `s`, the sum only
covers stages `ss >= s`. The alias `ss` aliases `s`, but the dollar condition
creates an asymmetric relationship.

### Potential Issues

1. **Conditional alias sum collapse**: When `_partial_collapse_sum` collapses
   `sum(ss$cond, body)` for a specific `ss` value, the condition must be
   correctly substituted and carried forward.

2. **Index substitution in ordinal conditions**: `ord(ss)` becomes `ord(conc_val)`
   after substitution. The `_apply_index_substitution` change from PR #1083
   (which now substitutes SymbolRef) may incorrectly remap the concrete value
   back to the wrong set (same issue as fdesign).

3. **Interaction with #945**: The per-instance stationarity dimension mismatch
   may compound with the alias gradient error.

### Investigation Steps

1. Generate the MCP and inspect stationarity equations
2. Check if the conditional `$ge(ss,s)` is correctly preserved after sum collapse
3. Compare with hand-derived KKT for the triangular sum pattern
4. Determine if fixing the fdesign SymbolRef substitution bug resolves this too

---

## Files

- `src/ad/derivative_rules.py` — `_partial_collapse_sum`, `_apply_index_substitution`
- `src/kkt/stationarity.py` — `_replace_indices_in_expr`
- `data/gamslib/raw/launch.gms` — Source model
