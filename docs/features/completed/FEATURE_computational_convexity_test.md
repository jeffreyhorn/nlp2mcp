# Computational Convexity Test via Dual KKT Comparison

**Status:** Proposed
**Priority:** Low — diagnostic/research feature, not blocking any models
**Depends on:** `--nlp-presolve` (implemented in Sprint 24)
**Estimated effort:** 2-3 hours

---

## Motivation

nlp2mcp currently detects potential non-convexity using heuristic pattern
matching (W301 nonlinear equality, W303 bilinear terms, W305 odd powers).
These are syntactic checks — they flag structures that are *often*
non-convex but produce false positives (e.g., `x^2 + y^2 = r^2` is flagged
as W301 even though it may be locally convex at the solution).

A computational test can **prove** non-convexity with zero false positives
by exploiting a fundamental property of convex optimization:

> **For a convex minimization problem, every KKT point is a global minimum.**
> Two KKT points with different objective values cannot exist.

If the MCP system has two solutions with different objective values, the
original NLP is provably non-convex.

---

## Method

The test exploits the fact that nlp2mcp already produces two independent
MCP solves when `--nlp-presolve` is used:

1. **Cold-start solve:** PATH solves the MCP from default initialization
   (all dual variables = 0). This finds KKT point A.

2. **Warm-start solve:** The NLP pre-solve provides primal + dual
   initialization near the NLP optimum. PATH finds KKT point B.

If both solves reach STATUS 1 (Optimal) but with **different objective
values** (|A - B| > tolerance), the problem is **provably non-convex**.

### Interpretation Table

| Cold Start | Pre-Solve | Conclusion |
|---|---|---|
| STATUS 1, obj=A | STATUS 1, obj=B, A ≠ B | **Non-convex (proven)** — two distinct KKT points |
| STATUS 1, obj=A | STATUS 1, obj=A | Inconclusive — same KKT point (or convex) |
| STATUS 5 | STATUS 1, obj=B | Likely non-convex — cold start couldn't converge |
| STATUS 5 | STATUS 5 | Inconclusive — could be formulation bug |
| STATUS 1, obj=A | STATUS 5 | Unusual — cold start found something pre-solve missed |

### Mathematical Justification

For a convex problem min f(x) s.t. g(x) ≤ 0, h(x) = 0:

- **Necessity:** KKT conditions are necessary at any local minimum.
- **Sufficiency:** Under convexity + constraint qualification, KKT
  conditions are also sufficient for global optimality.
- **Uniqueness of value:** All KKT points share the same objective value
  (even if the solution set is not a singleton — e.g., f(x)=0 on a convex
  feasible set has infinitely many solutions, all with f=0).

Therefore, two KKT solutions with f(A) ≠ f(B) implies that at least one
of them is NOT a global minimum, which means KKT sufficiency fails, which
means the problem is not convex.

This argument does not require strong convexity or uniqueness of the
minimizer — only convexity of f and the feasible set.

---

## Proposed Interface

### CLI Flag

```bash
nlp2mcp input.gms -o output.gms --check-convexity-numerical
```

This would:
1. Generate the MCP as normal
2. Solve it from cold start (capture obj_cold)
3. Solve it with NLP pre-solve (capture obj_warm)
4. Compare: if both STATUS 1 and |obj_cold - obj_warm| > 1e-4, report
   "Computational non-convexity detected"

### Output

```
Computational Convexity Check:
  Cold-start MCP:  STATUS 1 Optimal, obj = 950.913
  Warm-start MCP:  STATUS 1 Optimal, obj = 1075.547
  ⚠️  Non-convex: two distinct KKT points found (difference: 124.634)
```

Or for a convex model:

```
Computational Convexity Check:
  Cold-start MCP:  STATUS 1 Optimal, obj = 7.955
  Warm-start MCP:  STATUS 1 Optimal, obj = 7.955
  ✓ Consistent (same KKT point — convexity not disproven)
```

### Programmatic API

```python
from src.diagnostics import check_convexity_numerical

result = check_convexity_numerical(mcp_file, source_file)
# result.is_nonconvex: bool (True if proven non-convex)
# result.obj_cold: float | None
# result.obj_warm: float | None
# result.status_cold: int
# result.status_warm: int
```

---

## Design Considerations

### Tolerance for Objective Comparison

Use relative tolerance: `|A - B| / max(|A|, |B|, 1) > 1e-4`. Absolute
tolerance fails for models with very large or very small objectives.

### GAMS Dependency

This feature requires GAMS to be installed. It should:
- Skip gracefully if `gams` is not on PATH
- Not be part of the default pipeline (opt-in via flag)
- Not run in CI (no GAMS license)

### Relationship to Heuristic Checks

This does NOT replace the existing W301/W303/W305 heuristic checks:

| Check | Speed | False Positives | False Negatives |
|---|---|---|---|
| Heuristic (W301 etc.) | Fast (ms) | Yes (structural patterns may be convex) | Yes (misses non-convexity from variable domains) |
| Computational (this) | Slow (requires 2 GAMS solves) | **None** (theorem-based) | Yes (both solves may find the same point) |

The heuristic check runs always; the computational check is opt-in.

### Multiple Random Starts (Future Enhancement)

The two-start approach (cold + warm) is the simplest. A future enhancement
could try N random starting points to increase the chance of finding
distinct KKT points, at the cost of N GAMS solves.

---

## Implementation Plan

### Phase 1: Standalone Script (1h)

Write `scripts/check_convexity.py` that:
1. Takes an MCP file + source file
2. Runs `gams` twice (cold, warm-started)
3. Parses listing files for MODEL STATUS and objective
4. Reports result

### Phase 2: CLI Integration (1h)

Add `--check-convexity-numerical` flag to `src/cli.py` that:
1. Generates MCP as normal
2. Writes to temp file
3. Calls Phase 1 logic
4. Reports alongside heuristic warnings

### Phase 3: Pipeline Integration (0.5h)

Add to the pipeline test infrastructure so the GAMSlib full test can
optionally run the computational check and flag non-convex models.

---

## Known Models This Would Classify

Based on Sprint 24 testing:

| Model | Heuristic | Computational | Notes |
|---|---|---|---|
| bearing | W301, W303, W305 | **Proven non-convex** (cold=1751, warm=19517) | Multiple KKT points |
| dispatch | W301, W303 | Consistent (both 7.955) | Convexity not disproven |
| ramsey | W301 | Consistent (both 2.487) | Convexity not disproven |
| pak | None (LP) | Consistent (both 1075.547) | Convex (LP) |

---

## Related Work

- `--skip-convexity-check`: Existing heuristic check (W301/W303/W305)
- `--nlp-presolve`: Required infrastructure for warm-start solve
- `docs/errors/README.md`: Convexity warning documentation
- Issue #757, #1199: bearing non-convexity investigation
