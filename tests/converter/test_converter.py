"""Unit tests for the Converter class."""

from src.converter import ConversionResult, Converter
from src.ir.model_ir import ModelIR
from src.ir.symbols import ParameterDef, VariableDef, VarKind


class TestConverterScaffolding:
    """Test basic converter scaffolding."""

    def test_converter_instantiates(self):
        """Test that Converter can be instantiated with ModelIR."""
        ir = ModelIR()
        converter = Converter(ir)
        assert converter.ir is ir
        assert converter.output == []
        assert converter.errors == []

    def test_convert_empty_model(self):
        """Test converting an empty model returns success."""
        ir = ModelIR()
        converter = Converter(ir)
        result = converter.convert()

        assert isinstance(result, ConversionResult)
        assert result.success is True
        assert result.output == ""
        assert result.errors == []

    def test_conversion_result_structure(self):
        """Test ConversionResult dataclass has expected fields."""
        result = ConversionResult(success=True, output="test", errors=[])
        assert result.success is True
        assert result.output == "test"
        assert result.errors == []


class TestVariableConversion:
    """Test variable IR → MCP GAMS mappings."""

    def test_convert_scalar_free_variable(self):
        """Test converting a scalar free variable."""
        ir = ModelIR()
        ir.variables["x"] = VariableDef(name="x", kind=VarKind.CONTINUOUS)

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Free Variable x;" in result.output

    def test_convert_positive_variable(self):
        """Test converting a positive variable."""
        ir = ModelIR()
        ir.variables["x"] = VariableDef(name="x", kind=VarKind.POSITIVE)

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Positive Variable x;" in result.output

    def test_convert_variable_with_bounds(self):
        """Test converting a variable with lower and upper bounds."""
        ir = ModelIR()
        ir.variables["x"] = VariableDef(name="x", kind=VarKind.CONTINUOUS, lo=0.0, up=10.0)

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Free Variable x;" in result.output
        assert "x.lo = 0.0;" in result.output
        assert "x.up = 10.0;" in result.output

    def test_convert_variable_with_fixed_value(self):
        """Test converting a variable with fixed value."""
        ir = ModelIR()
        ir.variables["x"] = VariableDef(name="x", kind=VarKind.CONTINUOUS, fx=5.0)

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Free Variable x;" in result.output
        assert "x.fx = 5.0;" in result.output

    def test_convert_indexed_variable(self):
        """Test converting an indexed variable."""
        ir = ModelIR()
        ir.variables["x"] = VariableDef(name="x", kind=VarKind.POSITIVE, domain=("i", "j"))

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Positive Variable x(i,j);" in result.output

    def test_convert_variable_with_initial_value(self):
        """Test converting a variable with initial level value."""
        ir = ModelIR()
        ir.variables["x"] = VariableDef(name="x", kind=VarKind.CONTINUOUS, l=1.5)

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Free Variable x;" in result.output
        assert "x.l = 1.5;" in result.output

    def test_convert_multiple_variables(self):
        """Test converting multiple variables."""
        ir = ModelIR()
        ir.variables["x"] = VariableDef(name="x", kind=VarKind.POSITIVE)
        ir.variables["y"] = VariableDef(name="y", kind=VarKind.CONTINUOUS, lo=-5.0)

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Positive Variable x;" in result.output
        assert "Free Variable y;" in result.output
        assert "y.lo = -5.0;" in result.output


