"""Command-line interface for nlp2mcp.

Converts GAMS NLP models to MCP (Mixed Complementarity Problem) format
by deriving KKT (Karush-Kuhn-Tucker) conditions.
"""

import sys
from pathlib import Path

import click

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.emit.emit_gams import emit_gams_mcp
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.kkt.assemble import assemble_kkt_system
from src.kkt.reformulation import reformulate_model


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), help="Output file path")
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity (can be used multiple times: -v, -vv, -vvv)",
)
@click.option(
    "--no-comments",
    is_flag=True,
    help="Disable explanatory comments in generated code",
)
@click.option(
    "--model-name",
    default="mcp_model",
    help="Name for the GAMS model (default: mcp_model)",
)
@click.option(
    "--show-excluded/--no-show-excluded",
    default=True,
    help="Show duplicate bounds excluded from inequalities (default: show)",
)
def main(input_file, output, verbose, no_comments, model_name, show_excluded):
    """Convert GAMS NLP model to MCP format using KKT conditions.

    INPUT_FILE: Path to the GAMS NLP model file (.gms)

    The tool performs the following steps:
    1. Parse the GAMS model
    2. Normalize constraints to standard form
    3. Compute derivatives (gradient and Jacobian)
    4. Assemble KKT system (stationarity + complementarity)
    5. Emit GAMS MCP code

    Example:
        nlp2mcp examples/simple_nlp.gms -o output_mcp.gms
    """
    try:
        # Step 1: Parse model
        if verbose:
            click.echo(f"Parsing model: {input_file}")

        model = parse_model_file(input_file)

        if verbose >= 2:
            click.echo(f"  Sets: {len(model.sets)}")
            click.echo(f"  Parameters: {len(model.params)}")
            click.echo(f"  Variables: {len(model.variables)}")
            click.echo(f"  Equations: {len(model.equations)}")

        # Step 2: Normalize model
        if verbose:
            click.echo("Normalizing model...")

        normalize_model(model)

        if verbose >= 2:
            click.echo(f"  Equalities: {len(model.equalities)}")
            click.echo(f"  Inequalities: {len(model.inequalities)}")

        # Step 2.5: Reformulate min/max functions (Sprint 4 Day 4)
        if verbose:
            click.echo("Reformulating min/max functions...")

        vars_before = len(model.variables)
        eqs_before = len(model.equations)

        reformulate_model(model)

        vars_added = len(model.variables) - vars_before
        eqs_added = len(model.equations) - eqs_before

        if verbose >= 2 and (vars_added > 0 or eqs_added > 0):
            click.echo(f"  Added {vars_added} auxiliary variables")
            click.echo(f"  Added {eqs_added} complementarity constraints")

        # Step 3: Compute derivatives
        if verbose:
            click.echo("Computing derivatives...")

        gradient = compute_objective_gradient(model)
        J_eq, J_ineq = compute_constraint_jacobian(model)

        if verbose >= 2:
            click.echo(f"  Gradient columns: {gradient.num_cols}")
            click.echo(f"  Equality Jacobian: {J_eq.num_rows} × {J_eq.num_cols}")
            click.echo(f"  Inequality Jacobian: {J_ineq.num_rows} × {J_ineq.num_cols}")

        # Step 4: Assemble KKT system
        if verbose:
            click.echo("Assembling KKT system...")

        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        # Report excluded duplicate bounds
        if show_excluded and kkt.duplicate_bounds_excluded:
            click.echo(
                f"Excluded {len(kkt.duplicate_bounds_excluded)} duplicate bound(s):",
                err=True,
            )
            for eq_name in kkt.duplicate_bounds_excluded:
                click.echo(f"  - {eq_name}", err=True)

        # Verbose reporting
        if verbose:
            click.echo(f"  Stationarity equations: {len(kkt.stationarity)}")
            click.echo(f"  Inequality multipliers: {len(kkt.complementarity_ineq)}")
            click.echo(f"  Lower bound multipliers: {len(kkt.complementarity_bounds_lo)}")
            click.echo(f"  Upper bound multipliers: {len(kkt.complementarity_bounds_up)}")

            if kkt.skipped_infinite_bounds:
                click.echo(f"  Skipped {len(kkt.skipped_infinite_bounds)} infinite bound(s)")

                if verbose >= 2:
                    for var, indices, bound_type in kkt.skipped_infinite_bounds:
                        idx_str = f"({','.join(indices)})" if indices else ""
                        click.echo(f"    {var}{idx_str}.{bound_type} = ±INF")

        # Step 5: Emit GAMS MCP code
        if verbose:
            click.echo("Generating GAMS MCP code...")

        add_comments = not no_comments
        gams_code = emit_gams_mcp(kkt, model_name=model_name, add_comments=add_comments)

        # Step 6: Write output
        if output:
            output_path = Path(output)
            output_path.write_text(gams_code)
            click.echo(f"✓ Generated MCP: {output}")

            if verbose >= 2:
                click.echo(f"  Output size: {len(gams_code)} characters")
        else:
            # Print to stdout if no output file specified
            print(gams_code)

        if verbose:
            click.echo("✓ Conversion complete")

    except FileNotFoundError as e:
        click.echo(f"Error: File not found - {e}", err=True)
        sys.exit(1)

    except ValueError as e:
        click.echo(f"Error: Invalid model - {e}", err=True)
        sys.exit(1)

    except Exception as e:
        click.echo(f"Error: Unexpected error - {e}", err=True)
        if verbose >= 3:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
