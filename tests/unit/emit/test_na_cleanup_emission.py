"""Sprint 25 / #1322: NA-cleanup emission for division-based parameter
assignments.

When a model has parameters whose pre-solve assignment expressions
contain `Binary("/")` divisions, those parameters can evaluate to
`NA`/`UNDF` at runtime if their inputs include zero in the divisor
(e.g., gtm's `supb(i)` is computed via `(numerator)/(1/(supc-q1) -
1/(supc-q2))` and goes NA when `supc(i) = 0` from empty source data).
The NA values propagate into PATH's symbolic Jacobian as gigantic
coefficients (~1e30), making the model numerically unsolvable even
after PR #1321 closes the listing-time aborts.

The fix emits `param(d)$(NOT (param(d) > -inf and param(d) < inf)) = 0;`
for indexed parameters with division-based assignments. These tests
validate the helper detection and emission logic; the gtm corpus
regression lives in `tests/integration/emit/test_gtm_na_cleanup.py`.
"""

from __future__ import annotations

import pytest

from src.emit.original_symbols import (
    _expr_contains_division,
    _param_assignment_has_division,
    emit_post_assignment_na_cleanup,
)
from src.ir.ast import Binary, Const, ParamRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import ParameterDef


def _make_param(
    name: str,
    domain: tuple[str, ...],
    expressions: list,
) -> ParameterDef:
    """Build a minimal `ParameterDef` for testing the cleanup helpers."""
    return ParameterDef(
        name=name,
        domain=domain,
        expressions=expressions,
    )


@pytest.mark.unit
def test_indexed_param_with_division_emits_cleanup():
    """`p(i) = 1/q(i)` should produce a cleanup line for `p`."""
    p = _make_param(
        "p",
        ("i",),
        expressions=[(("i",), Binary("/", Const(1.0), ParamRef("q", ("i",))))],
    )
    model = ModelIR()
    model.params["p"] = p

    output = emit_post_assignment_na_cleanup(model)

    assert "p(i)$(NOT (p(i) > -inf and p(i) < inf)) = 0;" in output


@pytest.mark.unit
def test_indexed_param_without_division_no_cleanup():
    """`p(i) = a(i) + b(i)` (no division) should NOT produce a cleanup
    line.
    """
    p = _make_param(
        "p",
        ("i",),
        expressions=[(("i",), Binary("+", ParamRef("a", ("i",)), ParamRef("b", ("i",))))],
    )
    model = ModelIR()
    model.params["p"] = p

    output = emit_post_assignment_na_cleanup(model)

    assert output == "", f"Expected empty output for non-division param; got:\n{output}"


@pytest.mark.unit
def test_scalar_param_with_division_no_cleanup():
    """Scalar params (empty domain) are out of scope — their NA-ness
    is a static fact, and the user can pre-guard them differently if
    needed.
    """
    p = _make_param(
        "p",
        (),
        expressions=[((), Binary("/", Const(1.0), ParamRef("q", ())))],
    )
    model = ModelIR()
    model.params["p"] = p

    output = emit_post_assignment_na_cleanup(model)

    assert output == "", f"Expected empty output for scalar param; got:\n{output}"


@pytest.mark.unit
def test_model_relevant_filter_suppresses_unused_params():
    """If `p(i)` only appears in display blocks (not in any equation)
    and the caller passes `model_relevant_params={"q"}`, no cleanup
    line is emitted for `p`.
    """
    p = _make_param(
        "p",
        ("i",),
        expressions=[(("i",), Binary("/", Const(1.0), ParamRef("q", ("i",))))],
    )
    model = ModelIR()
    model.params["p"] = p

    # Filter to only `q` (which doesn't have an assignment in this test).
    output = emit_post_assignment_na_cleanup(model, model_relevant_params={"q"})

    assert output == "", f"Expected empty output when `p` is filtered out; got:\n{output}"


@pytest.mark.unit
def test_multiple_offending_params_emit_in_sorted_order():
    """When several indexed params have division-based assignments,
    emit cleanup lines in sorted (deterministic) order.
    """
    p_supb = _make_param(
        "supb",
        ("i",),
        expressions=[(("i",), Binary("/", Const(1.0), ParamRef("supc", ("i",))))],
    )
    p_supa = _make_param(
        "supa",
        ("i",),
        expressions=[(("i",), Binary("/", ParamRef("supb", ("i",)), ParamRef("supc", ("i",))))],
    )
    model = ModelIR()
    model.params["supb"] = p_supb
    model.params["supa"] = p_supa

    output = emit_post_assignment_na_cleanup(model)
    lines = [line for line in output.splitlines() if "$(NOT (" in line]

    # Two cleanup lines, sorted alphabetically: supa first, supb second.
    assert len(lines) == 2, f"Expected 2 cleanup lines; got {len(lines)}: {lines}"
    assert lines[0].startswith(
        "supa("
    ), f"Expected `supa` line first (alphabetical); got: {lines[0]}"
    assert lines[1].startswith(
        "supb("
    ), f"Expected `supb` line second (alphabetical); got: {lines[1]}"


@pytest.mark.unit
def test_expr_contains_division_detects_nested_division():
    """`_expr_contains_division` should recursively find divisions in
    nested expression trees (e.g., `a + (b/c)`, `f(g(x/y))`, etc.).
    """
    # a + b/c
    expr = Binary("+", ParamRef("a", ()), Binary("/", ParamRef("b", ()), ParamRef("c", ())))
    assert _expr_contains_division(expr)

    # No division
    expr_no_div = Binary("*", ParamRef("a", ()), ParamRef("b", ()))
    assert not _expr_contains_division(expr_no_div)


@pytest.mark.unit
def test_param_assignment_has_division_helper():
    """Direct test of `_param_assignment_has_division` on a
    `ParameterDef` with mixed expressions.
    """
    # Param with first expression simple, second containing division.
    p = _make_param(
        "p",
        ("i",),
        expressions=[
            (("i",), ParamRef("a", ("i",))),  # No division
            (
                ("i",),
                Binary("/", ParamRef("a", ("i",)), ParamRef("b", ("i",))),
            ),  # Has division
        ],
    )
    assert _param_assignment_has_division(p)

    # Param with no division anywhere.
    p_clean = _make_param(
        "p_clean",
        ("i",),
        expressions=[(("i",), Binary("+", ParamRef("a", ("i",)), Const(1.0)))],
    )
    assert not _param_assignment_has_division(p_clean)
