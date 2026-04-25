"""Issue #1311 regression: AD must recognize concrete elements as instances
of a dynamic-subset symbolic index when the subset is declared as a child of
a parent set whose membership is known.

Pre-fix, `_is_concrete_instance_of("1964-i", "ku", config)` returned False
even though `ku` is declared `Set ku(k);` (a dynamic subset of `k`) and
`"1964-i" ∈ k`. The criterion of qabel/abel uses
`sum((ku, m, mp), (u(m, ku) - utilde(m, ku)) * lambda(m, mp) * (u(mp, ku) - ...))`,
so AD's failure to bind concrete `k` elements to the symbolic `ku` index
caused the entire u-criterion-gradient term to be silently dropped — every
`∂J/∂u(m, k)` came out as `Const(0.0)`.

The fix routes `_is_concrete_instance_of` through `resolve_set_members`,
which already had the issue-#723 dynamic-subset → parent-set fallback. A
new `quiet=True` kwarg on `resolve_set_members` suppresses the per-call
warning that the membership-check use site would otherwise spam.
"""

from __future__ import annotations

import pytest

from src.ad.derivative_rules import _is_concrete_instance_of
from src.config import Config
from src.ir.model_ir import ModelIR
from src.ir.symbols import SetDef


def _make_dynamic_subset_ir() -> ModelIR:
    """ModelIR with parent set `k` and dynamic subset `ku(k)` whose
    members are populated at runtime (not at parse time, so .members is
    empty).
    """
    ir = ModelIR()
    ir.sets["k"] = SetDef(name="k", domain=(), members=["1964-i", "1964-ii", "1964-iii"])
    # Dynamic subset declaration: `Set ku(k); ku(k) = yes$cond;` — the
    # SetDef is constructed without explicit members because they're
    # assigned at runtime.
    ir.sets["ku"] = SetDef(name="ku", domain=("k",), members=[])
    return ir


@pytest.mark.unit
def test_concrete_in_parent_set_matches_dynamic_subset():
    """A concrete element of a parent set must be recognized as an instance
    of a child dynamic subset that has empty static members.
    """
    ir = _make_dynamic_subset_ir()
    config = Config(model_ir=ir)

    assert _is_concrete_instance_of("1964-i", "ku", config) is True, (
        "Pre-fix: this returned False because `ku.members == []`, even though "
        "ku is declared `Set ku(k);` (subset of `k`) and '1964-i' is in `k`. "
        "Post-fix: routing through resolve_set_members's issue-#723 parent "
        "fallback recognizes ku ⊆ k and accepts the parent's members."
    )


@pytest.mark.unit
def test_concrete_outside_parent_set_does_not_match_dynamic_subset():
    """A concrete element NOT in the parent set must still be rejected,
    even when checking a dynamic subset.
    """
    ir = _make_dynamic_subset_ir()
    config = Config(model_ir=ir)

    assert _is_concrete_instance_of("not-in-k", "ku", config) is False


@pytest.mark.unit
def test_direct_parent_set_membership_unchanged():
    """The direct-set-membership path must remain definitive — a concrete
    element either is or isn't in a set whose members are populated.
    """
    ir = _make_dynamic_subset_ir()
    config = Config(model_ir=ir)

    assert _is_concrete_instance_of("1964-i", "k", config) is True
    assert _is_concrete_instance_of("not-in-k", "k", config) is False


@pytest.mark.unit
def test_dynamic_subset_with_no_parent_returns_false_definitively():
    """If a dynamic subset has empty members AND no parent domain that
    resolves to non-empty members, return False rather than spuriously
    matching via the heuristic (preserves the pre-fix definitive behavior
    when set/alias resolution genuinely fails).
    """
    ir = ModelIR()
    # Pathological: subset declared but parent isn't known.
    ir.sets["empty_subset"] = SetDef(name="empty_subset", domain=(), members=[])
    config = Config(model_ir=ir)

    assert _is_concrete_instance_of("anything", "empty_subset", config) is False


@pytest.mark.unit
def test_alias_to_dynamic_subset_resolves_via_chain():
    """Alias chains that terminate at a dynamic subset must still resolve
    via the parent fallback. (Less common in practice but worth locking
    in so the alias path doesn't regress when the set path is fixed.)
    """
    from src.ir.symbols import AliasDef

    ir = _make_dynamic_subset_ir()
    ir.aliases["kup"] = AliasDef(name="kup", target="ku")
    config = Config(model_ir=ir)

    # alias kup → ku → (dynamic subset of) k → members of k.
    assert _is_concrete_instance_of("1964-i", "kup", config) is True