class TestParameterConversion:
    """Test parameter IR → MCP GAMS mappings."""

    def test_convert_scalar_parameter_with_value(self):
        """Test converting a scalar parameter with value."""
        ir = ModelIR()
        ir.params["p"] = ParameterDef(name="p", values={(): 5.0})

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Parameter p / 5.0 /;" in result.output

    def test_convert_scalar_parameter_without_value(self):
        """Test converting a scalar parameter without value."""
        ir = ModelIR()
        ir.params["p"] = ParameterDef(name="p")

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Parameter p;" in result.output

    def test_convert_indexed_parameter(self):
        """Test converting an indexed parameter."""
        ir = ModelIR()
        ir.params["demand"] = ParameterDef(name="demand", domain=("i",))

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Parameter demand(i);" in result.output

    def test_convert_indexed_parameter_with_values(self):
        """Test converting an indexed parameter with values."""
        ir = ModelIR()
        ir.params["cost"] = ParameterDef(
            name="cost",
            domain=("i", "j"),
            values={("seattle", "newyork"): 2.5, ("seattle", "chicago"): 1.7},
        )

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Parameter cost(i,j);" in result.output
        assert 'cost("seattle","newyork") = 2.5;' in result.output
        assert 'cost("seattle","chicago") = 1.7;' in result.output

    def test_convert_multiple_parameters(self):
        """Test converting multiple parameters."""
        ir = ModelIR()
        ir.params["a"] = ParameterDef(name="a", values={(): 10.0})
        ir.params["b"] = ParameterDef(name="b", domain=("i",))

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Parameter a / 10.0 /;" in result.output
        assert "Parameter b(i);" in result.output


class TestEquationConversion:
    """Test equation IR → MCP GAMS mappings."""

    def test_convert_scalar_equality_equation(self):
        """Test converting a scalar equality equation."""
        from src.ir.ast import Const, SymbolRef
        from src.ir.symbols import EquationDef, Rel

        ir = ModelIR()
        # Simple equation: eq.. x =e= 5;
        lhs = SymbolRef(name="x")
        rhs = Const(value=5.0)
        ir.equations["eq"] = EquationDef(name="eq", domain=(), relation=Rel.EQ, lhs_rhs=(lhs, rhs))

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Equation eq;" in result.output
        assert "eq.. x =E= 5;" in result.output

    def test_convert_inequality_equation(self):
        """Test converting an inequality equation."""
        from src.ir.ast import Const, SymbolRef
        from src.ir.symbols import EquationDef, Rel

        ir = ModelIR()
        # Inequality: ineq.. x =l= 10;
        lhs = SymbolRef(name="x")
        rhs = Const(value=10.0)
        ir.equations["ineq"] = EquationDef(
            name="ineq", domain=(), relation=Rel.LE, lhs_rhs=(lhs, rhs)
        )

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Equation ineq;" in result.output
        assert "ineq.. x =L= 10;" in result.output

    def test_convert_equation_with_binary_expression(self):
        """Test converting equation with binary operation."""
        from src.ir.ast import Binary, Const, SymbolRef
        from src.ir.symbols import EquationDef, Rel

        ir = ModelIR()
        # Equation: eq.. x + y =e= 10;
        x_ref = SymbolRef(name="x")
        y_ref = SymbolRef(name="y")
        lhs = Binary(op="+", left=x_ref, right=y_ref)
        rhs = Const(value=10.0)
        ir.equations["eq"] = EquationDef(name="eq", domain=(), relation=Rel.EQ, lhs_rhs=(lhs, rhs))

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Equation eq;" in result.output
        assert "eq.. x + y =E= 10;" in result.output

    def test_convert_multiple_equations(self):
        """Test converting multiple equations."""
        from src.ir.ast import Const, SymbolRef
        from src.ir.symbols import EquationDef, Rel

        ir = ModelIR()
        # eq1.. x =e= 5;
        ir.equations["eq1"] = EquationDef(
            name="eq1", domain=(), relation=Rel.EQ, lhs_rhs=(SymbolRef(name="x"), Const(value=5.0))
        )
        # eq2.. y =g= 0;
        ir.equations["eq2"] = EquationDef(
            name="eq2", domain=(), relation=Rel.GE, lhs_rhs=(SymbolRef(name="y"), Const(value=0.0))
        )

        converter = Converter(ir)
        result = converter.convert()

        assert result.success is True
        assert "Equation eq1;" in result.output
        assert "eq1.. x =E= 5;" in result.output
        assert "Equation eq2;" in result.output
        assert "eq2.. y =G= 0;" in result.output
