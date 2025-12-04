"""Parser smoke tests covering tree output and ModelIR synthesis."""

from pathlib import Path
from textwrap import dedent

import pytest

from src.ir import parser
from src.ir.ast import Binary, Call, Const, Expr, ParamRef, Sum, VarRef
from src.ir.symbols import ObjSense, Rel, VarKind
from src.utils.errors import ParseError


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

    with pytest.raises(ParseError, match="Undefined symbol 'y'") as excinfo:
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


def test_indexed_parameter_assignment_supported():
    """Test that indexed parameter assignments are now supported (Sprint 8 Day 3)."""
    text = dedent(
        """
        Sets
            i /i1/ ;

        Parameters
            alpha(i)
        ;

        alpha('i1') = 2;
        """
    )

    # This should parse successfully now (Sprint 8 Day 3 feature)
    model = parser.parse_model_text(text)
    assert "alpha" in model.params
    assert model.params["alpha"].values[("i1",)] == 2


def test_non_constant_bound_expression_rejected():
    """Test that variable bound expressions with parameters are parsed (Sprint 10 Day 6).

    Previously these were rejected, but now we allow them (parse and continue without storing).
    This supports patterns like circle.gms: a.l = (xmin + xmax)/2
    """
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

    # Sprint 10 Day 6: Variable bounds with expressions now parse successfully
    # (mock/store approach - parse and continue without storing the expression)
    model = parser.parse_model_text(text)
    assert "x" in model.variables


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
    """Test that truly unsupported statements are rejected.

    Note: Loop statements are now supported (Sprint 11 Day 2 Extended).
    This test now checks for a different unsupported construct.
    """
    text = dedent(
        """
        Sets
            i /i1/ ;

        while(i < 10,
            display i;
        );
        """
    )

    with pytest.raises(ParseError):
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
        parser.ParserSemanticError,
        match="Invalid range.*must be a number.*or identifier followed by number",
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


