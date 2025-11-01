"""
GAMS preprocessor for handling $include directives.

This module implements preprocessing of GAMS source files to expand
$include directives before parsing.
"""

import re
from pathlib import Path


class CircularIncludeError(Exception):
    """Raised when circular $include directives are detected."""

    pass


def preprocess_includes(
    file_path: Path, included_stack: list[Path] | None = None, max_depth: int = 100
) -> str:
    """
    Recursively expand all $include directives in a GAMS file.

    Args:
        file_path: Path to the GAMS file to preprocess
        included_stack: Stack of files currently being processed (for cycle detection)
        max_depth: Maximum include nesting depth (default: 100)

    Returns:
        str: Expanded source code with all includes resolved

    Raises:
        CircularIncludeError: If circular includes detected
        FileNotFoundError: If included file doesn't exist
        RecursionError: If max_depth exceeded

    Example:
        >>> from pathlib import Path
        >>> expanded = preprocess_includes(Path('model.gms'))
        >>> # expanded contains all $include files inlined
    """
    if included_stack is None:
        included_stack = []

    # Resolve to absolute path for cycle detection
    file_path = file_path.resolve()

    # Detect circular includes
    if file_path in included_stack:
        cycle = " -> ".join(str(f) for f in included_stack + [file_path])
        raise CircularIncludeError(f"Circular include detected: {cycle}")

    # Check depth limit
    if len(included_stack) >= max_depth:
        raise RecursionError(
            f"Maximum include depth ({max_depth}) exceeded. "
            f"Include chain: {' -> '.join(str(f) for f in included_stack)}"
        )

    # Read file content
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    content = file_path.read_text()

    # Pattern matches:
    # $include filename
    # $include "filename with spaces"
    # $include 'filename with spaces'
    include_pattern = r'\$include\s+(["\']?)([^"\'\s]+)\1'

    # Add current file to stack
    new_stack = included_stack + [file_path]

    # Process all includes
    result = []
    last_end = 0

    for match in re.finditer(include_pattern, content, re.IGNORECASE):
        # Add content before this include
        result.append(content[last_end : match.start()])

        # Get included filename
        included_filename = match.group(2)

        # Resolve path relative to current file's directory
        included_path = file_path.parent / included_filename

        # Add comment showing the include for debugging
        result.append(f"\n* BEGIN $include {included_filename}\n")

        # Recursively process the included file
        try:
            included_content = preprocess_includes(included_path, new_stack, max_depth)
            result.append(included_content)
        except FileNotFoundError as e:
            # Enhance error message with context
            raise FileNotFoundError(
                f"In file {file_path}, line {content[: match.start()].count(chr(10)) + 1}: {e}"
            ) from e

        result.append(f"\n* END $include {included_filename}\n")

        last_end = match.end()

    # Add remaining content after last include
    result.append(content[last_end:])

    return "".join(result)


def preprocess_gams_file(file_path: Path) -> str:
    """
    Main entry point for GAMS preprocessing.

    Expands all $include directives in the given file.

    Args:
        file_path: Path to the GAMS file

    Returns:
        str: Preprocessed source code

    Example:
        >>> from pathlib import Path
        >>> from src.ir.preprocessor import preprocess_gams_file
        >>> source = preprocess_gams_file(Path('model.gms'))
    """
    return preprocess_includes(file_path)
