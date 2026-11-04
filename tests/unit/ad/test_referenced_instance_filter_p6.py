"""Sprint 40 P6 (``SARF_JACOBIAN_DESIGN.md``): the referenced-instance filter.

E1/E2 put the equality path's filter on the inequality and bound paths through
one shared helper (``ReferencedInstanceFilter``); E3 applies it to the objective
gradient; E4 makes ``validate_jacobian_entries`` walk stored entries only.

The filter's whole contract is "skip only instances whose derivative is zero",
so every test here compares against the UNFILTERED path (``_referenced_index_tuples``
forced to ``None``, which is the documented fallback) and demands identical
entries, plus flat work as the declared set grows.
"""

from __future__ import annotations

import math
import sys

import pytest

import src.ad.constraint_jacobian as cj
import src.ad.gradient as gr
from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.config import Config
from src.ir.ast import Const
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_text
from src.validation.numerical import NumericalError, validate_jacobian_entries

# The design's §6 fixture: declared x(i,j) grows with N, every row references
# only x(i,a) with a = j1*j5. The .up bound lands in `inequalities` (E1); the
# .fx bound is Rel.EQ and is processed by _compute_bound_jacobian (E2).
_FIXTURE = """
Set i / i1*i3 /, j / j1*j{n} /, a(j) / j1*j5 /;
Variable z;
Positive Variable x(i,j);
x.up('i1','j1') = 5;
x.fx('i2','j2') = 1;
Equation obj, cap(i);
obj..    z =e= sum((i,a), x(i,a));
cap(i).. sum(a, x(i,a)) =l= 10;
Model m / all /;
solve m using lp minimizing z;
"""

# A maximised objective that references only part of x, so E3's unreferenced
# representative goes through the MAX negation.
_MAX_FIXTURE = """
Set i / i1*i3 /, j / j1*j{n} /, a(j) / j1*j2 /;
Positive Variable x(i,j);
Variable z;
x.up(i,j) = 4;
Equation defz, cap(i);
defz..   z =e= sum((i,a), log(1 + x(i,a)));
cap(i).. sum(a, sqr(x(i,a))) =l= 10;
Model m / all /;
solve m using nlp maximizing z;
"""

# PR #1794 review: a SUBSET binder whose members are spelled differently from
# the declared domain (`s(i) / i2 /` vs `i / I1, I2 /`). Uncanonicalised, the
# filter returned ('i2','i2'), matching no declared column ('I2','I2'): the
# inequality row lost its derivative and E3 stored a zero gradient for it.
_MIXED_CASE_FIXTURE = """
Set i / I1, I2 /;
Set s(i) / i2 /;
Variable x(i,i), z;
x.lo(i,i) = 0;
Equation obj, c, e;
obj.. z =e= sum(s, sqr(x(s,s))) + sum(i, x(i,'I1'));
c.. sum(s, x(s,s)) =g= 1;
e.. sum(s, x(s,'i1')) =e= 1;
Model m / all /; solve m using nlp minimizing z;
"""

# PR #1794 review: a SET name that is also a declared LABEL. Row c('j')'s
# substituted ``x(j)`` is the label 'j', but read as the subset j = {i1} the
# filter emptied the row (the inequality path lost d c('j') / d x('j') = 1).
_NAME_LABEL_COLLISION_FIXTURE = """
Set i / i1, 'j' /;
Set j(i) / i1 /;
Variable x(i), z;
Equation obj, c(i), e(i);
obj.. z =e= sum(i, sqr(x(i) - 1));
c(i).. x(i) =g= 0;
e(i).. x(i) + z =e= 2;
Model m / all /; solve m using nlp minimizing z;
"""


def _translate(src: str, monkeypatch, *, unfiltered: bool = False, simplification=None):
    calls: dict[str, int] = {}

    def counting(module, tag):
        orig = module.differentiate_expr

        def wrapper(*args, **kwargs):
            calls[tag] = calls.get(tag, 0) + 1
            return orig(*args, **kwargs)

        monkeypatch.setattr(module, "differentiate_expr", wrapper)

    counting(cj, "jacobian")
    counting(gr, "gradient")
    if unfiltered:
        monkeypatch.setattr(cj, "_referenced_index_tuples", lambda *a, **k: None)

    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_text(src)
        normalized_eqs, _ = normalize_model(model)
        config = Config(simplification=simplification) if simplification else None
        grad = compute_objective_gradient(model, config)
        j_eq, j_ineq = compute_constraint_jacobian(model, normalized_eqs, config)
    finally:
        sys.setrecursionlimit(old)
        monkeypatch.undo()
    return grad, j_eq, j_ineq, calls


def _jac(j) -> dict:
    return {(r, c): repr(e) for r, row in j.entries.items() for c, e in row.items()}


