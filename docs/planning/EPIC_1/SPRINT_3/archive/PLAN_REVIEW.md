# Sprint 3 Plan Review

## Gaps & Risks

- **Missing data/alias emission:** Day 4 only scopes emitting sets for multiplier indexing and the new KKT structures (`docs/planning/SPRINT_3/PLAN_ORIGINAL.md:430-480`), but it never schedules re-emitting the original set/alias declarations or parameter/scalar data from Sprint 1 (`ModelIR.sets`, `ModelIR.aliases`, `ModelIR.params`). The generated MCP will reference those symbols (e.g., `sum(i, x(i))`, `param(i)`), so without redeclaring them—or embedding the original declarations via `$include`—the emitted GAMS will not compile.
- **Bounds vs. explicit constraints not addressed:** The project plan calls out avoiding duplicate handling when a user already encoded bounds as equations. Current partitioning simply filters out normalized bounds (`docs/planning/SPRINT_3/PLAN_ORIGINAL.md:154-208`) and never checks for overlapping explicit constraints, so the MCP could end up with both the user’s inequality and an auto-generated bound complementarity pair.
- **Infinite bounds handling absent:** Bound multipliers are created unconditionally in stationarity/complementarity (`docs/planning/SPRINT_3/PLAN_ORIGINAL.md:218-320`), but Sprint 1 encodes ±INF using `math.inf`. There is no task to skip π^L/π^U rows or Jacobian columns when a bound is infinite, which will yield meaningless complementarity rows and non-compiling GAMS constants.
- **Objective variable/equation flow undefined:** Stationarity assembly iterates “for each variable instance” (`docs/planning/SPRINT_3/PLAN_ORIGINAL.md:230-248`) but the plan never calls out special handling for the objective variable and its defining equation (`ObjectiveIR`). Without an explicit plan, the KKT may miss the objective equation or produce an extra stationarity row for the objective variable.

## Suggested Adjustments

1. Add an emission task for original symbols: emit `Sets`, `Alias`, `Parameters`, and their data (or wire the generated MCP to `$include` the original declarations) before introducing the KKT blocks.
2. Extend constraint partitioning to detect user-authored bounds that duplicate `normalized_bounds` entries and warn/skip generating extra complementarity pairs as promised in the Sprint 3 project plan.
3. Teach the bound logic to skip π^L/π^U when `lo`/`up` are infinite, and ensure the emitted GAMS omits those complementarity rows.
4. Allocate work to thread the objective definition through the KKT system (e.g., pull `ObjectiveIR.objvar` and its equality) so the solver gets the correct stationarity row and doesn’t double-count or omit the objective variable.
