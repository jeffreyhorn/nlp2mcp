"""Converter class for transforming ModelIR to MCP GAMS format.

This module provides the main Converter class that takes a parsed ModelIR
and generates MCP GAMS code. This is a simplified conversion pipeline
focused on basic IR → GAMS mappings, separate from the full KKT transformation
pipeline in src/kkt and src/emit.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..emit.expr_to_gams import expr_to_gams
from ..ir.constants import PREDEFINED_GAMS_CONSTANTS
from ..ir.model_ir import ModelIR
from ..ir.symbols import EquationDef, Rel, VariableDef, VarKind


class ConversionError(Exception):
    """Exception raised when IR cannot be converted to MCP GAMS."""


@dataclass
class ConversionResult:
    """Result of converting ModelIR to MCP GAMS.

    Attributes:
        success: True if conversion succeeded, False otherwise
        output: Generated MCP GAMS code if successful, None otherwise
        errors: List of error messages encountered during conversion
    """

    success: bool
    output: str | None
    errors: list[str]


class Converter:
    """Converts ModelIR to MCP GAMS format.

    This converter performs basic IR → MCP GAMS transformations:
    - Variable declarations with bounds
    - Parameter declarations with values
    - Equation declarations with expressions

    Example:
        >>> from src.ir.parser import parse_model_file
        >>> from src.converter import Converter
        >>> ir = parse_model_file("model.gms")
        >>> converter = Converter(ir)
        >>> result = converter.convert()
        >>> if result.success:
        ...     print(result.output)
    """

    def __init__(self, ir: ModelIR):
        """Initialize converter with ModelIR.

        Args:
            ir: Parsed model intermediate representation
        """
        self.ir = ir
        self.output: list[str] = []
        self.errors: list[str] = []

    def convert(self) -> ConversionResult:
        """Convert IR to MCP GAMS.

        Returns:
            ConversionResult with success status, output, and any errors
        """
        try:
            self.convert_sets()
            self.convert_parameters()
            self.convert_variables()
            self.convert_equations()

            return ConversionResult(success=True, output="\n".join(self.output), errors=self.errors)
        except ConversionError as e:
            return ConversionResult(success=False, output=None, errors=[str(e)] + self.errors)

    def convert_sets(self):
        """Convert set declarations to GAMS format.

        Placeholder for Day 7. Sets are needed for indexed variables/parameters.
        """
        # TODO: Implement set conversion
        pass

    def convert_variables(self):
        """Convert variable declarations to GAMS format.

        Generates GAMS variable declarations with appropriate types and bounds.
        Handles both scalar and indexed variables.
        """
        if not self.ir.variables:
            return

        self.output.append("")
        self.output.append("* Variable Declarations")

        for var_name, var_def in self.ir.variables.items():
            # Map variable type
            var_type = self._map_variable_type(var_def.kind)

            # Generate declaration
            if var_def.domain:
                # Indexed variable: Variable x(i,j);
                domain_str = ",".join(var_def.domain)
                self.output.append(f"{var_type} Variable {var_name}({domain_str});")
            else:
                # Scalar variable: Variable x;
                self.output.append(f"{var_type} Variable {var_name};")

            # Generate bounds if present
            self._emit_variable_bounds(var_name, var_def)

    def _map_variable_type(self, kind: VarKind) -> str:
        """Map IR variable type to GAMS type keyword.

        Args:
            kind: Variable kind from IR

        Returns:
            GAMS variable type keyword
        """
        type_map = {
            VarKind.CONTINUOUS: "Free",
            VarKind.POSITIVE: "Positive",
            VarKind.NEGATIVE: "Negative",
            VarKind.BINARY: "Binary",
            VarKind.INTEGER: "Integer",
        }
        return type_map.get(kind, "Free")

    def _emit_variable_bounds(self, var_name: str, var_def: VariableDef):
        """Emit variable bounds and initial values.

        Args:
            var_name: Variable name
            var_def: Variable definition from IR
        """
        # Fixed value overrides bounds
        if var_def.fx is not None:
            self.output.append(f"{var_name}.fx = {var_def.fx};")
            return

        # Lower bound
        if var_def.lo is not None:
            self.output.append(f"{var_name}.lo = {var_def.lo};")

        # Upper bound
        if var_def.up is not None:
            self.output.append(f"{var_name}.up = {var_def.up};")

        # Initial level value
        if var_def.l is not None:
            self.output.append(f"{var_name}.l = {var_def.l};")

        # Marginal value (typically for MCP)
        if var_def.m is not None:
            self.output.append(f"{var_name}.m = {var_def.m};")

    def convert_parameters(self):
        """Convert parameter declarations to GAMS format.

        Generates GAMS parameter declarations with values.
        Handles both scalar and indexed parameters.
        Skips predefined GAMS constants (pi, inf, eps, na) since they are
        reserved words and already available in GAMS.
        """
        # Filter out predefined GAMS constants - they are reserved words
        user_params = {
            name: param_def
            for name, param_def in self.ir.params.items()
            if name not in PREDEFINED_GAMS_CONSTANTS
        }

        if not user_params:
            return

        self.output.append("")
        self.output.append("* Parameter Declarations")

        for param_name, param_def in user_params.items():
            # Generate declaration
            if param_def.domain:
                # Indexed parameter: Parameter p(i,j);
                domain_str = ",".join(param_def.domain)
                self.output.append(f"Parameter {param_name}({domain_str});")

                # Generate value assignments if present
                if param_def.values:
                    for indices, value in param_def.values.items():
                        indices_str = ",".join(f'"{idx}"' for idx in indices)
                        self.output.append(f"{param_name}({indices_str}) = {value};")
            else:
                # Scalar parameter
                if param_def.values and () in param_def.values:
                    # Scalar with value: Parameter p / 5.0 /;
                    value = param_def.values[()]
                    self.output.append(f"Parameter {param_name} / {value} /;")
                else:
                    # Scalar without initial value
                    self.output.append(f"Parameter {param_name};")

    def convert_equations(self):
        """Convert equation declarations to GAMS format.

        Generates GAMS equation declarations and definitions.
        Handles both scalar and indexed equations.
        """
        if not self.ir.equations:
            return

        self.output.append("")
        self.output.append("* Equation Declarations")

        for eq_name, eq_def in self.ir.equations.items():
            # Generate declaration
            if eq_def.domain:
                # Indexed equation: Equation cost(i,j);
                domain_str = ",".join(eq_def.domain)
                self.output.append(f"Equation {eq_name}({domain_str});")
            else:
                # Scalar equation: Equation cost;
                self.output.append(f"Equation {eq_name};")

            # Generate definition
            self._emit_equation_definition(eq_name, eq_def)

    def _emit_equation_definition(self, eq_name: str, eq_def: EquationDef):
        """Emit equation definition.

        Args:
            eq_name: Equation name
            eq_def: Equation definition from IR
        """
        # Map relation type
        rel_str = self._map_relation(eq_def.relation)

        # Convert LHS and RHS expressions to GAMS syntax
        lhs_expr, rhs_expr = eq_def.lhs_rhs
        lhs_gams = expr_to_gams(lhs_expr)
        rhs_gams = expr_to_gams(rhs_expr)

        # Generate equation definition
        if eq_def.domain:
            # Indexed equation: eq(i,j).. lhs =e= rhs;
            domain_str = ",".join(eq_def.domain)
            self.output.append(f"{eq_name}({domain_str}).. {lhs_gams} {rel_str} {rhs_gams};")
        else:
            # Scalar equation: eq.. lhs =e= rhs;
            self.output.append(f"{eq_name}.. {lhs_gams} {rel_str} {rhs_gams};")

    def _map_relation(self, relation: Rel) -> str:
        """Map IR equation relation to GAMS operator.

        Args:
            relation: Equation relation from IR

        Returns:
            GAMS relation operator
        """
        rel_map = {
            Rel.EQ: "=E=",
            Rel.LE: "=L=",
            Rel.GE: "=G=",
        }
        return rel_map.get(relation, "=E=")
