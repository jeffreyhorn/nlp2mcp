#!/usr/bin/env python3
"""
Version Bump Script for nlp2mcp

Automatically updates version numbers in pyproject.toml following semantic versioning.

Usage:
    python scripts/bump_version.py [major|minor|patch|beta|rc] [--dry-run]

Examples:
    python scripts/bump_version.py patch        # 0.5.0 → 0.5.1
    python scripts/bump_version.py minor        # 0.5.0 → 0.6.0
    python scripts/bump_version.py major        # 0.5.0 → 1.0.0
    python scripts/bump_version.py beta         # 0.5.0 → 0.6.0-beta
    python scripts/bump_version.py rc           # 0.5.0-beta → 0.5.0-rc.1
    python scripts/bump_version.py --dry-run patch  # Show what would change
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional, Tuple


def parse_version(version: str) -> dict:
    """
    Parse a semantic version string into components.

    Args:
        version: Version string (e.g., "0.5.0-beta", "1.0.0")

    Returns:
        Dictionary with keys: major, minor, patch, prerelease, build
    """
    # Pattern: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
    pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.]+))?(?:\+([a-zA-Z0-9.]+))?$"
    match = re.match(pattern, version)

    if not match:
        raise ValueError(f"Invalid version string: {version}")

    major, minor, patch, prerelease, build = match.groups()

    return {
        "major": int(major),
        "minor": int(minor),
        "patch": int(patch),
        "prerelease": prerelease,
        "build": build,
    }


def format_version(version_dict: dict) -> str:
    """
    Format version components back into a version string.

    Args:
        version_dict: Dictionary with version components

    Returns:
        Formatted version string
    """
    base = f"{version_dict['major']}.{version_dict['minor']}.{version_dict['patch']}"

    if version_dict.get("prerelease"):
        base += f"-{version_dict['prerelease']}"

    if version_dict.get("build"):
        base += f"+{version_dict['build']}"

    return base


def bump_version(current: str, bump_type: str) -> str:
    """
    Bump version according to specified type.

    Args:
        current: Current version string
        bump_type: One of: major, minor, patch, beta, rc

    Returns:
        New version string
    """
    v = parse_version(current)

    if bump_type == "major":
        v["major"] += 1
        v["minor"] = 0
        v["patch"] = 0
        v["prerelease"] = None
        v["build"] = None

    elif bump_type == "minor":
        v["minor"] += 1
        v["patch"] = 0
        v["prerelease"] = None
        v["build"] = None

    elif bump_type == "patch":
        v["patch"] += 1
        v["prerelease"] = None
        v["build"] = None

    elif bump_type == "beta":
        # If already has prerelease, increment minor first
        if v.get("prerelease"):
            v["minor"] += 1
            v["patch"] = 0
        else:
            v["minor"] += 1
            v["patch"] = 0
        v["prerelease"] = "beta"
        v["build"] = None

    elif bump_type == "rc":
        # Release candidate
        if v.get("prerelease"):
            # If beta, switch to rc.1
            if "beta" in v["prerelease"]:
                v["prerelease"] = "rc.1"
            # If already rc, increment number
            elif v["prerelease"].startswith("rc."):
                num = int(v["prerelease"].split(".")[1])
                v["prerelease"] = f"rc.{num + 1}"
            else:
                v["prerelease"] = "rc.1"
        else:
            # Add rc.1 to current version
            v["prerelease"] = "rc.1"
        v["build"] = None

    else:
        raise ValueError(f"Unknown bump type: {bump_type}")

    return format_version(v)


def read_pyproject_version(pyproject_path: Path) -> Tuple[str, str]:
    """
    Read current version from pyproject.toml.

    Args:
        pyproject_path: Path to pyproject.toml

    Returns:
        Tuple of (full_content, current_version)
    """
    content = pyproject_path.read_text()

    # Find version line
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")

    return content, match.group(1)


def update_pyproject_version(content: str, old_version: str, new_version: str) -> str:
    """
    Update version in pyproject.toml content.

    Args:
        content: Full pyproject.toml content
        old_version: Current version to replace
        new_version: New version to insert

    Returns:
        Updated content
    """
    # Replace version line
    pattern = f'^version\\s*=\\s*"{re.escape(old_version)}"'
    replacement = f'version = "{new_version}"'

    updated = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    if updated == content:
        raise ValueError(f"Failed to update version from {old_version} to {new_version}")

    return updated


def main():
    """Main entry point for version bump script."""
    parser = argparse.ArgumentParser(
        description="Bump version in pyproject.toml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s patch        # 0.5.0 → 0.5.1
  %(prog)s minor        # 0.5.0 → 0.6.0
  %(prog)s major        # 0.5.0 → 1.0.0
  %(prog)s beta         # 0.5.0 → 0.6.0-beta
  %(prog)s rc           # 0.5.0-beta → 0.5.0-rc.1
  %(prog)s --dry-run patch  # Show what would change
        """,
    )
    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch", "beta", "rc"],
        help="Type of version bump to perform",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without modifying files",
    )

    args = parser.parse_args()

    # Find pyproject.toml
    repo_root = Path(__file__).parent.parent
    pyproject_path = repo_root / "pyproject.toml"

    if not pyproject_path.exists():
        print(f"Error: pyproject.toml not found at {pyproject_path}", file=sys.stderr)
        return 1

    try:
        # Read current version
        content, current_version = read_pyproject_version(pyproject_path)
        print(f"Current version: {current_version}")

        # Calculate new version
        new_version = bump_version(current_version, args.bump_type)
        print(f"New version:     {new_version}")

        if args.dry_run:
            print("\n[DRY RUN] No changes made.")
            return 0

        # Update pyproject.toml
        updated_content = update_pyproject_version(content, current_version, new_version)
        pyproject_path.write_text(updated_content)

        print(f"\n✓ Updated {pyproject_path}")
        print(f"\nNext steps:")
        print(f"  1. Review changes: git diff pyproject.toml")
        print(f"  2. Update CHANGELOG.md with release notes")
        print(f"  3. Commit: git commit -am 'Bump version to {new_version}'")
        print(f"  4. Tag: git tag -a v{new_version} -m 'Release v{new_version}'")
        print(f"  5. Push: git push origin main --tags")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
