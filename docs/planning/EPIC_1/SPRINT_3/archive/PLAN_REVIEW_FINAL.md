# Sprint 3 Plan – Final Review

## Findings
- Partition logic still appends suspected duplicate bound inequalities even after flagging them (`docs/planning/SPRINT_3/PLAN_REVISED.md:197-210`), so the KKT assembly will continue to generate both the user-authored inequality and the auto-derived bound complementarity pair despite the warning.
- Bound processing only inspects scalar `.lo`/`.up` attributes (`docs/planning/SPRINT_3/PLAN_REVISED.md:217-230`) and ignores the per-index `lo_map` / `up_map` data Sprint 1 surfaces. Indexed bounds (and their ±∞ cases) will therefore never receive π multipliers or skips.
- The original-symbol emission examples reference fields that do not exist on the current IR (`set_def.elements`, `param_def.is_scalar`, `param_def.data`, `scalar_def.value`; see `docs/planning/SPRINT_3/PLAN_REVISED.md:689-770`). Multi-index parameters are also rendered as raw Python tuples, which is not valid GAMS syntax.
- Variable emission is planned as a generic `Variables`/`Positive Variables` split (e.g., `docs/planning/SPRINT_3/PLAN_REVISED.md:787-804`) without consulting `VariableDef.kind`, so positive/binary/integer variables from the original model will silently change type in the emitted MCP.

## Recommendations
- Update `partition_constraints()` so that once an inequality is classified as a duplicate bound it is excluded from the inequality list (and therefore from complementarity generation), while still surfacing the warning.
- Extend the bounds pass to iterate over `lo_map`, `up_map`, and `fx_map`, applying the same finite/∞ filtering for each indexed instance so every finite bound produces or skips π rows correctly.
- Rework the original-symbol emission tasks to align with the actual dataclasses: use `SetDef.members`, treat scalars as parameters with an empty domain (`values[()]`), and format tuple keys as GAMS index strings (e.g., `i1.j2`). Add time for tests covering multi-dimensional data and alias universes.
- Add a task that maps `VariableDef.kind` to the appropriate GAMS declaration blocks (Positive, Negative, Binary, Integer, Free) or emits explicit `.lo/.up` statements so the primal variable semantics match the source model.
