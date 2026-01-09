#!/usr/bin/env python3
"""Error recovery and edge case testing for GAMSLIB database.

Tests:
1. Backup creation and listing
2. Backup restoration
3. Corrupted database detection
4. Invalid update rejection
5. Backup pruning
6. Concurrent read access

This script performs non-destructive tests on backup/restore functionality.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.db_manager import (
    DATABASE_PATH,
    BACKUP_DIR,
    create_backup,
    list_backups,
    load_database,
    prune_backups,
    save_database,
    validate_database,
    load_schema,
)


def test_backup_creation() -> bool:
    """Test 1: Backup creation and listing."""
    print("\n" + "=" * 60)
    print("TEST 1: Backup Creation")
    print("=" * 60)

    # Get initial backup count
    initial_backups = list_backups()
    initial_count = len(initial_backups)
    print(f"Initial backup count: {initial_count}")

    # Create a backup
    backup_path = create_backup()

    if not backup_path:
        print("✗ FAILED: Backup creation returned None")
        return False

    if not backup_path.exists():
        print(f"✗ FAILED: Backup file not created: {backup_path}")
        return False

    # Verify backup count (may stay same if we hit MAX_BACKUPS and pruned)
    new_backups = list_backups()
    new_count = len(new_backups)

    # The count should either increase by 1 or stay the same (if at MAX_BACKUPS)
    if new_count not in [initial_count, initial_count + 1]:
        print(f"✗ FAILED: Unexpected backup count change: {initial_count} → {new_count}")
        return False

    # Verify the new backup is in the list
    if backup_path not in new_backups:
        print(f"✗ FAILED: New backup not found in backup list")
        return False

    print(f"✓ Backup created: {backup_path.name}")
    if new_count > initial_count:
        print(f"✓ Backup count increased: {initial_count} → {new_count}")
    else:
        print(f"✓ Backup count maintained (at MAX_BACKUPS={new_count}, oldest pruned)")

    # Verify backup content is valid
    try:
        with open(backup_path) as f:
            backup_data = json.load(f)

        if "models" not in backup_data:
            print("✗ FAILED: Backup file is missing 'models' key")
            return False

        print(f"✓ Backup is valid JSON with {len(backup_data.get('models', []))} models")
        return True

    except json.JSONDecodeError as e:
        print(f"✗ FAILED: Backup file is not valid JSON: {e}")
        return False


def test_backup_restoration() -> bool:
    """Test 2: Backup restoration."""
    print("\n" + "=" * 60)
    print("TEST 2: Backup Restoration")
    print("=" * 60)

    # Create a temporary backup of the current database
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_db_path = Path(tmpdir) / "test_db.json"

        # Save current database to temp location (ensure it can be loaded)
        load_database()
        shutil.copy(DATABASE_PATH, temp_db_path)
        print(f"✓ Saved current database to temp location")

        # Get most recent backup
        backups = list_backups()
        if not backups:
            print("✗ FAILED: No backups available for restoration test")
            return False

        most_recent_backup = backups[-1]
        print(f"✓ Using backup: {most_recent_backup.name}")

        # Load backup content
        with open(most_recent_backup) as f:
            backup_data = json.load(f)

        # Restore by copying backup to database location
        shutil.copy(most_recent_backup, DATABASE_PATH)
        print(f"✓ Restored database from backup")

        # Verify restored database is valid
        try:
            restored_db = load_database()
            print(f"✓ Restored database loaded successfully")
            print(f"  Models in backup: {len(backup_data.get('models', []))}")
            print(f"  Models restored: {len(restored_db.get('models', []))}")

            if len(backup_data['models']) != len(restored_db['models']):
                print("✗ FAILED: Restored database has different model count")
                return False

        except Exception as e:
            print(f"✗ FAILED: Could not load restored database: {e}")
            return False
        finally:
            # Restore original database
            shutil.copy(temp_db_path, DATABASE_PATH)
            print(f"✓ Original database restored")

    return True


def test_corrupted_database_detection() -> bool:
    """Test 3: Detect corrupted database."""
    print("\n" + "=" * 60)
    print("TEST 3: Corrupted Database Detection")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        corrupt_db_path = Path(tmpdir) / "corrupt.json"

        # Test 3a: Invalid JSON
        print("\nTest 3a: Invalid JSON")
        corrupt_db_path.write_text("not valid json {")

        try:
            load_database(corrupt_db_path)
            print("✗ FAILED: Should have raised JSONDecodeError")
            return False
        except json.JSONDecodeError:
            print("✓ Invalid JSON correctly detected")

        # Test 3b: Valid JSON but invalid schema
        print("\nTest 3b: Invalid schema")
        invalid_data = {
            "schema_version": "2.0.0",
            "models": [
                {
                    "model_id": "test",
                    "model_name": "Test",
                    "gamslib_type": "INVALID_TYPE",  # Invalid
                }
            ]
        }

        with open(corrupt_db_path, "w") as f:
            json.dump(invalid_data, f)

        schema = load_schema()
        errors = validate_database(invalid_data, schema)

        if not errors:
            print("✗ FAILED: Should have validation errors")
            return False

        print(f"✓ Schema validation caught {len(errors)} error(s)")
        print(f"  First error: {errors[0]['message'][:80]}...")

    return True


def test_invalid_update_rejection() -> bool:
    """Test 4: Invalid updates are rejected."""
    print("\n" + "=" * 60)
    print("TEST 4: Invalid Update Rejection")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_db_path = Path(tmpdir) / "test_db.json"

        # Create a test database
        test_db = {
            "schema_version": "2.0.0",
            "created_date": "2026-01-01T00:00:00Z",
            "updated_date": "2026-01-01T00:00:00Z",
            "total_models": 1,
            "models": [
                {
                    "model_id": "test",
                    "model_name": "Test Model",
                    "gamslib_type": "LP",
                }
            ]
        }

        save_database(test_db, temp_db_path)
        print("✓ Created test database")

        # Try to make an invalid update
        test_db["models"][0]["gamslib_type"] = "INVALID_TYPE"

        schema = load_schema()
        errors = validate_database(test_db, schema)

        if not errors:
            print("✗ FAILED: Invalid update should fail validation")
            return False

        print(f"✓ Invalid update correctly rejected")
        print(f"  Validation errors: {len(errors)}")

        # Verify original database is unchanged
        original_db = load_database(temp_db_path)
        if original_db["models"][0]["gamslib_type"] != "LP":
            print("✗ FAILED: Original database was modified")
            return False

        print("✓ Original database unchanged")

    return True


def test_backup_pruning() -> bool:
    """Test 5: Backup pruning keeps only recent backups."""
    print("\n" + "=" * 60)
    print("TEST 5: Backup Pruning")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_backup_dir = Path(tmpdir) / "archive"
        temp_backup_dir.mkdir()

        # Create 15 dummy backup files with timestamps
        for i in range(1, 16):
            backup_file = temp_backup_dir / f"202601{i:02d}_100000_gamslib_status.json"
            backup_file.write_text("{}")

        print(f"✓ Created 15 test backup files")

        # Monkey-patch BACKUP_DIR for this test
        import scripts.gamslib.db_manager as db_manager
        original_backup_dir = db_manager.BACKUP_DIR
        db_manager.BACKUP_DIR = temp_backup_dir

        try:
            # Prune to keep only 10
            pruned = prune_backups(keep_count=10)

            if pruned != 5:
                print(f"✗ FAILED: Should have pruned 5 backups, pruned {pruned}")
                return False

            print(f"✓ Pruned {pruned} old backups")

            # Verify only 10 remain
            remaining = list(temp_backup_dir.glob("*_gamslib_status.json"))
            if len(remaining) != 10:
                print(f"✗ FAILED: Should have 10 backups remaining, found {len(remaining)}")
                return False

            print(f"✓ Correct number of backups remaining: {len(remaining)}")

            # Verify the newest ones were kept
            remaining_names = sorted([b.name for b in remaining])
            expected_names = [
                f"202601{i:02d}_100000_gamslib_status.json" for i in range(6, 16)
            ]

            if remaining_names != expected_names:
                print(f"✗ FAILED: Wrong backups were kept")
                print(f"  Expected: {expected_names[0]} to {expected_names[-1]}")
                print(f"  Got: {remaining_names[0]} to {remaining_names[-1]}")
                return False

            print(f"✓ Correct backups kept (most recent 10)")

        finally:
            # Restore original BACKUP_DIR
            db_manager.BACKUP_DIR = original_backup_dir

    return True


def test_concurrent_read_access() -> bool:
    """Test 6: Multiple concurrent reads work correctly."""
    print("\n" + "=" * 60)
    print("TEST 6: Concurrent Read Access")
    print("=" * 60)

    # This is a simple test - just verify we can read the database multiple times
    # Real concurrent access would require threading/multiprocessing

    try:
        db1 = load_database()
        db2 = load_database()
        db3 = load_database()

        if db1 is db2:  # They should be different objects
            print("⚠ WARNING: Multiple reads returned same object (caching?)")

        # Verify all reads returned the same data
        if (db1["schema_version"] != db2["schema_version"] or
            db2["schema_version"] != db3["schema_version"]):
            print("✗ FAILED: Different reads returned different data")
            return False

        if (len(db1["models"]) != len(db2["models"]) or
            len(db2["models"]) != len(db3["models"])):
            print("✗ FAILED: Different reads returned different model counts")
            return False

        print("✓ Multiple concurrent reads successful")
        print(f"  Schema version: {db1['schema_version']}")
        print(f"  Models: {len(db1['models'])}")

        return True

    except Exception as e:
        print(f"✗ FAILED: Concurrent reads failed: {e}")
        return False


def run_all_tests() -> int:
    """Run all error recovery tests.

    Returns:
        0 on success, 1 if any test failed
    """
    print("\n" + "=" * 60)
    print("ERROR RECOVERY AND EDGE CASE TESTS")
    print("=" * 60)
    print(f"Database: {DATABASE_PATH}")
    print(f"Backup dir: {BACKUP_DIR}")
    print("=" * 60)

    tests = [
        ("Backup Creation", test_backup_creation),
        ("Backup Restoration", test_backup_restoration),
        ("Corrupted Database Detection", test_corrupted_database_detection),
        ("Invalid Update Rejection", test_invalid_update_rejection),
        ("Backup Pruning", test_backup_pruning),
        ("Concurrent Read Access", test_concurrent_read_access),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ UNEXPECTED ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")

    print("=" * 60)
    print(f"Total: {passed_count}/{total_count} tests passed")
    print("=" * 60)

    return 0 if passed_count == total_count else 1


def main() -> int:
    """Main entry point."""
    try:
        return run_all_tests()
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
