"""Unit tests for trigonometric identity transformations."""

from src.ir.ast import Binary, Call, Const, SymbolRef
from src.ir.transformations.trig_rules import apply_trig_identities


class TestPythagoreanIdentity:
    """Test Pythagorean identity: sin^2(x) + cos^2(x) → 1."""

    def test_simple_pythagorean_identity(self):
        """Test: sin^2(x) + cos^2(x) → 1"""
        x = SymbolRef("x")
        sin_x = Call("sin", [x])
        cos_x = Call("cos", [x])

        # sin^2(x) + cos^2(x)
        expr = Binary("+", Binary("**", sin_x, Const(2)), Binary("**", cos_x, Const(2)))

        result = apply_trig_identities(expr)

        # Expected: 1
        assert isinstance(result, Const)
        assert result.value == 1

    def test_pythagorean_identity_reversed(self):
        """Test: cos^2(x) + sin^2(x) → 1"""
        x = SymbolRef("x")
        sin_x = Call("sin", [x])
        cos_x = Call("cos", [x])

        # cos^2(x) + sin^2(x)
        expr = Binary("+", Binary("**", cos_x, Const(2)), Binary("**", sin_x, Const(2)))

        result = apply_trig_identities(expr)

        # Expected: 1
        assert isinstance(result, Const)
        assert result.value == 1

    def test_pythagorean_identity_with_extra_term(self):
        """Test: sin^2(x) + cos^2(x) + y → 1 + y"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        sin_x = Call("sin", [x])
        cos_x = Call("cos", [x])

        # sin^2(x) + cos^2(x) + y
        expr = Binary(
            "+",
            Binary("+", Binary("**", sin_x, Const(2)), Binary("**", cos_x, Const(2))),
            y,
        )

        result = apply_trig_identities(expr)

        # Expected: 1 + y
        assert isinstance(result, Binary)
        assert result.op == "+"
        # Result should contain Const(1) and y
        # The order may vary, so check both possibilities
        is_valid = (
            isinstance(result.left, Const) and result.left.value == 1 and result.right == y
        ) or (isinstance(result.right, Const) and result.right.value == 1 and result.left == y)
        assert is_valid

    def test_pythagorean_identity_different_arguments_no_match(self):
        """Test: sin^2(x) + cos^2(y) → sin^2(x) + cos^2(y) (no change)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        sin_x = Call("sin", [x])
        cos_y = Call("cos", [y])

        # sin^2(x) + cos^2(y)
        expr = Binary("+", Binary("**", sin_x, Const(2)), Binary("**", cos_y, Const(2)))

        result = apply_trig_identities(expr)

        # Expected: No change (different arguments)
        assert result == expr


class TestTrigFunctionConversions:
    """Test trigonometric function conversions."""

    def test_tan_conversion(self):
        """Test: tan(x) → sin(x)/cos(x)"""
        x = SymbolRef("x")
        expr = Call("tan", [x])

        result = apply_trig_identities(expr)

        # Expected: sin(x)/cos(x)
        assert isinstance(result, Binary)
        assert result.op == "/"
        assert isinstance(result.left, Call)
        assert result.left.func == "sin"
        assert result.left.args == (x,)
        assert isinstance(result.right, Call)
        assert result.right.func == "cos"
        assert result.right.args == (x,)

    def test_sec_conversion(self):
        """Test: sec(x) → 1/cos(x)"""
        x = SymbolRef("x")
        expr = Call("sec", [x])

        result = apply_trig_identities(expr)

        # Expected: 1/cos(x)
        assert isinstance(result, Binary)
        assert result.op == "/"
        assert isinstance(result.left, Const)
        assert result.left.value == 1
        assert isinstance(result.right, Call)
        assert result.right.func == "cos"
        assert result.right.args == (x,)

    def test_csc_conversion(self):
        """Test: csc(x) → 1/sin(x)"""
        x = SymbolRef("x")
        expr = Call("csc", [x])

        result = apply_trig_identities(expr)

        # Expected: 1/sin(x)
        assert isinstance(result, Binary)
        assert result.op == "/"
        assert isinstance(result.left, Const)
        assert result.left.value == 1
        assert isinstance(result.right, Call)
        assert result.right.func == "sin"
        assert result.right.args == (x,)

    def test_cot_conversion(self):
        """Test: cot(x) → cos(x)/sin(x)"""
        x = SymbolRef("x")
        expr = Call("cot", [x])

        result = apply_trig_identities(expr)

        # Expected: cos(x)/sin(x)
        assert isinstance(result, Binary)
        assert result.op == "/"
        assert isinstance(result.left, Call)
        assert result.left.func == "cos"
        assert result.left.args == (x,)
        assert isinstance(result.right, Call)
        assert result.right.func == "sin"
        assert result.right.args == (x,)

    def test_sin_no_conversion(self):
        """Test: sin(x) → sin(x) (no conversion)"""
        x = SymbolRef("x")
        expr = Call("sin", [x])

        result = apply_trig_identities(expr)

        # Expected: No change
        assert result == expr

    def test_cos_no_conversion(self):
        """Test: cos(x) → cos(x) (no conversion)"""
        x = SymbolRef("x")
        expr = Call("cos", [x])

        result = apply_trig_identities(expr)

        # Expected: No change
        assert result == expr