@pytest.mark.unit
@pytest.mark.parametrize(
    "fixture",
    [_FIXTURE, _MAX_FIXTURE, _MIXED_CASE_FIXTURE, _NAME_LABEL_COLLISION_FIXTURE],
    ids=["min_lp", "max_nlp", "mixed_case_subset", "set_name_label_collision"],
)
@pytest.mark.parametrize(
    "simplification",
    # "none": an unreferenced instance's derivative is a STRUCTURAL zero
    # (``0 - 0``), which the full enumeration stores, so the filter must be off
    # (PR #1794 review) -- on every path, the pre-existing equality one included.
    [None, "none", "basic", "aggressive"],
    ids=["default", "none", "basic", "aggressive"],
)
def test_filtered_paths_equal_the_unfiltered_enumeration(fixture, simplification, monkeypatch):
    src = fixture.format(n=40)
    grad, j_eq, j_ineq, _ = _translate(src, monkeypatch, simplification=simplification)
    ref_grad, ref_eq, ref_ineq, _ = _translate(
        src, monkeypatch, unfiltered=True, simplification=simplification
    )

    assert _jac(j_eq) == _jac(ref_eq)
    assert _jac(j_ineq) == _jac(ref_ineq)
    # E3: every column keeps an entry (consumers read a missing one as None),
    # and every entry is the one the unfiltered path stored.
    assert {c: repr(e) for c, e in grad.entries.items()} == {
        c: repr(e) for c, e in ref_grad.entries.items()
    }
    assert len(grad.entries) == grad.num_cols


@pytest.mark.unit
def test_work_is_flat_in_the_declared_size(monkeypatch):
    """The fail-before shape: unfiltered work grows with |j|, filtered does not."""
    per_n = {}
    for n in (20, 80):
        *_, calls = _translate(_FIXTURE.format(n=n), monkeypatch)
        *_, ref_calls = _translate(_FIXTURE.format(n=n), monkeypatch, unfiltered=True)
        per_n[n] = (calls, ref_calls)
    # Unfiltered: grows with N (the test can see the defect it guards).
    assert per_n[80][1]["jacobian"] > per_n[20][1]["jacobian"]
    assert per_n[80][1]["gradient"] > per_n[20][1]["gradient"]
    # Filtered: identical at both sizes.
    assert per_n[80][0] == per_n[20][0]


@pytest.mark.unit
def test_position_and_label_maps_are_built_once(monkeypatch):
    """A cached map that is rebuilt on every row (``cache.setdefault(k, {…})``)
    keeps every result identical and only shows up as work -- so count builds."""
    filters: list = []
    orig_init = cj.ReferencedInstanceFilter.__init__

    def recording_init(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        filters.append(self)

    monkeypatch.setattr(cj.ReferencedInstanceFilter, "__init__", recording_init)
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_text(_FIXTURE.format(n=60))
        normalized_eqs, _ = normalize_model(model)
        compute_constraint_jacobian(model, normalized_eqs)
    finally:
        sys.setrecursionlimit(old)

    # One filter shared by the equality, inequality and bound paths.
    assert len(filters) == 1
    (f,) = filters
    assert sorted(f._positions) == ["x", "z"]
    assert f.position_map_builds == 2
    assert f.label_map_builds <= 2


def _jacobian_with(entries: dict[tuple[int, int], Const]):
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_text(_FIXTURE.format(n=6))
        normalized_eqs, _ = normalize_model(model)
        _, j_ineq = compute_constraint_jacobian(model, normalized_eqs)
    finally:
        sys.setrecursionlimit(old)
    for (r, c), e in entries.items():
        j_ineq.set_derivative(r, c, e)
    return j_ineq


@pytest.mark.unit
def test_sparse_validation_still_raises_on_a_non_finite_constant():
    j = _jacobian_with({})
    validate_jacobian_entries(j, "J")  # finite: no error

    last_row, last_col = j.num_rows - 1, j.num_cols - 1
    j = _jacobian_with({(last_row, last_col): Const(math.inf)})
    with pytest.raises(NumericalError, match="not finite"):
        validate_jacobian_entries(j, "J")


@pytest.mark.unit
def test_sparse_validation_reports_the_dense_scans_first_error():
    """The dense scan was row-major, so it raised at the lowest (row, col).
    Insert the later error first: dict order must not decide which is reported."""
    j = _jacobian_with({})
    late = (j.num_rows - 1, j.num_cols - 1)
    early = (0, 0)
    j = _jacobian_with({late: Const(math.inf), early: Const(math.nan)})
    with pytest.raises(NumericalError) as info:
        validate_jacobian_entries(j, "J")
    eq_name, eq_idx = j.index_mapping.row_to_eq[0]
    assert eq_name in str(info.value)
    assert "nan" in str(info.value).lower()


@pytest.mark.unit
def test_sparse_validation_ignores_out_of_range_entries():
    """The dense scan never looked outside range(num_rows) x range(num_cols)."""
    j = _jacobian_with({})
    j.entries.setdefault(j.num_rows + 5, {})[0] = Const(math.inf)
    validate_jacobian_entries(j, "J")
