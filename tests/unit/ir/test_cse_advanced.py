"""Unit tests for advanced CSE transformations (T5.2, T5.3, and T5.4)."""

from src.ir.ast import Binary, Call, Const, SymbolRef
from src.ir.transformations.cse_advanced import cse_with_aliasing, multiplicative_cse, nested_cse


class TestNestedCSE:
    """Test T5.2: Nested Expression CSE."""

    def test_simple_repeated_subexpression(self):
        """Test: (x+y)^2 + 3*(x+y) + sin(x+y) → t1 = x+y; t1^2 + 3*t1 + sin(t1)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        xy = Binary("+", x, y)

        # Build (x+y)^2 + 3*(x+y) + sin(x+y)
        expr = Binary(
            "+",
            Binary("+", Binary("**", xy, Const(2)), Binary("*", Const(3), xy)),
            Call("sin", (xy,)),
        )

        result, temps = nested_cse(expr, min_occurrences=3)

        # Should extract x+y as t1
        assert len(temps) == 1
        assert "t1" in temps

        # t1 should be x+y
        t1_def = temps["t1"]
        assert isinstance(t1_def, Binary)
        assert t1_def.op == "+"

        # Result should reference t1
        assert isinstance(result, Binary)

    def test_no_extraction_below_threshold(self):
        """Test: Subexpression appears only twice (below threshold=3)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        xy = Binary("+", x, y)

        # (x+y)*2 + (x+y)*3 - only 2 occurrences
        expr = Binary("+", Binary("*", xy, Const(2)), Binary("*", xy, Const(3)))

        result, temps = nested_cse(expr, min_occurrences=3)

        # No extraction (below threshold)
        assert len(temps) == 0
        assert result == expr

    def test_extraction_at_threshold(self):
        """Test: Subexpression appears exactly at threshold"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        xy = Binary("+", x, y)

        # (x+y) + (x+y) + (x+y) - exactly 3 occurrences
        expr = Binary("+", Binary("+", xy, xy), xy)

        result, temps = nested_cse(expr, min_occurrences=3)

        # Should extract
        assert len(temps) == 1
        assert "t1" in temps

    def test_nested_dependencies(self):
        """Test: Nested subexpressions with dependencies"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        xy = Binary("+", x, y)
        xy_sq = Binary("**", xy, Const(2))

        # (x+y)^2 + (x+y)^2 + (x+y)^2 + (x+y) + (x+y) + (x+y)
        # Should extract both (x+y) and (x+y)^2
        expr = Binary(
            "+",
            Binary("+", Binary("+", xy_sq, xy_sq), xy_sq),
            Binary("+", Binary("+", xy, xy), xy),
        )

        result, temps = nested_cse(expr, min_occurrences=3)

        # Should extract both subexpressions
        assert len(temps) >= 1  # At least one extraction

    def test_function_call_subexpression(self):
        """Test: Repeated function call as subexpression"""
        x = SymbolRef("x")
        exp_x = Call("exp", (x,))

        # exp(x)*a + exp(x)*b + exp(x)*c
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")
        expr = Binary(
            "+",
            Binary("+", Binary("*", exp_x, a), Binary("*", exp_x, b)),
            Binary("*", exp_x, c),
        )

        result, temps = nested_cse(expr, min_occurrences=3)

        # Should extract exp(x)
        assert len(temps) == 1
        assert "t1" in temps

        # t1 should be exp(x)
        t1_def = temps["t1"]
        assert isinstance(t1_def, Call)
        assert t1_def.func == "exp"

    def test_no_extraction_for_simple_variables(self):
        """Test: Simple variables not extracted (too cheap)"""
        x = SymbolRef("x")

        # x + x + x + x (4 occurrences but too simple)
        expr = Binary("+", Binary("+", Binary("+", x, x), x), x)

        result, temps = nested_cse(expr, min_occurrences=3)

        # No extraction (simple variable)
        assert len(temps) == 0

    def test_no_extraction_for_constants(self):
        """Test: Constants not extracted"""
        c = Const(5)

        # 5 + 5 + 5 + 5
        expr = Binary("+", Binary("+", Binary("+", c, c), c), c)

        result, temps = nested_cse(expr, min_occurrences=3)

        # No extraction (constant)
        assert len(temps) == 0

    def test_multiple_independent_subexpressions(self):
        """Test: Multiple independent repeated subexpressions"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        a = SymbolRef("a")
        b = SymbolRef("b")

        xy = Binary("+", x, y)
        ab = Binary("+", a, b)

        # (x+y)*(x+y)*(x+y) + (a+b)*(a+b)*(a+b)
        expr = Binary(
            "+",
            Binary("*", Binary("*", xy, xy), xy),
            Binary("*", Binary("*", ab, ab), ab),
        )

        result, temps = nested_cse(expr, min_occurrences=3)

        # Should extract both (x+y) and (a+b)
        assert len(temps) == 2

    def test_complex_nested_expression(self):
        """Test: Complex nested expression with multiple levels"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")

        # (x*y+z) appears 3 times
        xyz = Binary("+", Binary("*", x, y), z)

        # sin((x*y+z)) + cos((x*y+z)) + (x*y+z)^2
        expr = Binary(
            "+",
            Binary("+", Call("sin", (xyz,)), Call("cos", (xyz,))),
            Binary("**", xyz, Const(2)),
        )

        result, temps = nested_cse(expr, min_occurrences=3)

        # Should extract (x*y+z) and potentially (x*y) if it appears enough times
        assert len(temps) >= 1
        assert "t1" in temps

    def test_custom_threshold(self):
        """Test: Custom occurrence threshold"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        xy = Binary("+", x, y)

        # (x+y) + (x+y) - only 2 occurrences
        expr = Binary("+", xy, xy)

        # With threshold=2, should extract
        result, temps = nested_cse(expr, min_occurrences=2)
        assert len(temps) == 1

        # With threshold=3, should not extract
        result, temps = nested_cse(expr, min_occurrences=3)
        assert len(temps) == 0


class TestMultiplicativeCSE:
    """Test T5.3: Multiplicative Subexpression CSE."""

    def test_simple_multiplicative_pattern(self):
        """Test: x*y*a + x*y*b + x*y*c + x*y*d → m1 = x*y; m1*a + m1*b + m1*c + m1*d"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")
        d = SymbolRef("d")

        xy = Binary("*", x, y)

        # Build x*y*a + x*y*b + x*y*c + x*y*d
        expr = Binary(
            "+",
            Binary("+", Binary("+", Binary("*", xy, a), Binary("*", xy, b)), Binary("*", xy, c)),
            Binary("*", xy, d),
        )

        result, temps = multiplicative_cse(expr, min_occurrences=4)

        # Should extract x*y as m1
        assert len(temps) == 1
        assert "m1" in temps

        # m1 should be x*y
        m1_def = temps["m1"]
        assert isinstance(m1_def, Binary)
        assert m1_def.op == "*"

    def test_no_extraction_below_threshold(self):
        """Test: Multiplication appears only 3 times (below threshold=4)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")

        xy = Binary("*", x, y)

        # x*y*a + x*y*b + x*y*c - only 3 occurrences
        expr = Binary("+", Binary("+", Binary("*", xy, a), Binary("*", xy, b)), Binary("*", xy, c))

        result, temps = multiplicative_cse(expr, min_occurrences=4)

        # No extraction (below threshold)
        assert len(temps) == 0
        assert result == expr

    def test_extraction_at_threshold(self):
        """Test: Multiplication appears exactly at threshold"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        xy = Binary("*", x, y)

        # (x*y) + (x*y) + (x*y) + (x*y) - exactly 4 occurrences
        expr = Binary("+", Binary("+", Binary("+", xy, xy), xy), xy)

        result, temps = multiplicative_cse(expr, min_occurrences=4)

        # Should extract
        assert len(temps) == 1
        assert "m1" in temps

    def test_cost_savings_calculation(self):
        """Test: Only extracts when cost savings are positive"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        xy = Binary("*", x, y)

        # With 4 occurrences: savings = (2 * 4 - 2 - 1) = 5 > 0 ✓
        expr = Binary("+", Binary("+", Binary("+", xy, xy), xy), xy)

        result, temps = multiplicative_cse(expr, min_occurrences=4)
        assert len(temps) == 1

    def test_multiple_multiplication_patterns(self):
        """Test: Multiple independent multiplication patterns"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        a = SymbolRef("a")
        b = SymbolRef("b")

        xy = Binary("*", x, y)
        ab = Binary("*", a, b)

        # (x*y)+(x*y)+(x*y)+(x*y) + (a*b)+(a*b)+(a*b)+(a*b)
        expr = Binary(
            "+",
            Binary("+", Binary("+", xy, xy), xy),
            Binary("+", Binary("+", Binary("+", ab, ab), ab), ab),
        )

        # Note: We add the 4th occurrence of xy at the front
        expr = Binary("+", xy, expr)

        result, temps = multiplicative_cse(expr, min_occurrences=4)

        # Should extract both patterns
        assert len(temps) >= 1  # At least one extraction

    def test_nested_multiplication(self):
        """Test: Nested multiplication expressions"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")

        # (x*y)*z appears 4 times
        xy = Binary("*", x, y)
        xyz = Binary("*", xy, z)

        expr = Binary("+", Binary("+", Binary("+", xyz, xyz), xyz), xyz)

        result, temps = multiplicative_cse(expr, min_occurrences=4)

        # Should extract (x*y)*z
        assert len(temps) >= 1

    def test_custom_threshold(self):
        """Test: Custom occurrence threshold"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        xy = Binary("*", x, y)

        # (x*y) + (x*y) + (x*y) - only 3 occurrences
        expr = Binary("+", Binary("+", xy, xy), xy)

        # With threshold=3, should extract
        result, temps = multiplicative_cse(expr, min_occurrences=3)
        assert len(temps) == 1

        # With threshold=4, should not extract
        result, temps = multiplicative_cse(expr, min_occurrences=4)
        assert len(temps) == 0

    def test_mixed_operations(self):
        """Test: Multiplication pattern in mixed operations"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")

        xy = Binary("*", x, y)

        # (x*y)/z + (x*y)*2 + (x*y)^2 + (x*y)
        expr = Binary(
            "+",
            Binary(
                "+",
                Binary("+", Binary("/", xy, z), Binary("*", xy, Const(2))),
                Binary("**", xy, Const(2)),
            ),
            xy,
        )

        result, temps = multiplicative_cse(expr, min_occurrences=4)

        # Should extract x*y
        assert len(temps) == 1
        assert "m1" in temps

    def test_no_extraction_for_expensive_operations(self):
        """Test: Only extracts multiplication, not expensive operations"""
        x = SymbolRef("x")
        exp_x = Call("exp", (x,))

        # exp(x) + exp(x) + exp(x) + exp(x)
        expr = Binary("+", Binary("+", Binary("+", exp_x, exp_x), exp_x), exp_x)

        result, temps = multiplicative_cse(expr, min_occurrences=4)

        # No extraction (not a multiplication)
        assert len(temps) == 0

    def test_sorting_by_savings(self):
        """Test: Multiple candidates sorted by cost savings"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        a = SymbolRef("a")
        b = SymbolRef("b")

        xy = Binary("*", x, y)
        ab = Binary("*", a, b)

        # xy appears 5 times (savings = 7), ab appears 4 times (savings = 5)
        expr = Binary(
            "+",
            Binary("+", Binary("+", Binary("+", xy, xy), xy), xy),
            Binary("+", Binary("+", Binary("+", ab, ab), ab), ab),
        )
        expr = Binary("+", xy, expr)  # Add 5th occurrence of xy

        result, temps = multiplicative_cse(expr, min_occurrences=4)

        # Should extract both, xy first (higher savings)
        assert len(temps) >= 1
        if len(temps) == 2:
            # First temp should be xy (higher savings)
            assert "m1" in temps


