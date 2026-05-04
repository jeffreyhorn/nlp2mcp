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

    # Issue #1270 (Sprint 25 Day 12): Top-level marginal-feedback assignments,
    # captured by the parser when a top-level (program-level, not nested in a
    # loop) assignment writes ``param[(idx)]$cond = expr-involving-X.m`` for
    # any equation/variable symbol ``X``. Each entry is the lowercase tuple
    # ``(param_name, sym_name, attr)`` where attr is currently ``"m"``. The
    # multi-solve gate (`scan_multi_solve_driver`) cross-references this list
    # against equation_names + bodies to flag saras-style primal/dual driver
    # scripts whose feedback happens between top-level solves rather than
    # inside a loop. Variable-attribute reads (e.g., ``var.l`` post-solve
    # reporting) and reads of unknown symbols are recorded too — the gate
    # filters them out — so this list is over-approximate by design.
    top_level_marginal_reads: list[tuple[str, str, str]] = field(default_factory=list)

    # Solve info  (Issue #729: track *all* declared model names, lowercase)
    declared_models: set[str] = field(default_factory=set)
    # File handles (Issue #746/#747: track File declarations for validation)
    declared_files: set[str] = field(default_factory=set)
    # Acronyms (Sprint 21 Day 1: symbolic constants declared via Acronym statement)
    acronyms: set[str] = field(default_factory=set)
    _first_declared_model: str | None = field(default=None, repr=False)
    model_equations: list[str] = field(default_factory=list)
    model_uses_all: bool = False
    # Issue #1033: Per-model equation map — maps model name (lowercase) to equation list.
    # For "/ all /" models, stores a snapshot of equations declared up to that point.
    model_equation_map: dict[str, list[str]] = field(default_factory=dict)
    model_name: str | None = None
    solve_type: str | None = None  # LP, NLP, QCP, etc. from solve statement
    objective: ObjectiveIR | None = None  # filled after parsing Solve
    # Issue #1154: Per-model objectives for reconciliation when multiple solves exist
    _solve_objectives: dict[str, ObjectiveIR] = field(default_factory=dict, repr=False)
    # Per-model solve types for reconciliation when multiple solves exist
    _solve_types: dict[str, str] = field(default_factory=dict, repr=False)

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

    def get_solved_model_equations(self) -> list[str] | None:
        """Return the equation list for the solved model, or None if unfiltered.

        Issue #1033 PR review: Centralizes the model equation resolution logic
        previously duplicated in normalize_model(), _collect_model_relevant_params(),
        and extract_objective_info().  Checks model_equation_map first (keyed by
        model_name), then falls back to model_equations for backward compatibility.

        Issue #1026: Resolves model references in equation lists. GAMS allows
        referencing other models in equation lists (e.g., ``P2R3_NonLinear /
        P2R3_Linear, DEMINT, SUPINT, OBJECT /``). When an entry matches a key
        in ``model_equation_map``, it is expanded to that model's equations.
        """
        solved_eqs: list[str] | None = None
        if self.model_name:
            solved_eqs = self.model_equation_map.get(self.model_name.lower())
        if solved_eqs is None and self.model_equations:
            solved_eqs = self.model_equations
        if not solved_eqs:
            return None
        # Resolve model references: if an entry matches another model name
        # in model_equation_map, expand it to that model's equations.
        resolved: list[str] = []
        seen: set[str] = set()
        self._resolve_model_refs(solved_eqs, resolved, seen)
        return resolved or None

    def _resolve_model_refs(
        self,
        refs: list[str],
        out: list[str],
        seen: set[str],
    ) -> None:
        """Recursively expand model references in an equation list."""
        for ref in refs:
            ref_lower = ref.lower()
            if ref_lower in seen:
                continue
            # Check if this ref is a model name (not an equation name)
            if ref_lower in self.model_equation_map and ref_lower not in self.equations:
                seen.add(ref_lower)
                self._resolve_model_refs(self.model_equation_map[ref_lower], out, seen)
            else:
                if ref_lower not in seen:
                    seen.add(ref_lower)
                    out.append(ref)

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
