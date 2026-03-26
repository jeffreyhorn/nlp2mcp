"""Tests for domain case normalization in equation/variable definitions.

Issue: GAMS is case-insensitive, but the parser preserved uppercase from
the definition head (e.g., SX(R,C).. produced domain ('R','C') instead of
('r','c')), causing Jacobian mismatches.
"""

from src.ir.parser import parse_model_file


def test_equation_domain_lowercased(tmp_path):
    """Equation definition with uppercase indices should produce lowercase domain."""
    gams = """\
Set r / r1, r2 /;
Set c / c1, c2 /;
Variable x(r,c), obj;
Equation eq(r,c), objdef;
eq(R,C).. x(R,C) =e= 0;
objdef.. obj =e= sum((r,c), x(r,c));
Model m / eq, objdef /;
solve m using lp minimizing obj;
"""
    gams_file = tmp_path / "test_case.gms"
    gams_file.write_text(gams)
    model = parse_model_file(str(gams_file))

    eq = model.equations.get("eq")
    assert eq is not None
    # Domain should be lowercase regardless of source casing
    assert eq.domain == ("r", "c"), f"Expected ('r', 'c'), got {eq.domain}"


def test_variable_declaration_domain_lowercased(tmp_path):
    """Variable declaration with uppercase domain sets should produce lowercase domain."""
    gams = """\
Set r / r1, r2 /;
Set c / c1, c2 /;
Variable x(R,C), obj;
Equation eq(r,c), objdef;
eq(r,c).. x(r,c) =e= 0;
objdef.. obj =e= sum((r,c), x(r,c));
Model m / eq, objdef /;
solve m using lp minimizing obj;
"""
    gams_file = tmp_path / "test_var_decl_domain.gms"
    gams_file.write_text(gams)
    model = parse_model_file(str(gams_file))

    var = model.variables.get("x")
    assert var is not None
    assert var.domain == ("r", "c"), f"Expected ('r', 'c'), got {var.domain}"


def test_variable_indices_lowercased_in_expressions(tmp_path):
    """Variable references in expressions should have lowercase indices."""
    gams = """\
Set r / r1, r2 /;
Variable x(r), obj;
Equation eq(r), objdef;
eq(R).. x(R) =e= 0;
objdef.. obj =e= sum(r, x(r));
Model m / eq, objdef /;
solve m using lp minimizing obj;
"""
    gams_file = tmp_path / "test_case2.gms"
    gams_file.write_text(gams)
    model = parse_model_file(str(gams_file))

    eq = model.equations.get("eq")
    assert eq is not None
    # The LHS should reference x with lowercase index
    lhs, _ = eq.lhs_rhs
    from src.ir.ast import VarRef

    assert isinstance(lhs, VarRef), f"Expected VarRef on LHS, got {type(lhs)}"
    assert all(
        idx == idx.lower() for idx in lhs.indices if isinstance(idx, str)
    ), f"VarRef indices should be lowercase: {lhs.indices}"


def test_sum_index_lowercased(tmp_path):
    """Sum iteration variables from uppercase source should be lowercase."""
    gams = """\
Set r / r1, r2 /;
Alias(r, rr);
Variable x(r,rr), obj;
Equation eq(r), objdef;
eq(R).. sum(RR, x(R,RR)) =e= 0;
objdef.. obj =e= sum((r,rr), x(r,rr));
Model m / eq, objdef /;
solve m using lp minimizing obj;
"""
    gams_file = tmp_path / "test_case3.gms"
    gams_file.write_text(gams)
    model = parse_model_file(str(gams_file))

    eq = model.equations.get("eq")
    assert eq is not None
    lhs, _ = eq.lhs_rhs
    from src.ir.ast import Sum

    assert isinstance(lhs, Sum), f"Expected Sum, got {type(lhs)}"
    # Sum index sets should be lowercase
    for idx_set in lhs.index_sets:
        assert idx_set == idx_set.lower(), f"Sum index '{idx_set}' should be lowercase"
