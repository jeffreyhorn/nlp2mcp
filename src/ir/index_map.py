"""Index-substitution maps that cannot silently collapse a repeated domain.

Sprint 39 P5 (`SPRINT_39/POSITIONAL_DOMAIN_SURVEY.md`).

``dict(zip(domain, values))`` is the natural way to bind a domain's symbols to a
concrete instance, and it is **silently wrong** when the domain repeats a
symbol: ``dict(zip(("i", "i"), ("i1", "i2")))`` is ``{"i": "i2"}``. The first
position is discarded without any error, so every downstream decision is made
against half the tuple.

``strict=True`` does **not** catch this. It compares *lengths*, and the lengths
agree — the collapse happens in the ``dict`` construction afterwards.

This helper raises instead. That converts a wrong answer into a diagnosable
failure, which is the trade this sprint kept paying for: dyncge and lnts both
*compiled* and *solved* while being wrong, and cost a day each to find.

⚠ WHY RAISING IS SAFE HERE, MEASURED. A 220-model corpus scan found **five**
models with a repeated-symbol declaration domain — ``ferts``, ``lop``,
``maxmin``, ``sarf``, ``tricp`` — and **every one is a VARIABLE domain**. No
corpus model declares a repeated EQUATION domain, and the callers below are
equation-keyed, so this cannot regress any model that translates today.

⚠ AND WHY VARIABLE-KEYED SITES DO NOT USE THIS. ``dedupe_repeated_variable_domains``
(`src/kkt/repeated_domain.py`) rewrites every repeated *variable* domain to fresh
aliases before the AD layer — measured on all five models, zero repeats
remaining. A guard there would be dead code whose fail-before has nothing to
fail on. The protection is complete for variables and absent for equations,
which is exactly why only the equation-keyed callers are guarded.
"""

from __future__ import annotations


class RepeatedDomainSymbolError(ValueError):
    """A domain repeats a symbol, so an index map would silently collapse.

    GAMS binds a repeated controlling index in an equation *definition*
    diagonally — the instances are the diagonal, not the full product. Nothing
    in the emitter implements that today, so the honest behaviour is to refuse
    rather than to emit a map that has quietly dropped positions.
    """


def assert_no_repeated_symbol(domain: tuple[str, ...] | list[str], *, context: str) -> None:
    """Refuse a domain that repeats a symbol, without building a map.

    Split out so a caller binding MANY instances of ONE domain can validate
    once instead of per instance: the domain is constant across the loop, so
    re-checking it adds cost without adding safety after the first iteration
    (PR #1736 review). ``build_index_map`` still checks, for callers that bind
    a single instance and would otherwise have to remember to call this.
    """
    # Single pass: detect duplicates AND collect them together. The previous
    # form tested `len(lowered) != len(set(lowered))` and then, on the raise
    # path, rebuilt the duplicate list with `lowered.count(d)` — O(n²) (PR #1736
    # review). One pass over a `seen` set gives both answers in O(n) and removes
    # the need to reason about which branch the quadratic work sat on.
    seen: set[str] = set()
    dupes: set[str] = set()
    for d in domain:
        low = d.lower()
        if low in seen:
            dupes.add(low)
        seen.add(low)
    if dupes:
        raise RepeatedDomainSymbolError(
            f"{context}: domain {tuple(domain)} repeats {sorted(dupes)}, so an index map "
            f"would silently collapse — a repeated symbol binds only its last "
            f"occurrence and discards the earlier position(s). GAMS binds a "
            f"repeated controlling index diagonally in an equation definition; "
            f"that is not implemented here, so this is refused rather than "
            f"emitted incorrectly. See "
            f"docs/planning/EPIC_4/SPRINT_39/POSITIONAL_DOMAIN_SURVEY.md."
        )


def build_index_map(
    domain: tuple[str, ...] | list[str],
    values: tuple[str, ...] | list[str],
    *,
    context: str,
) -> dict[str, str]:
    """Bind ``domain`` symbols to ``values``, refusing a collapsing domain.

    Args:
        domain: the controlling index symbols, in declaration order.
        values: one concrete element per position; must match ``domain`` in
            length, which is checked by ``zip(strict=True)``.
        context: what is being bound, for the error message — a caller name or
            an equation name. Included because the two call sites are in
            different layers and the traceback alone does not say which.

    Returns:
        The substitution map.

    Raises:
        RepeatedDomainSymbolError: if ``domain`` repeats a symbol
            (case-insensitively, because GAMS identifiers are).
        ValueError: if the lengths differ (from ``zip(strict=True)``).
    """
    assert_no_repeated_symbol(domain, context=context)
    return dict(zip(domain, values, strict=True))
