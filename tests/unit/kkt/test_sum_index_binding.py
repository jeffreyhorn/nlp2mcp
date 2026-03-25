"""Tests for sum index binding as implemented by `_compute_index_offset_key`.

These tests cover the index-offset and sentinel behavior needed for Issue #1038:
when a 3D variable x(r, rr, c) appears in a 2D equation DX(r, c) via
sum(rr, X(rr, r, c)), the helper must correctly remap indices so the
stationarity builder can emit the appropriate multipliers.
"""

from src.kkt.stationarity import _SENTINEL_UNMATCHED, _compute_index_offset_key


def _make_model_ir():
    """Build minimal ModelIR with sets r and alias rr."""
    from src.ir.model_ir import ModelIR, SetDef

    model = ModelIR()
    model.sets["r"] = SetDef(name="r", domain=(), members=["Reg1", "Reg2", "Reg3"])
    model.sets["c"] = SetDef(name="c", domain=(), members=["Com1", "Com2"])
    # rr is alias of r
    from types import SimpleNamespace

    model.aliases["rr"] = SimpleNamespace(target="r")
    return model


def test_offset_key_dim_mismatch_sentinel():
    """3D variable in 2D equation should produce sentinel for unmatched dim."""
    model = _make_model_ir()
    eq_domain = ("r", "c")
    var_domain = ("r", "rr", "c")

    # DX(Reg1,Com1) -> x(Reg1,Reg1,Com1)
    key = _compute_index_offset_key(
        ("Reg1", "Com1"), ("Reg1", "Reg1", "Com1"), eq_domain, var_domain, model
    )
    assert key[1] == _SENTINEL_UNMATCHED, "rr position should be sentinel"
    assert key[2] == 0, "c position should have zero offset"


def test_offset_key_varying_offsets():
    """Different entries produce varying offsets in the sum-bound dimension."""
    model = _make_model_ir()
    eq_domain = ("r", "c")
    var_domain = ("r", "rr", "c")

    key1 = _compute_index_offset_key(
        ("Reg1", "Com1"), ("Reg1", "Reg1", "Com1"), eq_domain, var_domain, model
    )
    key2 = _compute_index_offset_key(
        ("Reg1", "Com1"), ("Reg2", "Reg1", "Com1"), eq_domain, var_domain, model
    )
    # Position 0 should have different offsets (sum variable iterating)
    assert key1[0] != key2[0], "Sum variable position should produce varying offsets"
    # Position 1 (rr) should be sentinel in both
    assert key1[1] == _SENTINEL_UNMATCHED
    assert key2[1] == _SENTINEL_UNMATCHED
    # Position 2 (c) should be 0 in both
    assert key1[2] == 0
    assert key2[2] == 0
