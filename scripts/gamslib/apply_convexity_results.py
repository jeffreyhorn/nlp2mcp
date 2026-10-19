#!/usr/bin/env python3
"""Apply ``verify_convexity.py --output`` results to the results DB (writer W10).

Sprint 40 P1/P3 (``docs/planning/EPIC_4/SPRINT_40/SCHEMA_3_1_0_DESIGN.md`` §6).
Until this script, no command applied the verifier's results to the live DB:
``--update-catalog`` writes ``catalog.json``, and ``migrate_catalog.py``
rebuilds a whole DB from the catalog, which would wipe every pipeline stage.

⚠ A CONVEXITY WRITE IS A CORPUS WRITE. ``kpi_block``, ``batch_parse`` and
``run_full_test`` derive the candidate corpus from ``convexity.status``, so a
model newly classified convex silently JOINS the headline denominator (Prep
Task 6 measured 142 -> 143 on a scratch DB). So this writer holds the corpus:

* a model moving INTO ``{verified_convex, likely_convex}`` is REFUSED unless its
  id is passed with ``--admit``, AND that id is recorded in
  ``data/corpus_admissions.json`` (owner Decision 2: admit by rule). Without the
  record, ``kpi_block --corpus continuity`` could not drop it, and the
  continuity series would grow silently anyway;
* a refusal is a non-zero exit naming the models; nothing is written, and
  nothing is skipped silently;
* a status change that LEAVES the corpus, or stays outside it, is applied and
  listed in the summary, because it moves the denominator too.

Mapping, per result (``convexity`` is REPLACED, never merged, so no field from
an older run survives under a new run's provenance):

* ``convexity_status`` -> ``status``;
* ``verification_date``: the result's OWN stamp, copied verbatim. A result
  without one (a pre-3.1.0 verifier) is REFUSED, never back-dated from the
  report envelope's batch stamp;
* ``solver_status``, ``model_status``, ``objective_value``,
  ``solve_time_seconds``, ``timed_out``, ``solver``; ``error_message`` -> ``error``.
  The non-nullable ones are OMITTED when ``None``, never written as ``null``. A
  successful result carries ``error_message: null``, and ``error: null`` would
  make every successful application schema-invalid;
* ``license_edition`` and ``gams_version`` are nullable and ALWAYS written
  (the schema 3.1.0 invariant).

Unknown ids, and models whose type is outside LP/NLP/QCP, are refused: MINLP/MIP
are out of scope and are never relaxed.

Usage:
    python scripts/gamslib/apply_convexity_results.py \\
        --input <verify_convexity --output JSON> --db <path> [--admit ID ...] \\
        [--dry-run] [--validate] [--no-backup]

``--db`` has NO default: applying results to the committed DB must be a
deliberate choice. Exit codes: 0 applied (or would apply, under --dry-run);
1 refused or invalid; 2 bad input.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.db_manager import create_backup  # noqa: E402

SCHEMA_PATH = PROJECT_ROOT / "data" / "gamslib" / "schema.json"
ADMISSIONS_PATH = PROJECT_ROOT / "data" / "corpus_admissions.json"
CONVEX_STATUSES = frozenset({"verified_convex", "likely_convex"})
IN_SCOPE_TYPES = frozenset({"LP", "NLP", "QCP"})

#: verifier field -> convexity_result field, for the NON-NULLABLE fields that are
#: omitted (never written as null) when the verifier has no value.
_OPTIONAL = (
    ("solver_status", "solver_status"),
    ("model_status", "model_status"),
    ("objective_value", "objective_value"),
    ("solve_time_seconds", "solve_time_seconds"),
    ("timed_out", "timed_out"),
    ("solver", "solver"),
    ("error_message", "error"),
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Refusal(Exception):
    """The input cannot be applied as given. Nothing is written."""


def convexity_from_result(result: dict[str, Any]) -> dict[str, Any]:
    """Build a model's NEW ``convexity`` object from one verifier result."""
    vdate = result.get("verification_date")
    if not vdate:
        raise Refusal(
            f"{result.get('model_id')!r}: no per-result verification_date (a pre-3.1.0 "
            f"verifier report?). Refused, not back-dated from the batch stamp"
        )
    conv: dict[str, Any] = {"status": result["convexity_status"], "verification_date": vdate}
    for src, dst in _OPTIONAL:
        if result.get(src) is not None:
            conv[dst] = result[src]
    conv["license_edition"] = result.get("license_edition")
    conv["gams_version"] = result.get("gams_version")
    return conv


def load_admitted_record(path: Path) -> frozenset[str]:
    """Ids recorded in ``data/corpus_admissions.json`` (Decision 2's ledger)."""
    if not path.exists():
        return frozenset()
    entries = json.loads(path.read_text(encoding="utf-8")).get("admissions")
    if not isinstance(entries, list):
        raise Refusal(f"{path}: 'admissions' must be a list")
    return frozenset(e["model_id"] for e in entries if isinstance(e, dict) and e.get("model_id"))


