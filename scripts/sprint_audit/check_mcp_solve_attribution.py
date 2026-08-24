#!/usr/bin/env python3
"""Did the MCP actually solve, or did only the embedded NLP?

A ``--nlp-presolve`` emit warm-starts by running the original model inside the
generated file, then solves the MCP and reads the objective back::

    $include "data/gamslib/raw/<model>.gms"   * solves the NLP, sets <objvar>.l
    Solve mcp_model using MCP;                 * if this ABORTS, .l is untouched
    nlp2mcp_obj_val = <objvar>.l;              * still the NLP's own answer

On a **successful** run that listing therefore holds *two or more* solve
summaries — the embedded source's, then ours. **The failing case holds only
one**, and that asymmetry is the whole point: an MCP that aborts before its
solve never emits a summary at all, so the listing looks exactly like a
single-solve run whose one status happens to be someone else's.

**If the MCP solve aborts, the objective read returns the NLP's own value and
the comparison matches itself.** The recorded status is wrong the same way:
``parse_gams_listing`` takes the *last* ``MODEL STATUS`` in the listing, which
is the NLP's when the MCP produced none.

`weapons` is the discovered instance (Sprint 38 Day 9): one solve summary in the
whole listing (the embedded NLP's, MS-2 @ 1735.5696), the MCP aborted with
``EXECERROR = 1`` — yet the DB recorded ``model_optimal_presolve`` + match at
that same 1735.5696.

**The discriminator is per-solve attribution, not a global grep.** Every status
line in a GAMS listing belongs to the solve summary above it::

                   S O L V E      S U M M A R Y

         MODEL   mcp_model
         TYPE    MCP
         SOLVER  PATH                FROM LINE  1124

    **** SOLVER STATUS     1 Normal Completion
    **** MODEL STATUS      1 Optimal

So the question "did the MCP produce its own MODEL STATUS?" is answered by
finding a summary that is ``TYPE MCP`` **for our emitted model** and which
carries a ``MODEL STATUS`` — see ``EMITTED_MCP_MODEL`` for why the model name
matters and ``TYPE`` alone is not enough.

**Attribution is not success, and the verdicts keep them apart:**

===================  ===========================================================
``MCP-SOLVED``       our MCP reported MS-1/MS-2 — a usable answer
``MCP-FAILED``       our MCP reported a status, but a failing one (MS-4, MS-5…)
``EMBEDDED-ONLY``    **spurious** — only a non-emitted solve reported a status,
                     so the warm-start value is what gets read back
``MCP-NO-STATUS``    our MCP block exists but reported nothing — indeterminate
``NO-SOLVE``         no recognised solve at all — indeterminate
``ERROR``            could not be run — indeterminate
===================  ===========================================================

The three indeterminate verdicts are distinct on purpose. Folding them into the
spurious bucket would report "the embedded model solved and ours did not" when
*nothing* solved — a fabricated finding of exactly the kind this script exists
to catch.

``EMBEDDED-ONLY`` is named for provenance rather than model type: the population
includes LP, QCP and DNLP sources, so "NLP-ONLY" would misreport the solve kind
on a quarter of it.

**Deliberately NOT keyed on ``EXECERROR``.** `check_presolve_divergence.py`'s
first branch treats any execution error as an *embedded-NLP* divergence, which
is how weapons — whose embedded NLP solved perfectly — got reported against the
wrong side. An abort tells you *something* failed, not *which model*.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"

#: The model name our emitter always uses — verified uniform across all 39
#: committed presolve goldens.
#:
#: **`TYPE MCP` alone is NOT a safe test.** Two raw corpus sources solve an MCP
#: of their own (`cesam.gms`, `spatequ.gms`), and a presolve emit `$include`s the
#: raw source — so their listings carry a `TYPE MCP` summary that is *not* ours.
#: Neither is in the presolve+match population today, but keying on the model
#: name costs nothing and stops the check reading a foreign MCP solve as proof
#: that ours ran.
EMITTED_MCP_MODEL = "mcp_model"

#: Indentation is optional throughout. Real GAMS listings indent these lines,
#: but attribution must not depend on that: a column-0 header (the shape
#: `scripts/gamslib/test_solve.py` already accepts, and that
#: `tests/gamslib/test_test_solve.py` exercises) would otherwise parse as
#: **zero** summaries and report a perfectly good run as ``NO-SOLVE``.
_SUMMARY_HEADER = re.compile(r"^[ \t]*S O L V E {6}S U M M A R Y\s*$", re.MULTILINE)
_MODEL_LINE = re.compile(r"^[ \t]*MODEL\s+(\S+)", re.MULTILINE)
_TYPE_LINE = re.compile(r"^[ \t]*TYPE\s+(\S+)", re.MULTILINE)
_SOLVER_LINE = re.compile(r"^[ \t]*SOLVER\s+(\S+)", re.MULTILINE)
#: Same rule for the status lines — the header patterns above tolerate
#: indentation, and it would be incoherent for these not to: an otherwise valid
#: listing with indented ``****`` lines would yield a *statusless* summary and be
#: reported as indeterminate, or worse as spurious.
_SOLVER_STATUS = re.compile(r"^[ \t]*\*\*\*\* SOLVER STATUS\s+(\d+)\s*(.*?)$", re.MULTILINE)
_MODEL_STATUS = re.compile(r"^[ \t]*\*\*\*\* MODEL STATUS\s+(\d+)\s*(.*?)$", re.MULTILINE)


@dataclass
class SolveSummary:
    """One ``S O L V E   S U M M A R Y`` block and the statuses beneath it."""

    model: str | None
    type: str | None
    solver: str | None
    solver_status: int | None
    model_status: int | None
    model_status_text: str | None

    @property
    def is_mcp(self) -> bool:
        """An MCP-typed solve — ours or the raw model's own."""
        return (self.type or "").upper() == "MCP"

    @property
    def is_emitted_mcp(self) -> bool:
        """An MCP-typed solve of *our* generated model."""
        return self.is_mcp and self.model == EMITTED_MCP_MODEL


def parse_solve_summaries(lst_content: str) -> list[SolveSummary]:
    """Split a GAMS listing into solve summaries, each owning its status lines.

    Attribution is positional: a status line belongs to the nearest summary
    header *above* it. That is the whole point — a listing-wide search for
    ``MODEL STATUS`` cannot tell you which model produced it.
    """
    starts = [m.start() for m in _SUMMARY_HEADER.finditer(lst_content)]
    summaries: list[SolveSummary] = []

    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(lst_content)
        block = lst_content[start:end]

        # The header fields sit in the first few lines; the statuses follow.
        model = _MODEL_LINE.search(block)
        type_ = _TYPE_LINE.search(block)
        solver = _SOLVER_LINE.search(block)
        sstat = _SOLVER_STATUS.search(block)
        mstat = _MODEL_STATUS.search(block)

        summaries.append(
            SolveSummary(
                model=model.group(1) if model else None,
                type=type_.group(1) if type_ else None,
                solver=solver.group(1) if solver else None,
                solver_status=int(sstat.group(1)) if sstat else None,
                model_status=int(mstat.group(1)) if mstat else None,
                model_status_text=mstat.group(2).strip() if mstat else None,
            )
        )

    return summaries


