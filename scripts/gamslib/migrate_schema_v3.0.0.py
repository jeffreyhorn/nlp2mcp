#!/usr/bin/env python3
"""Migrate gamslib_status.json 2.2.1 -> 3.0.0: mcp_file_used -> mcp_file_generated.

Sprint 39 P7 / Remedy B. Owner decision 2026-09-10; design in
``docs/planning/EPIC_4/SPRINT_39/PRESOLVE_RECORD_REMEDY.md`` §9.

WHY THE FIELD IS RENAMED. The pipeline writes this path at emit time and knows
exactly one thing: that it **generated** that file. It does not know, then or
later, whether the file still exists -- the presolve artifacts are working files
and 14 of the 48 have since been cleaned up. ``mcp_file_used`` asserted a
present-tense fact its writer was never positioned to assert. Under the new name
a missing path is the expected steady state rather than an anomaly.

WHY THIS IS A **MAJOR** BUMP AND NOT 2.2.2. ``mcp_solve_result`` sets
``additionalProperties: false``, so the old and new shapes are **mutually
invalid**: a pre-rename DB fails the post-rename schema exactly as the reverse
fails today. The schema declares its own rule --

    properties.schema_version.description
    "Semantic version of the database schema (MAJOR.MINOR.PATCH)"

-- and under SemVer a breaking change takes the MAJOR digit. Every prior step
(2.1.0, 2.2.0, 2.2.1) was *additive*: new optional properties, old DBs stayed
valid. This one invalidates them, so it is the first major bump in this file's
history.

Usage:
    python scripts/gamslib/migrate_schema_v3.0.0.py --dry-run
    python scripts/gamslib/migrate_schema_v3.0.0.py
    python scripts/gamslib/migrate_schema_v3.0.0.py --validate

⚠ ``--validate`` is restored here deliberately. v2.2.0 and v2.2.1 dropped the
flag that v2.1.0 had, and a migration that cannot check its own output is the
wrong tool for a breaking change. It FAILS CLOSED without ``jsonschema``: the
library's absence is reported as an error rather than passing silently.
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

FROM_VERSION = "2.2.1"
TO_VERSION = "3.0.0"
OLD_KEY = "mcp_file_used"
NEW_KEY = "mcp_file_generated"

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def rename_field(database: dict[str, Any]) -> int:
    """Rename the key in every ``mcp_solve`` that carries it. Returns the count.

    ⚠ Order matters only in that ``pop`` must not run before the value is read;
    a dict rebuild is avoided so unrelated key order stays byte-stable.
    """
    renamed = 0
    for model in database.get("models", []):
        solve = model.get("mcp_solve")
        if isinstance(solve, dict) and OLD_KEY in solve:
            solve[NEW_KEY] = solve.pop(OLD_KEY)
            renamed += 1
    return renamed


def validate(database: dict[str, Any]) -> list[str]:
    """Validate against schema.json. FAILS CLOSED when jsonschema is absent."""
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        return [
            "jsonschema is not installed, so the migrated database was NOT "
            "validated. This is a breaking schema change; do not sign it off on "
            "an unvalidated run. Install jsonschema and re-run --validate."
        ]
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return [
        f"{'/'.join(str(p) for p in e.absolute_path)}: {e.message}"
        for e in Draft7Validator(schema).iter_errors(database)
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dry-run", "-n", action="store_true", help="Preview, write nothing")
    ap.add_argument("--validate", action="store_true", help="Validate against schema.json")
    ap.add_argument("--no-backup", action="store_true", help="Skip backup (not recommended)")
    ap.add_argument("--database", type=Path, default=DATABASE_PATH, help="Database path")
    args = ap.parse_args(argv)

    database = json.loads(args.database.read_text(encoding="utf-8"))
    current = database.get("schema_version", "unknown")

    # Validate-only: the database is already migrated, so there is nothing to do
    # but check it. ⚠ NOT gated on `not args.dry_run` — validation writes
    # nothing, so refusing to run it under --dry-run made `--dry-run --validate`
    # report a result it had never checked (PR #1740 review).
    if args.validate and current == TO_VERSION:
        errors = validate(database)
        if errors:
            logger.error("Validation FAILED with %d error(s):", len(errors))
            for e in errors[:20]:
                logger.error("  %s", e)
            return 1
        logger.info("Validation PASSED: %s is valid against schema.json", args.database)
        return 0

    if current != FROM_VERSION:
        logger.error(
            "Expected schema_version %s, found %r. Refusing to migrate: running "
            "this twice would rename nothing and still bump the version, which "
            "is how a DB ends up claiming a contract it does not meet.",
            FROM_VERSION,
            current,
        )
        return 1

    renamed = rename_field(database)
    database["schema_version"] = TO_VERSION
    # ⚠ `schema.json` defines this as "ISO 8601 timestamp of last modification",
    # and every prior migration (v2.1.0, v2.2.0, v2.2.1) sets it. Omitting it
    # left the DB reporting 2026-05-14 provenance for a file this script had just
    # rewritten 48 rows of — stale provenance is worse than none, because it
    # reads as a positive claim about when the data last moved (PR #1740 review).
    database["updated_date"] = datetime.now(UTC).isoformat()
    database["_migration_summary_v3_0_0"] = {
        "to_version": TO_VERSION,
        "renamed": {"from": OLD_KEY, "to": NEW_KEY, "rows": renamed},
    }

    logger.info("%s -> %s: renamed %s -> %s on %d row(s)",
                FROM_VERSION, TO_VERSION, OLD_KEY, NEW_KEY, renamed)

    # ⚠ Validate the IN-MEMORY migration BEFORE the dry-run exit. Validation
    # writes nothing, so there is no reason to skip it — and skipping it made
    # `--dry-run` the one mode that could not answer the question the flag
    # exists for: *would this migration produce a valid database?*
    errors = validate(database)
    if errors:
        logger.error("Migrated database does NOT validate (%d error(s)):", len(errors))
        for e in errors[:20]:
            logger.error("  %s", e)
        logger.error("Refusing to write.")
        return 1

    if args.dry_run:
        logger.info("--dry-run: migration validates; nothing written")
        return 0

    if not args.no_backup:
        backup = args.database.with_suffix(f".json.bak-{FROM_VERSION}")
        shutil.copy2(args.database, backup)
        logger.info("Backup: %s", backup)

    args.database.write_text(
        json.dumps(database, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    logger.info("Wrote %s", args.database)
    return 0


if __name__ == "__main__":
    sys.exit(main())
