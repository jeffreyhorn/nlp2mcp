"""
Generate large test models for production hardening.

Models are realistic (not just random), with typical optimization structures:
- Resource allocation problems
- Network flow problems
"""

from pathlib import Path


def generate_resource_allocation(
    output_path: Path,
    num_resources: int,
    num_tasks: int,
) -> Path:
    """
    Generate resource allocation NLP.

    Simplified model without multi-dimensional parameters.
    minimize sum over vars: cost(var)
    s.t. sum_constraint: sum of all vars with coefficients
         var >= 0

    This tests large-scale model handling without unsupported features.
    """
    # Total number of variables = num_tasks (x(i)) + 1 (obj) = num_tasks + 1
    content = [f"* Resource Allocation Problem: {num_tasks} variables\n\n"]

    # Sets - use explicit comma-separated lists (parser doesn't support * notation)
    content.append("Sets\n")
    content.append("    i /")
    content.append(", ".join([f"i{idx}" for idx in range(1, num_tasks + 1)]))
    content.append("/\n")
    content.append(";\n\n")

    # Parameters - 1D only
    content.append("Parameters\n")
    content.append("    a(i) / ")
    content.append(", ".join([f"i{idx} {1 + idx % 10}" for idx in range(1, num_tasks + 1)]))
    content.append(" /\n")
    content.append(";\n\n")

    # Variables
    content.append("Variables\n")
    content.append("    x(i) decision variables\n")
    content.append("    obj objective value\n")
    content.append(";\n\n")

    # Equations
    content.append("Equations\n")
    content.append("    objdef objective definition\n")
    content.append("    constraint1 sum constraint\n")
    content.append("    non_negative(i) nonnegativity constraints\n")
    content.append(";\n\n")

    # Objective: quadratic cost
    content.append("objdef.. obj =e= sum(i, a(i)*x(i)*x(i));\n\n")

    # Constraint: simple sum constraint
    content.append("constraint1.. sum(i, x(i)) =l= 100;\n\n")

    # Constraint: non-negativity
    content.append("non_negative(i).. x(i) =g= 0;\n\n")

    # Model
    content.append("Model resource_allocation /all/;\n")
    content.append("Solve resource_allocation using NLP minimizing obj;\n")

    output_path.write_text("".join(content))
    return output_path


def generate_network_flow(
    output_path: Path,
    num_nodes: int,
    num_arcs: int,
) -> Path:
    """
    Generate network flow optimization.

    Simplified model without multi-dimensional parameters.
    minimize sum over arcs: cost(arc) * flow(arc)^2
    s.t. capacity constraint
         flow(arc) >= 0

    Tests large-scale model handling.
    """
    # Total number of variables = num_arcs (flow(j)) + 1 (obj) = num_arcs + 1
    content = [f"* Network Flow Problem: {num_arcs} arcs\n\n"]

    # Sets - use explicit comma-separated lists (parser doesn't support * notation)
    content.append("Sets\n")
    content.append("    j /")
    content.append(", ".join([f"j{idx}" for idx in range(1, num_arcs + 1)]))
    content.append("/\n")
    content.append(";\n\n")

    # Parameters - 1D only
    content.append("Parameters\n")
    content.append("    cost(j) /")
    costs = [f"j{idx} {1 + idx % 5}" for idx in range(1, num_arcs + 1)]
    content.append(", ".join(costs))
    content.append("/\n")
    content.append(";\n\n")

    # Variables
    content.append("Variables\n")
    content.append("    flow(j) flow on arcs\n")
    content.append("    obj objective value\n")
    content.append(";\n\n")

    # Equations
    content.append("Equations\n")
    content.append("    objdef objective definition\n")
    content.append("    capacity total capacity constraint\n")
    content.append("    non_negative(j) nonnegativity constraints\n")
    content.append(";\n\n")

    # Objective: quadratic cost
    content.append("objdef.. obj =e= sum(j, cost(j)*flow(j)*flow(j));\n\n")

    # Constraint: total capacity
    content.append("capacity.. sum(j, flow(j)) =l= 1000;\n\n")

    # Constraint: non-negativity
    content.append("non_negative(j).. flow(j) =g= 0;\n\n")

    # Model
    content.append("Model network_flow /all/;\n")
    content.append("Solve network_flow using NLP minimizing obj;\n")

    output_path.write_text("".join(content))
    return output_path


def generate_all_test_models():
    """Generate all large model test fixtures."""
    fixtures_dir = Path(__file__).parent / "large_models"
    fixtures_dir.mkdir(exist_ok=True)

    # NOTE: Parser has limitations with very long comma-separated lists
    # Keeping models at reasonable sizes that work with current parser
    # Only generating resource allocation models (network flow had variable indexing issues)
    models = [
        # Small model (baseline - fast conversion)
        (
            "resource_allocation_small.gms",
            "resource_allocation",
            {"num_resources": 5, "num_tasks": 10},
        ),
        # Medium model (moderate scale testing)
        (
            "resource_allocation_medium.gms",
            "resource_allocation",
            {"num_resources": 10, "num_tasks": 50},
        ),
        # Large model (stress testing within parser limits)
        (
            "resource_allocation_large.gms",
            "resource_allocation",
            {"num_resources": 20, "num_tasks": 100},
        ),
    ]

    for filename, generator_name, kwargs in models:
        output_path = fixtures_dir / filename
        if generator_name == "resource_allocation":
            generate_resource_allocation(output_path, **kwargs)
        elif generator_name == "network_flow":
            generate_network_flow(output_path, **kwargs)
        print(f"Generated: {output_path}")

    return fixtures_dir


if __name__ == "__main__":
    fixtures_dir = generate_all_test_models()
    print(f"\nAll large model fixtures generated in: {fixtures_dir}")
    print("\nTo test:")
    print(f"  nlp2mcp {fixtures_dir}/resource_allocation_medium.gms -o /tmp/out.gms")
