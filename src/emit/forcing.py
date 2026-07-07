"""Solution-forcing harness scaffold (Sprint 30 Priority 8).

Wraps the terminal ``Solve <model> using MCP;`` in one of three forcing drivers,
plus a MODEL-STATUS reporter, so non-convergent non-convex MCPs (rocket #1462) can
be driven with a lever without editing the emitted core. This is the **stable
interface** the Sprint-31 PATH-consultation work inherits: a lever-injection hook
around the MCP solve + a status reporter, with the strategy chosen by ``--force``.

The scaffold provides the *plumbing* (the loop / optfile structure that runs the
lever) and a documented model-specific hook (the relaxation / ``.l`` perturbation);
it is validated to compile + run on rocket, but — per
``docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md`` §2 — is not expected
to make rocket converge on its own.

Strategies:
- ``homotopy``:   continuation loop over a relaxation parameter ``mu: 1 -> 0``,
  warm-restarting from each prior point.
- ``multistart``: re-solve from N perturbed ``.l`` starts, keep the first MS 1/2.
- ``optfile``:    a single solve with an emitted PATH ``path.opt``
  (``proximal_perturbation`` + ``merit_function normal``).
"""

from __future__ import annotations

FORCING_STRATEGIES = ("homotopy", "multistart", "optfile")


def _reporter(model_name: str, add_comments: bool) -> list[str]:
    """The MODEL-STATUS reporter — common to every strategy."""
    lines: list[str] = []
    if add_comments:
        lines.append("* Forcing-scaffold MODEL-STATUS reporter")
    lines.append("Scalar nlp2mcp_force_modelstat, nlp2mcp_force_solvestat;")
    lines.append(f"nlp2mcp_force_modelstat = {model_name}.modelStat;")
    lines.append(f"nlp2mcp_force_solvestat = {model_name}.solveStat;")
    lines.append("Display nlp2mcp_force_modelstat, nlp2mcp_force_solvestat;")
    return lines


def emit_forcing_scaffold(
    strategy: str, model_name: str = "mcp_model", add_comments: bool = True
) -> str:
    """Emit the forcing driver for ``strategy`` (replaces the plain Solve).

    Args:
        strategy: one of :data:`FORCING_STRATEGIES`.
        model_name: the GAMS MCP model name.
        add_comments: whether to emit explanatory comments.

    Returns:
        The GAMS driver (loop / optfile + Solve) followed by the status reporter.

    Raises:
        ValueError: if ``strategy`` is not a known forcing strategy.
    """
    if strategy not in FORCING_STRATEGIES:
        raise ValueError(
            f"unknown forcing strategy '{strategy}'; expected one of {FORCING_STRATEGIES}"
        )

    lines: list[str] = []

    if strategy == "optfile":
        # The tunable PATH levers (survey §1): a proximal_perturbation +
        # merit_function schedule delivered via an optfile, then one solve.
        if add_comments:
            lines.append(
                "* --force optfile: emit a PATH option file (trust-region regularization"
                " + non-monotone merit) and solve once"
            )
        lines.append("$onecho > path.opt")
        lines.append("proximal_perturbation 1e-2")
        lines.append("merit_function normal")
        lines.append("$offecho")
        lines.append(f"{model_name}.optfile = 1;")
        lines.append(f"Solve {model_name} using MCP;")

    elif strategy == "multistart":
        # Re-solve from N perturbed start points; stop at the first MS 1/2.
        if add_comments:
            lines.append(
                "* --force multistart: re-solve from perturbed .l starts, keep the first MS 1/2"
            )
        lines.append("Set nlp2mcp_force_pt / p1*p4 /;")
        lines.append(
            "Parameter nlp2mcp_force_scale(nlp2mcp_force_pt)"
            " / p1 1.0, p2 1.1, p3 0.9, p4 1.25 /;"
        )
        lines.append("Scalar nlp2mcp_force_done / 0 /;")
        lines.append("loop(nlp2mcp_force_pt$(nlp2mcp_force_done = 0),")
        if add_comments:
            lines.append(
                "*   HOOK (model-specific): perturb the primal .l start by"
                " nlp2mcp_force_scale(nlp2mcp_force_pt) here;"
            )
            lines.append("*   the default plumbing re-solves warm from the prior point.")
        lines.append(f"    Solve {model_name} using MCP;")
        lines.append(f"    nlp2mcp_force_done$({model_name}.modelStat <= 2) = 1;")
        lines.append(");")

    else:  # homotopy
        # Continuation over mu: 1 (relaxed) -> 0 (original), warm from each prior point.
        if add_comments:
            lines.append(
                "* --force homotopy: continuation over mu (relaxed -> original),"
                " warm-restart from each prior point"
            )
        lines.append("Set nlp2mcp_force_step / m1*m5 /;")
        lines.append(
            "Parameter nlp2mcp_force_mu(nlp2mcp_force_step)"
            " / m1 1.0, m2 0.5, m3 0.25, m4 0.1, m5 0.0 /;"
        )
        lines.append("loop(nlp2mcp_force_step,")
        if add_comments:
            lines.append(
                "*   HOOK (model-specific): scale the model relaxation by"
                " nlp2mcp_force_mu(nlp2mcp_force_step) here;"
            )
        lines.append(f"    Solve {model_name} using MCP;")
        lines.append(");")

    lines.append("")
    lines.extend(_reporter(model_name, add_comments))
    return "\n".join(lines)
