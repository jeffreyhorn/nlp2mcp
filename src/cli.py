"""Command-line interface for nlp2mcp.

Converts GAMS NLP models to MCP (Mixed Complementarity Problem) format
by deriving KKT (Karush-Kuhn-Tucker) conditions.
"""

import logging
import sys
from pathlib import Path

import click

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.config import Config
from src.diagnostics import compute_model_statistics, export_jacobian_matrix_market
from src.diagnostics.convexity.patterns import (
    BilinearTermPattern,
    NonlinearEqualityPattern,
    OddPowerPattern,
    QuotientPattern,
    TrigonometricPattern,
)
from src.emit.emit_gams import emit_gams_mcp
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.kkt.assemble import assemble_kkt_system
from src.kkt.reformulation import reformulate_model
from src.kkt.scaling import byvar_scaling, curtis_reid_scaling
from src.logging_config import setup_logging
from src.utils.error_codes import get_error_info
from src.validation.model import validate_model_structure
from src.validation.numerical import validate_jacobian_entries, validate_parameter_values


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
@click.option(
    "--smooth-abs",
    is_flag=True,
    default=False,
    help="Enable smooth approximation for abs() using sqrt(x^2 + epsilon) (default: reject abs())",
)
@click.option(
    "--smooth-abs-epsilon",
    type=float,
    default=1e-6,
    help="Epsilon parameter for abs() smoothing approximation (default: 1e-6)",
)
@click.option(
    "--scale",
    type=click.Choice(["none", "auto", "byvar"], case_sensitive=False),
    default="none",
    help="Apply scaling to Jacobian: none (default), auto (Curtis-Reid), byvar (per-variable)",
)
@click.option(
    "--stats",
    is_flag=True,
    default=False,
    help="Print model statistics (equations, variables, nonzeros breakdown)",
)
@click.option(
    "--dump-jacobian",
    type=click.Path(),
    help="Export Jacobian to Matrix Market format (.mtx file)",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    default=False,
    help="Suppress non-error output (overrides --verbose)",
)
@click.option(
    "--skip-convexity-check",
    is_flag=True,
    default=False,
    help="Skip convexity warnings (heuristic pattern detection for nonconvex models)",
)
def main(
    input_file,
    output,
    verbose,
    no_comments,
    model_name,
    show_excluded,
    smooth_abs,
    smooth_abs_epsilon,
    scale,
    stats,
    dump_jacobian,
    quiet,
    skip_convexity_check,
):
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

    Warning: This function modifies the global Python recursion limit for the entire
    interpreter process. If nlp2mcp is used as a library in a multi-threaded application,
    this could affect other threads. The limit is restored on exit, but concurrent calls
    may experience unexpected behavior.
    """
    # Increase recursion limit for large models with deeply nested expressions
    # (e.g., objectives with 1000+ terms create deep left-associative parse trees)
    # WARNING: sys.setrecursionlimit() affects the entire Python process globally,
    # not just this function. This could impact multi-threaded applications.
    original_limit = sys.getrecursionlimit()
    required_limit = 10000
    if required_limit > original_limit:
        sys.setrecursionlimit(required_limit)

    try:
        # Determine verbosity level (quiet overrides verbose)
        verbosity_level = 0 if quiet else verbose

        # Set up logging
        setup_logging(verbosity=verbosity_level)
        # Step 1: Parse model
        if verbose:
            click.echo(f"Parsing model: {input_file}")

        model = parse_model_file(input_file)

        if verbose >= 2:
            click.echo(f"  Sets: {len(model.sets)}")
            click.echo(f"  Parameters: {len(model.params)}")
            click.echo(f"  Variables: {len(model.variables)}")
            click.echo(f"  Equations: {len(model.equations)}")

        # Step 1.5: Validate model structure (Sprint 5 Day 4 - Task 4.2)
        if verbose:
            click.echo("Validating model structure...")

        validate_model_structure(model)

        # Step 1.6: Validate parameters for NaN/Inf (Sprint 5 Day 4 - Task 4.1)
        if verbose:
            click.echo("Validating parameters...")

        validate_parameter_values(model)

        # Step 1.7: Check for convexity warnings (Sprint 6 Day 4)
        if not skip_convexity_check:
            if verbose:
                click.echo("Checking for potential nonconvex patterns...")

            # Initialize all pattern matchers
            patterns = [
                NonlinearEqualityPattern(),
                TrigonometricPattern(),
                BilinearTermPattern(),
                QuotientPattern(),
                OddPowerPattern(),
            ]

            # Collect all warnings
            all_warnings = []
            for pattern in patterns:
                warnings = pattern.detect(model)
                all_warnings.extend(warnings)

            # Display warnings
            if all_warnings:
                click.echo()
                click.secho("⚠️  Convexity Warnings:", fg="yellow", bold=True)
                click.echo()
                for warning in all_warnings:
                    # Format with error code and documentation link
                    error_info = get_error_info(warning.error_code) if warning.error_code else None

                    click.secho(f"  {warning.error_code or 'W???'}: {warning.message}", fg="yellow")
                    click.echo(f"     Equation: {warning.equation}")
                    if warning.details:
                        click.echo(f"     Details: {warning.details}")
                    if error_info:
                        click.echo(f"     Docs: {error_info.doc_url()}")
                    click.echo()

                click.echo(f"  Found {len(all_warnings)} potential nonconvex pattern(s).")
                click.echo("  These are heuristic warnings and may include false positives.")
                click.echo("  Use --skip-convexity-check to suppress these warnings.")
                click.echo()

        # Step 2: Normalize model
        if verbose:
            click.echo("Normalizing model...")

        normalized_eqs, _ = normalize_model(model)

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

        # Re-normalize model after reformulation to capture new equations
        # and update equations that had min/max replaced with aux vars
        if vars_added > 0 or eqs_added > 0:
            normalized_eqs, _ = normalize_model(model)

        # Step 3: Compute derivatives
        if verbose:
            click.echo("Computing derivatives...")

        # Create configuration for derivative computation
        config = Config(
            smooth_abs=smooth_abs,
            smooth_abs_epsilon=smooth_abs_epsilon,
            scale=scale.lower(),
        )

        gradient = compute_objective_gradient(model, config)
        J_eq, J_ineq = compute_constraint_jacobian(model, normalized_eqs, config)

        if verbose >= 2:
            click.echo(f"  Gradient columns: {gradient.num_cols}")
            click.echo(f"  Equality Jacobian: {J_eq.num_rows} × {J_eq.num_cols}")
            click.echo(f"  Inequality Jacobian: {J_ineq.num_rows} × {J_ineq.num_cols}")

        # Step 3.5: Validate Jacobians for NaN/Inf (Sprint 5 Day 4)
        if verbose:
            click.echo("Validating derivatives...")

        validate_jacobian_entries(gradient, "objective gradient")
        validate_jacobian_entries(J_eq, "equality constraint Jacobian")
        validate_jacobian_entries(J_ineq, "inequality constraint Jacobian")

        # Step 4: Compute scaling factors (if requested)
        row_scales = None
        col_scales = None

        if config.scale != "none":
            if verbose:
                click.echo(f"Computing {config.scale} scaling...")

            # Scale based on the inequality Jacobian (larger system with bounds)
            # Note: Equality Jacobian could also be scaled separately if needed
            if config.scale == "auto":
                # Curtis-Reid scaling uses both row and column scaling
                R_ineq, C_ineq = curtis_reid_scaling(J_ineq)
                row_scales, col_scales = R_ineq.tolist(), C_ineq.tolist()

                if verbose >= 2:
                    click.echo(f"  Computed row scaling for {len(row_scales)} equations")
                    click.echo(f"  Computed column scaling for {len(col_scales)} variables")

            elif config.scale == "byvar":
                # Byvar scaling only scales columns (variables)
                C_ineq = byvar_scaling(J_ineq)
                row_scales = None
                col_scales = C_ineq.tolist()

                if verbose >= 2:
                    click.echo(f"  Computed column scaling for {len(col_scales)} variables")

        # Step 5: Assemble KKT system
        if verbose:
            click.echo("Assembling KKT system...")

        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        # Store scaling factors in KKT system
        if config.scale != "none":
            kkt.scaling_row_factors = row_scales
            kkt.scaling_col_factors = col_scales
            kkt.scaling_mode = config.scale

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

        # Step 5.5: Diagnostics (if requested)
        if stats:
            logger = logging.getLogger("nlp2mcp")
            model_stats = compute_model_statistics(kkt)
            logger.info("\n" + model_stats.format_report())

        if dump_jacobian:
            if verbose:
                click.echo(f"Exporting Jacobian to: {dump_jacobian}")

            jacobian_path = Path(dump_jacobian)
            export_jacobian_matrix_market(kkt, jacobian_path)

            if verbose:
                click.echo(f"✓ Jacobian exported to {dump_jacobian}")

        # Step 6: Emit GAMS MCP code
        if verbose:
            click.echo("Generating GAMS MCP code...")

        add_comments = not no_comments
        gams_code = emit_gams_mcp(
            kkt, model_name=model_name, add_comments=add_comments, config=config
        )

        # Step 7: Write output
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
    finally:
        # Restore original recursion limit
        sys.setrecursionlimit(original_limit)


if __name__ == "__main__":
    main()
