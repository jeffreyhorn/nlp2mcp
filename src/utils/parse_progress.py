"""
Parse progress tracking utilities.

Provides functions to calculate how much of a GAMS source file was successfully
parsed before an error occurred, and to extract hints about missing features.
"""

import re
from pathlib import Path


def count_logical_lines(source: str) -> int:
    """
    Count logical lines (non-empty, non-comment) in GAMS source.

    Logical lines are lines that contain actual GAMS code, excluding:
    - Empty lines (whitespace only)
    - Comment-only lines (lines starting with *)
    - Lines inside multiline comments ($ontext ... $offtext)

    Args:
        source: GAMS source code as string

    Returns:
        Count of logical lines
    """
    lines = source.split("\n")
    in_multiline_comment = False
    logical_count = 0

    for line in lines:
        stripped = line.strip()

        # Handle multiline comments
        if stripped.lower().startswith("$ontext"):
            in_multiline_comment = True
            continue
        if stripped.lower().startswith("$offtext"):
            in_multiline_comment = False
            continue
        if in_multiline_comment:
            continue

        # Skip empty lines and single-line comments
        if not stripped or stripped.startswith("*"):
            continue

        # Handle inline comments
        # Look for comment asterisk (preceded by whitespace, not a multiplication operator)
        # Match pattern: whitespace followed by asterisk
        comment_match = re.search(r"\s\*", stripped)
        if comment_match:
            # Check if there's code before the comment
            code_part = stripped[: comment_match.start()].strip()
            if code_part:
                logical_count += 1
        else:
            # No inline comment detected, count this line
            logical_count += 1

    return logical_count


def count_logical_lines_up_to(source: str, line_number: int) -> int:
    """
    Count logical lines from start of file up to (but not including) line_number.

    Args:
        source: GAMS source code as string
        line_number: Line number to count up to (1-indexed, exclusive)

    Returns:
        Count of logical lines before the specified line
    """
    lines = source.split("\n")
    in_multiline_comment = False
    logical_count = 0

    # Process lines 0 to line_number-2 (0-indexed, up to but not including line_number-1)
    for i in range(min(line_number - 1, len(lines))):
        line = lines[i]
        stripped = line.strip()

        # Handle multiline comments
        if stripped.lower().startswith("$ontext"):
            in_multiline_comment = True
            continue
        if stripped.lower().startswith("$offtext"):
            in_multiline_comment = False
            continue
        if in_multiline_comment:
            continue

        # Skip empty lines and single-line comments
        if not stripped or stripped.startswith("*"):
            continue

        # Handle inline comments
        # Look for comment asterisk (preceded by whitespace, not a multiplication operator)
        comment_match = re.search(r"\s\*", stripped)
        if comment_match:
            # Check if there's code before the comment
            code_part = stripped[: comment_match.start()].strip()
            if code_part:
                logical_count += 1
        else:
            # No inline comment detected, count this line
            logical_count += 1

    return logical_count


def extract_error_line(exception: Exception) -> int | None:
    """
    Extract line number from parser exception.

    Args:
        exception: Exception from parser (lark.exceptions or ParserSemanticError)

    Returns:
        Line number (1-indexed) or None if not found
    """
    # Check if exception has .line attribute (lark exceptions and ParserSemanticError)
    if hasattr(exception, "line") and exception.line is not None:
        return exception.line

    # Fallback: parse from error message
    error_str = str(exception)
    match = re.search(r"at line (\d+)", error_str)
    if match:
        return int(match.group(1))

    match = re.search(r"line (\d+)", error_str)
    if match:
        return int(match.group(1))

    return None


