"""Sprint 39 P5 — `build_index_map` refuses a collapsing domain.

`dict(zip(domain, values))` silently discards earlier positions when the domain
repeats, and `strict=True` does NOT catch it: strict compares lengths, and the
lengths agree. The collapse happens in the `dict` construction afterwards.

⚠ Only the EQUATION-keyed call sites use this. A 220-model scan found five
models with a repeated-symbol declaration domain — all VARIABLE domains — and
`dedupe_repeated_variable_domains` rewrites every one before the AD layer. A
guard on the variable-keyed sites would be dead code whose fail-before has
nothing to fail on (Sprint 39 Day 8 trace).
"""

from __future__ import annotations

import pytest

from src.ir.index_map import RepeatedDomainSymbolError, build_index_map


@pytest.mark.unit
def test_a_distinct_domain_binds_normally():
    assert build_index_map(("i", "j"), ("i1", "i2"), context="t") == {"i": "i1", "j": "i2"}


@pytest.mark.unit
def test_a_repeated_domain_raises_instead_of_collapsing():
    """The defect, made loud.

    Without the guard this returns {'i': 'i2'} — the first position silently
    discarded, and every downstream decision made against half the tuple.
    """
    assert dict(zip(("i", "i"), ("i1", "i2"), strict=True)) == {"i": "i2"}  # the defect
    with pytest.raises(RepeatedDomainSymbolError) as exc:
        build_index_map(("i", "i"), ("i1", "i2"), context="t")
    assert "collapse" in str(exc.value)


@pytest.mark.unit
def test_the_repeat_test_is_case_insensitive_like_gams():
    with pytest.raises(RepeatedDomainSymbolError):
        build_index_map(("I", "i"), ("i1", "i2"), context="t")


@pytest.mark.unit
def test_non_adjacent_and_higher_arity_repeats_are_caught():
    with pytest.raises(RepeatedDomainSymbolError):
        build_index_map(("i", "j", "i"), ("a", "b", "c"), context="t")


@pytest.mark.unit
def test_a_length_mismatch_still_raises_from_strict_zip():
    """`strict=True` is retained for the case it DOES cover."""
    with pytest.raises(ValueError):
        build_index_map(("i", "j"), ("i1",), context="t")


@pytest.mark.unit
def test_the_error_names_its_context_and_the_repeated_symbol():
    """Both call sites are in different layers; the traceback alone does not say
    which one refused."""
    with pytest.raises(RepeatedDomainSymbolError) as exc:
        build_index_map(("t", "t"), ("t1", "t2"), context="empty-equation scan of 'foo'")
    msg = str(exc.value)
    assert "empty-equation scan of 'foo'" in msg
    assert "['t']" in msg
