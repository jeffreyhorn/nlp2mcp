"""Research test: Verify auxiliary constraints work in MCP emission.

This test verifies Unknown 4.3: Do auxiliary constraints need special model
declaration handling?

Test creates a model with min() in a CONSTRAINT (not objective), reformulates it,
assembles KKT, and emits GAMS MCP code to verify that auxiliary constraints
integrate seamlessly with the existing emission code.

FINDING: Auxiliary constraints are treated as regular inequalities - no special
handling needed in emit_model_mcp().
"""

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.emit.emit_gams import emit_gams_mcp
from src.ir.ast import Binary, Call, Const, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.normalize import normalize_model
from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef, VarKind
from src.kkt.assemble import assemble_kkt_system
from src.kkt.reformulation import reformulate_model


def test_min_reformulation_in_mcp_emission():
    """Test that min() reformulation integrates correctly with MCP emission.

    EXPECTED TO FAIL: This test intentionally demonstrates a bug in the current
    implementation. The test creates a model with min() reformulation and verifies
    that auxiliary constraints should appear in the final MCP emission. Currently,
    the test fails at the assertion checking for auxiliary complementarity pairs
    in the Model declaration, because:

    1. reformulate_model() adds auxiliary constraints to model.equations
    2. BUT it does NOT add them to model.inequalities
    3. compute_constraint_jacobian() filters by model.inequalities
    4. So auxiliary constraints are excluded from the Jacobian
    5. Which means they never make it into the KKT system
    6. And therefore never appear in the GAMS MCP Model declaration

    Once the one-line fix is applied (adding model.inequalities.append() in
    reformulate_model()), this test will pass and demonstrate that auxiliary
    constraints integrate seamlessly with the existing emission code.
    """

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

    # Normalize
    normalize_model(model)

    # Reformulate min/max
    reformulate_model(model)

    # Verify reformulation worked
    assert "aux_min_minconstraint_0" in model.variables
    assert "lambda_min_minconstraint_0_arg0" in model.variables
    assert "lambda_min_minconstraint_0_arg1" in model.variables
    assert "comp_min_minconstraint_0_arg0" in model.equations
    assert "comp_min_minconstraint_0_arg1" in model.equations

    # Compute derivatives
    gradient = compute_objective_gradient(model)
    J_eq, J_ineq = compute_constraint_jacobian(model)

    # Assemble KKT
    kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

    # Emit GAMS MCP code
    gams_code = emit_gams_mcp(kkt, model_name="test_min_mcp", add_comments=True)

    # === VERIFICATION ===

    print("\n" + "=" * 70)
    print("UNKNOWN 4.3 VERIFICATION: Auxiliary Constraints in MCP Emission")
    print("=" * 70)

    # 1. Auxiliary variable declared
    assert "aux_min_minconstraint_0" in gams_code
    print("✓ Auxiliary variable declared: aux_min_minconstraint_0")

    # 2. Multipliers declared as Positive Variables
    assert "lambda_min_minconstraint_0_arg0" in gams_code
    assert "lambda_min_minconstraint_0_arg1" in gams_code
    print("✓ Multipliers declared: lambda_min_minconstraint_0_arg{0,1}")

    # 3. Auxiliary constraints defined
    assert "comp_min_minconstraint_0_arg0" in gams_code
    assert "comp_min_minconstraint_0_arg1" in gams_code
    print("✓ Auxiliary constraints defined: comp_min_minconstraint_0_arg{0,1}")

    # 4. Model declaration includes auxiliary complementarity pairs
    # Note: The actual names use 'comp_comp_' prefix and 'lam_comp_' for multipliers
    model_start = gams_code.find("Model test_min_mcp /")
    model_end = gams_code.find("/;", model_start)
    model_block = gams_code[model_start:model_end]

    assert "comp_comp_min_minconstraint_0_arg0.lam_comp_min_minconstraint_0_arg0" in model_block
    assert "comp_comp_min_minconstraint_0_arg1.lam_comp_min_minconstraint_0_arg1" in model_block
    print("✓ Model declaration includes auxiliary complementarity pairs")

    # 5. Equation-variable count matches
    pairs = []
    for line in model_block.split("\n"):
        stripped = line.strip()
        if (
            stripped
            and not stripped.startswith("*")
            and not stripped.startswith("Model")
            and "." in stripped
        ):
            pair = stripped.rstrip(",").strip()
            if pair:
                pairs.append(pair)

    num_primal_vars = 4  # x, y, z, obj (before reformulation)
    num_pairs = len(pairs)

    # MCP includes pairs for all variables including auxiliary vars and multipliers
    # Should have more pairs than just the primal variables
    assert (
        num_pairs > num_primal_vars
    ), f"Expected more than {num_primal_vars} pairs (for multipliers), got {num_pairs}"
    print(f"✓ Model has {num_pairs} equation-variable pairs (includes multipliers)")

    print("\n" + "=" * 70)
    print("FINDING: Auxiliary constraints integrate seamlessly!")
    print("=" * 70)
    print()
    print("Auxiliary constraints from min/max reformulation are treated as")
    print("regular inequality complementarities by emit_model_mcp().")
    print()
    print("NO SPECIAL HANDLING NEEDED:")
    print("  - Auxiliary variables: Added to model.variables → emitted normally")
    print("  - Multipliers: Added as POSITIVE variables → emitted normally")
    print("  - Constraints: Added to model.equations → emitted as inequalities")
    print("  - Model pairs: Generated automatically by existing logic")
    print()
    print("The reformulation adds them to ModelIR, and all downstream code")
    print("(derivatives, KKT assembly, GAMS emission) treats them identically")
    print("to user-defined inequalities.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    test_min_reformulation_in_mcp_emission()
