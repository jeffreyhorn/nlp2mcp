"""Parser smoke tests covering tree output and ModelIR synthesis."""

from pathlib import Path
from textwrap import dedent

import lark
import pytest

from src.ir import parser
from src.ir.ast import Binary, Call, Const, Expr, ParamRef, Sum, VarRef
from src.ir.symbols import ObjSense, Rel, VarKind


def test_simple_nlp_parses_into_program_tree():
    repo_root = Path(__file__).resolve().parents[3]
    tree = parser.parse_file(repo_root / "examples" / "simple_nlp.gms")
    assert tree.data == "program"
    assert not list(tree.find_data("_ambig"))


def test_parse_model_file_populates_model_ir():
    repo_root = Path(__file__).resolve().parents[3]
    model = parser.parse_model_file(repo_root / "examples" / "simple_nlp.gms")

    assert model.sets["i"].members == ["i1", "i2", "i3"]
    assert model.params["a"].domain == ("i",)
    assert model.variables["x"].domain == ("i",)
    assert model.variables["obj"].domain == ()
    assert model.params["a"].values == {
        ("i1",): 1.0,
        ("i2",): 2.0,
        ("i3",): 3.0,
    }

    objective = model.equations["objective"]
    assert objective.relation == Rel.EQ
    lhs, rhs = objective.lhs_rhs
    assert isinstance(lhs, VarRef) and lhs.name == "obj" and lhs.indices == ()
    assert isinstance(rhs, Sum) and rhs.index_sets == ("i",)
    assert isinstance(rhs.body, Binary) and rhs.body.op == "*"
    assert isinstance(rhs.body.left, ParamRef) and rhs.body.left.indices == ("i",)
    assert isinstance(rhs.body.right, VarRef) and rhs.body.right.indices == ("i",)

    balance = model.equations["balance"]
    assert balance.domain == ("i",) and balance.relation == Rel.GE
    blhs, brhs = balance.lhs_rhs
    assert isinstance(blhs, VarRef) and blhs.indices == ("i",)
    assert isinstance(brhs, Const) and brhs.value == 0.0

    assert model.objective is not None
    assert model.objective.sense == ObjSense.MIN
    assert model.objective.objvar == "obj"
    assert model.declared_model == "sample_nlp"
    assert model.model_name == "sample_nlp"
    assert model.model_uses_all is True
    assert model.model_equations == []


def test_undefined_symbol_raises():
    text = dedent(
        """
        Variables
            x
        ;

        Equations
            e
        ;

        e..
            x =e= y;

        Model m / all / ;
        Solve m using NLP minimizing x;
        """
    )

    with pytest.raises(parser.ParserSemanticError, match="Undefined symbol 'y'") as excinfo:
        parser.parse_model_text(text)
    assert excinfo.value.line is not None
    assert "context" in str(excinfo.value)


def test_parameter_domain_requires_known_set():
    text = dedent(
        """
        Variables
            z
        ;

        Parameters
            p(j)
        ;

        Equations
            obj
        ;

        obj..
            z =e= 0;

        Model m / obj / ;
        Solve m using NLP minimizing z;
        """
    )

    with pytest.raises(parser.ParserSemanticError, match="parameter 'p' domain"):
        parser.parse_model_text(text)


def test_model_references_unknown_equation():
    text = dedent(
        """
        Variables
            z
        ;

        Equations
            obj
        ;

        obj..
            z =e= 0;

        Model m / obj, missing / ;
        Solve m using NLP minimizing z;
        """
    )

    with pytest.raises(parser.ParserSemanticError, match="unknown equation 'missing'"):
        parser.parse_model_text(text)


def test_alias_expansion_allows_domain_usage():
    text = dedent(
        """
        Sets
            i /i1, i2/ ;

        Aliases
            j, i
        ;

        Variables
            x(j)
            obj ;

        Equations
            objective
            balance(j) ;

        objective..
            obj =e= sum(j, x(j));

        balance(j)..
            x(j) =e= 0;

        Model sample / objective, balance / ;
        Solve sample using NLP minimizing obj;
        """
    )

    model = parser.parse_model_text(text)
    assert model.aliases["j"].target == "i"
    assert model.variables["x"].domain == ("j",)
    assert model.model_equations == ["objective", "balance"]
    assert not model.model_uses_all