#: GAMS MODEL STATUS values that mean the solve produced a usable answer.
#: PATH reports **1 Optimal** for a solved complementarity problem; 2 is
#: CONOPT's "Locally Optimal". Anything else (4 Infeasible, 5 Locally
#: Infeasible, 6 Intermediate Infeasible, …) is a failure.
_SUCCESS_MODEL_STATUS = frozenset({1, 2})

#: GAMS SOLVER STATUS 1 = "Normal Completion". Required alongside the model
#: status, matching `scripts/gamslib/test_solve.py`'s solve gate.
_NORMAL_COMPLETION = 1

#: Model ids become filesystem path components (`<raw>/<id>.gms`,
#: `<workdir>/<id>_mcp_presolve.gms`). Validated against the repository's safe
#: pattern so a `../` or a separator cannot escape either directory — and
#: validated at BOTH the CLI boundary and the consumer that builds the path,
#: per CONTRIBUTING's defense-in-depth rule.
#:
#: ⚠ Anchored with ``\Z`` and matched with ``fullmatch``, **not** ``$``/``match``:
#: ``$`` also matches immediately *before* a trailing newline, so ``"weapons\n"``
#: would slip through a guard whose whole job is to reject whitespace.
_SAFE_MODEL_ID = re.compile(r"[A-Za-z0-9_.-]+\Z")


def _is_safe_model_id(model_id: str) -> bool:
    """Reject anything that could traverse out of the directories we build."""
    return bool(_SAFE_MODEL_ID.fullmatch(model_id)) and model_id not in {".", ".."}


#: Verdicts that conclude nothing. Counted as failures of the *check*, never as
#: evidence either way about the model.
_INDETERMINATE_VERDICTS = frozenset({"ERROR", "NO-SOLVE", "MCP-NO-STATUS"})


@dataclass
class Attribution:
    """Whether a listing shows the MCP solving in its own right."""

    model_id: str
    summaries: list[SolveSummary] = field(default_factory=list)
    error: str | None = None
    #: GAMS's own exit code, recorded for transparency. **Deliberately not used
    #: to invalidate a listing:** `weapons` — the whole finding — exits **3**
    #: (`USER ERROR(S) ENCOUNTERED`) precisely *because* its MCP aborted. Keying
    #: on it would discard the case this script was written to detect.
    gams_returncode: int | None = None

    @property
    def mcp_summaries(self) -> list[SolveSummary]:
        """Solves of *our* emitted MCP — not a raw source's own MCP solve."""
        return [s for s in self.summaries if s.is_emitted_mcp]

    @property
    def foreign_mcp_summaries(self) -> list[SolveSummary]:
        """MCP solves belonging to the included raw model (`cesam`, `spatequ`).

        Surfaced rather than ignored: if one of these ever appears it means the
        listing has an MCP status that must NOT be read as ours.
        """
        return [s for s in self.summaries if s.is_mcp and not s.is_emitted_mcp]

    @property
    def embedded_summaries(self) -> list[SolveSummary]:
        """Every solve that is not our emitted MCP.

        Named for its *provenance*, not its model type: the population includes
        LP (`marco`, `paperco`, `tforss`), QCP (`cpack`, `qsambal`), DNLP
        (`maxmin`) and mixed (`robustlp`) sources, so calling this "the NLP" would
        misreport the solve kind on a quarter of the corpus.
        """
        return [s for s in self.summaries if not s.is_emitted_mcp]

    @property
    def mcp_produced_status(self) -> bool:
        """**Attribution only:** *our* MCP reported a MODEL STATUS.

        ⚠ This says the status belongs to our model — **not** that the solve
        succeeded. Keep it separate from the verdict: an MCP that returns MS-4
        has been attributed and has still not produced a usable answer.
        """
        return any(s.model_status is not None for s in self.mcp_summaries)

    @property
    def mcp_succeeded(self) -> bool:
        """Our MCP produced a usable answer — **both** statuses must be good.

        Matches the repository's existing solve gate
        (`scripts/gamslib/test_solve.py`: ``solver_status == 1 and model_status
        in (1, 2)``). MODEL STATUS alone is not enough: a solver that hits a
        resource or iteration limit can report a stale-but-plausible model
        status alongside SOLVER STATUS 3/4, and that is not a solved model.
        """
        return any(
            s.solver_status == _NORMAL_COMPLETION and s.model_status in _SUCCESS_MODEL_STATUS
            for s in self.mcp_summaries
        )

    @property
    def embedded_produced_status(self) -> bool:
        """The **last** non-emitted solve reported a status.

        ⚠ Deliberately not ``any()``. The value a warm start leaves behind is
        set by the solve immediately preceding our MCP — not by any earlier one.
        `harker` runs 4 source solves and `mathopt4` 4, so with ``any()`` an
        early success followed by a *statusless* final source solve would be
        reported as a spurious match when the truth is that nothing usable was
        established: that is indeterminate, and inventing a finding there is the
        error this whole script exists to avoid.
        """
        last = self.embedded_summaries[-1] if self.embedded_summaries else None
        if last is None:
            return False
        # The SAME gate as `mcp_succeeded`, and for the same reason: a status is
        # not a usable answer. A resource- or iteration-interrupted source can
        # leave a stale MS-1/MS-2 beside SOLVER STATUS 3/4, and calling that a
        # warm-start value would report a spurious match where no successful
        # answer was ever established.
        return (
            last.solver_status == _NORMAL_COMPLETION and last.model_status in _SUCCESS_MODEL_STATUS
        )

    @property
    def verdict(self) -> str:
        """One of six outcomes. Only ``EMBEDDED-ONLY`` means *spurious*.

        The three indeterminate verdicts are deliberately distinct rather than
        folded into the spurious bucket: reporting "the embedded model solved and
        ours did not" when *nothing* solved would be a fabricated finding, which
        is the same error this script exists to catch.
        """
        if self.error:
            return "ERROR"
        if self.mcp_produced_status:
            return "MCP-SOLVED" if self.mcp_succeeded else "MCP-FAILED"
        if self.mcp_summaries:
            # Our MCP block exists but reported nothing — GAMS emits the header
            # during generation, so a solver that dies before reporting lands
            # here. Not attributable either way.
            return "MCP-NO-STATUS"
        if self.embedded_produced_status:
            # The spurious case: a status exists for the warm start to read back,
            # and it is not ours.
            return "EMBEDDED-ONLY"
        return "NO-SOLVE"

    @property
    def is_embedded_only(self) -> bool:
        """Only a non-emitted solve reported a usable status.

        ⚠ Deliberately NOT called ``is_spurious``. "Spurious *match*" is a claim
        about a **recorded** match, and an ``Attribution`` carries no
        selection-source context — for an explicit ``--models`` audit there is no
        recorded match to contradict. Provenance lives in ``main``, which is the
        only place that knows it, so that is where ``spurious`` is derived.
        """
        return self.verdict == "EMBEDDED-ONLY"

    @property
    def is_indeterminate(self) -> bool:
        """Nothing can be concluded — must not be silently counted as a pass."""
        return self.verdict in _INDETERMINATE_VERDICTS

    def as_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "verdict": self.verdict,
            "mcp_produced_status": self.mcp_produced_status,
            "mcp_succeeded": self.mcp_succeeded,
            "gams_returncode": self.gams_returncode,
            "n_summaries": len(self.summaries),
            "n_mcp_summaries": len(self.mcp_summaries),
            "n_foreign_mcp_summaries": len(self.foreign_mcp_summaries),
            "summaries": [
                {
                    "model": s.model,
                    "type": s.type,
                    "solver": s.solver,
                    "solver_status": s.solver_status,
                    "model_status": s.model_status,
                    "model_status_text": s.model_status_text,
                }
                for s in self.summaries
            ],
            "error": self.error,
        }


