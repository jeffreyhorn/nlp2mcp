"""Unit tests for src.validation.driver.

Covers the three-condition conjunction that the gate requires before
classifying a GAMS source as a multi-solve driver script:

  1. ≥ 2 declared ``Model`` names,
  2. ≥ 2 distinct solve-target model names,
  3. ≥ 1 equation-marginal access inside a solve-containing ``loop``.

All three must hold to raise. The critical regression guard is
``ibm1`` (single declared model, multiple solves): it must NOT raise.
Post-solve reporting that stores ``var.l`` into a display parameter
(partssupply pattern) must also NOT raise, since ``var.l`` is a
variable level — not an equation dual.
"""

from __future__ import annotations

from lark import Token, Tree

from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import (
    EquationDef,
    LoopStatement,
    ObjSense,
    Rel,
    VariableDef,
    VarKind,
)
from src.validation.driver import (
    MultiSolveDriverError,
    scan_multi_solve_driver,
    validate_single_optimization,
)

# ---------------------------------------------------------------------------
# Tree-building helpers (keep tests self-contained and free of real parse)
# ---------------------------------------------------------------------------


def _bound_scalar(sym: str, attr: str) -> Tree:
    """Build a ``bound_scalar`` node: ``sym.attr`` (e.g., ``tbal.m``)."""
    return Tree(
        "bound_scalar",
        [Token("ID", sym), Token("BOUND_K", attr)],
    )


def _solve(model_name: str) -> Tree:
    """Build a minimal ``solve`` node whose first child is the target model."""
    return Tree("solve", [Token("ID", model_name)])


def _assign_from_bound(lhs: str, rhs_tree: Tree) -> Tree:
    """Build ``assign`` node ``lhs = <rhs_tree>;``."""
    return Tree(
        "assign",
        [
            Tree("lvalue", [Token("ID", lhs)]),
            Token("ASSIGN", "="),
            rhs_tree,
            Token("SEMI", ";"),
        ],
    )


def _ir_with_declared_models(*names: str) -> ModelIR:
    ir = ModelIR()
    # ModelIR.declared_models is set[str]; populate via the declared_model
    # setter so _first_declared_model is also wired correctly.
    for name in names:
        ir.declared_model = name
    return ir


def _add_equation(ir: ModelIR, name: str) -> None:
    ir.equations[name] = EquationDef(name=name, domain=(), relation=Rel.EQ, lhs_rhs=(None, None))


def _add_solve_objective(ir: ModelIR, model_name: str) -> None:
    """Add a placeholder ObjectiveIR keyed by ``model_name`` so the
    detector sees ``model_name`` as a solve target. The value is
    immaterial for driver detection.
    """
    ir._solve_objectives[model_name] = ObjectiveIR(sense=ObjSense.MIN, objvar="z", expr=None)


# ---------------------------------------------------------------------------
# scan — structured report
# ---------------------------------------------------------------------------


def test_scan_empty_ir_reports_no_driver():
    ir = ModelIR()
    report = scan_multi_solve_driver(ir)
    assert report.declared_models == []
    assert report.solve_targets == []
    assert report.equation_marginals == []
    assert report.is_driver is False


def test_scan_single_model_multi_solve_is_not_driver():
    """ibm1 regression guard: 1 declared model, repeated solves on the
    same model must NEVER be flagged as a driver.
    """
    ir = _ir_with_declared_models("alloy")
    _add_equation(ir, "eq1")
    _add_solve_objective(ir, "alloy")
    loop = LoopStatement(
        indices=("t",),
        body_stmts=[_solve("alloy"), _solve("alloy")],
        location=None,
        raw_node=None,
    )
    ir.loop_statements.append(loop)
    report = scan_multi_solve_driver(ir)
    assert report.is_driver is False


def test_scan_partssupply_style_variable_level_is_not_driver():
    """partssupply regression guard: ``util.l`` is a variable level,
    not an equation dual. Even with two models + two solves, a loop
    body storing ``var.l`` into a display parameter is NOT a driver.
    """
    ir = _ir_with_declared_models("m", "m_mn")
    ir.variables["util"] = VariableDef(name="util", domain=(), kind=VarKind.CONTINUOUS)
    _add_solve_objective(ir, "m")
    _add_solve_objective(ir, "m_mn")
    loop = LoopStatement(
        indices=("t",),
        body_stmts=[
            _solve("m"),
            _assign_from_bound("util_lic", _bound_scalar("util", "l")),
        ],
        location=None,
        raw_node=None,
    )
    ir.loop_statements.append(loop)
    report = scan_multi_solve_driver(ir)
    assert report.is_driver is False