def plan(
    database: dict[str, Any],
    results: list[dict[str, Any]],
    admit: frozenset[str],
    recorded: frozenset[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, list[str]]]:
    """Validate every result and return ``({model_id: new convexity}, summary)``.

    Pure: nothing is mutated. Raises :class:`Refusal` naming EVERY offending
    model, so one run reports the whole problem, not just the first instance.
    """
    by_id = {m.get("model_id"): m for m in database.get("models", [])}
    problems: list[str] = []
    planned: dict[str, dict[str, Any]] = {}
    summary: dict[str, list[str]] = {"entering": [], "leaving": [], "outside": [], "inside": []}

    seen: set[str] = set()
    for r in results:
        mid = r.get("model_id")
        if not isinstance(mid, str) or mid not in by_id:
            problems.append(f"{mid!r}: not a model in the DB")
            continue
        if mid in seen:
            problems.append(f"{mid}: appears twice in the input")
            continue
        seen.add(mid)
        model = by_id[mid]
        if model.get("gamslib_type") not in IN_SCOPE_TYPES:
            problems.append(
                f"{mid}: type {model.get('gamslib_type')!r} is out of scope "
                f"(LP/NLP/QCP only; MINLP/MIP are never relaxed)"
            )
            continue
        try:
            conv = convexity_from_result(r)
        except (Refusal, KeyError) as exc:
            problems.append(str(exc) if isinstance(exc, Refusal) else f"{mid}: missing {exc}")
            continue
        was_in = (model.get("convexity") or {}).get("status") in CONVEX_STATUSES
        now_in = conv["status"] in CONVEX_STATUSES
        if now_in and not was_in:
            if mid not in admit:
                problems.append(
                    f"{mid}: would ENTER the corpus ({conv['status']}) without --admit. "
                    f"Admission is the owner's rule (Decision 2), passed explicitly"
                )
                continue
            if mid not in recorded:
                problems.append(
                    f"{mid}: --admit given, but it is not recorded in corpus_admissions.json. "
                    f"Record it first, or `kpi_block --corpus continuity` cannot drop it"
                )
                continue
            summary["entering"].append(mid)
        elif was_in and not now_in:
            summary["leaving"].append(mid)
        elif now_in:
            summary["inside"].append(mid)
        else:
            summary["outside"].append(mid)
        planned[mid] = conv

    unused = sorted(admit - set(summary["entering"]))
    if unused:
        problems.append(f"--admit ids that do not enter the corpus in this input: {unused}")
    if problems:
        raise Refusal("\n  ".join(["refused, nothing written:", *problems]))
    return planned, summary


def validate(database: dict[str, Any]) -> list[str] | None:
    """Schema errors, or ``None`` when validation COULD NOT RUN (``None`` != ``[]``)."""
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        return None
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return [
        f"{'/'.join(str(p) for p in e.absolute_path)}: {e.message}"
        for e in Draft7Validator(schema).iter_errors(database)
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("--input", type=Path, required=True, help="verify_convexity --output JSON")
    ap.add_argument("--db", type=Path, required=True, help="results DB to update (no default)")
    ap.add_argument("--admit", nargs="*", default=[], help="model ids admitted to the corpus")
    ap.add_argument("--admissions", type=Path, default=ADMISSIONS_PATH, help=argparse.SUPPRESS)
    ap.add_argument("--dry-run", action="store_true", help="report, write nothing")
    ap.add_argument("--validate", action="store_true", help="validation is REQUIRED")
    ap.add_argument("--no-backup", action="store_true", help="skip the archive backup")
    args = ap.parse_args(argv)

    try:
        report = json.loads(args.input.read_text(encoding="utf-8"))
        database = json.loads(args.db.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("error: %s", exc)
        return 2
    results = report.get("results")
    if not isinstance(results, list) or not results:
        logger.error("error: %s has no results", args.input)
        return 2

    try:
        recorded = load_admitted_record(args.admissions)
        planned, summary = plan(database, results, frozenset(args.admit), recorded)
    except Refusal as exc:
        logger.error("%s", exc)
        return 1

    by_id = {m.get("model_id"): m for m in database["models"]}
    for mid, conv in planned.items():
        by_id[mid]["convexity"] = conv  # REPLACE, never merge
    database["updated_date"] = datetime.now(UTC).isoformat()

    for key in ("entering", "leaving", "inside", "outside"):
        if summary[key]:
            logger.info("%-8s %s", key, ", ".join(sorted(summary[key])))
    if summary["entering"] or summary["leaving"]:
        logger.info(
            "⚠ the candidate corpus moves by +%d / -%d: report both denominators (close rule C4)",
            len(summary["entering"]),
            len(summary["leaving"]),
        )

    errors = validate(database)
    if errors is None:
        logger.warning("⚠ jsonschema is not installed, so the result was NOT validated")
        if args.validate:
            return 1
    elif errors:
        logger.error(
            "the updated DB does NOT validate (%d error(s)); nothing written:", len(errors)
        )
        for e in errors[:20]:
            logger.error("  %s", e)
        return 1

    if args.dry_run:
        logger.info("--dry-run: %d model(s) would be updated; nothing written", len(planned))
        return 0
    if not args.no_backup:
        create_backup(args.db)  # data/gamslib/archive/, which is git-ignored
    args.db.write_text(json.dumps(database, indent=2) + "\n", encoding="utf-8")
    logger.info("wrote %d model(s) to %s", len(planned), args.db)
    return 0


if __name__ == "__main__":
    sys.exit(main())
