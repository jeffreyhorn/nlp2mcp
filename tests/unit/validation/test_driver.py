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
