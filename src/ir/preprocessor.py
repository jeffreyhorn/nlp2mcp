"""GAMS file preprocessing for $include directives.

This module handles GAMS $include directives by performing simple textual
substitution before parsing. The preprocessor:
- Recursively expands all $include directives
- Resolves paths relative to the containing file
- Detects circular includes and reports the full cycle chain
- Maintains an include stack for error reporting
- Supports both quoted and unquoted file paths

Based on KNOWN_UNKNOWNS.md findings:
- Unknown 1.1: GAMS uses simple string substitution without macro expansion
- Unknown 1.4: Arbitrary nesting allowed, use depth limit (default 100)
- Unknown 1.5: Paths resolved relative to containing file, not CWD
"""

import re
from pathlib import Path


class CircularIncludeError(Exception):
    """Raised when a circular include dependency is detected.

    Attributes:
        chain: List of file paths showing the circular dependency chain
    """

    def __init__(self, chain: list[Path]):
        self.chain = chain
        chain_str = " -> ".join(str(p) for p in chain)
        super().__init__(f"Circular include detected: {chain_str}")


class IncludeDepthExceededError(Exception):
    """Raised when include nesting depth exceeds the maximum limit.

    Attributes:
        depth: The depth at which the limit was exceeded
        max_depth: The maximum allowed depth
        file_path: The file that would exceed the limit
    """

    def __init__(self, depth: int, max_depth: int, file_path: Path):
        self.depth = depth
        self.max_depth = max_depth
        self.file_path = file_path
        super().__init__(
            f"Include depth limit exceeded ({depth} > {max_depth}) at file: {file_path}"
        )


def preprocess_includes(
    file_path: Path,
    max_depth: int = 100,
    _include_stack: list[Path] | None = None,
) -> str:
    """Recursively expand all $include directives in a GAMS file.

    This function performs textual substitution of $include directives,
    replacing each directive with the contents of the included file.
    The process is recursive, allowing included files to contain their
    own $include directives.

    Args:
        file_path: Path to the GAMS file to preprocess
        max_depth: Maximum allowed include nesting depth (default: 100)
        _include_stack: Internal parameter for tracking include chain

    Returns:
        The preprocessed file content with all includes expanded

    Raises:
        FileNotFoundError: If an included file doesn't exist
        CircularIncludeError: If a circular include is detected
        IncludeDepthExceededError: If nesting depth exceeds max_depth

    Example:
        >>> content = preprocess_includes(Path("model.gms"))
        >>> # All $include directives have been expanded

    Notes:
        - Paths are resolved relative to the containing file, not CWD
        - Supports both `$include file.inc` and `$include "file with spaces.inc"`
        - Adds debug comments showing include boundaries
        - Detects circular includes and shows full dependency chain
    """
    # Initialize include stack on first call
    if _include_stack is None:
        _include_stack = []

    # Check for circular includes
    if file_path in _include_stack:
        # Circular dependency detected - show full chain
        chain = _include_stack + [file_path]
        raise CircularIncludeError(chain)

    # Check depth limit
    current_depth = len(_include_stack)
    if current_depth >= max_depth:
        raise IncludeDepthExceededError(current_depth, max_depth, file_path)

    # Read the file content
    if not file_path.exists():
        if _include_stack:
            # Show where the include was requested from
            parent = _include_stack[-1]
            raise FileNotFoundError(
                f"Included file not found: {file_path}\n  Referenced from: {parent}"
            )
        else:
            raise FileNotFoundError(f"File not found: {file_path}")

    content = file_path.read_text()

    # Pattern matches: $include filename.inc OR $include "filename with spaces.inc"
    # Case-insensitive, allows optional whitespace
    include_pattern = r'\$include\s+(?:"([^"]+)"|(\S+))'

    # Track position for building result
    result_parts = []
    last_end = 0

    # Add current file to include stack
    new_stack = _include_stack + [file_path]

    # Process all $include directives
    for match in re.finditer(include_pattern, content, re.IGNORECASE):
        # Add content before this include
        result_parts.append(content[last_end : match.start()])

        # Get the included filename (either from quoted or unquoted group)
        included_filename = match.group(1) or match.group(2)

        # Resolve path relative to the file containing the $include
        included_path = file_path.parent / included_filename

        # Add debug comment showing include boundary
        result_parts.append(f"\n* BEGIN INCLUDE: {included_filename}\n")

        # Recursively preprocess the included file
        included_content = preprocess_includes(
            included_path,
            max_depth=max_depth,
            _include_stack=new_stack,
        )

        result_parts.append(included_content)

        # Add end marker
        result_parts.append(f"\n* END INCLUDE: {included_filename}\n")

        last_end = match.end()

    # Add remaining content after last include
    result_parts.append(content[last_end:])

    return "".join(result_parts)


def preprocess_gams_file(file_path: Path | str) -> str:
    """Preprocess a GAMS file, expanding all $include directives.

    This is the main entry point for preprocessing GAMS files.
    It wraps preprocess_includes() with a simpler interface.

    Args:
        file_path: Path to the GAMS file (Path object or string)

    Returns:
        Preprocessed file content with all includes expanded

    Raises:
        FileNotFoundError: If the file or any included file doesn't exist
        CircularIncludeError: If a circular include is detected
        IncludeDepthExceededError: If nesting exceeds 100 levels

    Example:
        >>> content = preprocess_gams_file("model.gms")
        >>> # All $include directives expanded
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    return preprocess_includes(file_path)
