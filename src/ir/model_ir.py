from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..utils.case_insensitive_dict import CaseInsensitiveDict
from .ast import Expr
from .symbols import (
    AliasDef,
    ConditionalStatement,
    EquationDef,
    LoopStatement,
    ObjSense,
    OptionStatement,
    ParameterDef,
    SetAssignment,
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
    # Symbols - using case-insensitive dictionaries (Issue #373)
    # GAMS is case-insensitive, so 'myParam' and 'MYPARAM' refer to the same symbol
    sets: CaseInsensitiveDict[SetDef] = field(default_factory=CaseInsensitiveDict)
    aliases: CaseInsensitiveDict[AliasDef] = field(default_factory=CaseInsensitiveDict)
    params: CaseInsensitiveDict[ParameterDef] = field(default_factory=CaseInsensitiveDict)
    variables: CaseInsensitiveDict[VariableDef] = field(default_factory=CaseInsensitiveDict)

    # Equations - also case-insensitive
    equations: CaseInsensitiveDict[EquationDef] = field(default_factory=CaseInsensitiveDict)

    # Option statements (Sprint 8: mock/store approach)
    option_statements: list[OptionStatement] = field(default_factory=list)

    # Conditional statements (Sprint 8 Day 2: mock/store approach)
    conditional_statements: list[ConditionalStatement] = field(default_factory=list)

    # Loop statements (Sprint 11 Day 2 Extended: mock/store approach)
    loop_statements: list[LoopStatement] = field(default_factory=list)

    # Set assignments (Sprint 18 Day 3: dynamic subset initialization)
    set_assignments: list[SetAssignment] = field(default_factory=list)

    # Solve info  (Issue #729: track *all* declared model names, lowercase)
    declared_models: set[str] = field(default_factory=set)
    # File handles (Issue #746/#747: track File declarations for validation)
    declared_files: set[str] = field(default_factory=set)
    _first_declared_model: str | None = field(default=None, repr=False)
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

    # Backward-compatible property: returns first declared model name (or None)
    @property
    def declared_model(self) -> str | None:
        return self._first_declared_model

    @declared_model.setter
    def declared_model(self, value: str | None) -> None:
        if value is not None:
            lv = value.lower()
            self.declared_models.add(lv)
            if self._first_declared_model is None:
                self._first_declared_model = lv

    def add_set(self, s: SetDef) -> None:
        self.sets[s.name] = s

    def add_alias(self, a: AliasDef) -> None:
        self.aliases[a.name] = a

    def add_param(self, p: ParameterDef) -> None:
        self.params[p.name] = p

    def add_var(self, v: VariableDef) -> None:
        """Add or update a variable definition.

        When adding a variable that already exists:
        - If the new definition has an empty domain (scalar) but includes a non-default kind
          (e.g., from "positive variables x,y,z;"), merge by updating the kind while
          preserving the existing domain. This handles GAMS patterns like:
            variables x(i) "indexed var";
            positive variables x;  # Just updates kind, doesn't change domain
        - Otherwise, the new definition replaces the old one entirely.

        This fixes issue #418 where variables declared in include files with domains
        were being overwritten by subsequent "positive variables" statements.
        """
        from .symbols import VarKind

        if v.name in self.variables:
            existing = self.variables[v.name]
            # If new var is scalar (no domain) and existing has a domain,
            # and new var has a non-default kind, just update the kind
            if not v.domain and existing.domain and v.kind != VarKind.CONTINUOUS:
                # Update kind while preserving domain and other attributes
                existing.kind = v.kind
                return

        self.variables[v.name] = v

    def add_equation(self, e: EquationDef) -> None:
        self.equations[e.name] = e