def test_scan_decomp_style_equation_marginal_is_driver():
    """decomp: two declared models, two solve targets, and a loop
    body that reads ``tbal.m`` (equation marginal) into a parameter
    between solves. This IS a driver.
    """
    ir = _ir_with_declared_models("sub", "master")
    _add_equation(ir, "tbal")
    _add_solve_objective(ir, "sub")
    _add_solve_objective(ir, "master")
    loop = LoopStatement(
        indices=("ss",),
        body_stmts=[
            _assign_from_bound(
                "ctank",
                Tree("unaryop", [Token("MINUS", "-"), _bound_scalar("tbal", "m")]),
            ),
            _solve("sub"),
            _solve("master"),
        ],
        location=None,
        raw_node=None,
    )
    ir.loop_statements.append(loop)
    report = scan_multi_solve_driver(ir)
    assert report.is_driver is True
    assert ("tbal", "m") in report.equation_marginals
    assert report.solve_targets == ["master", "sub"]


def test_scan_loop_without_solve_does_not_flag():
    """A loop body containing ``eq.m`` but no ``solve`` is not a
    driver (e.g., post-solve reporting into a loop for display).
    """
    ir = _ir_with_declared_models("sub", "master")
    _add_equation(ir, "tbal")
    _add_solve_objective(ir, "sub")
    _add_solve_objective(ir, "master")
    loop = LoopStatement(
        indices=("ss",),
        body_stmts=[
            _assign_from_bound("report_param", _bound_scalar("tbal", "m")),
        ],
        location=None,
        raw_node=None,
    )
    ir.loop_statements.append(loop)
    report = scan_multi_solve_driver(ir)
    assert report.is_driver is False


def test_scan_two_models_two_solves_no_marginal_is_not_driver():
    """Two models, two solves, but no equation-marginal feedback is
    not a driver (falls through the third condition). The file can
    still be translated for the last-solved model.
    """
    ir = _ir_with_declared_models("m1", "m2")
    _add_solve_objective(ir, "m1")
    _add_solve_objective(ir, "m2")
    loop = LoopStatement(
        indices=("t",),
        body_stmts=[_solve("m1"), _solve("m2")],
        location=None,
        raw_node=None,
    )
    ir.loop_statements.append(loop)
    report = scan_multi_solve_driver(ir)
    assert report.is_driver is False


def test_scan_deduplicates_equation_marginals_first_seen_order():
    """Repeated ``eq.m`` reads (same equation, multiple loop statements)
    should appear once in the report, preserving first-seen order. Keeps
    user-facing messages and status-DB ``pipeline_status.details`` clean
    (the emitter previously produced strings like ``tbal.m, tbal.m``).
    """
    ir = _ir_with_declared_models("sub", "master")
    _add_equation(ir, "tbal")
    _add_equation(ir, "convex")
    _add_solve_objective(ir, "sub")
    _add_solve_objective(ir, "master")
    loop = LoopStatement(
        indices=("ss",),
        body_stmts=[
            _assign_from_bound("p1", _bound_scalar("tbal", "m")),
            _assign_from_bound("p2", _bound_scalar("convex", "m")),
            _assign_from_bound("p3", _bound_scalar("tbal", "m")),  # dup
            _solve("sub"),
            _solve("master"),
        ],
        location=None,
        raw_node=None,
    )
    ir.loop_statements.append(loop)
    report = scan_multi_solve_driver(ir)
    assert report.is_driver is True
    # Deduplicated and in first-seen order.
    assert report.equation_marginals == [("tbal", "m"), ("convex", "m")]


