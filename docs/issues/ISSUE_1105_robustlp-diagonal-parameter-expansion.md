# robustlp: Model Infeasible — Diagonal Parameter Expansion Bug

**GitHub Issue:** [#1105](https://github.com/jeffreyhorn/nlp2mcp/issues/1105)
**Status:** OPEN
**Model:** robustlp (GAMSlib SEQ=318)
**Error category:** `model_infeasible`
**MCP solve status:** MODEL STATUS 5 (Locally Infeasible)

## Description

The robustlp model (Robust Linear Programming as SOCP) translates to MCP but solves as model_infeasible. There are two issues: (1) a parser bug that expands diagonal parameter assignments `P(i,j,j)` to all (i,j,k) combinations instead of only diagonal entries, and (2) a PATH solver convergence difficulty from cold start even with correct parameters.

## Root Cause 1: Diagonal Parameter Expansion Bug (Primary)

The original model defines:

```gams
Alias (j,k);
Parameter P(i,j,k);
P(i,j,j) = %mu%;   * Only diagonal entries where 2nd and 3rd indices are equal
```

In GAMS, `P(i,j,j)` means "for all i, for all j, set P(i,j,j) = mu" — only 28 diagonal entries (7 i * 4 j). Off-diagonal entries remain 0.

The IR parser's parameter domain-over expansion (`src/ir/parser.py`, lines ~4471-4489) builds a full Cartesian product without checking for repeated index symbols:

```python
for combo in product(*dim_values):
    param.values[combo] = value
```

When indices `(i, j, j)` map to domains `(i, j, k)`, positions 1 and 2 both expand independently over j's members, producing all 4*4=16 combinations per i instead of just 4 diagonal pairs. This generates 112 entries instead of 28.

**Note:** This same bug pattern was already fixed for variable bounds in `_handle_variable_bounds_assignment` (Issue #1021, lines 6596-6704) which has explicit diagonal constraint logic. That same approach should be ported to parameter expansion.

### Impact on MCP

The wrong P matrix causes `defv(i,k)` and `stat_x(j)` equations to have incorrect coefficients, leading to structural infeasibility.

## Root Cause 2: PATH Convergence from Cold Start (Secondary)

Even with the corrected diagonal P matrix, PATH returns MODEL STATUS 5 from default (zero) initialization. However, warm-starting from the QCP solution produces MODEL STATUS 1 (Optimal, obj=-1.640, matching the reference).

The SOCP complementarity structure (`sqr(y(i)) >= sum(k, sqr(v(i,k)))`) creates a nonlinear landscape that PATH struggles to navigate from zero initialization.

## Reproduction

```bash
python -m src.cli data/gamslib/raw/robustlp.gms -o /tmp/robustlp_mcp.gms
gams /tmp/robustlp_mcp.gms lo=2
# MODEL STATUS 5 (Locally Infeasible)

# Verify wrong P matrix:
grep "P(" /tmp/robustlp_mcp.gms | wc -l
# Returns 112 — should be 28 (only diagonal entries)
```

## Affected Files

- `src/ir/parser.py` (lines ~4471-4489): Parameter domain-over expansion lacks repeated-index filtering
- `src/ir/parser.py` (lines ~6596-6704): Variable bounds already has the fix (port from here)

## Other Potentially Affected Models

Models with repeated-index parameter assignments:
- `saras.gms`: `VarRMR(r,p,p)` and `STDRMR(r,p,p)` patterns

## Recommended Fix

1. **Issue 1**: Port the diagonal constraint logic from `_handle_variable_bounds_assignment` (lines 6596-6704) to the parameter expansion code at line 4471. Track `symbol_positions` for repeated index names and filter the Cartesian product to only include tuples where repeated-index positions have equal values.
2. **Issue 2**: This is a `path_solve_terminated` category issue requiring warm-start infrastructure (defer).

## Related Issues

- #1021: Variable bounds diagonal expansion fix (same pattern, already resolved)
- #938: Previous robustlp issue was digamma derivative (RESOLVED)

## Estimated Effort

1-2h for the diagonal parameter fix (port existing logic). PATH convergence is a separate infrastructure issue.
