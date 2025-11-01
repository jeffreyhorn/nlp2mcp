# Sprint 2 Plan – Final Review

## Alignment With PROJECT_PLAN.md

- The revised plan now covers the Sprint 2 components listed in `docs/planning/PROJECT_PLAN.md:69-93`, including AD core work, indexed sums, sparse Jacobian extraction, objective gradients, and a comprehensive testing push.
- Days 5–8 explicitly address the sparse Jacobian map and the inclusion of normalized bounds, matching the Sprint 2 deliverables and acceptance criteria.

## Remaining Gaps & Risks

- **Differentiation approach documentation:** With the decision to pursue symbolic (AST → AST) differentiation, the revised plan aligns with implementation intent, but `docs/planning/PROJECT_PLAN.md:69-81` still promises reverse-mode AD. Unless those references are updated, stakeholders may expect an adjoint-style engine that will not materialize.
- **Finite-difference baselines unspecified:** Day 9 schedules FD validation (`docs/planning/SPRINT_2_PLAN_REVISED.md:346-390`), but the plan never states how concrete variable values will be generated or sourced for those checks. Lacking a repeatable seeding strategy risks flaky validation or unusable utilities.
- **Alias/universe expansion left implicit:** Days 5–6 talk about expanding domain sets to member tuples (`docs/planning/SPRINT_2_PLAN_REVISED.md:235-242`), yet there is no mention of resolving `ModelIR.aliases` or respecting alias universes from Sprint 1. Missing this nuance will break Jacobian row/column enumeration for aliased sets.
- **NaN/Inf detection still absent:** Safety requirements in `docs/planning/PROJECT_PLAN.md:85-88` call for automatic NaN/Inf checks, but the revised schedule only mentions domain guards and stability tests; no day allocates time to detect/propagate numeric contamination during AD or evaluation.

## Suggested Adjustments

1. Update PROJECT_PLAN (and any other high-level docs) to reflect the symbolic differentiation strategy so expectations stay consistent.
2. Introduce a Day 9 sub-task to define deterministic FD seed points (e.g., reproducible random seeds or IR-provided initial values) and store them in helper utilities/tests.
3. Extend the indexing work to cover alias resolution—enumerate member tuples through `ModelIR.sets` and `ModelIR.aliases`, and test scenarios that rely on alias universes.
4. Schedule a safety task (Day 2 or Day 9) to surface NaNs/Infs from the evaluator/AD passes with actionable errors, satisfying the reproducibility requirement from the sprint plan.
