"""Multi-solve driver gate for nlp2mcp's NLP→MCP translator.

nlp2mcp transforms a *single* NLP's KKT conditions into an MCP. GAMS
source files can also be driver scripts that run an iterative
algorithm — Dantzig–Wolfe decomposition, column generation, Benders'
decomposition, primal-dual alternation — by declaring multiple GAMS
``Model`` blocks and ``solve``-ing them in turn, with parameters
updated from prior-solve equation duals (``eq.m``).

Those driver scripts are *not* single optimizations. The catalog's
"reference objective" for such a file is the algorithm's converged
fixed point, which no one-shot KKT snapshot can reproduce. They are
categorically out of scope, analogous to MINLP (see
:mod:`src.validation.discreteness`).

This module provides a single-call gate,
``validate_single_optimization(model_ir)``, that flags a driver
script only when **three independent signals** all agree, so benign
multi-solve patterns (sensitivity analysis on a single model;
post-solve reporting that stores ``var.l`` into a display parameter)
are not mistakenly caught:

1. **Multiple ``Model`` declarations** — ``len(declared_models) ≥ 2``.
2. **Solves target multiple distinct models** — at least two distinct
   model names appear as the target of a ``solve`` statement anywhere
   in the file (top-level or nested in loop bodies).
3. **Equation-marginal feedback** — at least one ``eq.m`` access
   feeds back into a subsequent solve, captured via either of:
   * (a) inside a ``loop`` whose body also contains a ``solve`` statement
     (the canonical decomp / danwolfe shape); or
   * (b) Issue #1270 (Sprint 25 Day 12) — a top-level (non-loop)
     ``param[(idx)] = ... eq.m(...) ...`` whose receiving parameter
     is later referenced inside any declared model's constraint body
     (the saras / primal-dual cross-reference pattern: dual marginal
     read between solves of two different models). Variable-attribute
     reads (``var.l``) and parameters that never appear in a model
     body are filtered out so post-solve reporting / display patterns
     don't false-positive.

The equation-marginal restriction (only ``.m`` on declared equations)
rules out post-solve bookkeeping like ``util_lic(t) = util.l;``
(partssupply): ``util`` is a *variable* not an equation, and ``.l``
is not a dual. Single-model multi-solve patterns (ibm1) fail
condition 1 immediately.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from lark import Token, Tree

from ..utils.errors import UserError

if TYPE_CHECKING:
    from ..ir.model_ir import ModelIR


@dataclass
class MultiSolveReport:
    """Findings from a multi-solve-driver scan of a ModelIR."""

    declared_models: list[str]
    solve_targets: list[str]
    equation_marginals: list[tuple[str, str]] = field(default_factory=list)

    @property
    def is_driver(self) -> bool:
        """True when all three driver-pattern conditions hold."""
        return (
            len(self.declared_models) >= 2
            and len(self.solve_targets) >= 2
            and bool(self.equation_marginals)
        )


class MultiSolveDriverError(UserError):
    """Raised when validate_single_optimization() detects a driver script.

    nlp2mcp translates one NLP's KKT conditions into an MCP. Driver
    scripts (Dantzig–Wolfe, column generation, Benders', primal-dual
    iteration) run an algorithm by alternating solves of different
    models with dual feedback between them. Their converged objective
    is not the objective of any single KKT snapshot. The correct
    handling is to mark them as driver scripts in the corpus database
    and exclude them from pipeline runs; see PLAN_FIX_DECOMP.md.
    """

    def __init__(self, report: MultiSolveReport):
        self.report = report
        attr_desc = ""
        if report.equation_marginals:
            shown = ", ".join(f"{name}.{attr}" for name, attr in report.equation_marginals[:5])
            extra = (
                f" (+{len(report.equation_marginals) - 5} more)"
                if len(report.equation_marginals) > 5
                else ""
            )
            # PR #1353 review: scope-neutral wording — Approach A also
            # reaches top-level (between-solve) feedback, so "inside
            # solve loop" was misleading for the saras shape.
            attr_desc = f"; equation-marginal feedback to a subsequent solve: {shown}{extra}"
        message = (
            "Model is a multi-solve driver script and is out of scope for "
            "nlp2mcp (NLP→MCP via KKT). Declared models: "
            f"{report.declared_models}; distinct solve targets: "
            f"{report.solve_targets}{attr_desc}."
        )
        suggestion = (
            "nlp2mcp transforms a single NLP's KKT conditions into an MCP. "
            "Driver scripts (Dantzig–Wolfe, column generation, Benders', "
            "primal-dual alternation) combine multiple solves with dual "
            "feedback; their converged objective cannot be recovered from "
            "any single KKT snapshot. Mark this model as "
            "multi_solve_driver_out_of_scope in "
            "data/gamslib/gamslib_status.json and exclude it from the "
            "pipeline. To force translation anyway (for development/"
            "debugging only), pass --allow-multi-solve; the generated MCP "
            "will likely be unsolvable or meaningless."
        )
        super().__init__(message, suggestion)


def _collect_solve_targets(node: object, targets: set[str]) -> None:
    """Walk a Lark Tree collecting model names that appear as targets of
    any ``solve`` statement. The grammar puts the model name as the
    first child ID token of a ``solve`` node.
    """
    if not isinstance(node, Tree):
        return
    if str(node.data) == "solve":
        if node.children and isinstance(node.children[0], Token):
            targets.add(str(node.children[0]).lower())
    for child in node.children:
        _collect_solve_targets(child, targets)


def _tree_contains_solve(node: object) -> bool:
    """Return True if the subtree rooted at ``node`` contains any
    ``solve`` statement.
    """
    if not isinstance(node, Tree):
        return False
    if str(node.data) == "solve":
        return True
    return any(_tree_contains_solve(c) for c in node.children)


def _collect_equation_marginals(
    node: object,
    equation_names: frozenset[str],
    out: list[tuple[str, str]],
) -> None:
    """Walk a subtree collecting ``bound_scalar`` / ``bound_indexed``
    nodes whose symbol is in ``equation_names`` and whose attribute is
    ``.m``. These are equation duals being read into parameter state.
    """
    if not isinstance(node, Tree):
        return
    data = str(node.data)
    if data in ("bound_scalar", "bound_indexed"):
        if len(node.children) >= 2:
            sym = node.children[0]
            attr = node.children[1]
            sym_name = str(sym).lower() if isinstance(sym, Token) else ""
            attr_name = str(attr).lower() if isinstance(attr, Token) else ""
            if attr_name == "m" and sym_name in equation_names:
                out.append((sym_name, attr_name))
    for child in node.children:
        _collect_equation_marginals(child, equation_names, out)


def _collect_param_refs_in_expr(expr: object, out: set[str]) -> None:
    """Walk an IR ``Expr`` tree and collect lowercase names of every
    ``ParamRef`` node. Used by Issue #1270's cross-reference pass to
    find which top-level-marginal parameters are read inside a model's
    constraint body.
    """
    from ..ir.ast import Expr, ParamRef

    if not isinstance(expr, Expr):
        return
    if isinstance(expr, ParamRef):
        out.add(expr.name.lower())
    for child in expr.children():
        _collect_param_refs_in_expr(child, out)


def _params_referenced_in_any_constraint_body(model_ir: ModelIR) -> set[str]:
    """Return lowercase names of parameters that **feed** any declared
    equation's body — directly or transitively through other parameter
    assignments. Issue #1270 (Approach A): the cross-reference set used
    to filter top-level marginal-feedback candidates.

    Direct case: ``Equation foo.. ... + p(i) * x(i)`` — ``p`` is in
    the set.

    Transitive case (saras): ``clam(...) = eq.m(...)``, then
    ``cGam(...) = f(clam, ...)``, then ``Equation obj.. ... + cGam(...)``.
    Both ``cGam`` (direct) and ``clam`` (transitive via cGam) are in
    the set, so the saras-style ``clam = calibuc.m`` top-level marginal
    feeds the second-stage solve.

    Computed as: seed = {params directly referenced in any equation
    body}; then iterate the **dependency-walk direction** — for each
    seed parameter ``Q``, scan ``Q``'s assignment expressions and add
    every parameter ``P`` that ``Q`` reads. ``P`` reaches the equation
    body via ``Q``, so ``P`` is also a feeder. Saturate. Self-
    referential expressions (``deltaq(sc) = deltaq(sc) / (1 +
    deltaq(sc))``) terminate naturally — adding ``deltaq`` to itself
    is a no-op.
    """
    # Step 1: direct references in equation bodies.
    refs: set[str] = set()
    for eq in (model_ir.equations or {}).values():
        lhs, rhs = eq.lhs_rhs if eq.lhs_rhs else (None, None)
        _collect_param_refs_in_expr(lhs, refs)
        _collect_param_refs_in_expr(rhs, refs)

    # Step 2: transitive closure through parameter expressions, walked in
    # the data-flow direction. ``refs`` starts with parameters consumed by
    # an equation body. For each ``Q`` in ``refs`` whose computed
    # expression reads ``P``, ``P`` also feeds the equation body via
    # ``Q`` and is added. Repeat until no new additions. Self-referential
    # expressions (``deltaq(sc) = deltaq(sc)/(1+deltaq(sc))``) terminate
    # because adding the param to itself doesn't add anything new.
    if not refs:
        return refs
    params = model_ir.params
    while True:
        added = False
        for qname in tuple(refs):
            qdef = params.get(qname) if params else None
            if qdef is None or not qdef.expressions:
                continue
            for _, ex in qdef.expressions:
                expr_refs: set[str] = set()
                _collect_param_refs_in_expr(ex, expr_refs)
                new_refs = expr_refs - refs
                if new_refs:
                    refs |= new_refs
                    added = True
        if not added:
            break
    return refs


def scan_multi_solve_driver(model_ir: ModelIR) -> MultiSolveReport:
    """Scan a ModelIR for multi-solve-driver signals.

    Pure function: does not raise, does not mutate. Returns a
    structured report so callers can decide how to react (the CLI
    raises; the batch pipeline records and skips).
    """
    from ..ir.symbols import LoopStatement

    declared = sorted({m.lower() for m in (model_ir.declared_models or [])})

    # Walk every ``solve`` statement in the IR — top-level and nested
    # in loop bodies — since ``_solve_objectives`` is a dict keyed by
    # model name and can miss multi-solve patterns that targeted the
    # same model repeatedly (and, empirically, some nested-in-loop
    # solves are not captured in ``_solve_objectives`` at all).
    solve_targets: set[str] = set()
    solve_targets.update((model_ir._solve_objectives or {}).keys())
    for loop_stmt in model_ir.loop_statements or []:
        if not isinstance(loop_stmt, LoopStatement):
            continue
        for stmt in loop_stmt.body_stmts or []:
            _collect_solve_targets(stmt, solve_targets)

    equation_names = frozenset(name.lower() for name in (model_ir.equations or {}))

    # Only count equation-marginal accesses whose enclosing loop body
    # also contains a ``solve`` — a one-off ``eq.m`` after a single
    # solve (post-solve reporting) does not make the script a driver.
    equation_marginals: list[tuple[str, str]] = []
    for loop_stmt in model_ir.loop_statements or []:
        if not isinstance(loop_stmt, LoopStatement):
            continue
        if not any(_tree_contains_solve(stmt) for stmt in loop_stmt.body_stmts or []):
            continue
        for stmt in loop_stmt.body_stmts or []:
            _collect_equation_marginals(stmt, equation_names, equation_marginals)

    # Issue #1270 (Approach A): also flag top-level (non-loop) ``param =
    # ...eq.m...`` assignments whose receiving parameter is later read
    # inside any declared model's constraint body — the saras / primal-
    # dual cross-reference shape. Without this branch, the gate misses
    # primal/dual drivers that don't wrap their feedback in a loop.
    #
    # Filtering rules (mirror the design doc §1.4):
    #  - ``sym_name`` must be a declared equation (``equation_names``);
    #    variable marginals like ``var.m`` aren't dual-feedback.
    #  - ``param_name`` must appear in at least one equation body; pure
    #    post-solve reporting parameters (display only) are excluded.
    if model_ir.top_level_marginal_reads:
        cross_ref_params = _params_referenced_in_any_constraint_body(model_ir)
        for param_name, sym_name, attr in model_ir.top_level_marginal_reads:
            if attr != "m":
                continue
            if sym_name not in equation_names:
                continue
            if param_name not in cross_ref_params:
                continue
            equation_marginals.append((sym_name, attr))

    # Deduplicate equation-marginal references while preserving first-seen
    # order. A single `eq.m` read inside a loop body is emitted once per
    # AST traversal but can still repeat across sibling statements; we only
    # care about *which* equation duals feed the iteration, not how often.
    # Keeping the list unique yields stable user-facing messages
    # (e.g., "tbal.m" rather than "tbal.m, tbal.m") and stable
    # `pipeline_status.details` rows in the status DB.
    deduped_marginals = list(dict.fromkeys(equation_marginals))

    return MultiSolveReport(
        declared_models=declared,
        solve_targets=sorted(solve_targets),
        equation_marginals=deduped_marginals,
    )


def validate_single_optimization(model_ir: ModelIR) -> None:
    """Refuse translation if the model is a multi-solve driver script.

    Raises:
        MultiSolveDriverError: When all three driver-pattern conditions
            hold (multiple declared models + multiple distinct solve
            targets + at least one equation-marginal access inside a
            solve-containing loop).
    """
    report = scan_multi_solve_driver(model_ir)
    if report.is_driver:
        raise MultiSolveDriverError(report)