def extract_missing_features(
    error_type: str, error_message: str, source_line: str | None = None
) -> list[str]:
    """
    Extract missing feature hints from parse error.

    Uses pattern matching on error messages to identify GAMS features
    that are blocking the parse.

    Args:
        error_type: Exception class name (e.g., "UnexpectedToken", "ParserSemanticError")
        error_message: Error message text
        source_line: Optional source code line where error occurred

    Returns:
        List of missing feature names (max 2 for readability)
    """
    features = []

    # Pattern 1: Lead/lag indexing (i++1, i--1)
    if re.search(r"[a-z]\+\+\d", error_message, re.IGNORECASE) or re.search(
        r"[a-z]--\d", error_message, re.IGNORECASE
    ):
        features.append("lead/lag indexing (i++1, i--1)")
    elif source_line and (
        re.search(r"[a-z]\+\+\d", source_line, re.IGNORECASE)
        or re.search(r"[a-z]--\d", source_line, re.IGNORECASE)
    ):
        features.append("lead/lag indexing (i++1, i--1)")

    # Pattern 2: Option statements
    if "option" in error_message.lower() and any(
        keyword in error_message.lower()
        for keyword in ["limrow", "limcol", "decimals", "reslim", "iterlim"]
    ):
        features.append("option statements")

    # Pattern 3: Model sections (mx, my)
    if re.search(r"\bm[xyz]\b", error_message, re.IGNORECASE):
        features.append("model sections (mx, my, etc.)")
    elif source_line and re.search(r"\bm[xyz]\b", source_line, re.IGNORECASE):
        features.append("model sections (mx, my, etc.)")

    # Pattern 4: Function calls in assignments
    if "Call(" in error_message and any(
        func in error_message for func in ["uniform", "normal", "sin", "cos", "exp", "log", "sqrt"]
    ):
        features.append("function calls in assignments")

    # Pattern 5: Indexed assignments (from ParserSemanticError)
    if "indexed assignment" in error_message.lower() and "not supported" in error_message.lower():
        features.append("indexed assignments")

    # Pattern 6: Nested indexing
    if re.search(r"[a-zA-Z]+\([a-zA-Z]+\(", error_message):
        features.append("nested indexing")
    elif source_line and re.search(r"[a-zA-Z]+\([a-zA-Z]+\(", source_line):
        features.append("nested indexing")

    # Pattern 7: Short model syntax
    if re.search(r"model.*\/", error_message, re.IGNORECASE):
        features.append("short model declaration syntax")

    # Pattern 8: Variable attributes (.l, .m, etc.)
    if re.search(r"\.[lm]\b", error_message):
        features.append("variable attributes (.l, .m, etc.)")
    elif source_line and re.search(r"\.[lm]\b", source_line):
        features.append("variable attributes (.l, .m, etc.)")

    # Pattern 9: Generic unsupported feature (from ParserSemanticError)
    if "not supported" in error_message.lower() or "not yet supported" in error_message.lower():
        # Try to extract the specific feature mentioned
        match = re.search(
            r"([\w\s]+) (?:is |are )?not (?:yet )?supported",
            error_message,
            re.IGNORECASE,
        )
        if match:
            feature = match.group(1).strip()
            # Only add if not already captured by other patterns
            if feature and not any(f.lower() in feature.lower() for f in features):
                features.append(feature)

    # If no specific patterns matched, provide generic hint
    if not features:
        if error_type == "ParserSemanticError":
            features.append("semantic error after successful parse")
        elif error_type in ("UnexpectedToken", "UnexpectedCharacters"):
            features.append("syntax error")
        else:
            features.append("parse error")

    # Deduplicate and limit to top 2 for readability
    seen = set()
    unique_features = []
    for f in features:
        if f.lower() not in seen:
            seen.add(f.lower())
            unique_features.append(f)

    return unique_features[:2]


def calculate_parse_progress(source: str, error: Exception | None) -> dict[str, int | float | None]:
    """
    Calculate partial parse progress metrics.

    Args:
        source: Full GAMS source code
        error: Exception from parser, or None if successful parse

    Returns:
        Dictionary with keys:
        - percentage: float (0-100)
        - lines_parsed: int
        - lines_total: int
        - error_line: int | None
    """
    total_lines = count_logical_lines(source)

    if error is None:
        # Successful parse: 100%
        return {
            "percentage": 100.0,
            "lines_parsed": total_lines,
            "lines_total": total_lines,
            "error_line": None,
        }

    # Failed parse: count lines before error
    error_line = extract_error_line(error)

    if error_line is None:
        # Can't determine error location, assume early failure
        lines_parsed = 0
    else:
        lines_parsed = count_logical_lines_up_to(source, error_line)

    percentage = (lines_parsed / total_lines * 100) if total_lines > 0 else 0.0

    return {
        "percentage": round(percentage, 1),
        "lines_parsed": lines_parsed,
        "lines_total": total_lines,
        "error_line": error_line,
    }


def calculate_parse_progress_from_file(
    gms_path: Path, error: Exception | None
) -> dict[str, int | float | None]:
    """
    Calculate partial parse progress metrics from a file path.

    Args:
        gms_path: Path to .gms file
        error: Exception from parser, or None if successful parse

    Returns:
        Dictionary with progress metrics (see calculate_parse_progress)
    """
    source = gms_path.read_text()
    return calculate_parse_progress(source, error)
