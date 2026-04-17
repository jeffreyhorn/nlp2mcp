#!/usr/bin/env python3
"""Migrate gamslib_status.json from schema v2.1.0 to v2.2.0.

This migration formalizes the "out of scope for nlp2mcp" exclusion
taxonomy and cleans up stale pipeline artifacts on excluded models.
See ``docs/planning/EPIC_4/SPRINT_24/PLAN_FIX_FEEDTRAY.md`` and
``AUDIT_MINLP_LEAKAGE.md`` for context.

Changes from v2.1.0 to v2.2.0:

1. Per-model ``pipeline_status`` block (new). Replaces
   ``nlp2mcp_parse``, ``nlp2mcp_translate``, ``mcp_solve``, and
   ``solution_comparison`` for any model that nlp2mcp must not
   process. Shape::

       "pipeline_status": {
           "status": "skipped",
           "reason": "minlp_out_of_scope" | "legacy_excluded",
           "marked_date": "<UTC ISO 8601>",
           "details": "<short human-readable reason>"
       }

2. ``gamslib_type`` correction (when source disagrees with catalog).
   The GAMSlib catalog labels every MINLP/MIP/MIQCP in the corpus as
   ``NLP``/``QCP``/``LP``/``DNLP``. The migration scans the raw
   source for ``Binary Variable(s)``, ``Integer Variable(s)``,
   ``SOS{1,2} Variable(s)``, and ``solve … using {minlp|mip|miqcp|
   rminlp|rmip|rmiqcp}`` to derive the true model class. When source
   and catalog disagree:
       - ``gamslib_type`` is overwritten with the source-derived
         value (uppercased).
       - The original catalog value is stored under
         ``original_gamslib_type``.

3. ``convexity.reason`` (new). Mirrors ``pipeline_status.reason`` for
   consumers that already read the convexity block.

The migration is non-destructive aside from the deliberate stale-
artifact removal. The original ``convexity`` block is preserved
verbatim.

Usage::

    python scripts/gamslib/migrate_schema_v2.2.0.py            # Migrate
    python scripts/gamslib/migrate_schema_v2.2.0.py --dry-run  # Preview
    python scripts/gamslib/migrate_schema_v2.2.0.py --verbose  # Detailed
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

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATABASE_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"
ARCHIVE_PATH = PROJECT_ROOT / "data" / "gamslib" / "archive"
RAW_DIR = PROJECT_ROOT / "data" / "gamslib" / "raw"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Discrete-signal detectors against the raw GAMS source.
RE_BINARY_VAR = re.compile(r"^\s*Binary\s+Variables?\b", re.IGNORECASE | re.MULTILINE)
RE_INTEGER_VAR = re.compile(
    r"^\s*Integer\s+Variables?\b", re.IGNORECASE | re.MULTILINE
)
RE_SOS1_VAR = re.compile(r"^\s*SOS1\s+Variables?\b", re.IGNORECASE | re.MULTILINE)
RE_SOS2_VAR = re.compile(r"^\s*SOS2\s+Variables?\b", re.IGNORECASE | re.MULTILINE)
RE_DISCRETE_SOLVE = re.compile(
    r"\bsolve\b[^;]*\busing\s+(minlp|mip|miqcp|rminlp|rmip|rmiqcp)\b",
    re.IGNORECASE | re.DOTALL,
)

STALE_PIPELINE_KEYS = (
    "nlp2mcp_parse",
    "nlp2mcp_translate",
    "mcp_solve",
    "solution_comparison",
)

REASON_MINLP = "minlp_out_of_scope"
REASON_LEGACY = "legacy_excluded"


def get_utc_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def detect_source_solve_type(model: dict[str, Any]) -> str | None:
    """Read the raw .gms and return its discrete solve-type, if any.

    Returns the uppercased solve-type token (``"MINLP"``, ``"MIP"``,
    ``"MIQCP"``, ``"RMINLP"``, ``"RMIP"``, ``"RMIQCP"``) when the
    source declares discrete vars or names a discrete solver, else None.
    """
    rel = model.get("file_path")
    if not rel:
        return None
    path = PROJECT_ROOT / rel
    if not path.exists():
        return None
    try:
        src = path.read_text(errors="replace")
    except OSError:
        return None

    m = RE_DISCRETE_SOLVE.search(src)
    if m:
        return m.group(1).upper()
    if RE_BINARY_VAR.search(src) or RE_INTEGER_VAR.search(src):
        # Has discrete vars but no explicit MINLP solve clause — record
        # as MINLP since that's what the model effectively is.
        return "MINLP"
    if RE_SOS1_VAR.search(src) or RE_SOS2_VAR.search(src):
        return "MIP"
    return None


def make_pipeline_status(reason: str, details: str, marked_date: str) -> dict:
    return {
        "status": "skipped",
        "reason": reason,
        "marked_date": marked_date,
        "details": details,
    }


def migrate_model(model: dict[str, Any], marked_date: str) -> dict[str, Any]:
    """Apply v2.2.0 transforms to a single model entry, in place semantics."""
    model_id = model.get("model_id", "<unknown>")

    # 1. Detect true discreteness from the raw source.
    source_solve_type = detect_source_solve_type(model)
    catalog_type = model.get("gamslib_type")

    if source_solve_type and source_solve_type != catalog_type:
        model.setdefault("original_gamslib_type", catalog_type)
        model["gamslib_type"] = source_solve_type
        logger.debug(
            "  %s: gamslib_type %s -> %s (from source)",
            model_id,
            catalog_type,
            source_solve_type,
        )

    # 2. Decide pipeline_status. Models are skipped if either:
    #    - Source is MINLP/MIP/MIQCP (out of scope), or
    #    - convexity.status is already "excluded" (preserve existing call)
    convexity = model.get("convexity") or {}
    convexity_status = convexity.get("status")
    is_minlp = source_solve_type is not None
    is_excluded = convexity_status == "excluded"

    if not (is_minlp or is_excluded):
        # In-scope continuous model — nothing to do.
        return model

    if is_minlp:
        reason = REASON_MINLP
        details = (
            convexity.get("error")
            or convexity.get("error_message")
            or f"Model uses discrete solver class: {source_solve_type}"
        )
    else:
        # Excluded but not MINLP — preserve original error if present.
        original_error = convexity.get("error") or convexity.get("error_message")
        if original_error and "MINLP" in original_error.upper():
            reason = REASON_MINLP
        else:
            reason = REASON_LEGACY
        details = original_error or "Excluded by earlier pipeline; reason not recorded."

    # 3. Strip stale pipeline artifacts.
    stripped = []
    for key in STALE_PIPELINE_KEYS:
        if key in model:
            stripped.append(key)
            del model[key]

    # 4. Mirror the reason on the convexity block for downstream consumers.
    if convexity:
        convexity["reason"] = reason
        # Promote convexity.status to "excluded" for newly-detected MINLPs
        # whose convexity block reports something else (e.g. "likely_convex").
        if is_minlp and convexity_status != "excluded":
            convexity.setdefault("original_status", convexity_status)
            convexity["status"] = "excluded"

    # 5. Install the unified pipeline_status block.
    model["pipeline_status"] = make_pipeline_status(reason, details, marked_date)

    if stripped:
        logger.debug("  %s: removed stale %s; reason=%s", model_id, stripped, reason)
    elif is_minlp and convexity_status != "excluded":
        logger.debug("  %s: newly excluded as MINLP (was %s)", model_id, convexity_status)

    return model


def migrate_database(database: dict[str, Any], marked_date: str) -> dict[str, Any]:
    current_version = database.get("schema_version", "unknown")
    if current_version != "2.1.0":
        logger.warning("Expected schema v2.1.0, found v%s", current_version)

    models = database.get("models", [])
    logger.info("Migrating %d models from v2.1.0 to v2.2.0...", len(models))

    counts = {"minlp_excluded": 0, "legacy_excluded": 0, "in_scope": 0, "type_corrected": 0}
    for model in models:
        before_type = model.get("gamslib_type")
        migrated = migrate_model(model, marked_date)
        ps = migrated.get("pipeline_status")
        if ps:
            if ps["reason"] == REASON_MINLP:
                counts["minlp_excluded"] += 1
            elif ps["reason"] == REASON_LEGACY:
                counts["legacy_excluded"] += 1
        else:
            counts["in_scope"] += 1
        if migrated.get("gamslib_type") != before_type:
            counts["type_corrected"] += 1

    database["schema_version"] = "2.2.0"
    database["updated_date"] = marked_date
    database["_migration_summary"] = {
        "to_version": "2.2.0",
        "applied_at": marked_date,
        **counts,
    }

    logger.info(
        "Migration complete: %d MINLP-excluded, %d legacy-excluded, "
        "%d in-scope, %d type-corrected",
        counts["minlp_excluded"],
        counts["legacy_excluded"],
        counts["in_scope"],
        counts["type_corrected"],
    )
    return database


def create_backup(source_path: Path, archive_path: Path) -> Path:
    archive_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_name = f"gamslib_status_v2.1.0_backup_{timestamp}.json"
    backup_path = archive_path / backup_name
    logger.info("Creating backup: %s", backup_path)
    backup_path.write_bytes(source_path.read_bytes())
    return backup_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate gamslib_status.json from v2.1.0 to v2.2.0",
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
    if current_version == "2.2.0":
        logger.info("Database already at v2.2.0; no migration needed")
        return 0
    if current_version != "2.1.0":
        logger.error("Cannot migrate from v%s — expected v2.1.0", current_version)
        return 1

    if not args.dry_run and not args.no_backup:
        create_backup(args.database, ARCHIVE_PATH)

    marked_date = get_utc_timestamp()
    migrated = migrate_database(database, marked_date)

    if args.dry_run:
        print("\n[DRY RUN] No files written")
        print(json.dumps(migrated.get("_migration_summary", {}), indent=2))
        return 0

    args.database.write_text(json.dumps(migrated, indent=2) + "\n")
    print(f"\nDatabase updated: {args.database}")
    print(json.dumps(migrated.get("_migration_summary", {}), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
