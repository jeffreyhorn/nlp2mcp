"""GAMS syntax validation.

This module provides optional GAMS syntax validation by running GAMS
in compile-only mode to check for syntax errors.

GAMS validation is optional and only runs if GAMS is available on the system.
"""

import shutil
import subprocess
from pathlib import Path


def find_gams_executable() -> str | None:
    """Find GAMS executable on the system.

    Returns:
        Path to GAMS executable if found, None otherwise

    Checks common GAMS installation locations:
    - /Library/Frameworks/GAMS.framework/Versions/*/Resources/gams (macOS)
    - gams in PATH (all platforms)
    """
    # Check macOS framework location
    gams_framework = Path("/Library/Frameworks/GAMS.framework")
    if gams_framework.exists():
        # Find latest version
        versions_dir = gams_framework / "Versions"
        if versions_dir.exists():
            # Get all version directories (skip Current symlink)
            versions = [v for v in versions_dir.iterdir() if v.is_dir() and v.name != "Current"]
            if versions:
                # Sort by version number using numeric comparison
                # This handles version numbers like 10, 51, 9 correctly
                # (lexicographic would incorrectly sort 10 < 9)
                def version_key(path: Path) -> int:
                    """Extract numeric version for sorting."""
                    try:
                        return int(path.name)
                    except ValueError:
                        # If version is not a simple integer, fall back to 0
                        return 0

                versions.sort(key=version_key, reverse=True)
                for version_dir in versions:
                    gams_exe = version_dir / "Resources" / "gams"
                    if gams_exe.exists() and gams_exe.is_file():
                        return str(gams_exe)

    # Check if gams is in PATH (cross-platform using shutil.which)
    gams_path = shutil.which("gams")
    if gams_path and Path(gams_path).exists():
        return gams_path

    return None


def validate_gams_syntax(gams_file: str, gams_executable: str | None = None) -> tuple[bool, str]:
    """Run GAMS in compile-only mode to check syntax.

    Args:
        gams_file: Path to GAMS file to validate
        gams_executable: Optional explicit path to GAMS executable.
                        If None, will attempt to find GAMS automatically.

    Returns:
        Tuple of (success: bool, message: str)
        - If GAMS not found: (False, "GAMS not found")
        - If syntax valid: (True, "GAMS syntax valid")
        - If syntax invalid: (False, error_message)

    Raises:
        FileNotFoundError: If gams_file does not exist

    Example:
        >>> success, msg = validate_gams_syntax("model.gms")
        >>> if not success:
        ...     print(f"Validation failed: {msg}")
    """
    # Check if GAMS file exists and get absolute path
    gams_path = Path(gams_file).resolve()
    if not gams_path.exists():
        raise FileNotFoundError(f"GAMS file not found: {gams_file}")

    # Find GAMS executable
    if gams_executable is None:
        gams_executable = find_gams_executable()

    if gams_executable is None:
        return (False, "GAMS executable not found on system")

    # Run GAMS in compile-only mode
    # action=c : compile only (syntax check)
    #
    # IMPORTANT: We do NOT use the GAMS exit code to determine success/failure.
    # GAMS return codes are unreliable for compile-only mode:
    #   - Code 0: Normal completion (rare in compile-only mode)
    #   - Code 6: Parameter error (common in compile-only, but NOT a compilation error)
    #   - Code 2: Compilation error (actual syntax error)
    #
    # Instead, we parse the .lst file which is the authoritative source:
    #   - Presence of "COMPILATION TIME" → successful compilation
    #   - Presence of "****" or "Error" → compilation failed
    try:
        result = subprocess.run(
            [gams_executable, str(gams_path), "action=c"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=gams_path.parent,  # Run in file's directory
        )

        # Note: Exit code is intentionally ignored (see comment above)
        # But we capture it for diagnostic purposes if needed
        exit_code = result.returncode

        # Check the .lst file for compilation errors
        lst_file = gams_path.parent / (gams_path.stem + ".lst")
        if not lst_file.exists():
            return (False, "GAMS did not create .lst file (unexpected error)")

        # Parse .lst file for errors
        lst_content = lst_file.read_text()

        # Look for compilation errors (marked with **** in GAMS output)
        # Real GAMS errors have patterns like:
        #   **** 120  Unknown identifier entered as set
        #   **** $171,340  (column references)
        # Section headers like "**** FILE SUMMARY" are not errors
        error_lines = []
        in_error_section = False
        for line in lst_content.splitlines():
            stripped = line.strip()
            # GAMS errors: "**** <number>" or "**** $<numbers>"
            # NOT headers like "**** FILE SUMMARY"
            if stripped.startswith("****"):
                # Check if it's an actual error (has number/$ after ****)
                after_stars = stripped[4:].lstrip()
                if after_stars and (after_stars[0].isdigit() or after_stars[0] == "$"):
                    error_lines.append(stripped)
                    in_error_section = True
                else:
                    in_error_section = False
            elif in_error_section and stripped.startswith("****"):
                error_lines.append(stripped)
            elif in_error_section and not stripped:
                in_error_section = False

        # Check for GAMS-specific error markers in error_lines or summary section
        # Use specific error markers to avoid false positives from user comments/variable names
        if error_lines or ("SYNTAX ERROR" in lst_content or "COMPILATION ERROR" in lst_content):
            error_msg = (
                "\n".join(error_lines[:10]) if error_lines else "GAMS compilation errors found"
            )
            return (False, error_msg)

        # If COMPILATION TIME appears, compilation succeeded
        if "COMPILATION TIME" in lst_content:
            return (True, "GAMS syntax valid")

        # If we get here, something unexpected happened
        return (
            False,
            f"Could not determine compilation status from .lst file (exit code: {exit_code})",
        )

    except subprocess.TimeoutExpired:
        return (False, "GAMS validation timed out (30s limit)")
    except subprocess.SubprocessError as e:
        return (False, f"GAMS subprocess error: {e}")
    except Exception as e:
        return (False, f"Error reading GAMS output: {e}")


def validate_gams_syntax_or_skip(gams_file: str, gams_executable: str | None = None) -> str | None:
    """Validate GAMS syntax, returning error message or None if valid/skipped.

    This is a convenience wrapper for validate_gams_syntax that:
    - Returns None if GAMS not available (skips validation)
    - Returns None if syntax is valid
    - Returns error message string if syntax is invalid

    Args:
        gams_file: Path to GAMS file to validate
        gams_executable: Optional explicit path to GAMS executable

    Returns:
        None if validation passed or was skipped (GAMS not available)
        Error message string if validation failed

    Raises:
        FileNotFoundError: If gams_file does not exist

    Example:
        >>> error = validate_gams_syntax_or_skip("model.gms")
        >>> if error:
        ...     print(f"Syntax error: {error}")
        ... else:
        ...     print("Syntax OK or GAMS not available")
    """
    success, message = validate_gams_syntax(gams_file, gams_executable)

    # If GAMS not found, skip validation (return None)
    if not success and "not found" in message.lower():
        return None

    # If validation succeeded, return None
    if success:
        return None

    # Otherwise return error message
    return message
