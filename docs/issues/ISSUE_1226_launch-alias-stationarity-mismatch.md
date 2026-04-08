# launch: Alias Stationarity Mismatch — Incorrect Jacobian with Alias(s,ss)

**GitHub Issue:** [#1226](https://github.com/jeffreyhorn/nlp2mcp/issues/1226)
**Status:** OPEN
**Severity:** High — objective mismatch (20.9%)
**Date:** 2026-04-06
**Affected Models:** launch
**Supersedes:** #1142 (updated root cause analysis)

---

## Problem Summary

The launch model (Expendable Launch Vehicle Design, GAMSlib) uses `Alias(s,ss)`
and produces an MCP that solves to MODEL STATUS 1 (Optimal) but with the wrong
objective value. The 20.9% mismatch indicates an alias-related Jacobian error
in the stationarity equations.

| Metric | Value |
|--------|-------|
| NLP Objective | 2257.7976 |
| MCP Objective | 2731.711 |
| Relative Difference | ~17.3% (diff/MCP obj) or ~20.9% (diff/NLP obj) |
| Model Status | 1 (Optimal) |

The MCP solves cleanly (Optimal status), meaning the KKT system is structurally
valid but contains incorrect gradient terms due to alias handling.

---

## Root Cause

The launch model uses `Alias(s, ss)` where `ss` participates in conditional
sums with ordinal comparisons (e.g., `sum(ss$(ord(ss) >= ord(s)), ...)`). The
alias-bound index `ss` creates triangular summation patterns.

The AD engine's `_alias_match` in `derivative_rules.py` incorrectly handles
alias-bound indices in sum contexts. When differentiating expressions containing
`sum(ss$cond, f(s,ss))` with respect to a variable indexed by `s`, the partial
collapse of the sum over `ss` must correctly preserve:

1. The alias identity (ss aliases s but represents a different iteration variable)
2. The conditional restriction (`$ge(ss,s)` or `$ord` comparisons)
3. Index substitution without confusing `s` and `ss` positions

The result is incorrect stationarity equations that solve to a different
(incorrect) KKT point.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/launch.gms -o /tmp/launch_mcp.gms
gams /tmp/launch_mcp.gms lo=2
# MCP objective: ~2731.7, expected: ~2257.8
# MODEL STATUS 1 (Optimal) — wrong objective
```

---

## Model Structure

- **File**: `data/gamslib/raw/launch.gms` (198 lines)
- **Aliases**: `Alias(s, ss)`
- **Solve type**: NLP (single solve)
- **Key pattern**: Triangular sums with `sum(ss$(ord(ss) >= ord(s)), ...)`

---

## GAMS Errors

None — the MCP compiles and solves without errors. The issue is numerical
(wrong objective), not syntactic.

---

## Potential Fix Approaches

1. **Fix `_alias_match` for sum-bound aliases**: Ensure alias indices bound by
   `sum` are not confused with the outer iteration variable during partial
   collapse
2. **Position-aware index substitution**: Track which domain position an alias
   occupies to prevent s/ss confusion in `_apply_index_substitution`
3. **Conditional preservation**: Ensure `$ge(ss,s)` conditions survive sum
   collapse with correct variable references

---

## Files Involved

- `data/gamslib/raw/launch.gms` — Source model (198 lines)
- `src/ad/derivative_rules.py` — `_alias_match`, `_partial_collapse_sum`
- `src/kkt/stationarity.py` — `_replace_indices_in_expr`
- `docs/issues/ISSUE_1142_launch-conditional-alias-mismatch.md` — Superseded issue
