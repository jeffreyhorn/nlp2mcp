# markov: Objective Mismatch — AD Quoted-Index Literal Causes Missing Inequality Constraint

**GitHub Issue:** [#1104](https://github.com/jeffreyhorn/nlp2mcp/issues/1104)
**Status:** OPEN
**Model:** markov (GAMSlib SEQ=82)
**Error category:** `objective_mismatch`
**MCP objective:** 2571.794
**NLP objective:** 2401.577
**Absolute difference:** 170.2

## Description

The markov model (Strategic Petroleum Reserve) is a verified-convex LP that translates and solves to MODEL STATUS 1 (Optimal), but the MCP objective is 170 higher than the NLP reference. The root cause is that the `equil` inequality constraint is entirely missing from the generated MCP due to an AD differentiation bug involving quoted string literals in variable indices.

## Root Cause

The `equil` inequality constraint references variable `z` with a quoted string literal as one index:

```gams
equil(s,spp).. z(s,"disrupted",spp)*(ord(spp) - ord(s)) =l= 0;
```

When the AD system differentiates this constraint w.r.t. variable `z`, there is a quoting mismatch:

- **VarRef indices** (from IR): `('3', '"disrupted"', '6')` — embedded quotes preserved
- **Instance indices** (from set enumeration): `('3', 'disrupted', '6')` — unquoted

The literal comparison in `differentiate_expr` fails, returning `Const(0.0)` instead of `Const(1.0)` for every entry. This makes the entire inequality Jacobian empty (0 entries for 64 rows x 129 cols).

### Chain of Consequences

1. **AD layer**: All J_ineq entries for `equil` evaluate to zero
2. **Stationarity**: `lam_equil` multiplier never appears in any stationarity term
3. **MCP emitter**: `equil` equation, its complementarity pair, and `lam_equil` are all dropped
4. **MCP solve**: PATH solves a relaxed problem (without equil), producing a feasible but suboptimal solution

### Secondary Issue: Stationarity Index Lifting for `constr`

The `constr` equation's contribution to `stat_z` also has incorrect index lifting. The generated equation contains `pi(s,i,s,i,spp)` where the 3rd and 4th indices should be constraint domain indices being summed over, not the variable domain indices `s` and `i`.

## Reproduction

```bash
python -m src.cli data/gamslib/raw/markov.gms -o /tmp/markov_mcp.gms
gams /tmp/markov_mcp.gms lo=2
# MCP obj = 2571.794

gams data/gamslib/raw/markov.gms lo=2
# NLP obj = 2401.577

# Verify equil is missing from MCP:
grep -c 'lam_equil\|equil' /tmp/markov_mcp.gms
# Returns 0 — constraint entirely absent
```

## Affected Files

- `src/ad/constraint_jacobian.py` (lines ~652-684): Index substitution preserves quotes but instance enumeration strips them
- `src/ad/derivative_rules.py`: VarRef index matching is literal (no quote normalization)
- `src/kkt/stationarity.py` (~line 2529): Index lifting for `constr` Jacobian transpose

## Recommended Fix

Normalize quoted string literals during VarRef index comparison in the AD layer. Either:
1. Strip embedded quotes from VarRef indices during `_substitute_indices` in constraint_jacobian.py
2. Add quote-aware comparison in `differentiate_expr` to treat `"disrupted"` and `disrupted` as equivalent

The secondary index lifting issue in stationarity.py requires separate investigation.

## Related Issues

- #1099 (marco): Similar quoted-literal index issue in stationarity, fixed for parameter refs but not AD
- #914 (markov): Previous issue was uninitialized `pi` parameter (RESOLVED)

## Estimated Effort

2-3h for the primary AD quoting fix. Secondary stationarity index lifting is additional 2-3h.