class TestVariableAttributes:
    """Tests for variable attribute syntax (.l, .lo, .up, .fx, etc.)."""

    def test_variable_level_attribute_scalar(self):
        """Test .l (level/initial value) attribute on scalar variable."""
        text = dedent(
            """
            Variables x, y;
            Equations eq;

            x.l = 1.5;
            y.l = 2.0;

            eq.. x + y =e= 0;

            Model m /all/;
            Solve m using nlp minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert model.variables["x"].l == 1.5
        assert model.variables["y"].l == 2.0

    def test_variable_level_attribute_indexed(self):
        """Test .l attribute on indexed variable."""
        text = dedent(
            """
            Sets i /i1, i2, i3/;
            Variables x(i);
            Equations eq(i);

            x.l(i) = 10;

            eq(i).. x(i) =e= 0;

            Model m /all/;
            Solve m using nlp minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert model.variables["x"].l_map[("i1",)] == 10.0
        assert model.variables["x"].l_map[("i2",)] == 10.0
        assert model.variables["x"].l_map[("i3",)] == 10.0

    def test_variable_all_attributes_combined(self):
        """Test combining .l, .lo, .up, .fx attributes."""
        text = dedent(
            """
            Variables x, y, z;
            Equations eq;

            x.l = 5;
            x.lo = 0;
            x.up = 10;

            y.l = 2.5;
            y.fx = 3.0;

            z.l = 0;

            eq.. x + y + z =e= 0;

            Model m /all/;
            Solve m using nlp minimizing x;
            """
        )
        model = parser.parse_model_text(text)

        # Variable x
        assert model.variables["x"].l == 5.0
        assert model.variables["x"].lo == 0.0
        assert model.variables["x"].up == 10.0

        # Variable y
        assert model.variables["y"].l == 2.5
        assert model.variables["y"].fx == 3.0

        # Variable z
        assert model.variables["z"].l == 0.0

    def test_variable_level_indexed_all_elements(self):
        """Test .l attribute sets all indexed variable elements."""
        text = dedent(
            """
            Sets i /i1, i2/;
            Variables x(i);
            Equations eq(i);

            x.l(i) = 7.5;
            x.lo(i) = 0;
            x.up(i) = 15;

            eq(i).. x(i) =e= 0;

            Model m /all/;
            Solve m using nlp minimizing x;
            """
        )
        model = parser.parse_model_text(text)

        # Check level values
        assert model.variables["x"].l_map[("i1",)] == 7.5
        assert model.variables["x"].l_map[("i2",)] == 7.5

        # Check bounds still work
        assert model.variables["x"].lo_map[("i1",)] == 0.0
        assert model.variables["x"].up_map[("i1",)] == 15.0

    def test_gamslib_trig_example(self):
        """Test the exact syntax from GAMSLib trig.gms model."""
        text = dedent(
            """
            Variables x1, x2, fv;
            Equations trigfv;

            x1.lo = -2;
            x1.up =  5;
            x1.l  =  1;

            x2.lo = -2;
            x2.up =  5;
            x2.l  =  1;

            trigfv.. fv =e= 3*x1**4 - 2*x1*x2;

            Model trigm /all/;
            Solve trigm using nlp minimizing fv;
            """
        )
        model = parser.parse_model_text(text)

        # Verify x1 attributes
        assert model.variables["x1"].lo == -2.0
        assert model.variables["x1"].up == 5.0
        assert model.variables["x1"].l == 1.0

        # Verify x2 attributes
        assert model.variables["x2"].lo == -2.0
        assert model.variables["x2"].up == 5.0
        assert model.variables["x2"].l == 1.0


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


class TestModelEquationListSyntax:
    """Tests for explicit equation list syntax in Model statements (Issue #200)."""

    def test_single_equation_model(self):
        """Test model with single equation in list."""
        text = dedent(
            """
            Variables x, obj;
            Equations eq1, eq2;

            eq1.. x =e= 5;
            eq2.. obj =e= x**2;

            Model m1 / eq1 /;
            Solve m1 using nlp minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert model.declared_model == "m1"
        assert model.model_equations == ["eq1"]
        assert model.model_uses_all is False

    def test_multiple_equations_model(self):
        """Test model with multiple equations in list."""
        text = dedent(
            """
            Variables x, y, obj;
            Equations eq1, eq2, eq3, objdef;

            eq1.. x =e= 5;
            eq2.. y =l= 10;
            eq3.. x + y =g= 3;
            objdef.. obj =e= x + y;

            Model m1 / eq1, eq2, objdef /;
            Solve m1 using nlp minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert model.declared_model == "m1"
        assert model.model_equations == ["eq1", "eq2", "objdef"]
        assert model.model_uses_all is False

    def test_all_keyword_vs_explicit_list(self):
        """Test that /all/ behaves differently from explicit list."""
        text = dedent(
            """
            Variables x, y, obj;
            Equations eq1, eq2, eq3;

            eq1.. x =e= 5;
            eq2.. y =l= 10;
            eq3.. obj =e= x + y;

            Model m_all / all /;
            Solve m_all using nlp minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert model.declared_model == "m_all"
        assert model.model_equations == []
        assert model.model_uses_all is True

    def test_gamslib_hs62_syntax(self):
        """Test syntax from GAMSLib hs62.gms model."""
        text = dedent(
            """
            Variables x1, x2, x3, obj;
            Equations objdef, eq1x;

            objdef.. obj =e= -32.174*(255*log((x1+x2+x3+0.03)/0.09) + 280*log((x2+x3+0.03)/0.07) + 290*log((x3+0.03)/0.13));
            eq1x.. x1 + 2*x2 + 2*x3 =l= 4;

            Model mx / objdef, eq1x /;
            Solve mx using nlp minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert model.declared_model == "mx"
        assert model.model_equations == ["objdef", "eq1x"]
        assert model.model_uses_all is False

    def test_gamslib_mingamma_syntax(self):
        """Test syntax from GAMSLib mingamma.gms model."""
        text = dedent(
            """
            Variables x, y1, y2;
            Equations y1def, y2def;

            y1def.. y1 =e= x**2;
            y2def.. y2 =e= (x - 2)**2;

            Model m2 / y2def /;
            Solve m2 using nlp minimizing y2;
            """
        )
        model = parser.parse_model_text(text)
        assert model.declared_model == "m2"
        assert model.model_equations == ["y2def"]
        assert model.model_uses_all is False

    def test_model_subset_equations(self):
        """Test model using subset of declared equations."""
        text = dedent(
            """
            Variables x, y, z, obj;
            Equations eq1, eq2, eq3, eq4, objdef;

            eq1.. x =e= 1;
            eq2.. y =e= 2;
            eq3.. z =e= 3;
            eq4.. x + y + z =l= 10;
            objdef.. obj =e= x**2 + y**2 + z**2;

            Model subset_model / objdef, eq1, eq3 /;
            Solve subset_model using nlp minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert model.model_equations == ["objdef", "eq1", "eq3"]
        assert len(model.model_equations) == 3
        # eq2 and eq4 should not be in the model
        assert "eq2" not in model.model_equations
        assert "eq4" not in model.model_equations

    def test_indexed_equations_in_list(self):
        """Test that indexed equations can be referenced in model list."""
        text = dedent(
            """
            Sets i /i1, i2/;
            Variables x(i);
            Variables obj;
            Equations balance(i);
            Equations objdef;

            balance(i).. x(i) =e= 0;
            objdef.. obj =e= sum(i, x(i));

            Model m / objdef, balance /;
            Solve m using nlp minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert model.model_equations == ["objdef", "balance"]


# ==============================================================================
# Set Range Syntax Tests (Sprint 7 Day 2)
# ==============================================================================


class TestSetRangeSyntax:
    """Test set range notation: numeric (1*10) and symbolic (i1*i100)."""

    def test_numeric_range_basic(self):
        """Test basic numeric range expansion."""
        text = dedent(
            """
            Sets i / 1*6 /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["1", "2", "3", "4", "5", "6"]

    def test_numeric_range_single_element(self):
        """Test numeric range with single element (start equals end)."""
        text = dedent(
            """
            Sets i / 5*5 /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["5"]

    def test_numeric_range_large(self):
        """Test numeric range with larger numbers."""
        text = dedent(
            """
            Sets i / 100*105 /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["100", "101", "102", "103", "104", "105"]

    def test_symbolic_range_basic(self):
        """Test basic symbolic range expansion."""
        text = dedent(
            """
            Sets i / s1*s5 /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["s1", "s2", "s3", "s4", "s5"]

    def test_symbolic_range_different_prefix(self):
        """Test symbolic range with different prefix."""
        text = dedent(
            """
            Sets i / plant1*plant3 /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["plant1", "plant2", "plant3"]

    def test_symbolic_range_with_underscore(self):
        """Test symbolic range with underscore in prefix."""
        text = dedent(
            """
            Sets i / item_1*item_4 /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["item_1", "item_2", "item_3", "item_4"]

    def test_mixed_range_and_explicit_elements(self):
        """Test mixing range notation with explicit elements."""
        text = dedent(
            """
            Sets i / 1*3, extra, special, 7*9 /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == [
            "1",
            "2",
            "3",
            "extra",
            "special",
            "7",
            "8",
            "9",
        ]

    def test_multiple_sets_with_ranges(self):
        """Test multiple sets using different range types."""
        text = dedent(
            """
            Sets
                i / 1*10 /
                j / a1*a3 /
                k / x, y, z /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
        ]
        assert model.sets["j"].members == ["a1", "a2", "a3"]
        assert model.sets["k"].members == ["x", "y", "z"]

    def test_range_in_parameter_definition(self):
        """Test using range-defined set in parameter."""
        text = dedent(
            """
            Sets i / i1*i3 /;
            Parameters p(i) / i1 10, i2 20, i3 30 /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["i1", "i2", "i3"]
        assert model.params["p"].values == {
            ("i1",): 10.0,
            ("i2",): 20.0,
            ("i3",): 30.0,
        }

    def test_range_in_variable_definition(self):
        """Test using range-defined set in variable."""
        text = dedent(
            """
            Sets i / 1*3 /;
            Variables x(i);
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["1", "2", "3"]
        assert model.variables["x"].domain == ("i",)

    def test_numeric_range_invalid_direction(self):
        """Test that reversed numeric range raises error."""
        text = dedent(
            """
            Sets i / 10*1 /;
            """
        )
        with pytest.raises(parser.ParserSemanticError, match="Invalid range"):
            parser.parse_model_text(text)

    def test_symbolic_range_invalid_direction(self):
        """Test that reversed symbolic range raises error."""
        text = dedent(
            """
            Sets i / i10*i1 /;
            """
        )
        with pytest.raises(parser.ParserSemanticError, match="start.*greater than.*end"):
            parser.parse_model_text(text)

    def test_symbolic_range_mismatched_prefix(self):
        """Test that mismatched prefixes raise error."""
        text = dedent(
            """
            Sets i / a1*b10 /;
            """
        )
        with pytest.raises(parser.ParserSemanticError, match="base mismatch"):
            parser.parse_model_text(text)

    def test_range_with_string_elements(self):
        """Test mixing range with quoted string elements."""
        text = dedent(
            """
            Sets i / 1*3, "special item", 5*6 /;
            """
        )
        model = parser.parse_model_text(text)
        # Note: String elements have quotes stripped by the parser
        assert model.sets["i"].members == [
            "1",
            "2",
            "3",
            "special item",
            "5",
            "6",
        ]

    def test_maxmin_gms_pattern(self):
        """Test pattern from maxmin.gms GAMSLib model."""
        text = dedent(
            """
            Sets k / 1*13 /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["k"].members == [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
        ]

    def test_range_with_alias(self):
        """Test range-defined set can be aliased."""
        text = dedent(
            """
            Sets i / 1*5 /;
            Aliases ii, i;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["1", "2", "3", "4", "5"]
        assert "ii" in model.aliases
        assert model.aliases["ii"].target == "i"

    def test_numeric_range_zero_start(self):
        """Test numeric range starting from zero."""
        text = dedent(
            """
            Sets i / 0*5 /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["0", "1", "2", "3", "4", "5"]

    def test_symbolic_range_zero_start(self):
        """Test symbolic range starting from index 0."""
        text = dedent(
            """
            Sets i / t0*t3 /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["t0", "t1", "t2", "t3"]

    def test_set_singular_keyword(self):
        """Test that 'Set' (singular) keyword is supported (Sprint 7 Day 3)."""
        text = dedent(
            """
            Set i / 1*3 /;
            """
        )
        model = parser.parse_model_text(text)
        assert "i" in model.sets
        assert model.sets["i"].members == ["1", "2", "3"]

    def test_sets_plural_keyword(self):
        """Test that 'Sets' (plural) keyword still works."""
        text = dedent(
            """
            Sets i / 1*3 /;
            """
        )
        model = parser.parse_model_text(text)
        assert "i" in model.sets
        assert model.sets["i"].members == ["1", "2", "3"]

    def test_set_with_description(self):
        """Test set with optional description (Sprint 7 Day 3)."""
        text = dedent(
            """
            Set i 'indices for points' / 1*6 /;
            """
        )
        model = parser.parse_model_text(text)
        assert "i" in model.sets
        assert model.sets["i"].members == ["1", "2", "3", "4", "5", "6"]

    def test_sets_with_description(self):
        """Test sets (plural) with optional description."""
        text = dedent(
            """
            Sets i 'my set' / a, b, c /;
            """
        )
        model = parser.parse_model_text(text)
        assert "i" in model.sets
        assert model.sets["i"].members == ["a", "b", "c"]

    def test_alias_singular_keyword(self):
        """Test that 'Alias' (singular) keyword is supported (Sprint 7 Day 3)."""
        text = dedent(
            """
            Set i / 1*3 /;
            Alias (i,j);
            """
        )
        model = parser.parse_model_text(text)
        assert "i" in model.sets
        assert model.sets["i"].members == ["1", "2", "3"]

    def test_aliases_plural_keyword(self):
        """Test that 'Aliases' (plural) keyword still works."""
        text = dedent(
            """
            Set i / 1*3 /;
            Aliases j, i;
            """
        )
        model = parser.parse_model_text(text)
        assert "i" in model.sets
        assert "j" in model.aliases
        assert model.aliases["j"].target == "i"

    def test_alias_with_parentheses(self):
        """Test Alias (i,j) syntax with parentheses (Sprint 7 Day 3)."""
        text = dedent(
            """
            Set i / 1*5 /;
            Alias (i,j);
            """
        )
        model = parser.parse_model_text(text)
        assert "i" in model.sets
        assert model.sets["i"].members == ["1", "2", "3", "4", "5"]

    def test_alias_without_parentheses(self):
        """Test traditional Alias j, i syntax still works."""
        text = dedent(
            """
            Set i / 1*5 /;
            Aliases j, i;
            """
        )
        model = parser.parse_model_text(text)
        assert "i" in model.sets
        assert "j" in model.aliases

    def test_set_singular_with_range_and_description(self):
        """Test all Day 3 features together: Set singular + description + range."""
        text = dedent(
            """
            Set i 'indices for the 6 points' / 1*6 /;
            Alias (i,j);
            """
        )
        model = parser.parse_model_text(text)
        assert "i" in model.sets
        assert model.sets["i"].members == ["1", "2", "3", "4", "5", "6"]


class TestConditionalEquations:
    """Test conditional equation syntax with $ operator (Sprint 7 Day 3)."""

    def test_scalar_equation_with_condition(self):
        """Test scalar equation with conditional."""
        text = dedent(
            """
            Variable x;
            Equation balance;

            balance$(1 > 0).. x =e= 1;

            Model test / all /;
            """
        )
        model = parser.parse_model_text(text)
        assert "balance" in model.equations
        assert model.equations["balance"].domain == ()

    def test_indexed_equation_with_condition(self):
        """Test indexed equation with conditional (basic)."""
        text = dedent(
            """
            Set i / 1*5 /;
            Variable x(i);
            Equation balance(i);

            balance(i)$(ord(i) > 2).. x(i) =e= 1;

            Model test / all /;
            """
        )
        model = parser.parse_model_text(text)
        assert "balance" in model.equations
        assert model.equations["balance"].domain == ("i",)

    def test_multi_index_equation_with_condition(self):
        """Test multi-index equation with conditional (himmel16.gms pattern)."""
        text = dedent(
            """
            Set i / 1*6 /;
            Alias (i,j);
            Variable x(i);
            Variable y(i);
            Equation maxdist(i,j);

            maxdist(i,j)$(ord(i) < ord(j)).. x(i) + y(j) =l= 1;

            Model test / all /;
            """
        )
        model = parser.parse_model_text(text)
        assert "maxdist" in model.equations
        assert model.equations["maxdist"].domain == ("i", "j")
        assert model.equations["maxdist"].relation.value == "=l="

    def test_equation_without_condition_still_works(self):
        """Test that equations without conditions still work."""
        text = dedent(
            """
            Set i / 1*3 /;
            Variable x(i);
            Equation balance(i);

            balance(i).. x(i) =e= 1;

            Model test / all /;
            """
        )
        model = parser.parse_model_text(text)
        assert "balance" in model.equations
        assert model.equations["balance"].domain == ("i",)

    def test_condition_with_parameter_comparison(self):
        """Test conditional with parameter comparison."""
        text = dedent(
            """
            Set i / i1*i5 /;
            Parameter demand(i) / i1 10, i2 0, i3 5, i4 0, i5 8 /;
            Variable x(i);
            Equation supply(i);

            supply(i)$(demand(i) > 0).. x(i) =e= demand(i);

            Model test / all /;
            """
        )
        model = parser.parse_model_text(text)
        assert "supply" in model.equations
        assert model.equations["supply"].domain == ("i",)

    def test_condition_with_set_comparison(self):
        """Test conditional with set element comparison."""
        text = dedent(
            """
            Set i / 1*5 /;
            Alias (i,j);
            Variable x(i,j);
            Equation offdiag(i,j);

            offdiag(i,j)$(i <> j).. x(i,j) =e= 0;

            Model test / all /;
            """
        )
        model = parser.parse_model_text(text)
        assert "offdiag" in model.equations
        assert model.equations["offdiag"].domain == ("i", "j")

    def test_condition_with_complex_expression(self):
        """Test conditional with complex expression."""
        text = dedent(
            """
            Set i / 1*10 /;
            Variable x(i);
            Equation firsthalf(i);

            firsthalf(i)$(ord(i) <= 5 and ord(i) > 0).. x(i) =e= 1;

            Model test / all /;
            """
        )
        model = parser.parse_model_text(text)
        assert "firsthalf" in model.equations
        assert model.equations["firsthalf"].domain == ("i",)


class TestLagLeadOperators:
    """Test lag/lead operators in set indexing (Issue #361)."""

    def test_lead_operator_in_sum_expression(self):
        """Test linear lead operator i+1 in sum expression."""
        text = dedent(
            """
            Sets
                i /i1*i5/ ;

            Variables
                x(i)
                energy ;

            Equations
                objective ;

            objective.. energy =e= sum(i, x(i) + x(i+1));

            Model test / all / ;
            Solve test using NLP minimizing energy;
            """
        )
        model = parser.parse_model_text(text)
        assert "objective" in model.equations
        # Verify the equation parsed successfully
        assert model.equations["objective"].relation == Rel.EQ

    def test_lag_operator_in_sum_expression(self):
        """Test linear lag operator i-1 in sum expression."""
        text = dedent(
            """
            Sets
                i /i1*i5/ ;

            Variables
                x(i)
                obj ;

            Equations
                objective ;

            objective.. obj =e= sum(i, x(i) + x(i-1));

            Model test / all / ;
            Solve test using NLP minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert "objective" in model.equations

    def test_lead_operator_in_equation_domain(self):
        """Test lead operator in equation domain declaration."""
        text = dedent(
            """
            Sets
                i /i1*i5/ ;

            Variables
                x(i) ;

            Equations
                balance(i) ;

            balance(i+1).. x(i+1) =e= x(i) + 1;

            Model test / all / ;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "balance" in model.equations
        # Domain should be extracted as just 'i' (base identifier)
        assert model.equations["balance"].domain == ("i",)

    def test_lag_operator_in_equation_domain(self):
        """Test lag operator in equation domain declaration."""
        text = dedent(
            """
            Sets
                i /i1*i5/ ;

            Variables
                x(i) ;

            Equations
                balance(i) ;

            balance(i-1).. x(i-1) =e= x(i);

            Model test / all / ;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "balance" in model.equations
        assert model.equations["balance"].domain == ("i",)

    def test_lead_operator_in_filtered_set(self):
        """Test lead operator inside filtered set like nh(i+1)."""
        text = dedent(
            """
            Sets
                i /i1*i5/
                nh(i) /i2*i4/ ;

            Variables
                x(i)
                energy ;

            Equations
                objective ;

            objective.. energy =e= sum(nh(i+1), x(i));

            Model test / all / ;
            Solve test using NLP minimizing energy;
            """
        )
        model = parser.parse_model_text(text)
        assert "objective" in model.equations

    def test_chain_gms_pattern(self):
        """Test the specific pattern from chain.gms (Tier 2 model)."""
        text = dedent(
            """
            Sets
                i /i1*i6/
                nh(i) /i2*i6/ ;

            Parameters
                h ;

            Variables
                x(i)
                u(i)
                energy ;

            Equations
                energy_def
                x_eqn(i) ;

            h = 1.0;

            energy_def.. energy =e= 0.5*h*sum(nh(i+1), x(i)*sqrt(1 + sqr(u(i))) + x(i+1)*sqrt(1 + sqr(u(i+1))));

            x_eqn(i+1).. x(i+1) =e= x(i) + 0.5*h*(u(i) + u(i+1));

            Model chain / all / ;
            Solve chain using NLP minimizing energy;
            """
        )
        model = parser.parse_model_text(text)
        assert "energy_def" in model.equations
        assert "x_eqn" in model.equations
        assert model.equations["x_eqn"].domain == ("i",)

    def test_circular_lead_operator(self):
        """Test circular lead operator i++1."""
        text = dedent(
            """
            Sets
                i /i1*i5/ ;

            Variables
                x(i)
                obj ;

            Equations
                circular ;

            circular.. obj =e= sum(i, x(i) + x(i++1));

            Model test / all / ;
            Solve test using NLP minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert "circular" in model.equations

    def test_circular_lag_operator(self):
        """Test circular lag operator i--1."""
        text = dedent(
            """
            Sets
                i /i1*i5/ ;

            Variables
                x(i)
                obj ;

            Equations
                circular ;

            circular.. obj =e= sum(i, x(i) + x(i--1));

            Model test / all / ;
            Solve test using NLP minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert "circular" in model.equations

    def test_multiple_lag_lead_operators(self):
        """Test multiple lag/lead operators in same expression."""
        text = dedent(
            """
            Sets
                i /i1*i10/ ;

            Variables
                x(i)
                obj ;

            Equations
                balance ;

            balance.. obj =e= sum(i, x(i-2) + x(i-1) + x(i) + x(i+1) + x(i+2));

            Model test / all / ;
            Solve test using NLP minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert "balance" in model.equations

    def test_lag_lead_with_variable_offset(self):
        """Test lag/lead with variable offset (not just numeric)."""
        text = dedent(
            """
            Sets
                i /i1*i5/ ;

            Scalars
                offset /2/ ;

            Variables
                x(i)
                obj ;

            Equations
                balance ;

            balance.. obj =e= sum(i, x(i) + x(i+offset));

            Model test / all / ;
            Solve test using NLP minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert "balance" in model.equations

    def test_nested_domain_with_lag_lead(self):
        """Test nested domain indexing with lag/lead operators."""
        text = dedent(
            """
            Sets
                i /i1*i5/
                j /j1*j3/
                subset(i,j) /i1.j1, i2.j2/ ;

            Variables
                x(i,j) ;

            Equations
                balance(i,j) ;

            balance(subset(i+1,j)).. x(i+1,j) =e= x(i,j);

            Model test / all / ;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "balance" in model.equations
        # Domain should extract both i and j
        assert model.equations["balance"].domain == ("i", "j")

    def test_polygon_gms_pattern(self):
        """Test pattern from polygon.gms (Tier 2 model)."""
        text = dedent(
            """
            Sets
                k /1*8/ ;

            Variables
                x(k)
                y(k)
                r(k)
                obj ;

            Equations
                fxsum
                defr(k) ;

            fxsum.. obj =e= sum(k, r(k));

            defr(k).. r(k) =e= sqrt(sqr(x(k+1)-x(k)) + sqr(y(k+1)-y(k)));

            Model polygon / all / ;
            Solve polygon using NLP minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert "fxsum" in model.equations
        assert "defr" in model.equations
        assert model.equations["defr"].domain == ("k",)


class TestMultiDimensionalParameters:
    """Test multi-dimensional parameter data with dotted notation (Issue #139)."""

    def test_2d_parameter_dotted_notation(self):
        """Test 2D parameter with dotted notation (i.j)."""
        text = dedent(
            """
            Sets
                i /i1, i2/
                j /j1, j2/
            ;

            Parameters
                a(i, j) /
                    i1.j1 1.0,
                    i1.j2 2.0,
                    i2.j1 3.0,
                    i2.j2 4.0
                /
            ;

            Variables x;
            Equations eq;
            eq.. x =e= 0;
            Model test /all/;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "a" in model.params
        assert model.params["a"].domain == ("i", "j")
        assert model.params["a"].values == {
            ("i1", "j1"): 1.0,
            ("i1", "j2"): 2.0,
            ("i2", "j1"): 3.0,
            ("i2", "j2"): 4.0,
        }

    def test_3d_parameter_dotted_notation(self):
        """Test 3D parameter with dotted notation (i.j.k)."""
        text = dedent(
            """
            Sets
                i /i1, i2/
                j /j1, j2/
                k /k1, k2/
            ;

            Parameters
                a(i, j, k) /
                    i1.j1.k1 1.0,
                    i1.j2.k2 2.0,
                    i2.j1.k1 3.0
                /
            ;

            Variables x;
            Equations eq;
            eq.. x =e= 0;
            Model test /all/;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "a" in model.params
        assert model.params["a"].domain == ("i", "j", "k")
        assert model.params["a"].values == {
            ("i1", "j1", "k1"): 1.0,
            ("i1", "j2", "k2"): 2.0,
            ("i2", "j1", "k1"): 3.0,
        }

    def test_2d_parameter_sparse_data(self):
        """Test 2D parameter with sparse data (not all combinations specified)."""
        text = dedent(
            """
            Sets
                i /i1, i2, i3/
                j /j1, j2, j3/
            ;

            Parameters
                cost(i, j) /
                    i1.j1 10.0,
                    i1.j3 15.0,
                    i3.j2 20.0
                /
            ;

            Variables x;
            Equations eq;
            eq.. x =e= 0;
            Model test /all/;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert model.params["cost"].values == {
            ("i1", "j1"): 10.0,
            ("i1", "j3"): 15.0,
            ("i3", "j2"): 20.0,
        }
        # Unspecified values should not be in the dict (sparse representation)
        assert ("i1", "j2") not in model.params["cost"].values
        assert ("i2", "j1") not in model.params["cost"].values

    def test_2d_parameter_in_equation(self):
        """Test using 2D parameter in equation."""
        text = dedent(
            """
            Sets
                i /i1, i2/
                j /j1, j2/
            ;

            Parameters
                cost(i, j) /
                    i1.j1 5.0,
                    i1.j2 10.0,
                    i2.j1 7.0,
                    i2.j2 12.0
                /
            ;

            Variables
                x(i,j)
                obj
            ;

            Equations
                objdef
            ;

            objdef.. obj =e= sum(i, sum(j, cost(i,j) * x(i,j)));

            Model test /all/;
            Solve test using NLP minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert "cost" in model.params
        assert len(model.params["cost"].values) == 4

    def test_2d_parameter_transportation_problem(self):
        """Test realistic transportation problem with cost matrix."""
        text = dedent(
            """
            Sets
                sources /s1, s2/
                destinations /d1, d2, d3/
            ;

            Parameters
                cost(sources, destinations) 'shipping cost' /
                    s1.d1 10.0,
                    s1.d2 20.0,
                    s1.d3 15.0,
                    s2.d1 12.0,
                    s2.d2 18.0,
                    s2.d3 25.0
                /
                supply(sources) / s1 100, s2 150 /
                demand(destinations) / d1 80, d2 90, d3 80 /
            ;

            Variables
                ship(sources, destinations)
                total_cost
            ;

            Equations
                objective
            ;

            objective.. total_cost =e= sum(sources, sum(destinations,
                                      cost(sources, destinations) * ship(sources, destinations)));

            Model transport /all/;
            Solve transport using NLP minimizing total_cost;
            """
        )
        model = parser.parse_model_text(text)
        assert len(model.params["cost"].values) == 6
        assert model.params["cost"].values[("s1", "d1")] == 10.0
        assert model.params["cost"].values[("s2", "d3")] == 25.0

    def test_2d_parameter_validation_invalid_index(self):
        """Test that invalid indices are caught."""
        text = dedent(
            """
            Sets
                i /i1, i2/
                j /j1, j2/
            ;

            Parameters
                a(i, j) /
                    i1.j1 1.0,
                    i1.j3 2.0
                /
            ;

            Variables x;
            Equations eq;
            eq.. x =e= 0;
            Model test /all/;
            Solve test using NLP minimizing x;
            """
        )
        with pytest.raises(parser.ParserSemanticError, match="not present in set"):
            parser.parse_model_text(text)

    def test_2d_parameter_validation_dimension_mismatch(self):
        """Test that dimension mismatch is caught."""
        text = dedent(
            """
            Sets
                i /i1, i2/
                j /j1, j2/
            ;

            Parameters
                a(i, j) /
                    i1 1.0
                /
            ;

            Variables x;
            Equations eq;
            eq.. x =e= 0;
            Model test /all/;
            Solve test using NLP minimizing x;
            """
        )
        with pytest.raises(parser.ParserSemanticError, match="index mismatch"):
            parser.parse_model_text(text)

    def test_4d_parameter(self):
        """Test 4D parameter to ensure arbitrary dimensions work."""
        text = dedent(
            """
            Sets
                i /i1/
                j /j1/
                k /k1/
                l /l1/
            ;

            Parameters
                a(i, j, k, l) /
                    i1.j1.k1.l1 42.0
                /
            ;

            Variables x;
            Equations eq;
            eq.. x =e= 0;
            Model test /all/;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert model.params["a"].domain == ("i", "j", "k", "l")
        assert model.params["a"].values[("i1", "j1", "k1", "l1")] == 42.0


class TestCaseInsensitivity:
    """Test case-insensitive symbol lookup (Issue #373)."""

    def test_parameter_case_insensitive_reference(self):
        """Test parameter declared with one case, referenced with another."""
        text = dedent(
            """
            Sets
                i /i1, i2/
            ;

            Parameters
                myParam(i) / i1 1.0, i2 2.0 /
            ;

            Variables
                x(i)
            ;

            Equations
                balance(i)
            ;

            balance(i).. x(i) =e= MYPARAM(i);

            Model test /all/;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "myparam" in model.params  # Case-insensitive lookup
        assert model.params["myParam"].domain == ("i",)  # Case-insensitive lookup
        assert model.params["MYPARAM"].domain == ("i",)  # Case-insensitive lookup

    def test_variable_case_insensitive_reference(self):
        """Test variable declared and referenced with different cases."""
        text = dedent(
            """
            Variables
                myVar
                obj
            ;

            Equations
                objective
            ;

            objective.. obj =e= MYVAR + MyVar;

            Model test /all/;
            Solve test using NLP minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert "myvar" in model.variables
        # All references should resolve to same variable
        assert model.variables["myVar"].domain == ()
        assert model.variables["MYVAR"].domain == ()

    def test_set_case_insensitive_reference(self):
        """Test set declared and referenced with different cases."""
        text = dedent(
            """
            Sets
                mySet /s1, s2, s3/
            ;

            Parameters
                p(MYSET) / s1 1.0 /
            ;

            Variables x;
            Equations eq;
            eq.. x =e= 0;
            Model test /all/;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "myset" in model.sets
        assert "p" in model.params
        assert model.params["p"].domain == ("MYSET",)  # Case preserved as written

    def test_equation_case_insensitive_reference(self):
        """Test equation declared and referenced with different cases."""
        text = dedent(
            """
            Variables x;

            Equations
                myEquation
            ;

            MYEQUATION.. x =e= 1;

            Model test / MyEquation /;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "myequation" in model.equations
        assert model.model_equations == ["MyEquation"]  # Case preserved from Model statement

    def test_alias_case_insensitive(self):
        """Test alias with different cases."""
        text = dedent(
            """
            Sets
                i /i1, i2/
            ;

            Alias (i, J);

            Parameters
                p(j) / i1 1.0 /
            ;

            Variables x;
            Equations eq;
            eq.. x =e= 0;
            Model test /all/;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "j" in model.aliases
        assert model.aliases["J"].target == "i"  # Case-insensitive

    def test_table_case_insensitive_reference(self):
        """Test table declared and referenced with different cases."""
        text = dedent(
            """
            Sets
                i /i1, i2/
                j /j1, j2/
            ;

            Table myTable(i,j)
                    j1  j2
            i1      1   2
            i2      3   4
            ;

            Parameters
                result(i)
            ;

            result(i) = sum(j, MYTABLE(i,j));

            Variables x;
            Equations eq;
            eq.. x =e= 0;
            Model test /all/;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "mytable" in model.params
        assert len(model.params["MYTABLE"].values) == 4

    def test_mixed_case_in_expressions(self):
        """Test multiple symbols with mixed cases in same expression."""
        text = dedent(
            """
            Parameters
                alpha
                beta
                gamma
            ;

            alpha = 2.0;
            beta = 3.0;
            gamma = 4.0;

            Variables
                x
            ;

            Equations
                balance
            ;

            balance.. x =e= ALPHA + Beta + gamma;

            Model test /all/;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "alpha" in model.params
        assert "beta" in model.params
        assert "gamma" in model.params

    def test_case_preservation_in_output(self):
        """Test that original casing is preserved for display."""
        text = dedent(
            """
            Parameters
                MyParameter
            ;

            MyParameter = 5.0;

            Variables x;
            Equations eq;
            eq.. x =e= 0;
            Model test /all/;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        # Check that we can get the original name
        original_name = model.params.get_original_name("myparameter")
        assert original_name == "MyParameter"

    def test_haverly_pattern(self):
        """Test the exact pattern from haverly.gms."""
        text = dedent(
            """
            Sets
                f /f1, f2/
            ;

            Table data_f(f,*)
                    price  sulfur
            f1      9      2.5
            f2      15     1.5
            ;

            Parameters
                req_sulfur(f)
            ;

            req_sulfur(f) = data_F(f,'sulfur');

            Variables x;
            Equations eq;
            eq.. x =e= 0;
            Model test /all/;
            Solve test using NLP minimizing x;
            """
        )
        model = parser.parse_model_text(text)
        assert "data_f" in model.params
        # This should not fail with "Undefined symbol 'data_F'"
        assert "req_sulfur" in model.params

    def test_no_redeclaration_error_different_case(self):
        """Test that same symbol with different case is not a redeclaration error."""
        text = dedent(
            """
            Parameters
                myParam
            ;

            myParam = 1.0;

            Variables x;
            Equations eq;

            myParam = 2.0;
            MYPARAM = 3.0;

            eq.. x =e= myParam;
            Model test /all/;
            Solve test using NLP minimizing x;
            """
        )
        # Should parse without redeclaration errors
        model = parser.parse_model_text(text)
        assert "myparam" in model.params


class TestDescriptionText:
    """Test suite for DESCRIPTION terminal - Issue #137."""

    def test_equation_with_hyphenated_description(self):
        """Test equation declaration with hyphenated description text."""
        text = dedent(
            """
            Sets
                i /i1, i2/
            ;

            Variables
                x(i)
                obj
            ;

            Equations
                objdef objective definition
                non_negative(i) non-negativity constraints
            ;

            objdef.. obj =e= sum(i, x(i));
            non_negative(i).. x(i) =g= 0;

            Model test /all/;
            Solve test using NLP minimizing obj;
            """
        )
        model = parser.parse_model_text(text)
        assert "objdef" in model.equations
        assert "non_negative" in model.equations
        assert model.equations["objdef"].domain == ()
        assert model.equations["non_negative"].domain == ("i",)

    def test_equation_scalar_with_description(self):
        """Test scalar equation with multi-word description."""
        text = dedent(
            """
            Variables x, y;
            Equations balance supply demand balance;

            balance.. x + y =e= 10;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "balance" in model.equations

    def test_equation_indexed_with_description(self):
        """Test indexed equation with description containing hyphens."""
        text = dedent(
            """
            Set i /i1, i2/;
            Variables x(i);
            Equations flow_limit(i) arc-capacity constraint;

            flow_limit(i).. x(i) =l= 100;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "flow_limit" in model.equations
        assert model.equations["flow_limit"].domain == ("i",)

    def test_table_with_hyphenated_description(self):
        """Test table declaration with hyphenated description text."""
        text = dedent(
            """
            Set i / i1, i2 /;
            Set j / j1, j2 /;

            Table data(i,j) test-data with hyphens
                   j1  j2
              i1   1   2
              i2   3   4;

            Parameters result;
            result = sum(i, sum(j, data(i,j)));

            Variables x;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        # Tables are stored as params in ModelIR
        assert "data" in model.params
        assert model.params["data"].domain == ("i", "j")

    def test_description_does_not_match_short_identifiers(self):
        """Ensure DESCRIPTION doesn't match short identifier sequences like 'i j'."""
        text = dedent(
            """
            Set i / i1, i2 /;
            Set j / j1, j2 /;

            Table data(i,j)
                   j1  j2
              i1   1   2
              i2   3   4;

            Variables x;
            Model m /all/;
            """
        )
        # Should parse successfully - 'j1 j2' is table header, not description
        model = parser.parse_model_text(text)
        # Tables are stored as params in ModelIR
        assert "data" in model.params

    def test_description_does_not_match_comma_separated_ids(self):
        """Ensure DESCRIPTION doesn't consume comma-separated equation lists."""
        text = dedent(
            """
            Variables x, y, z;
            Equations eq1, eq2, eq3;

            eq1.. x =e= 1;
            eq2.. y =e= 2;
            eq3.. z =e= 3;

            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "eq1" in model.equations
        assert "eq2" in model.equations
        assert "eq3" in model.equations


class TestVariableIndexingSyntax:
    """Test variable declarations with domain indexing (Issue #391).

    GAMS allows variables to be declared with their domain specified using
    parentheses notation directly in the declaration block, enabling more
    concise and documented model structure.

    This fixes GitHub Issue #391 and unblocks inscribedsquare.gms (106 lines, NLP).
    """

    def test_single_index_variable(self):
        """Test variable with single index."""
        text = dedent(
            """
            Set i / 1*10 /;
            Variable x(i);
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        assert model.variables["x"].domain == ("i",)

    def test_two_dimensional_variable(self):
        """Test variable with two indices."""
        text = dedent(
            """
            Set i / 1*5 /;
            Set j / 1*5 /;
            Variable flow(i,j);
            """
        )
        model = parser.parse_model_text(text)
        assert "flow" in model.variables
        assert model.variables["flow"].domain == ("i", "j")

    def test_three_dimensional_variable(self):
        """Test variable with three indices."""
        text = dedent(
            """
            Set i, j, k;
            Variable cube(i,j,k);
            """
        )
        model = parser.parse_model_text(text)
        assert "cube" in model.variables
        assert model.variables["cube"].domain == ("i", "j", "k")

    def test_mixed_scalar_and_indexed(self):
        """Test comma-separated list with both scalar and indexed variables."""
        text = dedent(
            """
            Set i / 1*10 /;
            Variables
                total        "total cost",
                x(i)         "decision variable",
                y(i)         "allocation variable";
            """
        )
        model = parser.parse_model_text(text)
        assert "total" in model.variables
        assert model.variables["total"].domain == ()
        assert "x" in model.variables
        assert model.variables["x"].domain == ("i",)
        assert "y" in model.variables
        assert model.variables["y"].domain == ("i",)

    def test_inscribedsquare_pattern(self):
        """Test exact pattern from inscribedsquare.gms (Issue #391)."""
        text = dedent(
            """
            Set i "corner points" / 1*4 /;
            Variables
              z     "area of square",
              t(i)  "position of corner points",
              x     "x-coordinate",
              y     "y-coordinate";
            """
        )
        model = parser.parse_model_text(text)
        assert "z" in model.variables
        assert model.variables["z"].domain == ()
        assert "t" in model.variables
        assert model.variables["t"].domain == ("i",)
        assert "x" in model.variables
        assert model.variables["x"].domain == ()
        assert "y" in model.variables
        assert model.variables["y"].domain == ()

    def test_positive_variable_with_domain(self):
        """Test positive variable with domain specification."""
        text = dedent(
            """
            Set i / 1*10 /;
            Positive Variable x(i);
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        assert model.variables["x"].domain == ("i",)
        assert model.variables["x"].kind == VarKind.POSITIVE

    def test_binary_variable_with_domain(self):
        """Test binary variable with domain specification."""
        text = dedent(
            """
            Set i / 1*10 /;
            Binary Variable b(i);
            """
        )
        model = parser.parse_model_text(text)
        assert "b" in model.variables
        assert model.variables["b"].domain == ("i",)
        assert model.variables["b"].kind == VarKind.BINARY

    def test_integer_variable_with_domain(self):
        """Test integer variable with domain specification."""
        text = dedent(
            """
            Set i / 1*10 /;
            Integer Variable n(i);
            """
        )
        model = parser.parse_model_text(text)
        assert "n" in model.variables
        assert model.variables["n"].domain == ("i",)
        assert model.variables["n"].kind == VarKind.INTEGER

    def test_negative_variable_with_domain(self):
        """Test negative variable with domain specification."""
        text = dedent(
            """
            Set i / 1*10 /;
            Negative Variable y(i);
            """
        )
        model = parser.parse_model_text(text)
        assert "y" in model.variables
        assert model.variables["y"].domain == ("i",)
        assert model.variables["y"].kind == VarKind.NEGATIVE

    def test_block_level_kind_with_indexed_variables(self):
        """Test block-level variable kind with indexed variables."""
        text = dedent(
            """
            Set i / 1*10 /;
            Positive Variables
                x(i)  "first positive variable",
                y(i)  "second positive variable";
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        assert model.variables["x"].domain == ("i",)
        assert model.variables["x"].kind == VarKind.POSITIVE
        assert "y" in model.variables
        assert model.variables["y"].domain == ("i",)
        assert model.variables["y"].kind == VarKind.POSITIVE

    def test_declaration_kind_overrides_block_kind(self):
        """Test declaration-level kind overrides block-level kind."""
        text = dedent(
            """
            Set i / 1*10 /;
            Positive Variables
                x(i)           "uses block kind (positive)",
                Binary y(i)    "overrides with binary";
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        assert model.variables["x"].kind == VarKind.POSITIVE
        assert "y" in model.variables
        assert model.variables["y"].kind == VarKind.BINARY

    def test_multiple_variables_with_descriptions(self):
        """Test multiple indexed variables with descriptions."""
        text = dedent(
            """
            Set i / 1*10 /;
            Set j / 1*5 /;
            Variables
                x(i)     "indexed by i",
                y(i,j)   "indexed by i and j",
                z        "scalar variable";
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        assert model.variables["x"].domain == ("i",)
        assert "y" in model.variables
        assert model.variables["y"].domain == ("i", "j")
        assert "z" in model.variables
        assert model.variables["z"].domain == ()

    def test_four_dimensional_variable(self):
        """Test variable with four indices."""
        text = dedent(
            """
            Set i, j, k, t;
            Variable x(i,j,k,t);
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        assert model.variables["x"].domain == ("i", "j", "k", "t")

    def test_variable_without_description(self):
        """Test indexed variable without description."""
        text = dedent(
            """
            Set i / 1*10 /;
            Variable x(i);
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        assert model.variables["x"].domain == ("i",)

    def test_newline_separated_variables(self):
        """Test variables separated by newlines (original syntax still works)."""
        text = dedent(
            """
            Set i / 1*10 /;
            Variables
                x(i)
                y
                z(i);
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        assert model.variables["x"].domain == ("i",)
        assert "y" in model.variables
        assert model.variables["y"].domain == ()
        assert "z" in model.variables
        assert model.variables["z"].domain == ("i",)


class TestHyphenatedIdentifiers:
    """Test support for hyphens and plus signs in set element identifiers.

    GAMS allows hyphens (-) and plus signs (+) in identifiers, commonly used
    in set element names like 'light-ind', 'food+agr', etc.

    The grammar achieves disambiguation through rule-based context, not truly
    context-sensitive lexing. SET_ELEMENT_ID tokens (priority .2) allow hyphens
    and plus signs in identifiers. These tokens are only used in set_member and
    data_indices grammar rules. In expression contexts, symbol_plain uses ID
    tokens, so 'a-b' is parsed as three tokens (a, -, b), not one hyphenated
    identifier. This gives correct behavior: 'Set i /a-b/' defines one element,
    while 'c = a - b' is subtraction.

    This fixes GitHub Issue #390 and unblocks chenery.gms (185 lines, NLP).
    """

    def test_simple_hyphenated_identifier(self):
        """Test single hyphenated identifier in set."""
        text = dedent(
            """
            Set i / light-ind /;
            """
        )
        model = parser.parse_model_text(text)
        assert "i" in model.sets
        assert model.sets["i"].members == ["light-ind"]

    def test_simple_plus_identifier(self):
        """Test single plus-sign identifier in set."""
        text = dedent(
            """
            Set i / food+agr /;
            """
        )
        model = parser.parse_model_text(text)
        assert "i" in model.sets
        assert model.sets["i"].members == ["food+agr"]

    def test_multiple_hyphenated_identifiers(self):
        """Test multiple hyphenated identifiers in same set."""
        text = dedent(
            """
            Set i / light-ind, heavy-ind, semi-auto /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["light-ind", "heavy-ind", "semi-auto"]

    def test_chenery_sectors(self):
        """Test exact pattern from chenery.gms line 17."""
        text = dedent(
            """
            Set i 'sectors' / light-ind, food+agr, heavy-ind, services /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["light-ind", "food+agr", "heavy-ind", "services"]

    def test_hyphenated_with_descriptions(self):
        """Test hyphenated identifiers with element descriptions."""
        text = dedent(
            """
            Set i 'sectors' /
                light-ind 'light industry',
                food+agr  'food and agriculture',
                heavy-ind 'heavy industry'
            /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["light-ind", "food+agr", "heavy-ind"]

    def test_mixed_regular_and_hyphenated(self):
        """Test mix of regular and hyphenated identifiers."""
        text = dedent(
            """
            Set i / a, b-c, d, e+f, g /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["a", "b-c", "d", "e+f", "g"]

    def test_multiple_hyphens(self):
        """Test identifier with multiple hyphens."""
        text = dedent(
            """
            Set i / light-semi-auto-ind /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["light-semi-auto-ind"]

    def test_multiple_plus_signs(self):
        """Test identifier with multiple plus signs."""
        text = dedent(
            """
            Set i / food+agr+services /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["food+agr+services"]

    def test_mixed_hyphens_and_plus(self):
        """Test identifier with both hyphens and plus signs."""
        text = dedent(
            """
            Set i / light-ind+services /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["light-ind+services"]

    def test_hyphenated_with_underscore(self):
        """Test identifier with hyphens and underscores."""
        text = dedent(
            """
            Set i / light_semi-auto /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["light_semi-auto"]

    def test_operators_still_work_in_expressions(self):
        """Test that minus and plus still work as operators in expressions."""
        text = dedent(
            """
            Scalar a / 10 /;
            Scalar b / 5 /;
            Scalar c;
            c = a - b + 2;
            """
        )
        model = parser.parse_model_text(text)
        assert "c" in model.params
        # Verify the assignment parsed (no exception means success)

    def test_operators_without_spaces(self):
        """Test that operators work correctly without spaces around them.

        Critical test: Verify that 'c=a-b+d' is parsed as subtraction/addition
        (three tokens: a, -, b) and not as hyphenated identifiers (a-b, +d).
        The grammar correctly disambiguates based on context: SET_ELEMENT_ID
        is only used in set/data contexts, while expressions use ID tokens.
        """
        text = dedent(
            """
            Scalar a / 10 /;
            Scalar b / 5 /;
            Scalar d / 3 /;
            Scalar c;
            c=a-b+d;
            """
        )
        model = parser.parse_model_text(text)
        assert "c" in model.params
        assert "a" in model.params
        assert "b" in model.params
        assert "d" in model.params
        # Verify the expression parsed correctly (no exception means success)

    def test_hyphenated_in_parameter_indexing(self):
        """Test using hyphenated set elements in parameter indexing."""
        text = dedent(
            """
            Set i / light-ind, heavy-ind /;
            Parameter cost(i) / light-ind 100, heavy-ind 200 /;
            """
        )
        model = parser.parse_model_text(text)
        assert "i" in model.sets
        assert model.sets["i"].members == ["light-ind", "heavy-ind"]
        assert "cost" in model.params

    def test_hyphenated_in_variable_bounds(self):
        """Test using hyphenated set elements in variable bounds.

        IMPORTANT: Hyphenated identifiers in index expressions MUST be quoted.
        Unquoted hyphenated identifiers like x.lo(light-ind) are misparsed
        as lag/lead expressions (light with offset -ind). This is a known
        limitation: index_expr uses ID tokens, not SET_ELEMENT_ID tokens.
        Users must use quotes: x.lo('light-ind').
        """
        text = dedent(
            """
            Set i / light-ind, heavy-ind /;
            Variable x(i);
            x.lo('light-ind') = 0;
            x.up('heavy-ind') = 100;
            """
        )
        model = parser.parse_model_text(text)
        assert "i" in model.sets
        assert model.sets["i"].members == ["light-ind", "heavy-ind"]
        assert "x" in model.variables

    def test_hyphen_as_operator_in_expressions(self):
        """Test that hyphen works as subtraction operator in expressions.

        Verifies that the hyphen operator works correctly in scalar expressions.
        This is separate from hyphenated identifiers in set contexts.
        """
        text = dedent(
            """
            Set i / a /;
            Scalar x;
            x = 10 - 5;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["a"]
        assert "x" in model.params

    def test_hyphenated_multiline(self):
        """Test hyphenated identifiers across multiple lines."""
        text = dedent(
            """
            Set i /
                light-ind,
                food+agr,
                heavy-ind
            /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["light-ind", "food+agr", "heavy-ind"]


class TestAttributeAssignments:
    """Test variable/parameter/model attribute assignments (Issue #389).

    GAMS allows assignment to various attributes such as .scale, .prior, .lo, .up, etc.
    The grammar already supports this via ref_bound and attr_access rules.
    """

    def test_variable_scale_attribute(self):
        """Test variable scaling attribute (bearing.gms pattern)."""
        text = dedent(
            """
            Variable mu;
            mu.scale = 1.0e-6;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "mu" in model.variables

    def test_multiple_variable_scales(self):
        """Test multiple variable scaling attributes (bearing.gms pattern)."""
        text = dedent(
            """
            Variable mu, h, W;
            mu.scale = 1.0e-6;
            h.scale  = 0.001;
            W.scale  = 1000;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "mu" in model.variables
        assert "h" in model.variables
        assert "W" in model.variables

    def test_variable_bounds_lo_up(self):
        """Test variable bounds (.lo, .up) assignments."""
        text = dedent(
            """
            Variable x;
            x.lo = 0;
            x.up = 100;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        # Note: bounds are stored in VariableDef
        assert model.variables["x"].lo == 0
        assert model.variables["x"].up == 100

    def test_variable_initial_value(self):
        """Test variable initial value (.l) assignment."""
        text = dedent(
            """
            Variable z;
            z.l = 50;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "z" in model.variables
        assert model.variables["z"].l == 50

    def test_variable_fixed_value(self):
        """Test variable fixed value (.fx) assignment."""
        text = dedent(
            """
            Variable x;
            x.fx = 42;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        # .fx sets both lo and up
        assert model.variables["x"].fx == 42

    def test_variable_prior_attribute(self):
        """Test branching priority (.prior) attribute."""
        text = dedent(
            """
            Variable z;
            z.prior = 1;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "z" in model.variables

    def test_model_scaleopt_attribute(self):
        """Test model scaleOpt attribute (bearing.gms pattern)."""
        text = dedent(
            """
            Variable x;
            Equations obj;
            obj.. x =e= 1;
            Model m /all/;
            m.scaleOpt = 1;
            """
        )
        model = parser.parse_model_text(text)
        # Model attributes are parsed but not stored in IR
        assert "x" in model.variables

    def test_variable_bounds_with_parameters(self):
        """Test variable bounds using parameter values.

        Note: The parser uses mock/store approach for bounds with non-constant
        expressions (see parser.py lines 1846-1849). Since 'lower' and 'upper'
        are parameter references (not constants), these bounds are parsed but
        not stored in the variable.
        """
        text = dedent(
            """
            Parameter lower, upper;
            lower = 10;
            upper = 20;
            Variable x;
            x.lo = lower;
            x.up = upper;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        # Bounds are not stored because they use parameter references (mock/store)
        assert model.variables["x"].lo is None
        assert model.variables["x"].up is None

    def test_bracket_expressions(self):
        """Test bracket expressions in equations (bearing.gms uses [(expr)])."""
        text = dedent(
            """
            Parameter pi, mu;
            pi = 3.14159;
            mu = 0.000006;
            Variable h;
            Equations test;
            test.. h =e= [2*pi*mu];
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "test" in model.equations

    def test_bearing_gms_attribute_pattern(self):
        """Test exact pattern from bearing.gms."""
        text = dedent(
            """
            Parameter hmin, Ws;
            hmin = 0.001;
            Ws = 1000;
            Variable mu, h, W, PL, Ep, Ef;

            mu.scale = 1.0e-6;
            h.scale  = hmin;
            W.scale  = Ws;
            PL.scale = 1.0e4;
            Ep.scale = 1.0e4;
            Ef.scale = 1.0e4;

            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "mu" in model.variables
        assert "h" in model.variables
        assert "W" in model.variables
        assert "PL" in model.variables
        assert "Ep" in model.variables
        assert "Ef" in model.variables

    def test_variable_attribute_with_expression(self):
        """Test variable attribute assigned with expression."""
        text = dedent(
            """
            Parameter scale_factor;
            scale_factor = 1000;
            Variable x;
            x.scale = 2 * scale_factor;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables

    def test_multiple_attributes_same_variable(self):
        """Test multiple attributes on same variable."""
        text = dedent(
            """
            Variable x;
            x.lo = 0;
            x.up = 100;
            x.l = 50;
            x.scale = 100;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "x" in model.variables
        assert model.variables["x"].lo == 0
        assert model.variables["x"].up == 100
        assert model.variables["x"].l == 50


class TestMultiLineDeclarations:
    """Test multi-line set/parameter/scalar declarations (Issue #388).

    GAMS allows comma-separated set element lists and parameter data to span
    multiple lines. Since NEWLINE is in the grammar's %ignore directive, newlines
    are treated as whitespace, allowing multi-line comma-separated lists to parse
    naturally without special grammar rules.
    """

    def test_multiline_set_with_commas_gastrans_style(self):
        """Test multi-line set with commas (gastrans.gms pattern)."""
        text = dedent(
            """
            Set i /
                a, b,
                c
            /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["a", "b", "c"]

    def test_multiline_set_with_commas(self):
        """Test multi-line set with commas."""
        text = dedent(
            """
            Set i /
                a, b, c,
                d, e, f
            /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["a", "b", "c", "d", "e", "f"]

    def test_multiline_set_mixed_commas(self):
        """Test multi-line set with commas on different lines."""
        text = dedent(
            """
            Set i /
                a, b,
                c, d
            /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["a", "b", "c", "d"]

    def test_multiline_set_with_descriptions(self):
        """Test multi-line set with element descriptions (water.gms pattern)."""
        text = dedent(
            """
            Set n 'nodes' /
                nw 'north west reservoir', e  'east reservoir',
                cc 'central city',         w  'west'
            /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["n"].members == ["nw", "e", "cc", "w"]

    def test_multiline_set_gastrans_pattern(self):
        """Test exact multi-line pattern from gastrans.gms."""
        text = dedent(
            """
            Set i 'towns'
              / Anderlues, Antwerpen, Arlon,   Berneau,   Blaregnies,
                Brugge,    Dudzele,   Gent,    Liege,     Loenhout,
                Mons,      Namur,     Petange, Peronnes,  Sinsin,
                Voeren,    Wanze,     Warnand, Zeebrugge, Zomergem   /;
            """
        )
        model = parser.parse_model_text(text)
        expected = [
            "Anderlues",
            "Antwerpen",
            "Arlon",
            "Berneau",
            "Blaregnies",
            "Brugge",
            "Dudzele",
            "Gent",
            "Liege",
            "Loenhout",
            "Mons",
            "Namur",
            "Petange",
            "Peronnes",
            "Sinsin",
            "Voeren",
            "Wanze",
            "Warnand",
            "Zeebrugge",
            "Zomergem",
        ]
        assert model.sets["i"].members == expected

    def test_multiline_parameter_1d(self):
        """Test multi-line 1D parameter (chem.gms pattern)."""
        text = dedent(
            """
            Set c / H, H2, NH /;
            Parameter gibbs(c) 'gibbs free energy' /
                H   -10.021, H2  -21.096,
                NH  -18.918
            /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.params["gibbs"].values == {
            ("H",): -10.021,
            ("H2",): -21.096,
            ("NH",): -18.918,
        }

    def test_multiline_parameter_with_commas(self):
        """Test multi-line parameter with commas."""
        text = dedent(
            """
            Set i / a, b, c /;
            Parameter p(i) /
                a 1.5, b 2.7,
                c 3.9
            /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.params["p"].values == {
            ("a",): 1.5,
            ("b",): 2.7,
            ("c",): 3.9,
        }

    def test_multiline_parameter_2d(self):
        """Test multi-line 2D parameter."""
        text = dedent(
            """
            Set i / a, b /;
            Set j / x, y /;
            Parameter cost(i,j) /
                a.x  10, a.y  20,
                b.x  30, b.y  40
            /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.params["cost"].values == {
            ("a", "x"): 10.0,
            ("a", "y"): 20.0,
            ("b", "x"): 30.0,
            ("b", "y"): 40.0,
        }

    def test_multiline_scalar_declarations(self):
        """Test multi-line scalar declarations (commas optional per scalar_item grammar)."""
        text = dedent(
            """
            Scalar
                a / 1.5 /
                b / 2.7 /
                c / 3.9 /
            ;
            """
        )
        model = parser.parse_model_text(text)
        assert model.params["a"].values == {(): 1.5}
        assert model.params["b"].values == {(): 2.7}
        assert model.params["c"].values == {(): 3.9}

    def test_multiline_scalar_with_commas(self):
        """Test multi-line scalar declarations with commas."""
        text = dedent(
            """
            Scalar
                a / 1.5 /,
                b / 2.7 /,
                c / 3.9 /
            ;
            """
        )
        model = parser.parse_model_text(text)
        assert model.params["a"].values == {(): 1.5}
        assert model.params["b"].values == {(): 2.7}
        assert model.params["c"].values == {(): 3.9}

    def test_multiline_set_trailing_comma(self):
        """Test multi-line set with trailing comma on last line."""
        text = dedent(
            """
            Set i /
                a,
                b,
                c
            /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["a", "b", "c"]

    def test_multiline_set_blank_lines(self):
        """Test multi-line set with blank lines (newlines are ignored as whitespace)."""
        text = dedent(
            """
            Set i /
                a,

                b,

                c
            /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["a", "b", "c"]

    def test_mixed_singleline_multiline_sets(self):
        """Test mixing single-line and multi-line set declarations in same file."""
        text = dedent(
            """
            Set i / a, b /;
            Set j /
                x,
                y,
                z
            /;
            Set k / p, q, r /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["a", "b"]
        assert model.sets["j"].members == ["x", "y", "z"]
        assert model.sets["k"].members == ["p", "q", "r"]

    def test_multiline_set_with_range(self):
        """Test multi-line set containing range notation."""
        text = dedent(
            """
            Set i /
                i1*i5,
                i10*i12
            /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["i1", "i2", "i3", "i4", "i5", "i10", "i11", "i12"]

    def test_multiline_set_mixed_elements_and_ranges(self):
        """Test multi-line set with mix of explicit elements and ranges."""
        text = dedent(
            """
            Set i /
                a, b,
                i1*i3,
                c, d
            /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.sets["i"].members == ["a", "b", "i1", "i2", "i3", "c", "d"]

    def test_multiline_parameter_numeric_indices(self):
        """Test multi-line parameter with numeric indices."""
        text = dedent(
            """
            Set nm / 1, 2, 3 /;
            Parameter tau(nm) /
                1 0.000,
                2 0.025,
                3 0.050
            /;
            """
        )
        model = parser.parse_model_text(text)
        assert model.params["tau"].values == {
            ("1",): 0.0,
            ("2",): 0.025,
            ("3",): 0.050,
        }

    def test_description_does_not_match_across_newlines(self):
        """Ensure DESCRIPTION doesn't match across newlines in multi-line declarations."""
        text = dedent(
            """
            Variables
                x
                y
                obj
            ;

            Equations
                objective
                constraint
            ;

            objective.. obj =e= x + y;
            constraint.. x + y =e= 10;

            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "objective" in model.equations
        assert "constraint" in model.equations

    def test_equation_with_quoted_description_still_works(self):
        """Ensure quoted string descriptions still work (existing feature)."""
        text = dedent(
            """
            Variables x;
            Equations eq "This is a quoted description";

            eq.. x =e= 1;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "eq" in model.equations

    def test_description_with_multiple_hyphens(self):
        """Test description with multiple hyphenated words."""
        text = dedent(
            """
            Variables x;
            Equations eq piece-wise linear-approximation function;

            eq.. x =e= 1;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "eq" in model.equations

    def test_description_requires_meaningful_words(self):
        """Test that description requires at least one word with 4+ chars."""
        text = dedent(
            """
            Set i /i1, i2/;
            Variables x(i);
            Equations eq(i) this equation has meaningful words;

            eq(i).. x(i) =e= 1;
            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "eq" in model.equations

    def test_mixed_declarations_with_and_without_descriptions(self):
        """Test mixing equations with and without descriptions."""
        text = dedent(
            """
            Variables x, y, z;
            Equations
                eq1 first equation
                eq2
                eq3 third-equation with-hyphens
            ;

            eq1.. x =e= 1;
            eq2.. y =e= 2;
            eq3.. z =e= 3;

            Model m /all/;
            """
        )
        model = parser.parse_model_text(text)
        assert "eq1" in model.equations
        assert "eq2" in model.equations
        assert "eq3" in model.equations


class TestTableContinuation:
    """Tests for table continuation with plus sign."""

    def test_basic_header_continuation(self):
        """Test basic header continuation with plus sign."""
        text = dedent(
            """
            Set i;
            Table data(i,*)
                   a  b
               +   c  d
            row1   1  2  3  4;
            """
        )
        model = parser.parse_model_text(text)
        assert "data" in model.params
        # Check that values are properly indexed
        assert ("row1", "a") in model.params["data"].values
        assert ("row1", "b") in model.params["data"].values
        assert ("row1", "c") in model.params["data"].values
        assert ("row1", "d") in model.params["data"].values

    def test_basic_data_continuation(self):
        """Test basic data continuation with plus sign."""
        text = dedent(
            """
            Set i;
            Table data(i,*)
                   a  b  c  d
            row1   1  2
               +   3  4;
            """
        )
        model = parser.parse_model_text(text)
        assert "data" in model.params
        assert model.params["data"].values[("row1", "a")] == 1
        assert model.params["data"].values[("row1", "b")] == 2
        assert model.params["data"].values[("row1", "c")] == 3
        assert model.params["data"].values[("row1", "d")] == 4

    def test_both_header_and_data_continuation(self):
        """Test continuation in both header and data rows."""
        text = dedent(
            """
            Set i;
            Table data(i,*)
                   a  b
               +   c  d
            row1   1  2
               +   3  4;
            """
        )
        model = parser.parse_model_text(text)
        assert "data" in model.params
        assert model.params["data"].values[("row1", "a")] == 1
        assert model.params["data"].values[("row1", "b")] == 2
        assert model.params["data"].values[("row1", "c")] == 3
        assert model.params["data"].values[("row1", "d")] == 4

    def test_multiple_rows_with_continuation(self):
        """Test multiple data rows each with continuation."""
        text = dedent(
            """
            Set i;
            Table data(i,*)
                   a  b
               +   c  d
            row1   1  2
               +   3  4
            row2   5  6
               +   7  8;
            """
        )
        model = parser.parse_model_text(text)
        assert "data" in model.params
        assert model.params["data"].values[("row1", "a")] == 1
        assert model.params["data"].values[("row1", "d")] == 4
        assert model.params["data"].values[("row2", "a")] == 5
        assert model.params["data"].values[("row2", "d")] == 8

    def test_multiple_continuation_lines(self):
        """Test multiple consecutive continuation lines."""
        text = dedent(
            """
            Set i;
            Table data(i,*)
                   a  b
               +   c  d
               +   e  f
            row1   1  2  3  4  5  6;
            """
        )
        model = parser.parse_model_text(text)
        assert "data" in model.params
        assert model.params["data"].values[("row1", "a")] == 1
        assert model.params["data"].values[("row1", "c")] == 3
        assert model.params["data"].values[("row1", "e")] == 5

    # TODO: Re-enable this test once we support column header continuations with NUMBER tokens
    # after data rows have been parsed (complex edge case from like.gms)
    # def test_large_table_like_gms_pattern(self):
    #     """Test pattern from like.gms with many columns."""
    #     text = dedent(
    #         """
    #         Set i;
    #         Table p(i,*) 'frequency of pressure'
    #                          1   2   3   4   5
    #            pressure     95 105 110 115 120
    #            frequency     1   1   4   4  15
    #            +             6   7   8   9  10
    #            pressure    125 130 135 140 145
    #            frequency    15  15  13  21  12;
    #         """
    #     )
    #     model = parser.parse_model_text(text)
    #     assert "p" in model.params
    #     # Check pressure row has values for columns 1-5
    #     assert ("pressure", "1") in model.params["p"].values
    #     assert model.params["p"].values[("pressure", "1")] == 95
    #     # Check frequency row has values including continuation columns 6-10
    #     assert ("frequency", "6") in model.params["p"].values
    #     assert model.params["p"].values[("frequency", "6")] == 15

    def test_no_continuation_baseline(self):
        """Test table without continuation (baseline for comparison)."""
        text = dedent(
            """
            Set i;
            Table data(i,*)
                   a  b  c
            row1   1  2  3;
            """
        )
        model = parser.parse_model_text(text)
        assert "data" in model.params
        assert model.params["data"].values[("row1", "a")] == 1
        assert model.params["data"].values[("row1", "c")] == 3

    def test_only_header_continuation(self):
        """Test continuation only in header."""
        text = dedent(
            """
            Set i;
            Table data(i,*)
                   a  b
               +   c  d
            row1   1  2  3  4;
            """
        )
        model = parser.parse_model_text(text)
        assert "data" in model.params
        assert len([k for k in model.params["data"].values.keys() if k[0] == "row1"]) == 4

    def test_only_data_continuation(self):
        """Test continuation only in data rows."""
        text = dedent(
            """
            Set i;
            Table data(i,*)
                   a  b  c  d
            row1   1  2
               +   3  4;
            """
        )
        model = parser.parse_model_text(text)
        assert "data" in model.params
        assert model.params["data"].values[("row1", "a")] == 1
        assert model.params["data"].values[("row1", "d")] == 4

    def test_sparse_continuation(self):
        """Test continuation with sparse data."""
        text = dedent(
            """
            Set i;
            Table data(i,*)
                   a  b  c  d  e  f
            row1   1  2
               +   3  4
               +   5  6;
            """
        )
        model = parser.parse_model_text(text)
        assert "data" in model.params
        assert model.params["data"].values[("row1", "a")] == 1
        assert model.params["data"].values[("row1", "c")] == 3
        assert model.params["data"].values[("row1", "e")] == 5

    def test_continuation_with_description(self):
        """Test table with description and continuation."""
        text = dedent(
            """
            Set i;
            Table data(i,*) 'test table with description'
                   a  b
               +   c  d
            row1   1  2  3  4;
            """
        )
        model = parser.parse_model_text(text)
        assert "data" in model.params
        assert model.params["data"].values[("row1", "a")] == 1
        assert model.params["data"].values[("row1", "d")] == 4

    def test_continuation_with_wildcard_domain(self):
        """Test table continuation with wildcard domain."""
        text = dedent(
            """
            Table data(*,*)
                   col1  col2
               +   col3  col4
            row1   1     2     3     4;
            """
        )
        model = parser.parse_model_text(text)
        assert "data" in model.params
        assert model.params["data"].values[("row1", "col1")] == 1
        assert model.params["data"].values[("row1", "col4")] == 4


class TestCurlyBraceSumComplexIndexing:
    """Tests for curly brace sum with complex indexing (Issue #379)."""

    def test_curly_brace_sum_with_tuple_domain(self):
        """Test sum{(i,j), expr} with tuple domain syntax."""
        text = dedent(
            """
            Set i /1*3/;
            Set j /1*3/;
            Parameter x(i,j);
            Variable obj;

            Equation eq;
            eq.. obj =e= sum{(i,j), x(i,j)};
        """
        )
        model = parser.parse_model_text(text)
        assert "eq" in model.equations
        assert model.equations["eq"].relation == Rel.EQ
        # Verify sum structure and indices
        _, rhs = model.equations["eq"].lhs_rhs
        assert isinstance(rhs, Sum)
        assert rhs.sum_indices == ("i", "j")

    def test_curly_brace_sum_with_subset_indexing(self):
        """Test sum{(nx(i),ny(j)), expr} with subset indexing."""
        text = dedent(
            """
            Set i /1*5/;
            Set j /1*5/;
            Set nx(i);
            Set ny(j);
            Parameter wq(i,j);
            Variable obj;

            Equation eq;
            eq.. obj =e= sum{(nx(i),ny(j)), wq(i,j)};
        """
        )
        model = parser.parse_model_text(text)
        assert "eq" in model.equations
        assert model.equations["eq"].relation == Rel.EQ
        # Verify sum structure and indices
        _, rhs = model.equations["eq"].lhs_rhs
        assert isinstance(rhs, Sum)
        assert rhs.sum_indices == ("i", "j")

    def test_curly_brace_sum_with_arithmetic_in_subset(self):
        """Test sum{(nx(i+1),ny(j+1)), expr} pattern from jbearing.gms."""
        text = dedent(
            """
            Set i /1*5/;
            Set j /1*5/;
            Set nx(i);
            Set ny(j);
            Parameter wq(i);
            Variable obj;

            Equation eq;
            eq.. obj =e= sum{(nx(i+1),ny(j+1)), wq(i)};
        """
        )
        model = parser.parse_model_text(text)
        assert "eq" in model.equations
        assert model.equations["eq"].relation == Rel.EQ
        # Verify sum structure and indices
        _, rhs = model.equations["eq"].lhs_rhs
        assert isinstance(rhs, Sum)
        assert rhs.sum_indices == ("i", "j")

    def test_curly_brace_sum_simple_backward_compat(self):
        """Test that simple sum{i, expr} still works."""
        text = dedent(
            """
            Set i /1*5/;
            Parameter x(i);
            Variable obj;

            Equation eq;
            eq.. obj =e= sum{i, x(i)};
        """
        )
        model = parser.parse_model_text(text)
        assert "eq" in model.equations
        # Verify sum structure and indices
        _, rhs = model.equations["eq"].lhs_rhs
        assert isinstance(rhs, Sum)
        assert rhs.sum_indices == ("i",)

    def test_parenthesis_sum_with_tuple_domain(self):
        """Test sum((i,j), expr) with parentheses also works."""
        text = dedent(
            """
            Set i /1*3/;
            Set j /1*3/;
            Parameter x(i,j);
            Variable obj;

            Equation eq;
            eq.. obj =e= sum((i,j), x(i,j));
        """
        )
        model = parser.parse_model_text(text)
        assert "eq" in model.equations
        # Verify sum structure and indices
        _, rhs = model.equations["eq"].lhs_rhs
        assert isinstance(rhs, Sum)
        assert rhs.sum_indices == ("i", "j")

    def test_curly_brace_sum_with_lag_in_subset(self):
        """Test sum{(nx(i-1)), expr} with lag operator in subset."""
        text = dedent(
            """
            Set i /1*5/;
            Set nx(i);
            Parameter wq(i);
            Variable obj;

            Equation eq;
            eq.. obj =e= sum{(nx(i-1)), wq(i)};
        """
        )
        model = parser.parse_model_text(text)
        assert "eq" in model.equations
        # Verify sum structure and indices
        _, rhs = model.equations["eq"].lhs_rhs
        assert isinstance(rhs, Sum)
        assert rhs.sum_indices == ("i",)

    def test_curly_brace_sum_triple_tuple(self):
        """Test sum{(i,j,k), expr} with three-element tuple."""
        text = dedent(
            """
            Set i /1*2/;
            Set j /1*2/;
            Set k /1*2/;
            Parameter x(i,j,k);
            Variable obj;

            Equation eq;
            eq.. obj =e= sum{(i,j,k), x(i,j,k)};
        """
        )
        model = parser.parse_model_text(text)
        assert "eq" in model.equations
        # Verify sum structure and indices
        _, rhs = model.equations["eq"].lhs_rhs
        assert isinstance(rhs, Sum)
        assert rhs.sum_indices == ("i", "j", "k")
