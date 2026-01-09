#!/usr/bin/env python3
"""End-to-end workflow integration test for GAMSLIB pipeline.

This script tests the complete workflow:
1. Initialize database (with --force to reset)
2. Parse a small subset of models
3. Translate successfully parsed models
4. Query and export results

This is a destructive test that reinitializes the database.
Use with caution - creates backups before proceeding.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.db_manager import DATABASE_PATH, create_backup, load_database

# Test configuration
TEST_MODELS = ["chem", "dispatch"]  # Small, fast models that parse successfully
BACKUP_DIR = PROJECT_ROOT / "data" / "gamslib" / "archive"


def run_command(cmd: list[str], description: str) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'=' * 60}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )

    print(f"Return code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")

    return result.returncode, result.stdout, result.stderr


def test_step_1_init(force: bool = True) -> bool:
    """Test Step 1: Initialize database."""
    print("\n" + "=" * 60)
    print("STEP 1: Initialize Database")
    print("=" * 60)

    if not force:
        print("Skipping init (--no-reinit flag set)")
        return True

    # Create backup of existing database
    if DATABASE_PATH.exists():
        backup_path = create_backup()
        if backup_path:
            print(f"✓ Created backup: {backup_path}")

    # Initialize fresh database
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
        "init",
        "--force",
    ]

    returncode, stdout, stderr = run_command(cmd, "Initialize database")

    if returncode != 0:
        print("✗ FAILED: Database initialization failed")
        return False

    # Verify database exists and is valid
    if not DATABASE_PATH.exists():
        print("✗ FAILED: Database file not created")
        return False

    try:
        db = load_database()
        print(f"✓ Database created with {len(db.get('models', []))} models")
        return True
    except Exception as e:
        print(f"✗ FAILED: Database is invalid: {e}")
        return False


def test_step_2_parse(test_models: list[str]) -> bool:
    """Test Step 2: Parse models."""
    print("\n" + "=" * 60)
    print("STEP 2: Parse Models")
    print("=" * 60)

    success_count = 0
    for model_id in test_models:
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "gamslib" / "batch_parse.py"),
            "--model",
            model_id,
            "--verbose",
        ]

        returncode, stdout, stderr = run_command(
            cmd, f"Parse model: {model_id}"
        )

        if returncode != 0:
            print(f"✗ FAILED: Parse failed for {model_id}")
            continue

        # Check if parse was successful
        db = load_database()
        model = next(
            (m for m in db.get("models", []) if m.get("model_id") == model_id),
            None,
        )

        if model and model.get("nlp2mcp_parse", {}).get("status") == "success":
            print(f"✓ Parse succeeded for {model_id}")
            success_count += 1
        else:
            parse_status = model.get("nlp2mcp_parse", {}) if model else {}
            print(
                f"✗ Parse failed for {model_id}: "
                f"{parse_status.get('error', {}).get('message', 'Unknown error')}"
            )

    if success_count == 0:
        print(f"✗ FAILED: No models parsed successfully (0/{len(test_models)})")
        return False

    print(f"✓ Parsed {success_count}/{len(test_models)} models successfully")
    return True


def test_step_3_translate(test_models: list[str]) -> bool:
    """Test Step 3: Translate successfully parsed models."""
    print("\n" + "=" * 60)
    print("STEP 3: Translate Models")
    print("=" * 60)

    # Get models that parsed successfully
    db = load_database()
    parsed_models = [
        m.get("model_id")
        for m in db.get("models", [])
        if m.get("model_id") in test_models
        and m.get("nlp2mcp_parse", {}).get("status") == "success"
    ]

    if not parsed_models:
        print("✗ FAILED: No models available for translation")
        return False

    print(f"Found {len(parsed_models)} models to translate: {parsed_models}")

    success_count = 0
    for model_id in parsed_models:
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "gamslib" / "batch_translate.py"),
            "--model",
            model_id,
            "--verbose",
        ]

        returncode, stdout, stderr = run_command(
            cmd, f"Translate model: {model_id}"
        )

        if returncode != 0:
            print(f"✗ FAILED: Translation failed for {model_id}")
            continue

        # Check if translation was successful
        db = load_database()
        model = next(
            (m for m in db.get("models", []) if m.get("model_id") == model_id),
            None,
        )

        if model and model.get("nlp2mcp_translate", {}).get("status") == "success":
            output_file = model.get("nlp2mcp_translate", {}).get("output_file")
            print(f"✓ Translation succeeded for {model_id} -> {output_file}")
            success_count += 1
        else:
            trans_status = model.get("nlp2mcp_translate", {}) if model else {}
            print(
                f"✗ Translation failed for {model_id}: "
                f"{trans_status.get('error', {}).get('message', 'Unknown error')}"
            )

    if success_count == 0:
        print(
            f"✗ FAILED: No models translated successfully (0/{len(parsed_models)})"
        )
        return False

    print(f"✓ Translated {success_count}/{len(parsed_models)} models successfully")
    return True


def test_step_4_query() -> bool:
    """Test Step 4: Query and verify results."""
    print("\n" + "=" * 60)
    print("STEP 4: Query Database")
    print("=" * 60)

    # Test 1: List all models
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
        "list",
        "--format",
        "json",
    ]

    returncode, stdout, stderr = run_command(cmd, "List all models (JSON)")

    if returncode != 0:
        print("✗ FAILED: List command failed")
        return False

    try:
        data = json.loads(stdout)
        print(f"✓ Listed {data.get('total', 0)} models")
    except json.JSONDecodeError as e:
        print(f"✗ FAILED: Invalid JSON output: {e}")
        return False

    # Test 2: Get specific model details
    for model_id in TEST_MODELS:
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
            "get",
            model_id,
            "--format",
            "json",
        ]

        returncode, stdout, stderr = run_command(
            cmd, f"Get model details: {model_id}"
        )

        if returncode != 0:
            print(f"✗ FAILED: Get command failed for {model_id}")
            return False

        try:
            model = json.loads(stdout)
            print(f"✓ Retrieved model: {model.get('model_id')}")

            # Show parse/translate status
            parse_status = model.get("nlp2mcp_parse", {}).get("status", "not_tested")
            trans_status = model.get("nlp2mcp_translate", {}).get(
                "status", "not_tested"
            )
            print(f"  Parse: {parse_status}, Translate: {trans_status}")

        except json.JSONDecodeError as e:
            print(f"✗ FAILED: Invalid JSON output for {model_id}: {e}")
            return False

    # Test 3: Validate database
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "gamslib" / "db_manager.py"),
        "validate",
    ]

    returncode, stdout, stderr = run_command(cmd, "Validate database")

    if returncode != 0:
        print("✗ FAILED: Database validation failed")
        return False

    print("✓ Database validation passed")
    return True


def run_e2e_test(reinit: bool = True) -> int:
    """Run complete end-to-end workflow test.

    Args:
        reinit: If True, reinitialize database (destructive)

    Returns:
        0 on success, 1 on failure
    """
    print("\n" + "=" * 60)
    print("END-TO-END WORKFLOW INTEGRATION TEST")
    print("=" * 60)
    print(f"Test models: {', '.join(TEST_MODELS)}")
    print(f"Reinitialize database: {reinit}")
    print(f"Database path: {DATABASE_PATH}")
    print("=" * 60)

    start_time = time.perf_counter()

    # Step 1: Initialize
    if not test_step_1_init(force=reinit):
        print("\n✗ FAILED AT STEP 1: Database initialization")
        return 1

    # Step 2: Parse
    if not test_step_2_parse(TEST_MODELS):
        print("\n✗ FAILED AT STEP 2: Model parsing")
        return 1

    # Step 3: Translate
    if not test_step_3_translate(TEST_MODELS):
        print("\n✗ FAILED AT STEP 3: Model translation")
        return 1

    # Step 4: Query
    if not test_step_4_query():
        print("\n✗ FAILED AT STEP 4: Database queries")
        return 1

    elapsed = time.perf_counter() - start_time

    # Final summary
    print("\n" + "=" * 60)
    print("END-TO-END TEST SUMMARY")
    print("=" * 60)
    print(f"✓ All steps completed successfully")
    print(f"Total time: {elapsed:.1f}s")
    print("=" * 60)

    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="End-to-end workflow integration test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--no-reinit",
        action="store_true",
        help="Skip database reinitialization (use existing database)",
    )

    args = parser.parse_args()

    try:
        return run_e2e_test(reinit=not args.no_reinit)
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
