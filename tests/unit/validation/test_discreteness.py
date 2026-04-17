"""Unit tests for src.validation.discreteness.

Covers the eight outcomes the gate must distinguish:
- Five "discrete" cases that must raise: BINARY var, INTEGER var,
  SOS1 var, SOS2 var, discrete solve_type with no discrete vars.
- One "continuous" case that must pass: plain NLP.
- Two reporting cases for the pure scan function.
"""

from __future__ import annotations

import pytest

from src.ir.model_ir import ModelIR
from src.ir.symbols import VarKind, VariableDef
from src.validation.discreteness import (
    DISCRETE_SOLVE_TYPES,
    DISCRETE_VAR_KINDS,
    MINLPNotSupportedError,
    scan_discreteness,
    validate_continuous,
)


def _ir_with_var(kind: VarKind, *, solve_type: str | None = "NLP") -> ModelIR:
    """Build a minimal ModelIR with one variable of the given kind."""
    ir = ModelIR()
    ir.variables["x"] = VariableDef(name="x", domain=(), kind=kind)
    ir.solve_type = solve_type
    return ir


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_discrete_solve_types_are_uppercase_strings():
    assert DISCRETE_SOLVE_TYPES == frozenset(
        {"MIP", "MINLP", "MIQCP", "RMIP", "RMINLP", "RMIQCP"}
    )


def test_discrete_var_kinds_are_the_four_discrete_kinds():
    assert DISCRETE_VAR_KINDS == frozenset(
        {VarKind.BINARY, VarKind.INTEGER, VarKind.SOS1, VarKind.SOS2}
    )


# ---------------------------------------------------------------------------
# scan_discreteness — pure function, never raises
# ---------------------------------------------------------------------------


def test_scan_continuous_model_reports_no_signals():
    ir = _ir_with_var(VarKind.CONTINUOUS, solve_type="NLP")
    report = scan_discreteness(ir)
    assert report.discrete_vars == []
    assert report.solve_type is None
    assert report.is_discrete is False


def test_scan_collects_all_discrete_vars():
    ir = ModelIR()
    ir.variables["b"] = VariableDef(name="b", domain=(), kind=VarKind.BINARY)
    ir.variables["i"] = VariableDef(name="i", domain=(), kind=VarKind.INTEGER)
    ir.variables["s1"] = VariableDef(name="s1", domain=(), kind=VarKind.SOS1)
    ir.variables["s2"] = VariableDef(name="s2", domain=(), kind=VarKind.SOS2)
    ir.variables["c"] = VariableDef(name="c", domain=(), kind=VarKind.POSITIVE)
    ir.solve_type = "NLP"

    report = scan_discreteness(ir)

    names = sorted(n for n, _ in report.discrete_vars)
    assert names == ["b", "i", "s1", "s2"]
    assert report.solve_type is None
    assert report.is_discrete is True


def test_scan_normalizes_solve_type_case():
    ir = _ir_with_var(VarKind.CONTINUOUS, solve_type="minlp")
    report = scan_discreteness(ir)
    assert report.solve_type == "MINLP"
    assert report.is_discrete is True


def test_scan_ignores_non_discrete_solve_type():
    ir = _ir_with_var(VarKind.POSITIVE, solve_type="NLP")
    assert scan_discreteness(ir).is_discrete is False


def test_scan_handles_missing_solve_type():
    ir = _ir_with_var(VarKind.POSITIVE, solve_type=None)
    report = scan_discreteness(ir)
    assert report.solve_type is None
    assert report.is_discrete is False


# ---------------------------------------------------------------------------
# validate_continuous — raises on any discrete signal
# ---------------------------------------------------------------------------


def test_validate_passes_on_continuous_model():
    ir = _ir_with_var(VarKind.CONTINUOUS, solve_type="NLP")
    validate_continuous(ir)  # must not raise


def test_validate_passes_when_solve_type_is_none():
    ir = _ir_with_var(VarKind.POSITIVE, solve_type=None)
    validate_continuous(ir)


@pytest.mark.parametrize(
    "kind",
    [VarKind.BINARY, VarKind.INTEGER, VarKind.SOS1, VarKind.SOS2],
)
def test_validate_raises_for_each_discrete_kind(kind):
    ir = _ir_with_var(kind, solve_type="NLP")
    with pytest.raises(MINLPNotSupportedError) as exc_info:
        validate_continuous(ir)
    err = exc_info.value
    assert err.report.discrete_vars == [("x", kind.name)]
    assert err.report.solve_type is None


@pytest.mark.parametrize("solve_type", sorted(DISCRETE_SOLVE_TYPES))
def test_validate_raises_for_each_discrete_solve_type(solve_type):
    """A discrete solve_type alone (no discrete vars) is sufficient."""
    ir = _ir_with_var(VarKind.CONTINUOUS, solve_type=solve_type)
    with pytest.raises(MINLPNotSupportedError) as exc_info:
        validate_continuous(ir)
    err = exc_info.value
    assert err.report.discrete_vars == []
    assert err.report.solve_type == solve_type


def test_validate_combines_both_signals_in_report():
    ir = _ir_with_var(VarKind.BINARY, solve_type="MINLP")
    with pytest.raises(MINLPNotSupportedError) as exc_info:
        validate_continuous(ir)
    err = exc_info.value
    assert err.report.discrete_vars == [("x", "BINARY")]
    assert err.report.solve_type == "MINLP"


# ---------------------------------------------------------------------------
# Error message quality
# ---------------------------------------------------------------------------


def test_error_message_names_the_variable():
    ir = _ir_with_var(VarKind.BINARY)
    err = MINLPNotSupportedError(scan_discreteness(ir))
    assert "x" in str(err)
    assert "BINARY" in str(err)


def test_error_message_names_the_solve_type():
    ir = _ir_with_var(VarKind.CONTINUOUS, solve_type="MINLP")
    err = MINLPNotSupportedError(scan_discreteness(ir))
    assert "MINLP" in str(err)


def test_error_message_truncates_long_var_lists():
    ir = ModelIR()
    for k in range(10):
        ir.variables[f"y{k}"] = VariableDef(
            name=f"y{k}", domain=(), kind=VarKind.BINARY
        )
    ir.solve_type = "NLP"
    err = MINLPNotSupportedError(scan_discreteness(ir))
    assert "+5 more" in str(err)


def test_error_includes_actionable_suggestion():
    ir = _ir_with_var(VarKind.BINARY)
    err = MINLPNotSupportedError(scan_discreteness(ir))
    text = str(err)
    assert "--allow-discrete" in text
    assert "out of scope" in text.lower()
