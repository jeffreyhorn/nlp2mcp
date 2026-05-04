# mathopt3: Solve regression — `model_optimal_presolve` → `model_infeasible (status 5)`

**GitHub Issue:** [#1346](https://github.com/jeffreyhorn/nlp2mcp/issues/1346)
**Status:** RESOLVED
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (solve + match)
**Date:** 2026-05-03
**Affected Models:** mathopt3 (SEQ=201, NLP, MathOptimizer Example 3)
**Regression introduced:** between Sprint 25 Day 0 and Day 11

---

## Summary

`mathopt3` solved successfully at Sprint 25 Day 0 baseline via `model_optimal_presolve` (obj=0.0, **matched**). On the current branch solve fails with `Locally Infeasible (status 5)`.

One of three Sprint 25 regressions in the `model_optimal_presolve` cohort (with `bearing`, `rocket`).

---

## Resolution

**Same root cause as #1345 (bearing) and #1347 (rocket): pipeline test infrastructure, not emit/AD.** The presolve MCP file itself is correct — `gams data/gamslib/mcp/mathopt3_mcp_presolve.gms` from the project root succeeds with PATH "Normal Completion" in 3 major iterations.

The pipeline runner ran GAMS with `cwd=tmpdir`. After #1275 (commit `809b5008`) changed `--nlp-presolve` to emit a repo-relative `$include "data/gamslib/raw/mathopt3.gms"`, that include failed to resolve under tmpdir (`Error 282`). The source's NLP pre-solve then aborted, leaving no warm-start, and PATH converged to `model_infeasible (status 5)` on a cold start.

### Fix

`scripts/gamslib/test_solve.py::solve_mcp` now runs GAMS with `cwd=str(PROJECT_ROOT)` (so the include resolves) and passes `ScrDir=<tmpdir>` (so scratch files stay out of the repo). See #1345 for the detailed fix description and the regression test.

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --model mathopt3 --only-solve --verbose
…
[RETRY] SUCCESS with --nlp-presolve: objective=0
[COMPARE] MATCH

Solve Results:
  Success: 1 (100.0%)
  Pre-solve retry: 1/1 recovered from STATUS 5

Comparison Results:
  Match: 1 (100.0%)
```

### Acceptance criteria status

- ✅ `mathopt3` solves to `model_optimal_presolve` with obj ≈ 0.0.
- ✅ comparison status returns to `match`.
- ✅ Regression test added (shared with #1345 — the underlying fix is one cwd/ScrDir change in `solve_mcp`).

---

## Related

- Sister regressions: `bearing` (#1345), `rocket` (#1347) — same root cause.
- #1275 / `809b5008` — the absolute → repo-relative `$include` change that exposed the latent `cwd=tmpdir` mismatch.
- #1330 round 3 (`d9d50c65`) — initially suspected but actually unrelated.
