# robustlp: Diagonal Parameter Expansion Bug

**GitHub Issue:** [#1105](https://github.com/jeffreyhorn/nlp2mcp/issues/1105)
**Status:** FIXED
**Model:** robustlp (GAMSlib SEQ=318)

## Description

The robustlp model had two issues:

1. **Diagonal parameter expansion** (primary, FIXED earlier): `src/ir/parser.py`
   expanded `P(i,j,j)` to all 112 Cartesian product entries instead of the
   28 diagonal entries where the 2nd and 3rd indices are equal.

2. **PATH cold-start convergence** (secondary, FIXED by `--nlp-presolve`):
   Even with the corrected diagonal P matrix, PATH returned MODEL STATUS 5
   from default initialization. The SOCP complementarity structure creates
   a nonlinear landscape that PATH cannot navigate from zero initialization.

## Fix

**Primary fix** (Sprint 22): Ported diagonal constraint logic from
`_handle_variable_bounds_assignment` to parameter expansion code. Added
`symbol_positions` tracking to detect repeated index symbols and filter
the Cartesian product.

**Secondary fix** (Sprint 24, `--nlp-presolve`): The `--nlp-presolve`
flag solves the original NLP first and warm-starts MCP dual variables,
allowing PATH to converge.

```bash
nlp2mcp robustlp.gms -o robustlp_mcp.gms --nlp-presolve
```

The pipeline test runner now automatically retries STATUS 5 models with
`--nlp-presolve`, so robustlp passes the full pipeline without manual
intervention.

**Result:** MODEL STATUS 1 Optimal, obj = -2.330 (exact NLP match).

## Related Issues

- #1021: Variable bounds diagonal expansion fix (same pattern, ported from)
- #938: Previous robustlp digamma derivative issue (RESOLVED)