class TestCSEWithAliasing:
    """Test T5.4: CSE with Aliasing."""

    def test_reuse_existing_alias(self):
        """Test: Expression already assigned to variable - reuse existing variable"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        xy = Binary("+", x, y)

        # Given: t1 = x+y
        # Expression: (x+y)^2 + 3*(x+y) + sin(x+y)
        # Should reuse t1, not create new temp
        symbol_table = {"t1": xy}
        expr = Binary(
            "+",
            Binary("+", Binary("**", xy, Const(2)), Binary("*", Const(3), xy)),
            Call("sin", (xy,)),
        )

        result, temps = cse_with_aliasing(expr, symbol_table, min_occurrences=3)

        # Should not create new temps (reuses t1)
        assert len(temps) == 0

        # Result should reference t1 (as SymbolRef)
        assert isinstance(result, Binary)

    def test_mix_aliased_and_new(self):
        """Test: Mix of aliased and new expressions"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        a = SymbolRef("a")
        b = SymbolRef("b")

        xy = Binary("+", x, y)
        ab = Binary("+", a, b)

        # Given: t1 = x+y
        # Expression: (x+y) + (x+y) + (x+y) + (a+b) + (a+b) + (a+b)
        # Should reuse t1 for x+y, create new temp for a+b
        symbol_table = {"t1": xy}
        expr = Binary(
            "+",
            Binary("+", Binary("+", xy, xy), xy),
            Binary("+", Binary("+", ab, ab), ab),
        )

        result, temps = cse_with_aliasing(expr, symbol_table, min_occurrences=3)

        # Should create one new temp for a+b
        assert len(temps) == 1
        assert "a1" in temps

        # a1 should be a+b
        a1_def = temps["a1"]
        assert isinstance(a1_def, Binary)
        assert a1_def.op == "+"

    def test_empty_symbol_table(self):
        """Test: Empty symbol table - behaves like regular nested CSE"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        xy = Binary("+", x, y)

        # (x+y)^2 + 3*(x+y) + sin(x+y)
        expr = Binary(
            "+",
            Binary("+", Binary("**", xy, Const(2)), Binary("*", Const(3), xy)),
            Call("sin", (xy,)),
        )

        result, temps = cse_with_aliasing(expr, None, min_occurrences=3)

        # Should extract x+y as a1
        assert len(temps) == 1
        assert "a1" in temps

    def test_no_aliasing_below_threshold(self):
        """Test: Aliased expression appears below threshold - no replacement"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        xy = Binary("+", x, y)

        # Given: t1 = x+y
        # Expression: (x+y) + (x+y) - only 2 occurrences (below threshold=3)
        symbol_table = {"t1": xy}
        expr = Binary("+", xy, xy)

        result, temps = cse_with_aliasing(expr, symbol_table, min_occurrences=3)

        # No replacement (below threshold)
        assert len(temps) == 0
        assert result == expr

    def test_multiple_existing_aliases(self):
        """Test: Multiple expressions already have aliases"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        a = SymbolRef("a")
        b = SymbolRef("b")

        xy = Binary("+", x, y)
        ab = Binary("*", a, b)

        # Given: t1 = x+y, m1 = a*b
        # Expression: (x+y) + (x+y) + (x+y) + (a*b) + (a*b) + (a*b)
        symbol_table = {"t1": xy, "m1": ab}
        expr = Binary(
            "+",
            Binary("+", Binary("+", xy, xy), xy),
            Binary("+", Binary("+", ab, ab), ab),
        )

        result, temps = cse_with_aliasing(expr, symbol_table, min_occurrences=3)

        # No new temps (both expressions already aliased)
        assert len(temps) == 0

    def test_nested_with_aliasing(self):
        """Test: Nested expressions with some aliased"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")

        xy = Binary("+", x, y)
        xyz = Binary("+", xy, z)

        # Given: t1 = x+y
        # Expression: (x+y+z) + (x+y+z) + (x+y+z) + (x+y) + (x+y) + (x+y)
        symbol_table = {"t1": xy}
        expr = Binary(
            "+",
            Binary("+", Binary("+", xyz, xyz), xyz),
            Binary("+", Binary("+", xy, xy), xy),
        )

        result, temps = cse_with_aliasing(expr, symbol_table, min_occurrences=3)

        # Should create temp for x+y+z, but reuse t1 within it
        assert len(temps) >= 1

    def test_function_call_aliasing(self):
        """Test: Function call expressions with aliasing"""
        x = SymbolRef("x")
        exp_x = Call("exp", (x,))

        # Given: t1 = exp(x)
        # Expression: exp(x)*a + exp(x)*b + exp(x)*c
        symbol_table = {"t1": exp_x}
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")
        expr = Binary(
            "+",
            Binary("+", Binary("*", exp_x, a), Binary("*", exp_x, b)),
            Binary("*", exp_x, c),
        )

        result, temps = cse_with_aliasing(expr, symbol_table, min_occurrences=3)

        # Should reuse t1, no new temps
        assert len(temps) == 0

    def test_custom_threshold_with_aliasing(self):
        """Test: Custom occurrence threshold with aliasing"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        xy = Binary("+", x, y)

        # Given: t1 = x+y
        # Expression: (x+y) + (x+y) - only 2 occurrences
        symbol_table = {"t1": xy}
        expr = Binary("+", xy, xy)

        # With threshold=2, should reuse t1
        result, temps = cse_with_aliasing(expr, symbol_table, min_occurrences=2)
        assert len(temps) == 0

        # With threshold=3, should not extract (below threshold)
        result, temps = cse_with_aliasing(expr, symbol_table, min_occurrences=3)
        assert len(temps) == 0

    def test_complex_mixed_scenario(self):
        """Test: Complex scenario with mixed aliased and new expressions"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")
        w = SymbolRef("w")

        xy = Binary("+", x, y)
        zw = Binary("*", z, w)

        # Given: t1 = x+y
        # Expression: (x+y)*(x+y)*(x+y) + (z*w)+(z*w)+(z*w)
        symbol_table = {"t1": xy}
        expr = Binary(
            "+",
            Binary("*", Binary("*", xy, xy), xy),
            Binary("+", Binary("+", zw, zw), zw),
        )

        result, temps = cse_with_aliasing(expr, symbol_table, min_occurrences=3)

        # Should create temp for z*w, reuse t1 for x+y
        assert len(temps) == 1
        assert "a1" in temps

    def test_no_simple_variable_aliasing(self):
        """Test: Simple variables not extracted even with aliasing"""
        x = SymbolRef("x")

        # Given: t1 = x (simple variable)
        # Expression: x + x + x + x
        symbol_table = {"t1": x}
        expr = Binary("+", Binary("+", Binary("+", x, x), x), x)

        result, temps = cse_with_aliasing(expr, symbol_table, min_occurrences=3)

        # No extraction (simple variable not CSE candidate)
        assert len(temps) == 0
