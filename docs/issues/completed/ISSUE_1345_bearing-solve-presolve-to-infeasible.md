# bearing: Solve regression — `model_optimal_presolve` → `model_infeasible (status 5)`

**GitHub Issue:** [#1345](https://github.com/jeffreyhorn/nlp2mcp/issues/1345)
**Status:** RESOLVED
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (solve + match)
**Date:** 2026-05-03
**Affected Models:** bearing (SEQ=30, NLP, Hydrostatic Thrust Bearing Design for a Turbogenerator)
**Regression introduced:** between Sprint 25 Day 0 and Day 11

---

## Summary

`bearing` solved successfully at Sprint 25 Day 0 baseline via the `model_optimal_presolve` retry path (STATUS 5 retry with NLP pre-solve, obj=19517.3319, **matched** the NLP reference). On the current branch the solve stage now fails outright with `Locally Infeasible (status 5)` and the previous match is lost.

This is one of three Sprint 25 regressions in the `model_optimal_presolve` cohort (with `mathopt3`, `rocket`).

---

## Resolution

**Root cause: pipeline test infrastructure, not emit/AD.** The presolve MCP file itself is correct — running `gams data/gamslib/mcp/bearing_mcp_presolve.gms` directly from the project root succeeds with PATH "Normal Completion" (objective ≈ 19517.33).

The pipeline test runner (`scripts/gamslib/test_solve.py::solve_mcp`) invoked GAMS with `cwd=tmpdir` (a temporary directory used to isolate scratch files). When commit `809b5008` (#1275) changed the emitter to write a repo-relative `$include "data/gamslib/raw/<model>.gms"` (down from absolute `/Users/jeff/...`), the include began failing with `Error 282: Unable to open include file` because the relative path was resolved against the tmpdir, not the repo root. That cascaded to `MODEL STATUS 4` for the source's NLP solve, which produced no warm-start — and the MCP solve then converged to a `MODEL STATUS 5` (Locally Infeasible) on a cold start.

The `--nlp-presolve` warm-start logic itself is correct. The Sprint 25 Day-1–10 commits hypothesised in the issue (#1330 round 3, c667b658 #1313) do change emit ordering and var-init suppression, but the resulting MCP files solve correctly when GAMS can find the `$include`'d source.

### Fix

`scripts/gamslib/test_solve.py::solve_mcp` now:

1. Runs GAMS with `cwd=str(PROJECT_ROOT)` so repo-relative `$include "data/gamslib/raw/<model>.gms"` resolves.
2. Passes `ScrDir=<tmpdir>` so GAMS's scratch tree (`225a/`, .gdx, .pf, .lf) is still isolated to a TemporaryDirectory and never pollutes the repo.

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --model bearing --only-solve --verbose
…
[RETRY] SUCCESS with --nlp-presolve: objective=19517.3
[COMPARE] MATCH

Solve Results:
  Success: 1 (100.0%)
  Failure: 0
  Pre-solve retry: 1/1 recovered from STATUS 5

Comparison Results:
  Match: 1 (100.0%)
```

### Regression test

Added `tests/gamslib/test_test_solve.py::TestSolveMcp::test_solve_runs_from_project_root_with_isolated_scrdir`. Patches `subprocess.run` and asserts:

1. `cwd` passed to `subprocess.run` equals `str(PROJECT_ROOT)`.
2. The gams command line includes a `ScrDir=<...>` argument.

These two together prevent the regression from recurring (either reverting to `cwd=tmpdir` or dropping the scratch redirect).

### Acceptance criteria status

- ✅ `bearing` solves to `model_optimal_presolve` with obj ≈ 19517.33.
- ✅ comparison status returns to `match`.
- ✅ Regression test added.

---

## Related

- Closed: #757, #835, #1199 — historical bearing issues (different root causes).
- Sister regressions: `mathopt3` (#1346), `rocket` (#1347) — same root cause, fixed by the same pipeline change.
- #1275 / `809b5008` — the absolute → repo-relative `$include` change that exposed the latent `cwd=tmpdir` mismatch.
- #1330 round 3 (`d9d50c65`), #1313 (`c667b658`) — initially suspected but actually unrelated. The presolve emit changes they introduced are correct; the pipeline runner's working directory was the bug.
