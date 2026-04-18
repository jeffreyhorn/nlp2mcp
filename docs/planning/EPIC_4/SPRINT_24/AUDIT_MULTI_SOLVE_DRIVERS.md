# Audit: Multi-Solve Driver Scripts in GAMSlib

**Sprint 24 · Phase 0 of PLAN_FIX_DECOMP**

**Question.** Before adding a `multi_solve_driver_out_of_scope` gate
to the translator, which in-scope corpus models does the detector
flag as driver scripts? Are any of them currently solving
successfully (which would be a regression)?

**Method.** Pre-filter to models with `convexity.status ∈
{verified_convex, likely_convex}` AND no existing
`pipeline_status.status == "skipped"` AND at least 2 live `solve`
statements AND at least 2 `Model` declarations in the raw source.
Then parse with `src.ir.parser.parse_model_file` and classify via
`src.validation.driver.scan_multi_solve_driver` (three-condition
conjunction: ≥2 declared models, ≥2 distinct solve-target models,
≥1 equation-marginal access inside a solve-containing `loop`).

## Results

**Pre-filter:** 10 in-scope candidates.

**Detector hits:** 2.

| Model | Declared models | Solve targets | Equation marginals | Current solve status |
|---|---|---|---|---|
| **decomp** | `sub`, `master` | `sub`, `master` | `tbal.m`, `convex.m` | failure (path_syntax_error) |
| **danwolfe** | `master`, `mcf`, `pricing` | `master`, `mcf`, `pricing` | `mdefbal.m` | failure (path_solve_license) |

**Non-hits** (pre-filtered candidates that did NOT classify as
drivers — these must continue to translate/solve after the gate lands):

- `partssupply` (2 models, `m`/`m_mn`; attrs are `util.l` / `x.l`,
  which are *variable levels*, not equation marginals → not a
  driver). Today: solve=success, match. **Must not regress.**
- `saras` (2 models, 10 solves, `.m` on equations but at top level,
  not inside a solve-loop). Today: solve=failure. Not caught by the
  strict rule. Known gap; see Risks in `PLAN_FIX_DECOMP.md`.
- Other 2-model candidates with sensitivity-style patterns (all
  non-driver, all currently solving or failing independently of this
  gate).

## Conclusion

Safe to land the gate. Expected deltas:

- `decomp` and `danwolfe`: failure → skipped (
  `pipeline_status.reason = multi_solve_driver_out_of_scope`).
- `partssupply`: unchanged (continues to succeed).
- No other in-scope model flips status.

**Key regression guards for the test suite:**
- `ibm1` (single declared model, 5 solves on it): must NOT raise
  `MultiSolveDriverError`. Continues to translate/solve today.
- `partssupply` (2 models but no equation marginals in its solve
  loop): must NOT raise. End-to-end test asserts it remains
  `solve=success, comparison=match`.

The known gap on `saras`-style two-stage calibration scripts
(equation marginals read at *top level* between solves, not inside
a solve-containing loop) is deliberate: broadening the rule risks
false positives on post-solve reporting patterns common in the
corpus. Revisit if `saras` becomes a priority.