#: From ``data/gamslib/schema.json`` (``solve_outcome_category``) — the enum
#: declared for **this field**.
#:
#: ⚠ An earlier revision mirrored `error_taxonomy.SOLVE_OUTCOME_CATEGORIES`,
#: which is a **broader union** spanning several fields. That was wrong in both
#: directions: it **rejected** the schema-valid ``permanent_exclusion`` (which
#: would abort the audit on real data) and **accepted** seven ``compare_*``
#: values that are invalid for this field. Same mistake as the round-6
#: ``comparison_status`` bug, one level over — a producer's constant is not the
#: field's contract.
#:
#: ``model_optimal_presolve`` is listed here directly, so no suffix stripping is
#: needed: `run_full_test.py` writes exactly that literal.
#: `test_outcome_allowlist_matches_the_schema` fails on drift.
_SOLVE_OUTCOME_CATEGORIES = frozenset(
    {
        "path_solve_normal",
        "path_solve_iteration_limit",
        "path_solve_time_limit",
        "path_solve_terminated",
        "path_solve_eval_error",
        "path_solve_license",
        "path_syntax_error",
        "model_optimal",
        "model_optimal_presolve",
        "model_locally_optimal",
        "model_infeasible",
        "model_unbounded",
        "permanent_exclusion",
    }
)


#: From ``data/gamslib/schema.json`` (``solution_comparison_result``), **not**
#: from the values that happen to be in the DB today.
#:
#: ⚠ An earlier revision omitted ``error`` because no current row uses it — a
#: valid row would then have been rejected as an unknown enum. **Derive an
#: allow-list from the declared schema, never from observed data.**
#: `test_comparison_status_allowlist_matches_the_schema` fails on drift.
_COMPARISON_STATUSES = frozenset({"match", "mismatch", "skipped", "error", "not_tested"})

#: From ``data/gamslib/schema.json`` (``mcp_solve_result``), where it is
#: **required** whenever the object is present.
_MCP_SOLVE_STATUSES = frozenset({"success", "failure", "timeout", "not_tested"})

#: ``schema_version`` is a MAJOR.MINOR.PATCH string; ``"2.2"``, ``null`` and
#: ``[]`` are all malformed. From ``data/gamslib/schema.json``.
_SCHEMA_VERSION = re.compile(r"\d+\.\d+\.\d+")

#: ``model_entry.gamslib_type`` enum, from ``data/gamslib/schema.json``.
#: `test_gamslib_type_allowlist_matches_the_schema` fails on drift.
_GAMSLIB_TYPES = frozenset(
    {
        "LP",
        "NLP",
        "QCP",
        "MIP",
        "MINLP",
        "MIQCP",
        "MCP",
        "CNS",
        "DNLP",
        "MPEC",
        "RMPEC",
        "EMP",
        "RMIP",
        "RMINLP",
        "RMIQCP",
    }
)


def _outcome_is_known(value: str) -> bool:
    """Strict membership of the schema's enum.

    No suffix stripping: the schema lists ``model_optimal_presolve`` itself, and
    tolerating an arbitrary ``<base>_presolve`` would accept values the DB
    contract does not permit — the same over-permissiveness that let the
    ``compare_*`` categories through.
    """
    return value in _SOLVE_OUTCOME_CATEGORIES


def _reject_nul(value: str, flag: str) -> str | None:
    """A NUL in a path is an input error, reported before any filesystem call.

    ⚠ It cannot be detected by probing: ``Path.is_dir()``, ``.exists()`` and
    ``.is_symlink()`` **swallow** the ``ValueError`` and return ``False``, so a
    preflight built from them sails past a NUL and the run only dies at the
    final ``open``/``os.replace`` — after the whole sweep. Checking the string is
    the only reliable point.
    """
    if "\x00" in value:
        return f"ERROR: {flag} path contains an embedded NUL character"
    return None


class InputError(Exception):
    """Bad input — reported with a concrete message and exit code 2, never a traceback."""


SCHEMA_PATH = PROJECT_ROOT / "data" / "gamslib" / "schema.json"

#: RFC 3339 ``date-time`` — what JSON Schema's ``format: date-time`` means.
#: **Deliberately stricter than ``datetime.fromisoformat``**, which accepts a
#: missing UTC offset, a space instead of ``T``, and bare dates.
_RFC3339 = re.compile(r"\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(\.\d+)?([Zz]|[+-]\d{2}:\d{2})")


