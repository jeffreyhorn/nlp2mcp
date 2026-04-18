#!/usr/bin/env python3
"""Migrate gamslib_status.json from schema v2.2.0 to v2.2.1.

This migration extends the "out of scope for nlp2mcp" exclusion
taxonomy introduced in v2.2.0 (``minlp_out_of_scope``) with a new
exclusion reason for multi-solve driver scripts: ``multi_solve_driver_
out_of_scope``. See ``docs/planning/EPIC_4/SPRINT_24/
PLAN_FIX_DECOMP.md`` and ``AUDIT_MULTI_SOLVE_DRIVERS.md`` for context.

Changes from v2.2.0 to v2.2.1:

1. New exclusion reason ``multi_solve_driver_out_of_scope``. Applied
   to models that
   :func:`src.validation.driver.validate_single_optimization`
   classifies as driver scripts — iterative algorithms that alternate
   solves of multiple models with equation-marginal feedback between
   them. nlp2mcp targets single-NLP KKT translation; these scripts'
   converged objective is the fixed point of a loop, not the
   objective of any single snapshot.

   Shape of the resulting ``pipeline_status`` block is unchanged
   (identical to v2.2.0); only the ``reason`` keyword is new::

       "pipeline_status": {
           "status": "skipped",
           "reason": "multi_solve_driver_out_of_scope",
           "marked_date": "<UTC ISO 8601>",
           "details": "<detector message naming declared models and "
                      "the equation marginals that trigger it>"
       }

2. Stale ``nlp2mcp_parse`` / ``nlp2mcp_translate`` / ``mcp_solve`` /
   ``solution_comparison`` blocks on flagged models are removed
   (same logic as the v2.2.0 sweep for MINLP).

3. Schema version bump to 2.2.1.

The migration is idempotent: it checks each model via the live
detector in :mod:`src.validation.driver`, so re-running against a
database already at v2.2.1 is a no-op.

Usage::

    python scripts/gamslib/migrate_schema_v2.2.1.py            # Migrate
    python scripts/gamslib/migrate_schema_v2.2.1.py --dry-run  # Preview
    python scripts/gamslib/migrate_schema_v2.2.1.py --verbose  # Detailed
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Cheap regex pre-filter: a file cannot be a driver unless its source
# contains at least two ``Model`` declarations and at least two
# ``solve`` statements. These patterns count live (non-commented)
# occurrences to avoid wasting the parser on obvious non-drivers.
_RE_MODEL_DECL = re.compile(r"^\s*Model\s+\w+", re.IGNORECASE | re.MULTILINE)
_RE_SOLVE = re.compile(r"\bsolve\s+\w+", re.IGNORECASE)
_RE_ONTEXT = re.compile(
    r"\$onText.*?\$offText", re.IGNORECASE | re.DOTALL
)

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATABASE_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"
ARCHIVE_PATH = PROJECT_ROOT / "data" / "gamslib" / "archive"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

STALE_PIPELINE_KEYS = (
    "nlp2mcp_parse",
    "nlp2mcp_translate",
    "mcp_solve",
    "solution_comparison",
)

REASON_MULTI_SOLVE = "multi_solve_driver_out_of_scope"


def get_utc_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _cheap_prefilter(path: Path) -> bool:
    """Cheap regex pre-filter: True if the source might be a driver.

    Requires 2+ ``Model`` declarations and 2+ ``solve`` statements in
    the raw source (with ``$onText``/``$offText`` blocks stripped).
    Skipping parsing on the ~98% of files that fail this cuts the
    migration from ~minutes to seconds.
    """
    try:
        src = path.read_text(errors="replace")
    except OSError:
        return False
    src = _RE_ONTEXT.sub("", src)
    n_models = len(_RE_MODEL_DECL.findall(src))
    if n_models < 2:
        return False
    # Only count solve statements outside line comments. In GAMS, `*`
    # is a comment delimiter *only* when it is the first non-whitespace
    # character on a line — `2*x` (multiplication) does not start a
    # comment. Splitting on the first `*` anywhere would incorrectly
    # strip inline multiplication and undercount solves, producing
    # false negatives that skip legitimate driver scripts.
    n_solves = sum(
        1
        for line in src.splitlines()
        if not line.lstrip().startswith("*") and _RE_SOLVE.search(line)
    )
    return n_solves >= 2


def detect_multi_solve_driver(model: dict[str, Any]) -> dict[str, Any] | None:
    """Parse the raw .gms and classify via
    :func:`src.validation.driver.scan_multi_solve_driver`.

    Returns a dict with ``declared_models``, ``solve_targets``, and
    ``equation_marginals`` (a list of ``(name, attr)`` tuples) if the
    model is a driver, else None.
    """
    rel = model.get("file_path")
    if not rel:
        return None
    path = PROJECT_ROOT / rel
    if not path.exists():
        return None
    if not _cheap_prefilter(path):
        return None

    # Lazy import so the script does not depend on heavy parser imports
    # when running --dry-run on a machine without the project installed.
    sys.setrecursionlimit(50000)
    from src.ir.parser import parse_model_file
    from src.validation.driver import scan_multi_solve_driver

    logger.info("  Parsing candidate: %s", model.get("model_id"))
    try:
        ir = parse_model_file(path)
    except Exception as e:
        logger.debug("  parse failed for %s: %s", model.get("model_id"), e)
        return None

    report = scan_multi_solve_driver(ir)
    if not report.is_driver:
        return None
    return {
        "declared_models": report.declared_models,
        "solve_targets": report.solve_targets,
        "equation_marginals": [
            f"{name}.{attr}" for name, attr in report.equation_marginals
        ],
    }


def make_pipeline_status(reason: str, details: str, marked_date: str) -> dict:
    return {
        "status": "skipped",
        "reason": reason,
        "marked_date": marked_date,
        "details": details,
    }


def migrate_model(model: dict[str, Any], marked_date: str) -> bool:
    """Apply v2.2.1 transforms to a single model entry.

    Returns True if the model was changed (flagged as a driver), False
    otherwise. Already-skipped models (e.g., MINLP) are left alone —
    they have their own reason keyword and must not be overwritten.
    """
    model_id = model.get("model_id", "<unknown>")

    # Don't re-classify models that are already skipped for another
    # reason (e.g., MINLP). Multi-solve drivers that happen to also be
    # MINLP remain under the MINLP reason — first exclusion wins.
    existing_ps = model.get("pipeline_status") or {}
    if existing_ps.get("status") == "skipped":
        return False

    # Only consider models that the pipeline currently treats as in-scope
    # candidates. Out-of-scope models (convexity=error, convexity=unknown,
    # or convexity=excluded) are already filtered by batch_parse; flagging
    # them here would also incur the cost of parsing — which, for some
    # edge-case .gms files like t1000 (a deliberately ill-conditioned
    # test problem), can hang the Earley parser indefinitely.
    convexity_status = (model.get("convexity") or {}).get("status")
    if convexity_status not in ("verified_convex", "likely_convex"):
        return False

    report = detect_multi_solve_driver(model)
    if not report:
        return False

    shown_marginals = ", ".join(report["equation_marginals"][:5])
    if len(report["equation_marginals"]) > 5:
        shown_marginals += f" (+{len(report['equation_marginals']) - 5} more)"

    details = (
        "Multi-solve driver script (declared models: "
        f"{report['declared_models']}; solve targets: "
        f"{report['solve_targets']}; equation-marginal feedback: "
        f"{shown_marginals}). Out of scope for single-NLP KKT."
    )

    stripped: list[str] = []
    for key in STALE_PIPELINE_KEYS:
        if key in model:
            stripped.append(key)
            del model[key]

    model["pipeline_status"] = make_pipeline_status(
        REASON_MULTI_SOLVE, details, marked_date
    )

    logger.info(
        "  %s: flagged as driver; stripped %s", model_id, stripped or "(none)"
    )
    return True


def migrate_database(database: dict[str, Any], marked_date: str) -> dict[str, Any]:
    current_version = database.get("schema_version", "unknown")
    if current_version not in ("2.2.0", "2.2.1"):
        logger.warning("Expected schema v2.2.0 or v2.2.1, found v%s", current_version)

    models = database.get("models", [])
    logger.info("Scanning %d models for multi-solve-driver patterns...", len(models))

    changed = 0
    for model in models:
        if migrate_model(model, marked_date):
            changed += 1

    database["schema_version"] = "2.2.1"
    database["updated_date"] = marked_date
    database["_migration_summary_v2_2_1"] = {
        "to_version": "2.2.1",
        "applied_at": marked_date,
        "multi_solve_excluded": changed,
    }

    logger.info(
        "Migration complete: %d newly flagged as multi_solve_driver_out_of_scope",
        changed,
    )
    return database


def create_backup(source_path: Path, archive_path: Path, source_version: str) -> Path:
    """Archive the current database before an in-place migration.

    ``source_version`` is tagged into the filename so backups made from
    a fresh v2.2.0 input vs. an idempotent re-run on an already-v2.2.1
    database can be told apart at a glance. Unknown versions fall back
    to ``vunknown``.
    """
    archive_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    version_tag = source_version.replace("/", "_") if source_version else "unknown"
    backup_name = f"gamslib_status_v{version_tag}_backup_{timestamp}.json"
    backup_path = archive_path / backup_name
    logger.info("Creating backup: %s", backup_path)
    backup_path.write_bytes(source_path.read_bytes())
    return backup_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate gamslib_status.json from v2.2.0 to v2.2.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", "-n", action="store_true", help="Preview")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose")
    parser.add_argument(
        "--no-backup", action="store_true", help="Skip backup (not recommended)"
    )
    parser.add_argument(
        "--database", type=Path, default=DATABASE_PATH, help="Database path"
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        database = json.loads(args.database.read_text())
    except FileNotFoundError:
        logger.error("Database not found: %s", args.database)
        return 1

    current_version = database.get("schema_version", "unknown")
    if current_version not in ("2.2.0", "2.2.1"):
        logger.error(
            "Cannot migrate from v%s — expected v2.2.0 (or idempotent re-run on v2.2.1)",
            current_version,
        )
        return 1

    if not args.dry_run and not args.no_backup:
        create_backup(args.database, ARCHIVE_PATH, current_version)

    marked_date = get_utc_timestamp()
    migrated = migrate_database(database, marked_date)

    if args.dry_run:
        print("\n[DRY RUN] No files written")
        print(json.dumps(migrated.get("_migration_summary_v2_2_1", {}), indent=2))
        return 0

    args.database.write_text(json.dumps(migrated, indent=2) + "\n")
    print(f"\nDatabase updated: {args.database}")
    print(json.dumps(migrated.get("_migration_summary_v2_2_1", {}), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
