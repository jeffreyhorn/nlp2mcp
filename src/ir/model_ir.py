from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .ast import Expr
from .symbols import (
    AliasDef,
    EquationDef,
    ObjSense,
    ParameterDef,
    SetDef,
    VariableDef,
)

if TYPE_CHECKING:
    from .normalize import NormalizedEquation


@dataclass
class ObjectiveIR:
    sense: ObjSense
    objvar: str  # name of objective variable/symbol
    expr: Expr | None = None  # if objective given by explicit expression via eqn


@dataclass
class ModelIR:
    # Symbols
    sets: dict[str, SetDef] = field(default_factory=dict)
    aliases: dict[str, AliasDef] = field(default_factory=dict)
    params: dict[str, ParameterDef] = field(default_factory=dict)
    variables: dict[str, VariableDef] = field(default_factory=dict)

    # Equations
    equations: dict[str, EquationDef] = field(default_factory=dict)

    # Solve info
    declared_model: str | None = None
    model_equations: list[str] = field(default_factory=list)
    model_uses_all: bool = False
    model_name: str | None = None
    objective: ObjectiveIR | None = None  # filled after parsing Solve

    # Convenience lookups (to be populated during normalization)
    equalities: list[str] = field(default_factory=list)  # equation names =e=
    inequalities: list[str] = field(default_factory=list)  # equation names with <=0 form
    normalized_bounds: dict[str, NormalizedEquation] = field(default_factory=dict)

    # Min/max reformulation tracking
    strategy1_applied: bool = False  # True if Strategy 1 (objective substitution) was applied
    # These multipliers are paired with complementarity constraints in MCP
    # They should NOT have stationarity equations generated for them
    complementarity_multipliers: dict[str, str] = field(
        default_factory=dict
    )  # mult_name -> constraint_name

    def add_set(self, s: SetDef) -> None:
        self.sets[s.name] = s

    def add_alias(self, a: AliasDef) -> None:
        self.aliases[a.name] = a

    def add_param(self, p: ParameterDef) -> None:
        self.params[p.name] = p

    def add_var(self, v: VariableDef) -> None:
        self.variables[v.name] = v

    def add_equation(self, e: EquationDef) -> None:
        self.equations[e.name] = e