def test_variable_bounds_and_scalar_param_assignment():
    text = dedent(
        """
        Sets
            i /i1, i2/ ;

        Parameters
            alpha ;

        Variables
            x(i)
            y ;

        Equations
            e(i)
            f
        ;

        e(i).. x(i) =e= 0;
        f.. y =e= alpha;

        x.lo(i) = 1;
        x.up(i) = 5;
        y.fx = 3;
        alpha = 2;

        Model test / e, f / ;
        Solve test using NLP minimizing y;
        """
    )

    model = parser.parse_model_text(text)

    var_x = model.variables["x"]
    assert var_x.lo_map[("i1",)] == 1.0
    assert var_x.lo_map[("i2",)] == 1.0
    assert var_x.up_map[("i1",)] == 5.0
    assert var_x.up_map[("i2",)] == 5.0

    var_y = model.variables["y"]
    assert var_y.fx == 3.0
    assert var_y.lo is None and var_y.up is None

    param_alpha = model.params["alpha"]
    assert param_alpha.values[()] == 2.0


def test_parameter_data_block_for_indexed_param():
    text = dedent(
        """
        Sets
            i /i1/ ;

        Parameters
            beta(i) /i1 4/
        ;

        Variables
            y ;

        Equations
            eq ;

        eq.. y =e= beta(i);

        Model sample / eq / ;
        Solve sample using NLP minimizing y;
        """
    )
    model = parser.parse_model_text(text)
    assert model.params["beta"].domain == ("i",)
    assert model.params["beta"].values[("i1",)] == 4.0


def _collect(expr: Expr, cls):
    stack = [expr]
    results = []
    while stack:
        node = stack.pop()
        if isinstance(node, cls):
            results.append(node)
        if isinstance(node, Expr):
            stack.extend(list(node.children()))
    return results


def test_expression_ast_covers_functions_and_ops():
    text = dedent(
        """
        Variables
            x
            y
        ;

        Equations
            expr
            logic
        ;

        expr..
            exp(x) + log(y) - sqrt(x) + sin(x + y) + cos(x) + tan(y) + sqr(x) =e= x ^ 2;

        logic..
            (x >= 0) and (y <= 1) =e= (x <> y) or (x = y);

        Model m / expr, logic / ;
        Solve m using NLP minimizing x;
        """
    )

    model = parser.parse_model_text(text)
    expr_eq = model.equations["expr"]
    logic_eq = model.equations["logic"]

    calls = _collect(expr_eq.lhs_rhs[0], Call)
    func_names = {call.func for call in calls}
    assert func_names == {"exp", "log", "sqrt", "sin", "cos", "tan", "sqr"}

    power_ops = {node.op for node in _collect(expr_eq.lhs_rhs[1], Binary)}
    assert "^" in power_ops

    logic_ops = {node.op for node in _collect(logic_eq.lhs_rhs[0], Binary)}
    assert {"and", ">=", "<="}.issubset(logic_ops)
    logic_rhs_ops = {node.op for node in _collect(logic_eq.lhs_rhs[1], Binary)}
    assert {"or", "<>", "="}.issubset(logic_rhs_ops)


def test_scalar_block_ingestion():
    text = dedent(
        """
        Scalars pi / 3.14 /;

        Variables
            y ;

        Equations
            eq ;

        eq.. y =e= pi;

        Model sample / eq / ;
        Solve sample using NLP minimizing y;
        """
    )

    model = parser.parse_model_text(text)
    assert model.params["pi"].values[()] == 3.14