def test_scan_counts_nested_loop_solves():
    """Solve targets nested inside a loop body must count toward the
    solve-targets total even if they do not appear in
    ``_solve_objectives`` (the parser drops some).
    """
    ir = _ir_with_declared_models("a", "b", "c")
    _add_equation(ir, "eq_a")
    _add_solve_objective(ir, "a")
    loop = LoopStatement(
        indices=("t",),
        body_stmts=[
            _solve("b"),
            _solve("c"),
            _assign_from_bound("p", _bound_scalar("eq_a", "m")),
        ],
        location=None,
        raw_node=None,
    )
    ir.loop_statements.append(loop)
    report = scan_multi_solve_driver(ir)
    assert sorted(report.solve_targets) == ["a", "b", "c"]
    assert report.is_driver is True


# ---------------------------------------------------------------------------
# validate_single_optimization — raises on driver input
# ---------------------------------------------------------------------------


def test_validate_passes_on_single_model():
    ir = _ir_with_declared_models("alloy")
    validate_single_optimization(ir)  # no raise


def test_validate_raises_on_decomp_style():
    ir = _ir_with_declared_models("sub", "master")
    _add_equation(ir, "tbal")
    _add_solve_objective(ir, "sub")
    _add_solve_objective(ir, "master")
    loop = LoopStatement(
        indices=("ss",),
        body_stmts=[
            _assign_from_bound("ctank", _bound_scalar("tbal", "m")),
            _solve("sub"),
            _solve("master"),
        ],
        location=None,
        raw_node=None,
    )
    ir.loop_statements.append(loop)
    import pytest

    with pytest.raises(MultiSolveDriverError) as exc:
        validate_single_optimization(ir)
    # Message must name the declared models and include the .m ref.
    msg = str(exc.value)
    assert "sub" in msg and "master" in msg
    assert "tbal.m" in msg


def test_validate_error_exposes_report():
    ir = _ir_with_declared_models("sub", "master")
    _add_equation(ir, "tbal")
    _add_solve_objective(ir, "sub")
    _add_solve_objective(ir, "master")
    loop = LoopStatement(
        indices=("ss",),
        body_stmts=[
            _assign_from_bound("ctank", _bound_scalar("tbal", "m")),
            _solve("sub"),
        ],
        location=None,
        raw_node=None,
    )
    ir.loop_statements.append(loop)
    import pytest

    with pytest.raises(MultiSolveDriverError) as exc:
        validate_single_optimization(ir)
    assert exc.value.report.is_driver is True
    assert ("tbal", "m") in exc.value.report.equation_marginals


# ---------------------------------------------------------------------------
# Issue #1270 (Sprint 25 Day 12) — Approach A cross-reference fixtures.
# Top-level (non-loop) `param[(idx)] = ...eq.m...` whose receiving param
# is later read inside any declared model's constraint body is the
# saras / primal-dual driver shape.
# ---------------------------------------------------------------------------


def _add_param(
    ir: ModelIR,
    name: str,
    domain: tuple[str, ...] = (),
    expressions: list | None = None,
) -> None:
    """Helper: register a parameter with optional expression-based assignment."""
    from src.ir.symbols import ParameterDef

    pd = ParameterDef(
        name=name,
        domain=domain,
        expressions=list(expressions or []),
    )
    ir.params[name] = pd


def _add_equation_body(
    ir: ModelIR,
    name: str,
    domain: tuple[str, ...],
    lhs,
    rhs,
) -> None:
    """Helper: register an equation with explicit lhs/rhs ASTs so the
    cross-reference walker can find ParamRef nodes inside the body.
    """
    ir.equations[name] = EquationDef(
        name=name,
        domain=domain,
        relation=Rel.EQ,
        lhs_rhs=(lhs, rhs),
    )


