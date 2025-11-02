"""Research test: Verify auxiliary variables are included in IndexMapping.

This test verifies Unknown 6.4: Do auxiliary variables affect IndexMapping?

The test demonstrates that the current architecture is CORRECT BY DESIGN:
1. reformulate_model() adds auxiliary variables to model.variables (Step 2.5)
2. build_index_mapping() is called during derivative computation (Step 3)
3. Therefore, IndexMapping automatically includes all auxiliary variables

This test creates a model with min() reformulation and verifies that:
- Auxiliary variables (aux_min_*, lambda_min_*) are in model.variables
- build_index_mapping() includes them in the mapping
- Gradient and Jacobian have correct dimensions (including auxiliary vars)
- Column indices align between gradient and Jacobian

FINDING: No code changes needed - architecture is correct by design.
The integration point (Step 2.5) ensures auxiliary vars are always included.
"""

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.ad.index_mapping import build_index_mapping
from src.ir.ast import Binary, Call, Const, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.normalize import normalize_model
from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef, VarKind
from src.kkt.reformulation import reformulate_model


def test_auxiliary_variables_in_index_mapping():
    """Test that auxiliary variables from min/max reformulation are included in IndexMapping."""

    # Create model: minimize x^2 + y^2 subject to z = min(x, y), z >= 1
    model = ModelIR()

    # Variables
    model.add_var(VariableDef("x", (), VarKind.CONTINUOUS, lo=0.0))
    model.add_var(VariableDef("y", (), VarKind.CONTINUOUS, lo=0.0))
    model.add_var(VariableDef("z", (), VarKind.CONTINUOUS))
    model.add_var(VariableDef("obj", (), VarKind.CONTINUOUS))

    # Objective equation: obj = x^2 + y^2
    obj_eq = EquationDef(
        name="objdef",
        domain=(),
        relation=Rel.EQ,
        lhs_rhs=(
            VarRef("obj", ()),
            Binary(
                "+",
                Binary("^", VarRef("x", ()), Const(2.0)),
                Binary("^", VarRef("y", ()), Const(2.0)),
            ),
        ),
    )
    model.add_equation(obj_eq)

    # Constraint: z = min(x, y)
    min_eq = EquationDef(
        name="minconstraint",
        domain=(),
        relation=Rel.EQ,
        lhs_rhs=(VarRef("z", ()), Call("min", (VarRef("x", ()), VarRef("y", ())))),
    )
    model.add_equation(min_eq)

    # Constraint: z >= 1
    z_bound = EquationDef(
        name="z_lower", domain=(), relation=Rel.GE, lhs_rhs=(VarRef("z", ()), Const(1.0))
    )
    model.add_equation(z_bound)

    # Objective: minimize obj
    model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

    # === STEP 1: Before reformulation ===
    vars_before = len(model.variables)
    assert vars_before == 4  # x, y, z, obj

    # === STEP 2: Normalize ===
    normalize_model(model)

    # === STEP 2.5: Reformulate (adds auxiliary variables) ===
    reformulate_model(model)

    # === VERIFICATION 1: Auxiliary variables added to model ===
    vars_after = len(model.variables)
    assert vars_after > vars_before, "Reformulation should add auxiliary variables"

    # Check specific auxiliary variables exist
    assert "aux_min_minconstraint_0" in model.variables, "Auxiliary variable should exist"
    assert "lambda_min_minconstraint_0_arg0" in model.variables, "Lambda multiplier should exist"
    assert "lambda_min_minconstraint_0_arg1" in model.variables, "Lambda multiplier should exist"

    print("\n" + "=" * 70)
    print("UNKNOWN 6.4 VERIFICATION: Auxiliary Variables in IndexMapping")
    print("=" * 70)
    print(f"✓ Variables before reformulation: {vars_before}")
    print(f"✓ Variables after reformulation: {vars_after}")
    print(f"✓ Auxiliary variables added: {vars_after - vars_before}")

    # === VERIFICATION 2: build_index_mapping includes auxiliary vars ===
    index_mapping = build_index_mapping(model)

    # IndexMapping should have entries for ALL variables (including auxiliary)
    assert (
        index_mapping.num_vars == vars_after
    ), f"IndexMapping should have {vars_after} vars, got {index_mapping.num_vars}"

    # Check that auxiliary variables are mapped
    aux_col = index_mapping.get_col_id("aux_min_minconstraint_0", ())
    assert aux_col is not None, "Auxiliary variable should be in IndexMapping"

    lambda_0_col = index_mapping.get_col_id("lambda_min_minconstraint_0_arg0", ())
    assert lambda_0_col is not None, "Lambda multiplier should be in IndexMapping"

    lambda_1_col = index_mapping.get_col_id("lambda_min_minconstraint_0_arg1", ())
    assert lambda_1_col is not None, "Lambda multiplier should be in IndexMapping"

    print(f"✓ IndexMapping has {index_mapping.num_vars} columns (includes auxiliary vars)")
    print(f"✓ aux_min_minconstraint_0 → column {aux_col}")
    print(f"✓ lambda_min_minconstraint_0_arg0 → column {lambda_0_col}")
    print(f"✓ lambda_min_minconstraint_0_arg1 → column {lambda_1_col}")

    # === VERIFICATION 3: Gradient has correct dimensions ===
    gradient = compute_objective_gradient(model)

    assert (
        gradient.num_cols == vars_after
    ), f"Gradient should have {vars_after} columns, got {gradient.num_cols}"

    print(f"✓ Gradient has {gradient.num_cols} columns (includes auxiliary vars)")

    # === VERIFICATION 4: Jacobian has correct dimensions ===
    J_eq, J_ineq = compute_constraint_jacobian(model)

    assert (
        J_eq.num_cols == vars_after
    ), f"Equality Jacobian should have {vars_after} columns, got {J_eq.num_cols}"
    assert (
        J_ineq.num_cols == vars_after
    ), f"Inequality Jacobian should have {vars_after} columns, got {J_ineq.num_cols}"

    print(f"✓ Equality Jacobian has {J_eq.num_cols} columns (includes auxiliary vars)")
    print(f"✓ Inequality Jacobian has {J_ineq.num_cols} columns (includes auxiliary vars)")

    # === VERIFICATION 5: Column alignment between gradient and Jacobian ===
    # Both should use the same IndexMapping (created fresh from same model state)
    assert (
        gradient.index_mapping.num_vars == J_eq.index_mapping.num_vars
    ), "Gradient and Jacobian should have same number of columns"

    # Check that specific variables map to same columns
    grad_x_col = gradient.index_mapping.get_col_id("x", ())
    jac_x_col = J_eq.index_mapping.get_col_id("x", ())
    assert (
        grad_x_col == jac_x_col
    ), "Variable 'x' should map to same column in gradient and Jacobian"

    grad_aux_col = gradient.index_mapping.get_col_id("aux_min_minconstraint_0", ())
    jac_aux_col = J_eq.index_mapping.get_col_id("aux_min_minconstraint_0", ())
    assert (
        grad_aux_col == jac_aux_col
    ), "Auxiliary variable should map to same column in gradient and Jacobian"

    print("✓ Gradient and Jacobian column indices aligned")
    print(f"  - 'x' maps to column {grad_x_col} in both")
    print(f"  - 'aux_min_minconstraint_0' maps to column {grad_aux_col} in both")

    # === VERIFICATION 6: All variables accounted for ===
    # List all variables in the mapping
    all_mapped_vars = set()
    for col_id in range(index_mapping.num_vars):
        var_name, indices = index_mapping.get_var_instance(col_id)
        all_mapped_vars.add(var_name)

    all_model_vars = set(model.variables.keys())
    assert (
        all_mapped_vars == all_model_vars
    ), f"All model variables should be mapped. Missing: {all_model_vars - all_mapped_vars}"

    print(f"✓ All {len(all_model_vars)} variables mapped (no missing variables)")

    print("\n" + "=" * 70)
    print("FINDING: Architecture is CORRECT BY DESIGN")
    print("=" * 70)
    print()
    print("IndexMapping is created DURING derivative computation (Step 3),")
    print("AFTER reformulation has already added auxiliary variables (Step 2.5).")
    print()
    print("Pipeline order:")
    print("  1. Parse")
    print("  2. Normalize")
    print("  2.5. Reformulate ← Adds auxiliary vars to model.variables")
    print("  3. Derivatives ← build_index_mapping() called here")
    print("  4. KKT Assembly")
    print("  5. Emit")
    print()
    print("Because build_index_mapping() enumerates model.variables at call time,")
    print("it AUTOMATICALLY includes all auxiliary variables added by reformulation.")
    print()
    print("NO CODE CHANGES NEEDED:")
    print("  ✓ Pipeline order is correct in src/cli.py")
    print("  ✓ build_index_mapping() already enumerates all variables")
    print("  ✓ Gradient and Jacobian create fresh mappings from same model state")
    print("  ✓ Column indices automatically aligned")
    print("=" * 70 + "\n")

    return True


if __name__ == "__main__":
    test_auxiliary_variables_in_index_mapping()