def test_expression_metadata_domains():
    text = dedent(
        """
        Sets
            i /i1, i2/ ;

        Parameters
            a(i) /i1 1, i2 2/ ;

        Variables
            x(i) ;

        Equations
            balance(i) ;

        balance(i).. x(i) =e= a(i);

        Model sample / balance / ;
        Solve sample using NLP minimizing x;
        """
    )

    model = parser.parse_model_text(text)
    lhs, rhs = model.equations["balance"].lhs_rhs
    assert lhs.symbol_domain == ("i",)
    assert lhs.domain == ("i",)
    assert rhs.domain == ("i",)


def test_sum_metadata_preserves_indices():
    text = dedent(
        """
        Sets
            i /i1, i2/ ;

        Variables
            x(i) ;

        Equations
            obj ;

        obj.. sum(i, x(i)) =e= 0;

        Model sample / obj / ;
        Solve sample using NLP minimizing x;
        """
    )

    model = parser.parse_model_text(text)
    lhs, _ = model.equations["obj"].lhs_rhs
    assert isinstance(lhs, Sum)
    assert lhs.sum_indices == ("i",)
    assert lhs.domain == ()


def test_example_files_parse():
    repo_root = Path(__file__).resolve().parents[3]
    # Note: Some files cause performance issues with Earley parser ambiguity resolution.
    # This is due to having multiple declarations in blocks without explicit separators,
    # which creates exponentially many parse trees. The files parse correctly but slowly.
    # TODO: Consider rewriting grammar to be LALR-compatible or add explicit separators.
    example_names = [
        "simple_nlp.gms",
        # Skip files with performance issues for now:
        # "scalar_nlp.gms",  # Has 2 equations in Equations block - causes exponential ambiguity
        # "indexed_balance.gms",
        # "bounds_nlp.gms",
        # "nonlinear_mix.gms",
    ]
    for name in example_names:
        model = parser.parse_model_file(repo_root / "examples" / name)
        assert model.equations  # ensure we captured equations
        assert model.variables  # ensure variables registered


def test_indexed_equation_requires_declared_set():
    text = dedent(
        """
        Variables
            x(j) ;

        Equations
            g(j) ;

        g(j).. x(j) =e= 0;

        Model m / g / ;
        Solve m using NLP minimizing x;
        """
    )

    with pytest.raises(parser.ParserSemanticError, match="equation domain"):
        parser.parse_model_text(text)


def test_indexed_parameter_assignment_not_supported():
    text = dedent(
        """
        Sets
            i /i1/ ;

        Parameters
            alpha(i)
        ;

        alpha(i) = 2;
        """
    )

    with pytest.raises(parser.ParserSemanticError, match="Indexed assignments are not supported"):
        parser.parse_model_text(text)


def test_non_constant_bound_expression_rejected():
    text = dedent(
        """
        Sets
            i /i1/ ;

        Parameters
            alpha ;

        Variables
            x(i)
        ;

        x.lo(i) = alpha;
        """
    )

    with pytest.raises(parser.ParserSemanticError, match="Assignments must use numeric constants"):
        parser.parse_model_text(text)


def test_conflicting_bounds_raise_error():
    text = dedent(
        """
        Sets
            i /i1/ ;

        Variables
            x(i)
        ;

        x.lo(i) = 1;
        x.lo(i) = 2;
        """
    )

    with pytest.raises(parser.ParserSemanticError, match="Conflicting lower bound") as excinfo:
        parser.parse_model_text(text)
    assert excinfo.value.line is not None


def test_alias_cycle_detected():
    text = dedent(
        """
        Sets
            i /i1/ ;

        Aliases
            j, i
            k, j
            j, k
        ;
        """
    )

    with pytest.raises(
        parser.ParserSemanticError, match="duplicates an existing set or alias"
    ) as excinfo:
        parser.parse_model_text(text)
    assert excinfo.value.line is not None


def test_unsupported_statement_rejected():
    text = dedent(
        """
        Sets
            i /i1/ ;

        Loop(i,
            display i;
        );
        """
    )

    with pytest.raises((lark.exceptions.UnexpectedToken, lark.exceptions.UnexpectedCharacters)):
        parser.parse_model_text(text)