def test_scan_saras_style_top_level_marginal_with_feedback_is_driver():
    """F1 (saras): two declared models + two solves, top-level
    ``clam(...) = calibuc.m(...)`` then ``cGam = f(clam)`` then a
    constraint body referencing ``cGam``. Approach A's cross-reference
    walks the equation body to ``cGam``, walks ``cGam``'s expression
    transitively to ``clam``, and matches the top-level marginal
    feedback. MUST flag.
    """
    from src.ir.ast import Binary, Const, ParamRef, VarRef

    ir = _ir_with_declared_models("sarasdual", "sarasprimal")
    _add_equation(ir, "calibuc")
    _add_solve_objective(ir, "sarasdual")
    _add_solve_objective(ir, "sarasprimal")

    # clam directly receives an equation marginal at top level.
    _add_param(ir, "clam", domain=("i",))
    # cGam computed from clam: cGam(i) = clam(i) * 2.
    _add_param(
        ir,
        "cgam",
        domain=("i",),
        expressions=[
            (("i",), Binary("*", ParamRef("clam", ("i",)), Const(2.0))),
        ],
    )
    # An equation in the *primal* model body that references cGam directly.
    # nclpobj_(i).. x(i) =E= cGam(i)
    _add_equation_body(
        ir,
        "nclpobj_",
        domain=("i",),
        lhs=VarRef("x", ("i",)),
        rhs=ParamRef("cgam", ("i",)),
    )

    # Top-level capture (would normally be populated by the parser hook).
    ir.top_level_marginal_reads.append(("clam", "calibuc", "m"))

    report = scan_multi_solve_driver(ir)
    assert report.is_driver is True
    assert ("calibuc", "m") in report.equation_marginals


def test_scan_post_solve_reporting_no_constraint_feedback_is_not_driver():
    """F2 (single solve, post-solve reporting): one declared model, one
    solve, top-level ``report = eq.m`` for *display only* — the
    receiving parameter never appears in any equation body. MUST NOT
    flag (current ibm1 / single-solve baseline preserved).
    """
    ir = _ir_with_declared_models("m1")
    _add_equation(ir, "eq1")
    _add_solve_objective(ir, "m1")
    _add_param(ir, "report", domain=())
    # No equation references `report` — it's a pure display target.
    ir.top_level_marginal_reads.append(("report", "eq1", "m"))

    report = scan_multi_solve_driver(ir)
    assert report.is_driver is False


def test_scan_multi_stage_display_no_constraint_feedback_is_not_driver():
    """F3 (multi-stage display): two declared models, two solves, top-
    level ``report = eq.m`` between solves but the parameter is never
    read inside any model's constraint body. This is the case
    Approach B (sequence between solves) would over-fire on; Approach
    A correctly skips it.
    """
    from src.ir.ast import ParamRef, VarRef

    ir = _ir_with_declared_models("m1", "m2")
    _add_equation(ir, "eq1")
    _add_solve_objective(ir, "m1")
    _add_solve_objective(ir, "m2")
    # `report` is a pure display target — exists, but the m2 model body
    # below references a *different* parameter (`p_input`).
    _add_param(ir, "report", domain=())
    _add_param(ir, "p_input", domain=())
    _add_equation_body(
        ir,
        "eq2",
        domain=(),
        lhs=VarRef("y", ()),
        rhs=ParamRef("p_input", ()),
    )
    ir.top_level_marginal_reads.append(("report", "eq1", "m"))

    report = scan_multi_solve_driver(ir)
    assert report.is_driver is False


def test_scan_partssupply_var_l_top_level_is_not_driver_under_approach_a():
    """F4 (partssupply-style ``var.l``): two declared models, two
    solves, ``util_lic(t) = util.l(t)`` at top level. ``util`` is a
    variable, not an equation, so its ``.l`` (level) is *not* a dual.
    Approach A scopes its detector to ``.m`` on declared equations
    only — so even with a constraint-body reference to ``util_lic``,
    this MUST NOT flag.
    """
    from src.ir.ast import ParamRef, VarRef

    ir = _ir_with_declared_models("m1", "m2")
    _add_solve_objective(ir, "m1")
    _add_solve_objective(ir, "m2")
    _add_param(ir, "util_lic", domain=("t",))
    _add_equation_body(
        ir,
        "eq2",
        domain=("t",),
        lhs=VarRef("y", ("t",)),
        rhs=ParamRef("util_lic", ("t",)),
    )
    # Top-level capture records both the marginal-style and var.l-style
    # reads; the parser hook is over-approximate by design. The gate
    # filters to ``attr == "m"`` and ``sym in equation_names``, so
    # var.l (attr "l") and reads of bare variables are skipped.
    ir.top_level_marginal_reads.append(("util_lic", "util", "l"))
    # Sanity: even a `.m` on a *variable* (not an equation) must not flag.
    ir.top_level_marginal_reads.append(("util_lic", "util", "m"))

    report = scan_multi_solve_driver(ir)
    assert report.is_driver is False