def _validate_against_schema(db: object, db_path: Path) -> str | None:
    """Validate the whole DB against ``schema.json``; ``None`` if it passes.

    Returns a message rather than raising so the caller keeps one error path.
    **Absent `jsonschema`, this is a no-op** — the targeted checks that follow
    still run, so the audit degrades in coverage rather than failing outright.
    """
    try:
        from jsonschema import Draft7Validator, FormatChecker
    except ImportError:  # pragma: no cover - depends on the environment
        # `jsonschema` is an OPTIONAL, undeclared dependency — degrade quietly.
        return None

    # `schema.json` is NOT optional the way `jsonschema` is: it is the repo's
    # checked-in contract. If it is missing or corrupt, the backstop is silently
    # disabled and a schema-only violation (a misspelled key) would sail through
    # — so this is reported as an error rather than treated as a pass.
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except OSError as exc:
        return f"cannot read the schema contract {SCHEMA_PATH}: {exc}"
    except ValueError as exc:
        return f"schema contract {SCHEMA_PATH} is not valid JSON: {exc}"

    # A syntactically valid file need not be a valid Draft-7 *schema*, and
    # `iter_errors` then raises from inside jsonschema rather than reporting.
    try:
        Draft7Validator.check_schema(schema)
    except Exception as exc:  # jsonschema raises SchemaError; keep this broad
        return f"schema contract {SCHEMA_PATH} is not a valid Draft-7 schema: {exc}"

    # ⚠ `format` keywords are inert unless a FormatChecker is supplied — and
    # even then `date-time` is a NO-OP here, because jsonschema delegates it to
    # the optional `rfc3339-validator` package, which is not installed.
    # (Measured: an invalid timestamp passed both with and without a bare
    # `FormatChecker()`.) Registered locally rather than taking a second
    # undeclared dependency.
    #
    # ⚠ And `datetime.fromisoformat` is NOT RFC 3339: it accepts a missing
    # offset, a space separator, and date-only values. The full shape is matched
    # instead — see `_RFC3339` — because a looser check silently passes the
    # malformed timestamps this exists to catch.
    format_checker = FormatChecker()

    @format_checker.checks("date-time", raises=())
    def _is_date_time(value: object) -> bool:
        if not isinstance(value, str):
            return True  # the `type` keyword owns non-strings
        return bool(_RFC3339.fullmatch(value))

    errors = sorted(
        Draft7Validator(schema, format_checker=format_checker).iter_errors(db),
        key=lambda e: list(e.absolute_path),
    )

    # Format violations are WARNED about, not fatal; everything else is fatal.
    #
    # This is not squeamishness: the checked-in DB carries **8** date-only
    # `convexity.updated_date` values in a `format: date-time` field (abel,
    # ps10_s, ps2_f_s, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp). That is a
    # real, pre-existing data defect — but it is not this audit's business, and
    # refusing to run over it would break the tool on the production database to
    # police a timestamp. Structure, enums and `additionalProperties` stay hard
    # errors, since those are what can silently shrink the cohort.
    format_errors = [e for e in errors if e.validator == "format"]
    errors = [e for e in errors if e.validator != "format"]
    if format_errors:
        shown = format_errors[:3]
        detail = "; ".join(
            f"{'.'.join(str(p) for p in e.absolute_path)}: {e.message}" for e in shown
        )
        more = f" (+{len(format_errors) - len(shown)} more)" if len(format_errors) > 3 else ""
        print(
            f"WARNING: {db_path} has {len(format_errors)} format violation(s) "
            f"against schema.json — {detail}{more}",
            file=sys.stderr,
        )
    if not errors:
        return None

    shown = errors[:5]
    lines = [
        f"  {'.'.join(str(p) for p in e.absolute_path) or '(root)'}: {e.message}" for e in shown
    ]
    more = f"\n  ... and {len(errors) - len(shown)} more" if len(errors) > len(shown) else ""
    return f"results DB {db_path} does not match schema.json:\n" + "\n".join(lines) + more


