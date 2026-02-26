"""Tests for lead/lag indexing in parameter assignment LHS.

Sprint 21 Day 4: Extends _extract_indices() and _extract_indices_with_subset()
to handle lead/lag syntax (i+1, t-1, t++expr) in parameter assignments.
Unblocks GAMSlib models imsl, sarf, tfordy.
"""

from src.ir.ast import Call, Const, IndexOffset, Unary
from src.ir.parser import parse_model_text


class TestLinearLeadParamAssign:
    """Test linear lead (i+N) in parameter assignment LHS."""

    def test_simple_linear_lead(self):
        """Test p(t+1) = 1 stores IndexOffset in expressions."""
        gams = """
Set t / 1*5 /;
Parameter p(t);
p(t+1) = 1;
"""
        model = parse_model_text(gams)
        param = model.params["p"]
        assert len(param.expressions) == 1
        key, _expr = param.expressions[0]
        assert len(key) == 1
        assert isinstance(key[0], IndexOffset)
        assert key[0].base == "t"
        assert key[0].circular is False
        # Offset should be a positive constant
        assert isinstance(key[0].offset, Const)
        assert key[0].offset.value == 1

    def test_multi_index_with_lead(self):
        """Test yv(te,te+3,s,cl,k) = expr — tfordy pattern."""
        gams = """
Set te / 1*10 /;
Set s / a, b /;
Set cl / x, y /;
Set k / 1*3 /;
Parameter yv(te,te,s,cl,k);
Scalar val / 5 /;
yv(te,te+3,s,cl,k) = val;
"""
        model = parse_model_text(gams)
        param = model.params["yv"]
        assert len(param.expressions) == 1
        key, _expr = param.expressions[0]
        assert len(key) == 5
        # First index is plain 'te'
        assert key[0] == "te"
        # Second index is te+3 (IndexOffset)
        assert isinstance(key[1], IndexOffset)
        assert key[1].base == "te"
        assert key[1].circular is False
        # Remaining are plain strings
        assert key[2] == "s"
        assert key[3] == "cl"
        assert key[4] == "k"


class TestLinearLagParamAssign:
    """Test linear lag (i-N) in parameter assignment LHS."""

    def test_simple_linear_lag(self):
        """Test avl(t,t-1) = 1 — tfordy pattern."""
        gams = """
Set t / 1*10 /;
Parameter avl(t,t);
avl(t,t-1) = 1;
"""
        model = parse_model_text(gams)
        param = model.params["avl"]
        assert len(param.expressions) == 1
        key, _expr = param.expressions[0]
        assert len(key) == 2
        assert key[0] == "t"
        assert isinstance(key[1], IndexOffset)
        assert key[1].base == "t"
        assert key[1].circular is False
        assert isinstance(key[1].offset, Const)
        assert key[1].offset.value == -1

    def test_multiple_lag_assignments(self):
        """Test multiple lag assignments to same parameter — tfordy pattern."""
        gams = """
Set t / 1*10 /;
Parameter avl(t,t);
avl(t,t-1) = 1;
avl(t,t-2) = 1;
"""
        model = parse_model_text(gams)
        param = model.params["avl"]
        assert len(param.expressions) == 2
        # First: t-1
        key1, _ = param.expressions[0]
        assert isinstance(key1[1], IndexOffset)
        assert key1[1].offset.value == -1
        # Second: t-2
        key2, _ = param.expressions[1]
        assert isinstance(key2[1], IndexOffset)
        assert key2[1].offset.value == -2


class TestCircularLeadParamAssign:
    """Test circular lead (t++expr) in parameter assignment LHS."""

    def test_circular_lead_constant(self):
        """Test q(t++1) = expr — circular lead with constant offset."""
        gams = """
Set t / 1*5 /;
Parameter q(t);
q(t++1) = 1;
"""
        model = parse_model_text(gams)
        param = model.params["q"]
        assert len(param.expressions) == 1
        key, _expr = param.expressions[0]
        assert len(key) == 1
        assert isinstance(key[0], IndexOffset)
        assert key[0].base == "t"
        assert key[0].circular is True


class TestConditionalLeadLagParamAssign:
    """Test conditional parameter assignments with lead/lag."""

    def test_conditional_with_lead(self):
        """Test w(m+1,n)$w(m,n) = expr — imsl conditional pattern."""
        gams = """
Set m / 1*5 /;
Set n / 1*5 /;
Parameter w(m,n);
w(m,n) = 0;
w(m+1,n)$w(m,n) = 1;
"""
        model = parse_model_text(gams)
        param = model.params["w"]
        # First assignment: w(m,n) = 0 (stored in param.values via domain-over expansion)
        # Second assignment: w(m+1,n)$w(m,n) = 1 (stored in param.expressions due to lead/lag)
        assert len(param.expressions) >= 1
        # Find the lead/lag expression
        lead_exprs = [
            (k, e) for k, e in param.expressions if any(isinstance(idx, IndexOffset) for idx in k)
        ]
        assert len(lead_exprs) == 1
        key, _expr = lead_exprs[0]
        assert isinstance(key[0], IndexOffset)
        assert key[0].base == "m"
        assert key[0].circular is False
        assert key[1] == "n"


class TestComplexOffsetExprParamAssign:
    """Test complex offset expressions (offset_func / offset_paren) in LHS."""

    def test_function_call_in_offset(self):
        """Test w(m+floor((ord(n)-1)/k),n) — imsl pattern with func call offset."""
        gams = """
Set m / 1*5 /;
Set n / 1*5 /;
Scalar k / 2 /;
Parameter w(m,n);
w(m+floor((ord(n)-1)/k),n) = 1;
"""
        model = parse_model_text(gams)
        param = model.params["w"]
        assert len(param.expressions) == 1
        key, _expr = param.expressions[0]
        assert len(key) == 2
        # First index: m+floor(...) — IndexOffset with Call offset
        assert isinstance(key[0], IndexOffset)
        assert key[0].base == "m"
        assert key[0].circular is False
        assert isinstance(key[0].offset, Call)
        assert key[0].offset.func == "floor"
        # Second index: plain n
        assert key[1] == "n"
        # Verify to_gams_string handles ParamRef in offset
        gams_str = key[0].to_gams_string()
        assert gams_str.startswith("m+floor(")
        assert "k" in gams_str

    def test_parenthesized_offset(self):
        """Test p(l,t-(ord(l)-1)) — offset_paren with arithmetic expression."""
        gams = """
Set t / 1*10 /;
Set l / a, b, c /;
Parameter p(l,t);
p(l,t-(ord(l)-1)) = 1;
"""
        model = parse_model_text(gams)
        param = model.params["p"]
        assert len(param.expressions) == 1
        key, _expr = param.expressions[0]
        assert key[0] == "l"
        assert isinstance(key[1], IndexOffset)
        assert key[1].base == "t"
        # Offset is Unary(-, Binary(-, Call(ord, ...), Const(1)))
        assert isinstance(key[1].offset, Unary)
        assert key[1].offset.op == "-"