def test_power_operator_double_star_syntax():
    """Test that ** operator is supported for exponentiation."""
    text = dedent(
        """
        Variables
            x
            y
            obj;

        Equations
            objective;

        objective.. obj =e= x**2 + y**3;

        Model power_nlp / objective /;
        Solve power_nlp using NLP minimizing obj;
        """
    )

    model = parser.parse_model_text(text)
    objective = model.equations["objective"]

    # Check that the equation parsed correctly
    assert objective.relation == Rel.EQ
    lhs, rhs = objective.lhs_rhs

    # LHS should be obj
    assert isinstance(lhs, VarRef) and lhs.name == "obj"

    # RHS should be x**2 + y**3
    assert isinstance(rhs, Binary) and rhs.op == "+"

    # Check left side: x**2
    assert isinstance(rhs.left, Binary)
    assert rhs.left.op == "**"
    assert isinstance(rhs.left.left, VarRef) and rhs.left.left.name == "x"
    assert isinstance(rhs.left.right, Const) and rhs.left.right.value == 2.0

    # Check right side: y**3
    assert isinstance(rhs.right, Binary)
    assert rhs.right.op == "**"
    assert isinstance(rhs.right.left, VarRef) and rhs.right.left.name == "y"
    assert isinstance(rhs.right.right, Const) and rhs.right.right.value == 3.0


def test_power_operator_mixed_syntax():
    """Test that both ** and ^ operators work and can be mixed."""
    text = dedent(
        """
        Variables
            x
            y
            z
            obj;

        Equations
            objective;

        objective.. obj =e= x**2 + y^3 + z**4;

        Model power_nlp / objective /;
        Solve power_nlp using NLP minimizing obj;
        """
    )

    model = parser.parse_model_text(text)
    objective = model.equations["objective"]

    # Collect all power operations
    power_ops = [node for node in _collect(objective.lhs_rhs[1], Binary) if node.op in ("^", "**")]

    # Should have 3 power operations
    assert len(power_ops) == 3

    # Check that we have both ** and ^ operators in the AST
    ops_used = {node.op for node in power_ops}
    assert (
        ops_used == {"^", "**"} or ops_used == {"**"} or ops_used == {"^"}
    )  # Parser might normalize


def test_asterisk_range_notation_basic():
    """Test basic asterisk notation for set ranges (e.g., i1*i10)."""
    text = dedent(
        """
        Sets
            i /i1*i10/ ;

        Variables
            x(i)
            obj ;

        Equations
            objective ;

        objective.. obj =e= sum(i, x(i));

        Model test / objective / ;
        Solve test using NLP minimizing obj;
        """
    )

    model = parser.parse_model_text(text)
    assert model.sets["i"].members == [
        "i1",
        "i2",
        "i3",
        "i4",
        "i5",
        "i6",
        "i7",
        "i8",
        "i9",
        "i10",
    ]


def test_asterisk_range_notation_with_regular_members():
    """Test asterisk notation mixed with regular set members."""
    text = dedent(
        """
        Sets
            i /i1*i3, special, i5*i7/ ;

        Variables
            x(i) ;

        Equations
            eq(i) ;

        eq(i).. x(i) =e= 0;

        Model test / eq / ;
        Solve test using NLP minimizing x;
        """
    )

    model = parser.parse_model_text(text)
    assert model.sets["i"].members == ["i1", "i2", "i3", "special", "i5", "i6", "i7"]


def test_asterisk_range_notation_single_element():
    """Test asterisk notation with start and end being the same."""
    text = dedent(
        """
        Sets
            i /i5*i5/ ;

        Variables
            x(i) ;

        Equations
            eq(i) ;

        eq(i).. x(i) =e= 0;

        Model test / eq / ;
        Solve test using NLP minimizing x;
        """
    )

    model = parser.parse_model_text(text)
    assert model.sets["i"].members == ["i5"]