def presolve_match_models(db_path: Path | None = None) -> list[str]:
    """Every model recorded ``model_optimal_presolve`` **and** match.

    ``db_path`` defaults to :data:`DB_PATH` **resolved at call time**, not as a
    default-argument value — a ``db_path: Path = DB_PATH`` default binds at
    import and would silently ignore any later reassignment of the module
    global, which makes the function untestable against a fixture DB.

    The DB is hand-editable, so its shape is checked before it is indexed: a
    malformed file must produce an actionable error, not a ``KeyError`` from
    inside a list comprehension.
    """
    db_path = DB_PATH if db_path is None else db_path
    try:
        raw = db_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError(f"cannot read results DB {db_path}: {exc}") from exc
    except UnicodeError as exc:
        # A DB with invalid UTF-8 must still produce the promised exit-2 error
        # rather than a UnicodeDecodeError traceback.
        raise InputError(f"results DB {db_path} is not valid UTF-8: {exc}") from exc

    try:
        db = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InputError(f"results DB {db_path} is not valid JSON: {exc}") from exc

    if not isinstance(db, dict):
        raise InputError(f"results DB {db_path} must be a JSON object, got {type(db).__name__}")
    # The schema requires BOTH top-level keys. Accepting a bare
    # `{"models": [...]}` would let an incompatible file pass the input gate.
    if "schema_version" not in db:
        raise InputError(f"results DB {db_path} has no top-level 'schema_version'")
    version = db["schema_version"]
    if not isinstance(version, str) or not _SCHEMA_VERSION.fullmatch(version):
        raise InputError(
            f"results DB {db_path} has a malformed 'schema_version' {version!r} "
            "(expected a MAJOR.MINOR.PATCH string)"
        )
    models = db.get("models")
    if not isinstance(models, list):
        raise InputError(f"results DB {db_path} has no top-level 'models' list")

    out = []
    for i, m in enumerate(models):
        if not isinstance(m, dict):
            raise InputError(f"{db_path}: models[{i}] must be an object, got {type(m).__name__}")
        # Validate the id for EVERY row, before the selection predicate. Doing it
        # inside the predicate meant a malformed id on a non-matching row was
        # silently ignored — so a corrupted DB could quietly drop a model from
        # the default cohort while this function advertised per-entry validation.
        # `model_id`, `model_name` and `gamslib_type` are all required per entry —
        # and validated for TYPE and ENUM, not merely presence: `model_name: null`
        # or `gamslib_type: "NLPX"` would otherwise be audited as valid.
        for required in ("model_id", "model_name", "gamslib_type"):
            if required not in m:
                raise InputError(f"{db_path}: models[{i}] is missing required '{required}'")
        model_name = m.get("model_name")
        if not isinstance(model_name, str) or not model_name:
            raise InputError(
                f"{db_path}: models[{i}] has a missing or empty 'model_name' {model_name!r}"
            )
        gamslib_type = m.get("gamslib_type")
        if not isinstance(gamslib_type, str) or gamslib_type not in _GAMSLIB_TYPES:
            raise InputError(
                f"{db_path}: models[{i}] has an unknown 'gamslib_type' {gamslib_type!r}"
            )
        model_id = m.get("model_id")
        if not isinstance(model_id, str) or not model_id:
            raise InputError(f"{db_path}: models[{i}] has a missing or non-string 'model_id'")
        if not _is_safe_model_id(model_id):
            raise InputError(f"{db_path}: models[{i}] has an unsafe model_id {model_id!r}")

        # Default ONLY on missing/null. `or {}` would swallow `mcp_solve: []` or
        # `solution_comparison: ""` — falsey but malformed — and silently skip the
        # row rather than reject it, which is the opposite of validating it.
        solve = m.get("mcp_solve")
        cmp_ = m.get("solution_comparison")
        # Both are `$ref`s to object definitions, so an explicitly present `null`
        # is schema-INVALID — only an omitted optional property is absent.
        # Treating null as "missing" would silently drop a malformed row.
        for key in ("mcp_solve", "solution_comparison"):
            if key in m and m[key] is None:
                raise InputError(
                    f"{db_path}: models[{i}] ({model_id}) has an explicit null '{key}'; "
                    "omit the key instead"
                )
        # Presence is tracked separately from the defaulted value: `{}` is falsey,
        # so a present-but-empty object would otherwise be indistinguishable from
        # an absent one and would skip the required-field checks below.
        has_solve = "mcp_solve" in m
        has_cmp = "solution_comparison" in m
        solve = {} if solve is None else solve
        cmp_ = {} if cmp_ is None else cmp_
        if not isinstance(solve, dict) or not isinstance(cmp_, dict):
            raise InputError(
                f"{db_path}: models[{i}] has a malformed mcp_solve/solution_comparison "
                f"(got {type(solve).__name__}/{type(cmp_).__name__}, expected an object; "
                "omit the key entirely if absent)"
            )
        # Validate the enums BEFORE comparing them. Comparing only against the
        # wanted pair means a typo — `model_optimal_presolvee`, `matc` — silently
        # drops the row and the audit runs on a quietly incomplete cohort. Per
        # CONTRIBUTING §Schema validation an unknown enum is a hard error naming
        # the entry index, never a downgrade.
        # `status` is REQUIRED by the schema whenever `mcp_solve` is present, so
        # a row missing it is malformed even though our predicate never reads it.
        # Validating only the fields we consume is how an incomplete cohort goes
        # unnoticed — the thing this validation exists to prevent.
        if has_solve:
            solve_status = solve.get("status")
            if not isinstance(solve_status, str) or solve_status not in _MCP_SOLVE_STATUSES:
                raise InputError(
                    f"{db_path}: models[{i}] ({model_id}) has missing or unknown "
                    f"mcp_solve.status {solve_status!r} "
                    f"(required; known: {', '.join(sorted(_MCP_SOLVE_STATUSES))})"
                )
        if has_cmp and cmp_.get("comparison_status") is None:
            raise InputError(
                f"{db_path}: models[{i}] ({model_id}) has a solution_comparison "
                "without the required 'comparison_status'"
            )

        # `outcome_category` is a `$ref` to a string enum and is not nullable, so
        # an explicit null is malformed rather than omitted.
        if "outcome_category" in solve and solve["outcome_category"] is None:
            raise InputError(
                f"{db_path}: models[{i}] ({model_id}) has an explicit null "
                "'mcp_solve.outcome_category'; omit the key instead"
            )
        outcome = solve.get("outcome_category")
        if outcome is not None:
            if not isinstance(outcome, str) or not _outcome_is_known(outcome):
                raise InputError(
                    f"{db_path}: models[{i}] ({model_id}) has unknown "
                    f"mcp_solve.outcome_category {outcome!r}"
                )
        status = cmp_.get("comparison_status")
        if status is not None:
            if not isinstance(status, str) or status not in _COMPARISON_STATUSES:
                raise InputError(
                    f"{db_path}: models[{i}] ({model_id}) has unknown "
                    f"solution_comparison.comparison_status {status!r} "
                    f"(known: {', '.join(sorted(_COMPARISON_STATUSES))})"
                )

        if outcome == "model_optimal_presolve" and status == "match":
            out.append(model_id)

    # Full-schema validation as a BACKSTOP, deliberately AFTER the targeted
    # checks above rather than before them.
    #
    # The targeted checks give a better error — they name the model and say what
    # to do ("omit the key instead") — so they get first refusal. What only the
    # schema can catch is what they cannot see: `additionalProperties: false` is
    # set on the top level and on the model / mcp_solve / solution_comparison
    # objects, so a MISSPELLED key (`mcp_solves`, `outcome_catagory`) reads as
    # "field absent" to any check that looks up fields by name.
    #
    # Imported lazily and optionally, exactly as `scripts/gamslib/db_manager.py`
    # does: `jsonschema` is NOT a declared dependency, so absent it the audit
    # still runs — with the narrower guarantee rather than none.
    schema_error = _validate_against_schema(db, db_path)
    if schema_error:
        raise InputError(schema_error)

    return sorted(out)


def find_gams() -> str | None:
    """Locate GAMS the way the rest of the repo does.

    Versioned install paths are preferred over a bare ``PATH`` lookup — mirrors
    `scripts/gamslib/test_solve.py`, where the comment explains why: a `PATH`
    entry may point at an older version whose time-limited license has expired.
    ``Current`` follows whatever version was installed last.
    """
    for candidate in (
        "/Library/Frameworks/GAMS.framework/Versions/Current/Resources/gams",
        "/opt/gams/gams",
        "C:\\GAMS\\win64\\gams.exe",
    ):
        # `shutil.which` on an absolute path checks it is an EXECUTABLE FILE.
        # `Path.exists()` would happily return a directory or a non-executable,
        # and the preflight would then report GAMS as available — every
        # translation would run before each model failed with the same OSError,
        # which is exactly what the preflight exists to prevent.
        resolved = shutil.which(candidate)
        if resolved:
            return str(Path(resolved).resolve())

    found = shutil.which("gams")
    # Absolutise: a relative `PATH` entry (`.`) makes `which` return a relative
    # path, which the preflight would validate against the CALLER's directory
    # while every launch resolves it under `cwd=PROJECT_ROOT` — succeeding here
    # and failing there.
    return str(Path(found).resolve()) if found else None


def _tail(text: str | None, limit: int = 400) -> str:
    """Last ``limit`` characters of subprocess output, flattened for one-line errors."""
    if not text:
        return ""
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else "…" + flat[-limit:]


