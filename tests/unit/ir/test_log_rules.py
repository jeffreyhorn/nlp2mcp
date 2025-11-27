"""Unit tests for logarithm simplification transformations."""

from src.ir.ast import Binary, Call, Const, SymbolRef
from src.ir.transformations.log_rules import apply_log_rules


class TestLogConstants:
    """Test logarithm simplifications for constant arguments."""

    def test_log_of_one(self):
        """Test: log(1) → 0"""
        expr = Call("log", [Const(1)])
        result = apply_log_rules(expr)

        # Expected: 0
        assert isinstance(result, Const)
        assert result.value == 0

    def test_ln_of_one(self):
        """Test: ln(1) → 0"""
        expr = Call("ln", [Const(1)])
        result = apply_log_rules(expr)

        # Expected: 0
        assert isinstance(result, Const)
        assert result.value == 0

    def test_log_of_e(self):
        """Test: log(e) → 1"""
        # e ≈ 2.71828182845904523536
        expr = Call("log", [Const(2.71828182845904523536)])
        result = apply_log_rules(expr)

        # Expected: 1
        assert isinstance(result, Const)
        assert result.value == 1


class TestLogProductRule:
    """Test log(a*b) → log(a) + log(b)."""

    def test_log_of_product(self):
        """Test: log(x*y) → log(x) + log(y)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        expr = Call("log", [Binary("*", x, y)])

        result = apply_log_rules(expr)

        # Expected: log(x) + log(y)
        assert isinstance(result, Binary)
        assert result.op == "+"
        assert isinstance(result.left, Call)
        assert result.left.func == "log"
        assert result.left.args == (x,)
        assert isinstance(result.right, Call)
        assert result.right.func == "log"
        assert result.right.args == (y,)

    def test_ln_of_product(self):
        """Test: ln(x*y) → ln(x) + ln(y)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        expr = Call("ln", [Binary("*", x, y)])

        result = apply_log_rules(expr)

        # Expected: ln(x) + ln(y)
        assert isinstance(result, Binary)
        assert result.op == "+"
        assert isinstance(result.left, Call)
        assert result.left.func == "ln"
        assert result.left.args == (x,)
        assert isinstance(result.right, Call)
        assert result.right.func == "ln"
        assert result.right.args == (y,)


class TestLogQuotientRule:
    """Test log(a/b) → log(a) - log(b)."""

    def test_log_of_quotient(self):
        """Test: log(x/y) → log(x) - log(y)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        expr = Call("log", [Binary("/", x, y)])

        result = apply_log_rules(expr)

        # Expected: log(x) - log(y)
        assert isinstance(result, Binary)
        assert result.op == "-"
        assert isinstance(result.left, Call)
        assert result.left.func == "log"
        assert result.left.args == (x,)
        assert isinstance(result.right, Call)
        assert result.right.func == "log"
        assert result.right.args == (y,)


class TestLogPowerRule:
    """Test log(a^n) → n*log(a)."""

    def test_log_of_power(self):
        """Test: log(x^2) → 2*log(x)"""
        x = SymbolRef("x")
        expr = Call("log", [Binary("**", x, Const(2))])

        result = apply_log_rules(expr)

        # Expected: 2*log(x)
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert isinstance(result.left, Const)
        assert result.left.value == 2
        assert isinstance(result.right, Call)
        assert result.right.func == "log"
        assert result.right.args == (x,)

    def test_log_of_power_with_variable_exponent(self):
        """Test: log(x^n) → n*log(x)"""
        x = SymbolRef("x")
        n = SymbolRef("n")
        expr = Call("log", [Binary("**", x, n)])

        result = apply_log_rules(expr)

        # Expected: n*log(x)
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == n
        assert isinstance(result.right, Call)
        assert result.right.func == "log"
        assert result.right.args == (x,)

    def test_log_of_negative_power(self):
        """Test: log(x^(-1)) → -1*log(x)"""
        x = SymbolRef("x")
        expr = Call("log", [Binary("**", x, Const(-1))])

        result = apply_log_rules(expr)

        # Expected: -1*log(x)
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert isinstance(result.left, Const)
        assert result.left.value == -1
        assert isinstance(result.right, Call)
        assert result.right.func == "log"
        assert result.right.args == (x,)


class TestNoSimplification:
    """Test cases where no simplification should occur."""

    def test_non_log_function(self):
        """Test: exp(x) → exp(x) (no change)"""
        x = SymbolRef("x")
        expr = Call("exp", [x])

        result = apply_log_rules(expr)

        # Expected: No change
        assert result == expr

    def test_log_of_simple_variable(self):
        """Test: log(x) → log(x) (no change)"""
        x = SymbolRef("x")
        expr = Call("log", [x])

        result = apply_log_rules(expr)

        # Expected: No change
        assert result == expr

    def test_log_of_sum(self):
        """Test: log(x+y) → log(x+y) (no change, no rule for sum)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        expr = Call("log", [Binary("+", x, y)])

        result = apply_log_rules(expr)

        # Expected: No change (no rule for log(a+b))
        assert result == expr
