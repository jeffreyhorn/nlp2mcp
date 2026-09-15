"""Row-level attribution predicates for a persisted or live MCP solve result.

⚠ WHY THIS LIVES IN ``src/`` AND NOT IN THE AUDIT SCRIPT (PR #1740 review).
These predicates are pure functions of a result dict — no GAMS, no filesystem,
no database. `src/diagnostics/convexity_numerical.py` needs them on its
RESULT-ONLY path (`check_convexity_from_results`), which callers reach with
already-computed dictionaries and without running anything.

Importing them from `scripts.sprint_audit` made that path depend on a package
the wheel does not ship: `pyproject.toml` sets ``include = ["src*"]``, so an
installed nlp2mcp would raise ``ModuleNotFoundError`` on a previously
self-contained API. `scripts/sprint_audit/check_mcp_solve_attribution.py`
re-exports everything here, so the audit tool and its tests are unaffected.

⚠ The distinction these encode has been mis-read at seven call sites in
Sprint 39 P7, so it is worth stating once more:

* `status_is_ours`              — ATTRIBUTION. Did our model produce this status?
* `own_solve_completed`         — COMPLETION. Did our model run to the end?
* `status_is_ours_and_complete` — the conjunction, which is what a consumer
  reading an objective, proving non-convexity, or recording a match needs.
"""

from __future__ import annotations

#: The verdicts that mean "our emitted model did not produce this status".
_NOT_OUR_STATUS = frozenset({"EMBEDDED-ONLY", "MCP-NO-STATUS", "NO-SOLVE", "ERROR"})

#: Every value `mcp_attribution` may legitimately hold. Anything else — a typo,
#: an explicit ``null``, a non-string — is malformed and must NOT be read as an
#: attributed solve. ⚠ `schema.json`'s enum is only a backstop here: `jsonschema`
#: is an undeclared optional dependency, so validation may never have run on the
#: row being inspected, and this predicate also accepts LIVE result dicts that
#: no schema ever sees.
_KNOWN_VERDICTS = frozenset(
    {"MCP-SOLVED", "MCP-FAILED", "MCP-NO-STATUS", "EMBEDDED-ONLY", "NO-SOLVE", "ERROR"}
)


#: The completion-flag field name, in one place so a rename cannot half-land.
_COMPLETED_KEY = "mcp_completed_own_solve"


def own_solve_completed(row: dict) -> bool:
    """Did our model run to COMPLETION and report this status itself?

    ⚠ IDENTITY, not truthiness. ``bool("false")`` is True, so the likeliest
    malformed serialisation of a boolean would read as completed — and this flag
    is the only thing separating a genuine failing solve from an abort that left
    a stale status above its abort line. Absent reads as NOT completed, which is
    the conservative answer for a question about what happened.
    """
    return row.get(_COMPLETED_KEY) is True


def completion_flag_is_malformed(row: dict) -> bool:
    """The flag is PRESENT and is not the literal ``True`` or ``False``.

    Distinguished from "absent" because absence is the legacy shape and must
    stay permissive, while a present-but-corrupt value is evidence the row
    cannot be trusted — the schema declares a boolean.
    """
    if _COMPLETED_KEY not in row:
        return False
    return row[_COMPLETED_KEY] is not True and row[_COMPLETED_KEY] is not False


def status_is_ours_and_complete(row: dict) -> bool:
    """Ours AND the solve actually finished — what most consumers want.

    ⚠ `status_is_ours` is ATTRIBUTION-ONLY by design, so it accepts
    ``MCP-SOLVED`` whose ``mcp_completed_own_solve`` is absent or literally
    ``False``: the two fields are independently valid under the schema, so that
    contradictory combination is storable. Every consumer that goes on to read
    an OBJECTIVE, prove NON-CONVEXITY, or record a MATCH needs completion too.

    That gap has now been found at seven separate call sites in Sprint 39 P7,
    each time as "the consumer forgot to add the completion check". This exists
    so there is nothing to remember: ask for the property you need.

    ⚠ Legacy rows — no ``mcp_attribution`` at all — stay permissive, exactly as
    in `status_is_ours`. Absence is a known state; re-classifying the committed
    corpus is not on the table.
    """
    if not status_is_ours(row):
        return False
    # ⚠ ONE definition of "legacy", and it lives in `status_is_ours` above
    # (PR #1740 review): a genuine legacy row carries NEITHER field, and a
    # hybrid is judged on the flag it does carry. Re-stating that rule here
    # measured as UNTESTABLE — with `status_is_ours` fixed, no row reaches this
    # line where the two definitions differ, so a mutant restoring the old
    # one-field form survived every test. A second copy that cannot be
    # discriminated is not defence in depth; it is a second thing to drift.
    if "mcp_attribution" not in row:
        return True
    return own_solve_completed(row)


