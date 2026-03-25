"""
Tests for loop body variable bound extraction (Issue #953).

When a loop body contains variable bound assignments like:
    Loop(scenario,
        purchase.up(p) = psdat(scenario, p, "p");
        sales.up(p) = psdat(scenario, p, "s");
        Solve model using NLP minimizing cost;
    );

The parser should extract bounds for the first iteration (scenario='scenario-1')
so that the KKT pipeline can create upper-bound complementarity equations.
"""

from __future__ import annotations

import pytest

from src.ir.parser import parse_model_text

pytestmark = pytest.mark.unit

# Minimal GAMS model with loop-body variable bounds
_LOOP_BOUNDS_MODEL = """\
Sets
    s /'s1', 's2'/
    p /'p1', 'p2'/
;

Parameters
    bnd(s,p) /'s1'.'p1' 10, 's1'.'p2' 20, 's2'.'p1' 15, 's2'.'p2' 25/
;

Positive Variables
    x(p)
;

Variable z;

Equations
    obj
    con(p)
;

obj.. z =E= sum(p, x(p));
con(p).. x(p) =L= bnd('s1', p);

Model m /all/;

Loop(s,
    x.up(p) = bnd(s, p);
    Solve m using NLP minimizing z;
);
"""


class TestLoopBodyVarBoundExtraction:
    """Tests for _extract_loop_body_var_bounds in parser."""

    def test_upper_bound_extracted(self):
        """Variable .up bounds from loop body should be stored in VariableDef."""
        model_ir = parse_model_text(_LOOP_BOUNDS_MODEL)
        xdef = model_ir.variables.get("x")
        assert xdef is not None
        # The parser should extract bounds using the first loop iteration (s='s1')
        # x.up('p1') = bnd('s1','p1') = 10
        # x.up('p2') = bnd('s1','p2') = 20
        # Verify numeric per-element bounds were created
        assert hasattr(xdef, "up_map"), "xdef should have an up_map for per-element upper bounds"
        up_map = xdef.up_map
        assert up_map, "up_map should not be empty after extracting loop-body bounds"
        assert (
            up_map.get(("p1",)) == 10
        ), f"Expected upper bound 10 for p1, got {up_map.get(('p1',))}"
        assert (
            up_map.get(("p2",)) == 20
        ), f"Expected upper bound 20 for p2, got {up_map.get(('p2',))}"
        # After resolving bounds, expression-based upper bounds should be cleared
        if hasattr(xdef, "up_expr_map"):
            assert (
                not xdef.up_expr_map
            ), f"up_expr_map should be empty after resolution, got {xdef.up_expr_map}"


_LOOP_BOUNDS_NO_SOLVE = """\
Sets
    s /'s1', 's2'/
    p /'p1', 'p2'/
;

Positive Variables
    x(p)
;

Variable z;

Equations
    obj
;

obj.. z =E= sum(p, x(p));

Model m /all/;

Loop(s,
    x.up(p) = 5;
);
"""


class TestLoopBodyWithoutSolve:
    """Loop bodies without Solve should NOT have bounds extracted."""

    def test_no_extraction_without_solve(self):
        """Bounds from loop without Solve should not be extracted."""
        model_ir = parse_model_text(_LOOP_BOUNDS_NO_SOLVE)
        xdef = model_ir.variables.get("x")
        assert xdef is not None
        # Without Solve in the loop, bounds should NOT be extracted
        has_numeric_up = hasattr(xdef, "up_map") and xdef.up_map
        has_expr_up = hasattr(xdef, "up_expr_map") and xdef.up_expr_map
        assert not has_numeric_up and not has_expr_up