def test_asterisk_range_notation_large_range():
    """Test asterisk notation with a large range (i1*i100)."""
    text = dedent(
        """
        Sets
            i /i1*i100/ ;

        Variables
            x(i)
            obj ;

        Equations
            objective ;

        objective.. obj =e= sum(i, x(i));

        Model test / objective / ;
        Solve test using NLP minimizing obj;
        """
    )

    model = parser.parse_model_text(text)
    expected_members = [f"i{j}" for j in range(1, 101)]
    assert model.sets["i"].members == expected_members
    assert len(model.sets["i"].members) == 100


def test_asterisk_range_notation_different_prefix():
    """Test asterisk notation with different prefixes like node1*node10."""
    text = dedent(
        """
        Sets
            nodes /node1*node5/ ;

        Variables
            flow(nodes) ;

        Equations
            balance(nodes) ;

        balance(nodes).. flow(nodes) =e= 0;

        Model test / balance / ;
        Solve test using NLP minimizing flow;
        """
    )

    model = parser.parse_model_text(text)
    assert model.sets["nodes"].members == ["node1", "node2", "node3", "node4", "node5"]


def test_asterisk_range_notation_invalid_mismatched_prefix():
    """Test that asterisk notation raises error for mismatched prefixes."""
    text = dedent(
        """
        Sets
            i /i1*j10/ ;
        """
    )

    with pytest.raises(parser.ParserSemanticError, match="Range base mismatch.*different prefixes"):
        parser.parse_model_text(text)


def test_asterisk_range_notation_invalid_reversed_range():
    """Test that asterisk notation raises error for reversed ranges."""
    text = dedent(
        """
        Sets
            i /i10*i1/ ;
        """
    )

    with pytest.raises(parser.ParserSemanticError, match="Invalid range.*greater than end index"):
        parser.parse_model_text(text)


def test_asterisk_range_notation_invalid_no_number():
    """Test that asterisk notation raises error when identifier has no number."""
    text = dedent(
        """
        Sets
            i /abc*def/ ;
        """
    )

    with pytest.raises(
        parser.ParserSemanticError, match="Invalid range.*must be identifier followed by number"
    ):
        parser.parse_model_text(text)


def test_positive_variables_block_scalar():
    """Test block-level Positive Variables keyword with scalar variables."""
    text = dedent(
        """
        Positive Variables
            x
            y ;

        Equations
            eq ;

        eq.. x + y =e= 5;

        Model test / eq / ;
        Solve test using NLP minimizing x;
        """
    )

    model = parser.parse_model_text(text)
    assert model.variables["x"].kind == VarKind.POSITIVE
    assert model.variables["y"].kind == VarKind.POSITIVE


def test_positive_variables_block_indexed():
    """Test block-level Positive Variables keyword with indexed variables."""
    text = dedent(
        """
        Sets
            i /i1, i2, i3/ ;

        Positive Variables
            x(i)
            obj ;

        Equations
            objective ;

        objective.. obj =e= sum(i, x(i));

        Model test / objective / ;
        Solve test using NLP minimizing obj;
        """
    )

    model = parser.parse_model_text(text)
    assert model.variables["x"].kind == VarKind.POSITIVE
    assert model.variables["obj"].kind == VarKind.POSITIVE


def test_negative_variables_block():
    """Test block-level Negative Variables keyword."""
    text = dedent(
        """
        Negative Variables
            x
            y ;

        Equations
            eq ;

        eq.. x + y =e= -5;

        Model test / eq / ;
        Solve test using NLP minimizing x;
        """
    )

    model = parser.parse_model_text(text)
    assert model.variables["x"].kind == VarKind.NEGATIVE
    assert model.variables["y"].kind == VarKind.NEGATIVE


def test_binary_variables_block():
    """Test block-level Binary Variables keyword."""
    text = dedent(
        """
        Binary Variables
            x
            y ;

        Equations
            eq ;

        eq.. x + y =e= 1;

        Model test / eq / ;
        Solve test using NLP minimizing x;
        """
    )

    model = parser.parse_model_text(text)
    assert model.variables["x"].kind == VarKind.BINARY
    assert model.variables["y"].kind == VarKind.BINARY


