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
    lowered = [d.lower() for d in domain]
    if len(lowered) != len(set(lowered)):
        dupes = sorted({d for d in lowered if lowered.count(d) > 1})
        raise RepeatedDomainSymbolError(
            f"{context}: domain {tuple(domain)} repeats {dupes}, so an index map "
            f"would silently collapse — {tuple(values)} would bind only the last "
            f"occurrence of each repeated symbol and discard the earlier "
            f"position(s). GAMS binds a repeated controlling index diagonally in "
            f"an equation definition; that is not implemented here, so this is "
            f"refused rather than emitted incorrectly. See "
            f"docs/planning/EPIC_4/SPRINT_39/POSITIONAL_DOMAIN_SURVEY.md."
        )
    return dict(zip(domain, values, strict=True))