def run_one(
    model_id: str, workdir: Path, reslim: int = 300, gams: str | None = None
) -> Attribution:
    """Emit ``--nlp-presolve`` for one model, run GAMS, and attribute the solves.

    GAMS runs with ``cwd`` at the project root — the emitted
    ``$include "data/gamslib/raw/<id>.gms"`` is repo-relative — while every
    scratch artifact goes to ``workdir``. Never run GAMS *from* the repo root
    without ``ScrDir``: Sprint 37 Day 9 swept the scratch files into a commit.

    ``workdir`` **must already be absolute** (``main`` resolves it): the paths
    below are handed to subprocesses whose ``cwd`` is ``PROJECT_ROOT``, so a
    relative one would have the child write somewhere the parent never looks.

    ``gams`` may be passed in so the sweep resolves the executable **once**,
    before any translation runs; omitted, it is resolved here.
    """
    # Defense in depth: `main` validates too, but this is the consumer that
    # actually builds the paths, and it is importable on its own.
    if not _is_safe_model_id(model_id):
        return Attribution(model_id, error=f"unsafe model id {model_id!r}")

    # Likewise for `reslim` — a direct caller bypasses `main`'s range check, and
    # the value reaches GAMS *and* derives the wall-clock timeout (`reslim + 120`).
    if reslim < 0:
        return Attribution(model_id, error=f"reslim must be >= 0 seconds, got {reslim}")

    # And the docstring's absolute-`workdir` precondition is ENFORCED, not merely
    # documented. A relative one splits the run in two: `src.cli`'s `-o`, GAMS's
    # `o=` and `ScrDir` resolve under `cwd=PROJECT_ROOT`, while `emitted.exists()`,
    # `lst.exists()` and `TemporaryDirectory(dir=...)` resolve under the caller's
    # CWD — so the child writes somewhere the parent never looks and the run
    # reports a missing emit that was in fact produced.
    # A NUL passes `is_absolute()` and then makes `emitted.unlink()` raise
    # `ValueError`, which the `OSError` handlers below do not catch. Same
    # pre-filesystem string check `main` uses — applied here because `run_one`
    # is importable and validates its other direct inputs already.
    if "\x00" in str(workdir):
        return Attribution(model_id, error="workdir path contains an embedded NUL character")

    workdir = Path(workdir)
    if not workdir.is_absolute():
        return Attribution(
            model_id,
            error=f"workdir must be an absolute path, got {str(workdir)!r}",
        )

    raw = PROJECT_ROOT / "data" / "gamslib" / "raw" / f"{model_id}.gms"
    if not raw.exists():
        return Attribution(
            model_id,
            error=(
                f"raw source absent: {raw} — the corpus is gitignored; "
                "run ./scripts/download_gamslib_raw.sh --all"
            ),
        )

    emitted = workdir / f"{model_id}_mcp_presolve.gms"
    lst = workdir / f"{model_id}.lst"

    # Clear the emit target too, for the same reason the listing is cleared
    # below. If a later `src.cli` returns 0 without recreating its output, a
    # surviving file makes `emitted.exists()` succeed and GAMS runs the PREVIOUS
    # translation — the audit then attributes an older model's listing. Clearing
    # it is also what makes the "wrote no file" check below mean anything.
    try:
        emitted.unlink(missing_ok=True)
    except OSError as exc:
        return Attribution(model_id, error=f"cannot clear stale emit {emitted}: {exc}")

    try:
        emit = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.cli",
                str(raw.relative_to(PROJECT_ROOT)),
                "--nlp-presolve",
                # Pinned, not inherited: attribution recognises only this name,
                # so if `src.cli`'s default ever changed, every genuine MCP solve
                # would lose its matching summary and be reported as
                # indeterminate or embedded-only.
                "--model-name",
                EMITTED_MCP_MODEL,
                "-o",
                str(emitted),
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        # One slow translation must not abort the whole sweep before it can
        # write its report — `sarf` alone runs for ~28 minutes.
        return Attribution(model_id, error="emit timeout after 600s")
    except OSError as exc:
        # A missing/unexecutable interpreter is one model's problem, not the
        # sweep's: return a structured indeterminate result and carry on.
        return Attribution(model_id, error=f"emit could not be launched: {exc}")

    if emit.returncode != 0:
        detail = _tail(emit.stderr) or _tail(emit.stdout)
        return Attribution(
            model_id,
            error=f"emit failed (rc={emit.returncode})" + (f": {detail}" if detail else ""),
        )
    if not emitted.exists():
        # Distinct from a nonzero rc: the translation claimed success but wrote
        # nothing, which points at the output path rather than the model.
        detail = _tail(emit.stderr) or _tail(emit.stdout)
        return Attribution(
            model_id,
            error=f"emit reported success but wrote no file at {emitted}"
            + (f": {detail}" if detail else ""),
        )

    gams = gams or find_gams()
    if not gams:
        return Attribution(model_id, error="gams executable not found")

    # Never let a previous run's listing answer for this one. If GAMS dies
    # before writing (licensing, startup), a stale file would be parsed as this
    # run's result — a status attributed to the wrong invocation, which is the
    # very defect this script exists to detect, one level up.
    try:
        lst.unlink(missing_ok=True)
    except OSError as exc:
        return Attribution(model_id, error=f"cannot clear stale listing {lst}: {exc}")

    try:
        with tempfile.TemporaryDirectory(dir=str(workdir)) as scr:
            try:
                proc = subprocess.run(
                    [
                        gams,
                        str(emitted),
                        f"o={lst}",
                        "lo=2",
                        f"reslim={reslim}",
                        f"ScrDir={scr}",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=str(PROJECT_ROOT),
                    timeout=reslim + 120,
                )
            except subprocess.TimeoutExpired:
                # Report the WALL-CLOCK limit that actually fired, not GAMS's
                # own `reslim` — they differ by the 120 s launch allowance, and
                # quoting the smaller one makes a timeout look like a solver
                # limit when it was the harness.
                return Attribution(
                    model_id,
                    error=(
                        f"GAMS wall-clock timeout after {reslim + 120}s "
                        f"(GAMS reslim={reslim}s + 120s launch allowance)"
                    ),
                )
            except OSError as exc:
                # `find_gams` returned a path that is gone, a directory, or not
                # executable. One runner problem, not a dead sweep.
                return Attribution(model_id, error=f"GAMS could not be launched ({gams}): {exc}")
    except OSError as exc:
        return Attribution(model_id, error=f"cannot create scratch dir under {workdir}: {exc}")

    if not lst.exists():
        # Licensing and startup failures surface only here, so carry GAMS's own
        # output — an rc alone is not actionable.
        detail = _tail(proc.stderr) or _tail(proc.stdout)
        return Attribution(
            model_id,
            error=f"no listing produced (gams rc={proc.returncode})"
            + (f": {detail}" if detail else ""),
            # GAMS DID run, so keep the code structured rather than only inside
            # the free-form message — the JSON report is what gets analysed.
            gams_returncode=proc.returncode,
        )

    try:
        content = lst.read_text(errors="replace")
    except OSError as exc:
        return Attribution(
            model_id,
            error=f"cannot read listing {lst}: {exc}",
            gams_returncode=proc.returncode,
        )

    return Attribution(
        model_id,
        summaries=parse_solve_summaries(content),
        gams_returncode=proc.returncode,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--models",
        help="comma-separated model ids (default: every presolve+match row in the DB)",
    )
    ap.add_argument("--workdir", default=None, help="where to keep emits and listings")
    ap.add_argument("--reslim", type=int, default=300, help="GAMS resource limit, seconds (>= 0)")
    ap.add_argument("--json", dest="json_out", help="write the full record here")
    ap.add_argument(
        "--allow-empty",
        action="store_true",
        help=(
            "permit a selection of zero models. The run then CERTIFIES NOTHING — "
            "use only when an empty selection is the expected state."
        ),
    )
    args = ap.parse_args(argv)

    # Range, not just type: `reslim` is handed to GAMS and also derives the
    # subprocess timeout (`reslim + 120`), where a negative would be nonsense.
    # `int >= 0` per CONTRIBUTING; `scripts/ci/run_pr19_solves.py` accepts 0 and
    # GAMS treats reslim=0 as valid, so only a NEGATIVE value is an input error.
    if args.reslim < 0:
        print(
            f"ERROR: --reslim must be >= 0 seconds, got {args.reslim}",
            file=sys.stderr,
        )
        return 2

    # `is not None`, NOT truthiness: `--models ""` is an explicitly empty
    # selection and must hit the empty-selection guard, not silently fall
    # through to auditing the entire DB cohort.
    explicit_models = args.models is not None

    try:
        if explicit_models:
            models = [m.strip() for m in args.models.split(",") if m.strip()]
            unsafe = [m for m in models if not _is_safe_model_id(m)]
            if unsafe:
                raise InputError(
                    "unsafe model id(s) "
                    + ", ".join(repr(m) for m in unsafe)
                    + " — must match [A-Za-z0-9_.-]+ (no separators, no '..')"
                )
        else:
            models = presolve_match_models()
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    # An empty selection is NOT a pass. Every bucket would be empty, the
    # partition assertion would hold vacuously, and the run would exit 0 having
    # checked nothing — which is exactly how an unprovisioned or stale DB turns
    # into a green report. Same rule as `run_full_test.py --resolve-changed`.
    if not models:
        if not args.allow_empty:
            source = (
                "--models" if explicit_models else f"{DB_PATH} (model_optimal_presolve + match)"
            )
            print(
                f"ERROR: selection is empty — nothing to audit from {source}.\n"
                "       An empty run certifies nothing. Pass --allow-empty if that is expected.",
                file=sys.stderr,
            )
            return 2
        print("WARNING: selection is empty; this run CERTIFIES NOTHING.", file=sys.stderr)

    # Resolve before use: these paths are handed to subprocesses running with
    # `cwd=PROJECT_ROOT`, so a relative --workdir would send the child's output
    # somewhere the parent never looks.
    # `is not None`, not truthiness: `--workdir ""` is a supplied-but-empty path.
    # Treating it as omitted would silently ignore the caller and scatter the
    # artifacts into a system temp dir they never asked for.
    if args.workdir is not None:
        if not args.workdir.strip():
            print("ERROR: --workdir was given an empty path", file=sys.stderr)
            return 2
        nul = _reject_nul(args.workdir, "--workdir")
        if nul:
            print(nul, file=sys.stderr)
            return 2

    try:
        workdir = (
            Path(args.workdir).resolve()
            if args.workdir is not None
            else Path(tempfile.mkdtemp(prefix="mcp_attr_"))
        )
        workdir.mkdir(parents=True, exist_ok=True)

        # Per-INVOCATION subdirectory, per CONTRIBUTING "Marker uniqueness".
        # `<workdir>/<model>.gms` and `<workdir>/<model>.lst` are deterministic,
        # so two runs sharing a --workdir would unlink and overwrite each other's
        # artifacts and could attribute the OTHER invocation's listing — the
        # cross-run form of the very bug this script detects. `mkdtemp` is unique
        # by construction, so no token scheme is needed.
        run_dir = Path(tempfile.mkdtemp(dir=str(workdir), prefix="run-"))
    except (OSError, RuntimeError, ValueError) as exc:
        # `Path.resolve()` raises RuntimeError — not OSError — on a symlink loop,
        # and an embedded NUL in the path raises ValueError. Both would otherwise
        # escape as a traceback and exit 1 instead of the promised exit 2.
        print(f"ERROR: cannot create workdir {args.workdir!r}: {exc}", file=sys.stderr)
        return 2

    # Preflight the report destination BEFORE the sweep. Discovering an
    # unwritable path after a multi-hour run is a poor trade even with the
    # stderr fallback at the end.
    #
    # `is not None`, not truthiness — consistent with --models and --workdir:
    # `--json ""` is a supplied-but-blank path, not an omitted flag, and
    # silently writing nothing while exiting 0 is the wrong answer.
    if args.json_out is not None:
        if not args.json_out.strip():
            print("ERROR: --json was given an empty path", file=sys.stderr)
            return 2
        nul = _reject_nul(args.json_out, "--json")
        if nul:
            print(nul, file=sys.stderr)
            return 2
        out_path = Path(args.json_out)
        try:
            # `is_dir()` touches the filesystem, so it can raise on an
            # inaccessible parent — that must be the exit-2 path, not a traceback.
            if out_path.is_dir():
                print(f"ERROR: --json {args.json_out} is a directory", file=sys.stderr)
                return 2
            parent = out_path.parent if str(out_path.parent) else Path(".")
            if not parent.is_dir():
                print(
                    f"ERROR: --json parent directory does not exist: {parent}",
                    file=sys.stderr,
                )
                return 2

            # Existence is not writability. A read-only destination (or a
            # read-only parent when the file is absent) would pass the checks
            # above and only fail after the whole sweep.
            if out_path.is_symlink():
                # `is_file()` follows the link but `os.replace(tmp, dest)` replaces
                # the LINK — so this would pass preflight, leave the link's target
                # untouched, and silently turn the symlink into a regular file.
                # Refusing is better than picking one of two surprising behaviours.
                print(
                    f"ERROR: --json {args.json_out} is a symlink; "
                    "the atomic write would replace the link itself, not its target",
                    file=sys.stderr,
                )
                return 2
            if out_path.exists():
                # A FIFO or other special file passes `is_dir()` and would then
                # block `open()` indefinitely waiting for a reader — which
                # defeats the whole point of preflighting.
                if not out_path.is_file():
                    print(
                        f"ERROR: --json {args.json_out} exists but is not a regular file",
                        file=sys.stderr,
                    )
                    return 2
                # Append, so the probe cannot truncate a file the caller may
                # still want.
                with out_path.open("a"):
                    pass

            # ALWAYS probe the parent, existing destination or not: the final
            # write is atomic (`mkstemp` in this directory, then `os.replace`),
            # so a writable file inside a READ-ONLY parent would otherwise pass
            # here and fail only after the whole sweep. The round-8 atomic-write
            # change is what made the parent the thing that matters.
            #
            # A UNIQUE probe, removed by the path it created: a deterministic
            # name could clobber an unrelated file the caller already has.
            probe_fd, probe_name = tempfile.mkstemp(dir=str(parent), prefix=".writetest-")
            os.close(probe_fd)
            os.unlink(probe_name)
        except (OSError, ValueError) as exc:
            # ValueError: an embedded NUL makes `exists()`/`is_file()`/`open()`
            # raise rather than return False.
            print(f"ERROR: cannot use --json path {args.json_out}: {exc}", file=sys.stderr)
            return 2

    # Printed because artifacts are kept for inspection and are no longer at a
    # path the caller can guess.
    print(f"artifacts: {run_dir}", flush=True)

    # Resolve GAMS ONCE, before any translation runs. Resolving it per-model
    # inside `run_one` meant a runner without GAMS still paid for every emit —
    # and some take minutes — before reporting the same missing dependency N
    # times. A missing tool should fail fast.
    gams = find_gams()
    if not gams and models:
        print(
            "ERROR: gams executable not found (checked the versioned install paths, then PATH).\n"
            "       Every model would fail identically after a full translation, so stopping now.",
            file=sys.stderr,
        )
        return 2

    results: list[Attribution] = []
    for i, mid in enumerate(models, 1):
        res = run_one(mid, run_dir, reslim=args.reslim, gams=gams)
        results.append(res)
        detail = ", ".join(
            f"{s.model}/{s.type}"
            + (f" MS-{s.model_status}" if s.model_status is not None else " (no status)")
            for s in res.summaries
        )
        print(
            f"[{i:>2}/{len(models)}] {mid:<12} {res.verdict:<14} " f"{res.error or detail}",
            flush=True,
        )

    embedded_only = [r for r in results if r.is_embedded_only]
    indeterminate = [r for r in results if r.is_indeterminate]
    mcp_failed = [r for r in results if r.verdict == "MCP-FAILED"]
    solved = [r for r in results if r.verdict == "MCP-SOLVED"]

    # "Spurious match" is a claim about a RECORDED match, so it only applies to
    # the DB-derived cohort. An explicit `--models` run audits arbitrary named
    # models — a mismatch or unrecorded model has no match to be spurious about,
    # and calling it one would manufacture the very kind of false claim this
    # script exists to catch. The attribution verdict is unchanged either way;
    # only the label and the JSON key differ.
    spurious = [] if explicit_models else embedded_only

    print()
    # The population claim must match the selection actually used: an explicit
    # `--models camcge` audits whatever was named, which need not be recorded
    # `model_optimal_presolve` + match at all.
    if explicit_models:
        print(f"Checked {len(results)} model(s) named explicitly via --models.")
    else:
        print(f"Checked {len(results)} model(s) recorded model_optimal_presolve + match.")
    print(f"  our MCP solved (MS-1/MS-2)          : {len(solved)}")
    print(f"  our MCP ran but FAILED              : {len(mcp_failed)}")
    print(f"  ONLY an embedded solve reported     : {len(embedded_only)}")
    print(f"  could not be determined             : {len(indeterminate)}")

    # Every result lands in exactly one bucket, asserted rather than assumed —
    # a verdict added later must not fall through the reporting unnoticed.
    assert len(solved) + len(mcp_failed) + len(embedded_only) + len(indeterminate) == len(results)

    if embedded_only:
        print()
        if spurious:
            print("SPURIOUS MATCHES — the recorded objective is the embedded solve's own value:")
        else:
            # Explicit selection: the verdict stands, the "spurious match"
            # framing does not — these models were never claimed to match.
            print("EMBEDDED-ONLY — our MCP produced no status of its own:")
        for r in embedded_only:
            print(f"  {r.model_id}")
    if mcp_failed:
        print()
        print("MCP RAN AND FAILED — attributed, but not a usable answer:")
        for r in mcp_failed:
            # Both statuses: the success gate requires SOLVER STATUS 1 too, so a
            # run with SOLVER STATUS 3 / MODEL STATUS 1 would otherwise print
            # "(MS-1)" and give the reader no visible reason for the failure.
            statuses = ", ".join(
                f"solver {s.solver_status}/MS-{s.model_status}" for s in r.mcp_summaries
            )
            print(f"  {r.model_id} ({statuses})")
    if indeterminate:
        print()
        print("INDETERMINATE — the check concluded nothing for these:")
        for r in indeterminate:
            print(f"  {r.model_id} [{r.verdict}] {r.error or ''}".rstrip())

    if args.json_out:
        report = json.dumps(
            {
                "checked": len(results),
                "selection": "explicit" if explicit_models else "db-cohort",
                "embedded_only": [r.model_id for r in embedded_only],
                # Only a DB-cohort run can call an EMBEDDED-ONLY result a
                # spurious *match*; an explicit selection has no recorded match.
                "spurious": [r.model_id for r in spurious],
                "mcp_failed": [r.model_id for r in mcp_failed],
                "indeterminate": [r.model_id for r in indeterminate],
                "results": [r.as_dict() for r in results],
            },
            indent=2,
        )
        # Always keep a per-run copy first. `--workdir` is made unique per
        # invocation, but `--json` is a caller-chosen path: two concurrent runs
        # pointing at the same file would otherwise leave only the last writer's
        # report. The run-local copy means no invocation's result is ever lost.
        try:
            (run_dir / "attribution.json").write_text(report)
        except OSError as exc:  # pragma: no cover - the shared path still tries
            print(f"WARNING: could not write the per-run report copy: {exc}", file=sys.stderr)

        # Atomic replace rather than `write_text`, which truncates first: two
        # concurrent runs could otherwise interleave and leave a reader with
        # invalid half-written JSON. Same discipline as the repository's DB
        # writers. The temp file is in the destination's own directory so the
        # replace stays on one filesystem.
        try:
            dest = Path(args.json_out)
            tmp_fd, tmp_name = tempfile.mkstemp(dir=str(dest.parent), prefix=f".{dest.name}.")
            try:
                with os.fdopen(tmp_fd, "w") as fh:
                    fh.write(report)
                os.replace(tmp_name, dest)
            except BaseException:
                # Never leave the temp file behind on a failure path.
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)
                raise
        except OSError as exc:
            # This runs AFTER every GAMS solve. Losing hours of work to an
            # unwritable path would be absurd — dump to stderr, then exit 2.
            print(f"ERROR: cannot write report to {args.json_out}: {exc}", file=sys.stderr)
            print("--- report follows on stderr so the run is not lost ---", file=sys.stderr)
            print(report, file=sys.stderr)
            return 2

    # Exit non-zero when a determination FAILED (a listing with no recognised
    # solve concludes nothing) **or when a selected model's MCP ran and failed**.
    #
    # `MCP-FAILED` used to print and still exit 0, so automation could read a
    # disproven match as a successful audit — the same "green while wrong" shape
    # this script was written to expose.
    #
    # `EMBEDDED-ONLY` deliberately stays exit 0: it is the finding the audit is
    # *for*, and making it non-zero would mean a successful investigation looked
    # like a broken tool.
    return 1 if (indeterminate or mcp_failed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