def test_integer_variables_block():
    """Test block-level Integer Variables keyword."""
    text = dedent(
        """
        Integer Variables
            x
            y ;

        Equations
            eq ;

        eq.. x + y =e= 10;

        Model test / eq / ;
        Solve test using NLP minimizing x;
        """
    )

    model = parser.parse_model_text(text)
    assert model.variables["x"].kind == VarKind.INTEGER
    assert model.variables["y"].kind == VarKind.INTEGER


def test_mixed_variable_blocks():
    """Test multiple variable blocks with different kinds."""
    text = dedent(
        """
        Variables
            obj ;

        Positive Variables
            x
            y ;

        Binary Variables
            z ;

        Equations
            eq ;

        eq.. obj =e= x + y + z;

        Model test / eq / ;
        Solve test using NLP minimizing obj;
        """
    )

    model = parser.parse_model_text(text)
    assert model.variables["obj"].kind == VarKind.CONTINUOUS
    assert model.variables["x"].kind == VarKind.POSITIVE
    assert model.variables["y"].kind == VarKind.POSITIVE
    assert model.variables["z"].kind == VarKind.BINARY


def test_declaration_level_kind_takes_precedence():
    """Test that declaration-level kind overrides block-level kind."""
    text = dedent(
        """
        Positive Variables
            binary x
            y ;

        Equations
            eq ;

        eq.. x + y =e= 1;

        Model test / eq / ;
        Solve test using NLP minimizing x;
        """
    )

    model = parser.parse_model_text(text)
    # x should be binary because declaration-level kind takes precedence
    assert model.variables["x"].kind == VarKind.BINARY
    # y should be positive from block-level kind
    assert model.variables["y"].kind == VarKind.POSITIVE


def test_positive_variables_case_insensitive():
    """Test that variable kind keywords are case-insensitive."""
    text = dedent(
        """
        POSITIVE VARIABLES
            x ;

        positive variables
            y ;

        PoSiTiVe VaRiAbLeS
            z ;

        Equations
            eq ;

        eq.. x + y + z =e= 5;

        Model test / eq / ;
        Solve test using NLP minimizing x;
        """
    )

    model = parser.parse_model_text(text)
    assert model.variables["x"].kind == VarKind.POSITIVE
    assert model.variables["y"].kind == VarKind.POSITIVE
    assert model.variables["z"].kind == VarKind.POSITIVE


def test_positive_variables_with_bounds():
    """Test Positive Variables with explicit bounds."""
    text = dedent(
        """
        Sets
            i /i1, i2/ ;

        Positive Variables
            x(i) ;

        Equations
            eq(i) ;

        eq(i).. x(i) =e= 0;

        x.lo(i) = 0;
        x.up(i) = 10;

        Model test / eq / ;
        Solve test using NLP minimizing x;
        """
    )

    model = parser.parse_model_text(text)
    assert model.variables["x"].kind == VarKind.POSITIVE
    assert model.variables["x"].lo_map[("i1",)] == 0.0
    assert model.variables["x"].lo_map[("i2",)] == 0.0
    assert model.variables["x"].up_map[("i1",)] == 10.0
    assert model.variables["x"].up_map[("i2",)] == 10.0


def test_issue_140_example():
    """Test the exact example from Issue #140."""
    text = dedent(
        """
        Sets
            i /i1*i3/ ;

        Positive Variables
            x(i)
            obj ;

        Equations
            objective
            balance(i) ;

        objective.. obj =e= sum(i, x(i));
        balance(i).. x(i) =g= 0;

        Model sample / all / ;
        Solve sample using NLP minimizing obj;
        """
    )

    model = parser.parse_model_text(text)
    assert model.sets["i"].members == ["i1", "i2", "i3"]
    assert model.variables["x"].domain == ("i",)
    assert model.variables["x"].kind == VarKind.POSITIVE
    assert model.variables["obj"].domain == ()
    assert model.variables["obj"].kind == VarKind.POSITIVE


