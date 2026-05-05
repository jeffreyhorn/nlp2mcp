# Multi-Solve Gate: Extend Detector for `saras`-Style Top-Level `eq.m` Feedback

**GitHub Issue:** [#1270](https://github.com/jeffreyhorn/nlp2mcp/issues/1270)
**Status:** RESOLVED — Sprint 25 Day 12 (PR #1353)
**Severity:** High — Known gap in the driver-detection gate; allows a class of driver scripts through
**Date:** 2026-04-18
**Last Updated:** 2026-05-05
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

---

## Resolution (Sprint 25 Day 12, PR #1353)

Approach A (cross-reference) landed three pieces:

1. **IR addition (`src/ir/model_ir.py`, `src/ir/parser.py`)** — new field `top_level_marginal_reads: list[tuple[str, str, str]]` populated by `_ModelBuilder.build` whenever a top-level (program-level) `assign` or `conditional_assign_general` Tree contains `bound_scalar` / `bound_indexed` reads on the RHS. The capture is over-approximate by design: every `(param_name, sym_name, attr)` tuple is recorded — the gate is the single point of truth for what counts as "feedback".

2. **Validator extension (`src/validation/driver.py`)** — new helper `_params_referenced_in_any_constraint_body(model_ir)` computes the transitive closure of "parameters that feed any equation body":
   - Seed: walk every equation's `lhs_rhs` for `ParamRef` nodes (direct refs).
   - Closure: for each `Q` in the seed, walk `Q`'s assignment expressions and add every parameter `P` that `Q` reads. `P` reaches the body via `Q`. Repeat until saturation. Self-referential expressions terminate naturally.

3. **Gate update** — `scan_multi_solve_driver` now walks `top_level_marginal_reads`, filters to `attr == "m"` AND `sym ∈ equation_names`, and emits `(eq_name, "m")` whenever the receiving parameter is in the transitive cross-ref set. Variable-attribute reads (`var.l`, `var.m` for non-equation symbols) and parameters that never feed a constraint body (post-solve display targets) are filtered out.

Catches saras's chain end-to-end:
```
clam(r,f,t,p)$cond = calibuc.m(r,f,t,p)   ← captured in top_level_marginal_reads
cGam(...) = f(clam(...))                   ← cgam consumes clam (param expr)
nclpobj_(...).. ... + cGam(...) =E= ...    ← cgam in equation body → seed → closure adds clam
```

### Verification

Corpus check (saras flags as target; canaries / previous false-positive candidates do not):

| Model | declared | solves | margs | is_driver | Notes |
|---|---|---|---|---|---|
| `saras` | 2 | 2 | calibuc.m, calibul.m | **TRUE** | Target — primal/dual driver. |
| `gussrisk` | 1 | 1 | — | False | Single-model regression canary. |
| `sparta` | 4 | 4 | — | False | Multi-model matching canary. |
| `partssupply` | 2 | 2 | — | False | `var.l` post-solve report — Approach A scopes to `.m`. |
| `ibm1` | 1 | 1 | — | False | Single-model regression canary. |
| `imsl` | 2 | 2 | — | False | Previous false-positive candidate; correctly excluded. |
| `otpop` | 3 | 3 | — | False | Same. |
| `turkey` | 2 | 2 | — | False | Same. |

### Tests

`tests/unit/validation/test_driver.py`:
- F1 `test_scan_saras_style_top_level_marginal_with_feedback_is_driver` — saras-shape: `clam = calibuc.m`, `cGam = f(clam)`, equation body uses `cGam`. MUST flag.
- F2 `test_scan_post_solve_reporting_no_constraint_feedback_is_not_driver` — single solve + display-only param. MUST NOT flag.
- F3 `test_scan_multi_stage_display_no_constraint_feedback_is_not_driver` — two solves, marginal read between, but param never reaches a body. MUST NOT flag (the case Approach B would over-fire on).
- F4 `test_scan_partssupply_var_l_top_level_is_not_driver_under_approach_a` — `var.l` and `var.m` (variable, not equation) reads filtered out by gate.

`tests/integration/test_decomp_skipped.py`:
- New `test_cli_refuses_synthetic_saras_primal_dual_exit_code_4` covers exit-4 + error-message wiring on a self-contained primal/dual fixture.

### PR review hardening (PR #1353)

- Docstring of `_params_referenced_in_any_constraint_body` reworded to match the implemented dependency-walk direction.
- `MultiSolveDriverError` message changed from "feedback inside solve loop" to scope-neutral "feedback to a subsequent solve".
- Parser hook now records all attrs (over-approximation) so the gate's filter is the single point of truth — matches the field comment.
- Fixed a latent indexing bug in `_loop_tree_to_gams`'s `dollar_cond` non-substituting path that read RHS from the DOLLAR-token slot (verified safe via byte-diff: no model produced `$$` artifacts pre-fix).

### Note on saras's pipeline status

`data/gamslib/gamslib_status.json` saras entry is left for the next pipeline retest. The translate stage now raises `MultiSolveDriverError`, which `batch_translate.py` records as `translate.status = failure / category = internal_error` with the multi-solve message — matching how decomp / danwolfe are tracked. The retest will auto-write the canonical `pipeline_status.reason = multi_solve_driver_out_of_scope` entry.
