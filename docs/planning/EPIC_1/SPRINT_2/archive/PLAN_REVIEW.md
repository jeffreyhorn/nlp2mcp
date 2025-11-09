# Sprint 2 Plan Review

## Gaps & Risks

- `docs/planning/SPRINT_2_PLAN.md:117` claims v1 unary coverage includes `abs`, but `docs/planning/PROJECT_PLAN.md:16` explicitly defers it; clarify whether Sprint 2 will reject or smooth `abs`, or update the success metric.
- Unary `+`/`-` derivatives are missing from the Day 2 scope even though the parser emits `Unary` nodes for them (`docs/planning/SPRINT_2_PLAN.md:58`, `src/ir/ast.py:44`); add work to support these forms.
- Finite-difference validation on Day 9 (`docs/planning/SPRINT_2_PLAN.md:244`) needs an expression evaluator that can plug concrete values into the AST (e.g., using `ParameterDef.values` and variable assignments); schedule its implementation earlier so AD and FD can run.
- Objective gradient tasks (`docs/planning/SPRINT_2_PLAN.md:191`) assume access to an explicit objective expression, but `ObjectiveIR` often contains only the objective variable name (`src/ir/model_ir.py:19`); plan to retrieve the defining equation or stored expression before computing gradients.
- The plan adds a runtime dependency on `numpy` (`docs/planning/SPRINT_2_PLAN.md:360`), yet `pyproject.toml:22` still lists only `lark`; include dependency updates or document a pure-Python fallback.
- Constraint Jacobian work on Day 8 (`docs/planning/SPRINT_2_PLAN.md:218`) should also cover normalized bound equations emitted in `normalize_model` (`src/ir/normalize.py:49`); ensure those rows enter the sparsity and Jacobian build.
- Every day is already fully allocated while aiming for 60+ new tests (`docs/planning/SPRINT_2_PLAN.md:18`); consider reserving slack or stretching the sum/sparsity milestones to absorb debugging time for indexing and FD mismatches.

## Suggested Adjustments

1. Decide on the Sprint 2 policy for `abs` (reject, smooth, or postpone) and align the success metrics accordingly.
2. Slot unary-operator derivative support alongside the binary rules.
3. Add an AST evaluator task before FD validation begins.
4. Extend the gradient plan to locate the objective expression from the IR.
5. Update packaging documentation/dependencies when introducing `numpy`.
6. Explicitly include bound-derived rows in Jacobian tasks and tests.
7. Rebalance the schedule (e.g., two days for sums/sparsity) to provide debugging slack.