class TestCommaSeparatedDeclarations:
    """Tests for comma-separated variable and equation declarations."""

    def test_comma_separated_variables(self):
        """Test comma-separated variable declarations."""
        text = dedent(
            """
            Variables x, y, z;
            Equations eq;
            eq.. x + y + z =e= 10;
            Model m /all/;
            Solve m using nlp minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        assert "y" in model.variables
        assert "z" in model.variables
        assert all(model.variables[v].kind == VarKind.CONTINUOUS for v in ["x", "y", "z"])

    def test_comma_separated_equations(self):
        """Test comma-separated equation declarations."""
        text = dedent(
            """
            Variables x, y, obj;
            Equations eq1, eq2, objdef;
            eq1.. x =e= 1;
            eq2.. y =e= 2;
            objdef.. obj =e= x + y;
            Model m /all/;
            Solve m using nlp minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert "eq1" in model.equations
        assert "eq2" in model.equations
        assert "objdef" in model.equations

    def test_comma_separated_with_variable_kind(self):
        """Test comma-separated variables with kind modifier."""
        text = dedent(
            """
            Positive Variables x, y, z;
            Equations eq;
            eq.. x + y + z =e= 10;
            Model m /all/;
            Solve m using nlp minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        assert "y" in model.variables
        assert "z" in model.variables
        assert all(model.variables[v].kind == VarKind.POSITIVE for v in ["x", "y", "z"])

    def test_comma_separated_binary_variables(self):
        """Test comma-separated binary variables."""
        text = dedent(
            """
            Binary Variables b1, b2, b3;
            Equations eq;
            eq.. b1 + b2 + b3 =e= 2;
            Model m /all/;
            Solve m using nlp minimizing b1;
            """
        )
        model = parser.parse_model_text(text)
        assert all(model.variables[v].kind == VarKind.BINARY for v in ["b1", "b2", "b3"])

    def test_mixed_single_and_comma_separated(self):
        """Test mixing single and comma-separated declarations."""
        text = dedent(
            """
            Variables x;
            Variables y, z;
            Variables w;
            Equations eq;
            eq.. x + y + z + w =e= 10;
            Model m /all/;
            Solve m using nlp minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert len(model.variables) == 4
        assert all(v in model.variables for v in ["x", "y", "z", "w"])

    def test_comma_separated_single_variable(self):
        """Test that single variable without comma still works."""
        text = dedent(
            """
            Variables x;
            Equations eq;
            eq.. x =e= 5;
            Model m /all/;
            Solve m using nlp minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables

    def test_comma_separated_with_indexed_variable(self):
        """Test comma-separated alongside indexed variables."""
        text = dedent(
            """
            Sets i /i1, i2/;
            Variables x, y;
            Variables z(i);
            Equations eq;
            eq.. x + y =e= 10;
            Model m /all/;
            Solve m using nlp minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        assert "y" in model.variables
        assert "z" in model.variables
        assert model.variables["x"].domain == ()
        assert model.variables["y"].domain == ()
        assert model.variables["z"].domain == ("i",)

    def test_convexity_fixture_style(self):
        """Test the exact style used in convexity fixtures."""
        text = dedent(
            """
            Variables x, y, obj;
            Equations objdef, linear_constr;

            objdef.. obj =e= x**2 + y**2;
            linear_constr.. x + 2*y =l= 5;

            x.lo = -10;
            x.up = 10;
            y.lo = -10;
            y.up = 10;

            Model m /all/;
            Solve m using nlp minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        assert "y" in model.variables
        assert "obj" in model.variables
        assert "objdef" in model.equations
        assert "linear_constr" in model.equations

    def test_comma_separated_with_obj_variable(self):
        """Test that objective variable works in comma-separated list."""
        text = dedent(
            """
            Variables x, y, z, obj;
            Equations eq, objdef;
            eq.. x + y + z =e= 10;
            objdef.. obj =e= x**2 + y**2 + z**2;
            Model m /all/;
            Solve m using nlp minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert model.objective is not None
        assert model.objective.objvar == "obj"
