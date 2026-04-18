# Multi-Solve Gate: Extend Detector for `saras`-Style Top-Level `eq.m` Feedback

**GitHub Issue:** [#1270](https://github.com/jeffreyhorn/nlp2mcp/issues/1270)
**Status:** OPEN — Deferred to Sprint 25
**Severity:** High — Known gap in the driver-detection gate; allows a class of driver scripts through
**Date:** 2026-04-18
**Last Updated:** 2026-04-18
**Affected Models:** `saras` (two-stage primal-dual calibration) and any other two-stage calibration pattern that reads `eq.m` at top level between `solve` statements
**Labels:** `sprint-25`

---

## Problem Summary

The multi-solve-driver gate added in PR #1265 (`src/validation/driver.py::scan_multi_solve_driver`) flags a file as a driver script only when **three conditions all hold**:

1. `len(declared_models) ≥ 2`
2. `len(solve_targets) ≥ 2` (distinct model names across all `solve` statements)
3. `≥ 1 equation marginal (eq.m) accessed inside a loop that also contains a solve`

Condition 3 was deliberately narrowed to "inside a solve-containing loop" to avoid false positives on post-solve reporting — the common GAMSlib pattern where a `.m` value is written into a display parameter for table output after a single solve.

This narrow rule correctly catches `decomp` and `danwolfe` (classical Dantzig–Wolfe iteration) but **misses `saras`-style two-stage calibration**, which reads `eq.m` at *top level* (outside any `loop`) between two `solve` statements. The receiving parameter then feeds the second solve's constraints. This is semantically a driver script — the converged objective is a fixed point across the two solves — but the gate lets it through with `is_driver=False`, and the resulting MCP represents only the second solve's KKT, not the converged primal-dual result.

---

## Why This Was Deferred

`decomp` and `danwolfe` were the immediate DW targets for Sprint 24 and matched the strict rule cleanly. `saras` was identified as a known gap during the Sprint 24 audit (`AUDIT_MULTI_SOLVE_DRIVERS.md`) but extending the rule risked breaking the ~dozen post-solve-reporting patterns in the corpus. The narrow rule was shipped (PR #1265) and the broader detection is tracked here.

Full context: `SPRINT_LOG.md` Day 8 §"Known gap (deferred)"; `PLAN_FIX_DECOMP.md` §"Known gap (deferred to Sprint 25)".

---

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/saras.gms -o /tmp/saras_mcp.gms
# → currently: translates to an MCP (gate does not fire)
# → desired:   exit 4 with the `multi_solve_driver_out_of_scope` message
```

Confirm the gate's report:

```bash
.venv/bin/python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
from src.validation.driver import scan_multi_solve_driver
ir = parse_model_file('data/gamslib/raw/saras.gms')
r = scan_multi_solve_driver(ir)
print('is_driver =', r.is_driver)
print('declared =', r.declared_models)
print('targets  =', r.solve_targets)
print('marginals=', r.equation_marginals)
"
# → is_driver=False; equation_marginals=[]  (the top-level reads don't qualify)
```

---

## Candidate Approaches (Decide in Sprint 25)

### Approach A — Cross-reference parameters to constraints

Flag an `eq.m` read whose receiving parameter is later referenced in another declared model's constraint body. Tighter false-positive profile because post-solve reporting writes `eq.m` into *display* parameters, not into KKT-relevant coefficients.

**Pros:** Principled — matches the semantic definition of dual feedback.
**Cons:** Requires parameter-usage tracking across equation bodies; moderately complex to implement reliably.

### Approach B — Sequence awareness (between two solves)

Flag `eq.m` reads that appear **between** two `solve` statements in source order, whether or not inside a loop.

**Pros:** Simple to implement.
**Cons:** Still catches post-solve reporting placed between two solves in multi-stage display code. May need an additional exclusion for `display` / `put` / `abort` statements in the vicinity.

### Approach C — Explicit corpus allowlist

Add `multi_solve_driver_out_of_scope` to specific models (including `saras`) directly in `gamslib_status.json`, bypassing the detector.

**Pros:** Zero detection-logic churn.
**Cons:** Does not scale to new corpora; treats symptoms rather than cause.

**Recommendation:** Start with Approach A. It has the cleanest semantics and the tests can be written to distinguish reporting from feedback.

---

## Scope of Work

- `src/validation/driver.py::scan_multi_solve_driver` — detector extension.
- `src/validation/driver.py::MultiSolveReport` — may need a new field to distinguish top-level-between-solves reads from in-loop reads for better user messaging.
- `tests/unit/validation/test_driver.py` — add fixtures:
  - `saras`-style (top-level between solves, parameter then feeds second solve) → **must flag**
  - Post-solve reporting (top-level after single solve, parameter goes to `display`) → **must NOT flag**
  - Multi-stage display (top-level between two solves but parameter unused in later solves) → **must NOT flag**
- `tests/integration/test_decomp_skipped.py` — add synthetic fixture for the saras-style pattern exercising CLI exit-code 4.

---

## Regression Guards (must continue to pass)

- `ibm1` (1 model, 5 solves on same model) — not a driver, must translate.
- `partssupply` (2 models, 2 targets, post-solve reporting reads `var.l`, not `eq.m`) — not a driver, must translate.
- All currently-matching models — no false positives.

---

## Estimated Effort

2–3 hours for Approach A + test matrix. Add 1–2 hours if the scope extends to parameter-usage tracking across solves.

---

## References

- `docs/planning/EPIC_4/SPRINT_24/SPRINT_LOG.md` Day 8 §"Known gap (deferred)"
- `docs/planning/EPIC_4/SPRINT_24/AUDIT_MULTI_SOLVE_DRIVERS.md`
- `docs/planning/EPIC_4/SPRINT_24/PLAN_FIX_DECOMP.md` §"Known gap (deferred to Sprint 25)"
- PR #1265 (merged) — multi-solve-driver gate
- Sibling issues: #1268 (emitter), #1269 (KKT assembly), #1271 (dispatcher refactor)

---

## Files Involved

- `src/validation/driver.py` — detector and report
- `tests/unit/validation/test_driver.py` — unit tests
- `tests/integration/test_decomp_skipped.py` — CLI integration tests
- `data/gamslib/raw/saras.gms` — reference corpus example