@pytest.mark.unit
def test_concrete_value_not_treated_as_symbolic_set_when_model_ir_present():
    """Issue #1312 regression: when `model_ir` is available and `symbolic`
    is NOT a registered set or alias, return False definitively rather than
    falling through to the prefix-based heuristic.

    Pre-fix, `_is_concrete_instance_of("q75", "q7", config)` returned True
    via the heuristic (`"q75".startswith("q7")` and `"5".isdigit()`), even
    though `q7` is itself a concrete element of set `k`, not a symbolic
    set name. That spurious True caused qabel's stat_u/stat_x emission to
    grow 60+ phantom stateq lag terms (`k-9 .. k-68`) post-#1311 and
    blow up the MCP objective to ~1.4e17.

    Post-fix: when model_ir is present, the heuristic only fires for known
    sets/aliases. Two concrete values that share a digit-suffix prefix no
    longer match.
    """
    ir = ModelIR()
    ir.sets["k"] = SetDef(name="k", domain=(), members=["q1", "q2", "q7", "q75"])
    config = Config(model_ir=ir)

    # "q7" is a concrete element of `k`, not a set name. Pre-fix, the
    # heuristic at the bottom of `_is_concrete_instance_of` returned True
    # for ("q75", "q7"). Post-fix, the function returns False because "q7"
    # is not a registered set/alias and model_ir is available.
    assert _is_concrete_instance_of("q75", "q7", config) is False, (
        "Pre-#1312 fix: returned True via prefix heuristic — `q75` starts "
        "with `q7` and the suffix `5` is a digit. Post-fix: with model_ir "
        "available, only registered sets/aliases activate the heuristic; "
        "an unrecognized name (a concrete element like `q7`) returns False."
    )

    # Sanity: the legitimate symbolic case still works.
    assert _is_concrete_instance_of("q1", "k", config) is True


@pytest.mark.unit
def test_concrete_prefix_heuristic_still_works_without_model_ir():
    """The prefix-and-digit heuristic must stay available when model_ir is
    NOT supplied, for legacy unit-test paths that don't construct a Config.
    """
    # No config: fall through to heuristic.
    assert _is_concrete_instance_of("i1", "i", None) is True
    assert _is_concrete_instance_of("j23", "j", None) is True
    # Heuristic correctly rejects mismatched prefix.
    assert _is_concrete_instance_of("j1", "i", None) is False


@pytest.mark.unit
def test_qabel_abel_criterion_u_gradient_end_to_end():
    """End-to-end check via the public AD entry: the criterion's u-quadratic
    gradient (`sum((ku, m, mp), ...)` with `ku ⊆ k`) must produce non-zero
    derivatives for every `u(m, k)` instance in the gradient table.

    Pre-fix, every entry was `Const(0.0)`. Post-fix, all should be
    non-zero AST expressions (the symmetric quadratic form).

    Skipped if the gamslib sources aren't available locally (CI). Mirrors
    the gamslib-skip convention used in
    `tests/unit/ir/test_normalize_scalar_widening.py`.
    """
    import os
    import sys

    src = "data/gamslib/raw/abel.gms"
    if not os.path.exists(src):
        pytest.skip(
            "data/gamslib/raw/abel.gms is gitignored; run "
            "scripts/download_gamslib_raw.sh to populate the corpus."
        )

    sys.setrecursionlimit(50000)
    from src.ad.gradient import compute_objective_gradient
    from src.ir.ast import Const
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file

    model = parse_model_file(src)
    normalize_model(model)
    grad = compute_objective_gradient(model)

    u_zero_count = 0
    u_total_count = 0
    for col_id in range(grad.num_cols):
        var_name, _ = grad.index_mapping.col_to_var[col_id]
        if var_name != "u":
            continue
        u_total_count += 1
        deriv = grad.get_derivative(col_id)
        if isinstance(deriv, Const) and deriv.value == 0.0:
            u_zero_count += 1

    assert u_total_count > 0, "abel must declare a `u` variable"
    assert u_zero_count == 0, (
        "Pre-#1311 fix: all u-gradient entries returned Const(0.0) because "
        "the criterion's `sum((ku, m, mp), ...)` failed to bind concrete k "
        "elements to symbolic ku. Post-fix: every u entry must be a "
        f"non-zero gradient expression. Got {u_zero_count}/{u_total_count} zero entries."
    )
