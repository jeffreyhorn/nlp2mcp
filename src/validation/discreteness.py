"""Discreteness gate for nlp2mcp's NLP→MCP translator.

nlp2mcp targets continuous NLP→MCP transformation via KKT conditions.
MINLP/MIP/MIQCP models are categorically out of scope: their KKT
characterization does not apply, and PATH (the MCP solver) rejects
discrete variables outright (GAMS Error 65).

This module provides a single-call gate, ``validate_continuous(model_ir)``,
that detects discrete inputs from two independent signals and raises
:class:`MINLPNotSupportedError` if either fires:

1. A primal variable's :class:`~src.ir.symbols.VarKind` is one of
   ``BINARY``, ``INTEGER``, ``SOS1``, ``SOS2``.
2. The model's ``solve … using …`` clause names a discrete solver
   class (``MIP``, ``MINLP``, ``MIQCP``, ``RMIP``, ``RMINLP``,
   ``RMIQCP``).

Either signal alone is sufficient to refuse translation.

The CLI maps the exception to a distinct exit code so callers can
distinguish "out of scope" from parse errors / compile errors.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..ir.symbols import VarKind
from ..utils.errors import UserError

if TYPE_CHECKING:
    from ..ir.model_ir import ModelIR


# Solver-class strings (uppercased) that imply discrete variables.
DISCRETE_SOLVE_TYPES: frozenset[str] = frozenset(
    {"MIP", "MINLP", "MIQCP", "RMIP", "RMINLP", "RMIQCP"}
)

# VarKind values that imply discreteness.
DISCRETE_VAR_KINDS: frozenset[VarKind] = frozenset(
    {VarKind.BINARY, VarKind.INTEGER, VarKind.SOS1, VarKind.SOS2}
)


@dataclass
class DiscretenessReport:
    """Findings from a discreteness scan of a ModelIR.

    Attributes:
        discrete_vars: List of (var_name, kind_name) tuples for any
            primal variables whose VarKind is in DISCRETE_VAR_KINDS.
        solve_type: The model's solve_type if it implies discreteness
            (one of DISCRETE_SOLVE_TYPES), else None.
    """

    discrete_vars: list[tuple[str, str]]
    solve_type: str | None

    @property
    def is_discrete(self) -> bool:
        return bool(self.discrete_vars) or self.solve_type is not None


class MINLPNotSupportedError(UserError):
    """Raised when validate_continuous() detects discrete input.

    nlp2mcp does not translate MINLP/MIP/MIQCP models. The proper
    handling is to mark the model as discrete in the corpus database
    and exclude it from pipeline runs; see PLAN_FIX_FEEDTRAY.md.
    """

    def __init__(self, report: DiscretenessReport):
        self.report = report
        parts: list[str] = []
        if report.discrete_vars:
            shown = ", ".join(f"{n} ({k})" for n, k in report.discrete_vars[:5])
            extra = (
                f" (+{len(report.discrete_vars) - 5} more)"
                if len(report.discrete_vars) > 5
                else ""
            )
            parts.append(f"discrete primal variables: {shown}{extra}")
        if report.solve_type:
            parts.append(f"discrete solve clause: using {report.solve_type}")
        detail = "; ".join(parts) if parts else "discrete signal detected"
        message = (
            "Model is MINLP/MIP and is out of scope for nlp2mcp "
            f"(NLP→MCP via KKT). Detected: {detail}."
        )
        suggestion = (
            "nlp2mcp transforms continuous NLPs to MCP via KKT conditions, "
            "and MCP/PATH cannot accept discrete variables. Mark this model "
            "as MINLP/MIP in data/gamslib/gamslib_status.json and exclude "
            "it from the pipeline. To force translation anyway (for "
            "development/debugging only), pass --allow-discrete; the "
            "generated MCP file will fail GAMS compilation."
        )
        super().__init__(message, suggestion)


def scan_discreteness(model_ir: ModelIR) -> DiscretenessReport:
    """Scan a ModelIR for discrete-variable signals.

    Pure function: does not raise, does not mutate. Returns a
    structured report so callers can decide how to react (the CLI
    raises; the batch pipeline records and skips).
    """
    discrete_vars: list[tuple[str, str]] = []
    for name, var_def in model_ir.variables.items():
        if var_def.kind in DISCRETE_VAR_KINDS:
            discrete_vars.append((name, var_def.kind.name))

    solve_type = (model_ir.solve_type or "").upper() or None
    if solve_type not in DISCRETE_SOLVE_TYPES:
        solve_type = None

    return DiscretenessReport(
        discrete_vars=discrete_vars,
        solve_type=solve_type,
    )


def validate_continuous(model_ir: ModelIR) -> None:
    """Refuse translation if the model has any discrete signals.

    Raises:
        MINLPNotSupportedError: If any primal variable has a discrete
            VarKind, or the solve_type is in DISCRETE_SOLVE_TYPES.
    """
    report = scan_discreteness(model_ir)
    if report.is_discrete:
        raise MINLPNotSupportedError(report)