def status_is_ours(row: dict) -> bool:
    """Did OUR emitted model produce the status recorded in ``row`` itself?

    ⚠ NOT the same question as "is this a usable answer". ``MCP-SOLVED`` answers
    that one; this is the weaker and more often needed property, true also for a
    solve that ran to completion and reported a genuine failing status. The two
    have now been conflated at five separate call sites in Sprint 39 P7 — the
    retry gate, `kkt_residual`'s divergence mapping, `convexity_numerical`'s
    infeasible path, the rejection counter, and the comparison guard — each time
    costing a real finding or inventing a false one. Defined once here so the
    next consumer asks rather than re-derives.

    Args:
        row: a persisted ``mcp_solve`` entry, or a live ``solve_mcp`` result.

    Returns:
        True when the status is attributable to our model. ⚠ Also True when the
        ``mcp_attribution`` KEY IS ABSENT: rows written before attribution
        existed must keep their previous behaviour, and treating "unknown" as
        "not ours" would silently re-classify the committed corpus.

        ⚠ Everything else fails CLOSED — an explicit ``null``, an unrecognised
        verdict, a non-boolean completion flag. Absence is a known state; a
        malformed value is not, and this predicate gates the infeasibility and
        match paths.
    """
    # ⚠ KEY ABSENT is the ONLY permissive case (PR #1740 review). An earlier
    # revision used `row.get(...)`, which conflates an omitted field — the
    # intended legacy shape — with an explicitly present `null`. The schema
    # declares this field a non-null string, so a row carrying `null` is
    # MALFORMED and took the legacy allow path.
    # ⚠ The malformed-flag check runs BEFORE the legacy fast path (PR #1740
    # review). An earlier revision returned early on a missing verdict, so
    # `{"mcp_completed_own_solve": "false"}` — a HYBRID, not a legacy row — was
    # accepted as attributed, and this helper is documented as fail-closed.
    # A genuine legacy row carries NEITHER field.
    if completion_flag_is_malformed(row):
        return False

    if "mcp_attribution" not in row:
        # ⚠ A GENUINE legacy row carries NEITHER field (PR #1740 review). An
        # earlier revision keyed the compatibility path on the VERDICT alone, so
        # a HYBRID row — completion flag present, verdict absent — took the
        # legacy allow path even when the flag said `False`, i.e. even when the
        # row itself stated our solve did NOT complete. Downstream that let
        # objective and comparison consumers trust stale scalars from a solve
        # the row disclaims. The comment above already said "neither field";
        # the code checked one.
        if "mcp_completed_own_solve" not in row:
            return True
        return own_solve_completed(row)

    verdict = row["mcp_attribution"]
    # ⚠ FAIL CLOSED on anything unrecognised. An earlier revision fell through
    # to `return True`, so a typo or corrupt value — `"MCP-SOLVE"`, `None`, a
    # non-string — was treated as an attributed solve and bypassed every guard
    # built on this predicate.
    # ⚠ `isinstance` FIRST: `x not in frozenset` raises TypeError for an
    # unhashable value, so a corrupt row holding a list or dict would crash the
    # caller rather than fail closed. A guard that raises is not a guard.
    if not isinstance(verdict, str) or verdict not in _KNOWN_VERDICTS:
        return False
    if verdict in _NOT_OUR_STATUS:
        return False
    if verdict == "MCP-FAILED":
        # Ours, but only if it ran to completion — an abort leaves a stale
        # status above its abort line that belongs to nothing.
        return own_solve_completed(row)
    return True  # MCP-SOLVED, with a valid or absent completion flag
