#!/usr/bin/env python3
"""Migrate gamslib_status.json 3.0.0 -> 3.1.0: add license provenance fields.

Sprint 40 P1. Design: ``docs/planning/EPIC_4/SPRINT_40/SCHEMA_3_1_0_DESIGN.md`` §7.

WHAT IS ADDED. Every ``mcp_solve`` object gains ``license_edition``; every
``convexity`` object gains ``license_edition`` and ``gams_version``. All are added
as ``null``, and only where ABSENT. An existing value is never overwritten.

WHY ``null`` AND NOT ``"demo"``. ``null`` means *unrecorded*. A pre-license row's
edition is unknown. Most corpus rows were small enough to solve on either
edition, so writing ``"demo"`` would be a positive claim nobody measured. A
row's edition changes only when the run that produced it is re-run.

WHY ``convexity.solver`` IS NOT ADDED. It is non-nullable in ``convexity_result``
and nothing has recorded it, so it stays absent until a real value is written
(the P3 application writer, W10).

WHY THIS IS A **MINOR** BUMP. The change is additive: new optional properties.
(``additionalProperties: false`` still means a 3.1.0 row fails the 3.0.0 schema,
exactly as 2.2.1's additions did for 2.2.0.)

Usage:
    python scripts/gamslib/migrate_schema_v3.1.0.py --dry-run --validate
    python scripts/gamslib/migrate_schema_v3.1.0.py
    python scripts/gamslib/migrate_schema_v3.1.0.py --validate

``jsonschema`` is optional and UNDECLARED, exactly as in
``migrate_schema_v3.0.0.py``. A default run WARNS when it is absent and
proceeds; an explicit ``--validate`` treats its absence as an ERROR.
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"
SCHEMA_PATH = PROJECT_ROOT / "data" / "gamslib" / "schema.json"

FROM_VERSION = "3.0.0"
TO_VERSION = "3.1.0"

#: (stage object, field) pairs this migration adds, each as ``None`` if absent.
ADDED_FIELDS: tuple[tuple[str, str], ...] = (
    ("mcp_solve", "license_edition"),
    ("convexity", "license_edition"),
    ("convexity", "gams_version"),
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

_UNAVAILABLE = (
    "jsonschema is not installed, so the database was NOT validated. "
    "`pip install jsonschema` and re-run with --validate."
)


def add_fields(database: dict[str, Any]) -> dict[str, int]:
    """Add each field as ``None`` where absent. Returns the per-field counts.

    ⚠ Never overwrites, so a value a 3.1.0 writer already recorded survives.
    Keys are appended, never rebuilt into a new dict, so the existing key order
    (and therefore the diff) stays byte-stable outside the new keys.
    """
    added = {f"{stage}.{field}": 0 for stage, field in ADDED_FIELDS}
    for model in database.get("models", []):
        for stage, field in ADDED_FIELDS:
            obj = model.get(stage)
            if isinstance(obj, dict) and field not in obj:
                obj[field] = None
                added[f"{stage}.{field}"] += 1
    return added


def validate(database: dict[str, Any]) -> list[str] | None:
    """Schema errors, or ``None`` when validation COULD NOT RUN.

    ``None`` and ``[]`` are different answers, as in ``migrate_schema_v3.0.0``:
    "could not check" must never read as "found nothing".
    """
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
    ap.add_argument("--dry-run", "-n", action="store_true", help="Preview, write nothing")
    ap.add_argument("--validate", action="store_true", help="Validate against schema.json")
    ap.add_argument("--no-backup", action="store_true", help="Skip backup (not recommended)")
    ap.add_argument("--database", type=Path, default=DATABASE_PATH, help="Database path")
    args = ap.parse_args(argv)

    database = json.loads(args.database.read_text(encoding="utf-8"))
    current = database.get("schema_version", "unknown")

    # Validate-only: already migrated, so there is nothing to do but check it.
    # Not gated on --dry-run, because validation writes nothing.
    if args.validate and current == TO_VERSION:
        errors = validate(database)
        if errors is None:
            logger.error(_UNAVAILABLE)
            return 1
        if errors:
            logger.error("Validation FAILED with %d error(s):", len(errors))
            for e in errors[:20]:
                logger.error("  %s", e)
            return 1
        logger.info("Validation PASSED: %s is valid against schema.json", args.database)
        return 0

    if current != FROM_VERSION:
        logger.error(
            "Expected schema_version %s, found %r. Refusing to migrate: a second run "
            "would add nothing and still bump the version.",
            FROM_VERSION,
            current,
        )
        return 1

    added = add_fields(database)
    database["schema_version"] = TO_VERSION
    # `schema.json`: "ISO 8601 timestamp of last modification". Every prior
    # migration sets it; a stale one reads as a claim about when data last moved.
    database["updated_date"] = datetime.now(UTC).isoformat()
    database["_migration_summary_v3_1_0"] = {"to_version": TO_VERSION, "added": added}

    logger.info(
        "%s -> %s: added %s",
        FROM_VERSION,
        TO_VERSION,
        ", ".join(f"{k}={v}" for k, v in added.items()),
    )

    # Validate the IN-MEMORY result before the dry-run exit, so --dry-run can
    # answer "would this produce a valid database?".
    errors = validate(database)
    validated = errors is not None
    if errors is None:
        logger.warning("⚠ %s", _UNAVAILABLE)
        if args.validate:
            return 1
    elif errors:
        logger.error("Migrated database does NOT validate (%d error(s)):", len(errors))
        for e in errors[:20]:
            logger.error("  %s", e)
        logger.error("Refusing to write.")
        return 1

    if args.dry_run:
        logger.info(
            "--dry-run: %s; nothing written",
            "migration validates" if validated else "migration NOT validated (see above)",
        )
        return 0

    if not args.no_backup:
        backup = args.database.with_suffix(f".json.bak-{FROM_VERSION}")
        shutil.copy2(args.database, backup)
        logger.info("Backup: %s", backup)

    # DEFAULT escaping (no ensure_ascii=False), matching every prior migration
    # and `db_manager.save_database`, so the diff is only the added keys.
    args.database.write_text(json.dumps(database, indent=2) + "\n", encoding="utf-8")
    logger.info("Wrote %s", args.database)
    return 0


if __name__ == "__main__":
    sys.exit(main())
