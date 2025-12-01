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

    # Normalize path for consistent comparison (handles relative vs absolute paths)
    file_path = file_path.resolve()

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
        # Normalize to handle different forms (./file.inc vs file.inc, etc.)
        included_path = (file_path.parent / included_filename).resolve()

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


def _has_statement_ending_semicolon(line: str) -> bool:
    """Check if a line has a semicolon that ends a statement (not in string/comment).

    This handles:
    - Semicolons inside single or double quoted strings are ignored
    - Escaped quotes within strings (e.g., "test\\"quote" or 'test\\'quote')
    - Semicolons after GAMS inline comments (*) are ignored

    Note: This doesn't handle nested quotes, but works for typical GAMS code.
    """
    in_string = None
    i = 0
    while i < len(line):
        c = line[i]

        # Handle string state
        if in_string:
            if c == in_string:
                # Check if the quote is escaped by counting preceding backslashes
                # An odd number of backslashes means the quote is escaped
                backslash_count = 0
                j = i - 1
                while j >= 0 and line[j] == "\\":
                    backslash_count += 1
                    j -= 1
                if backslash_count % 2 == 1:
                    # Quote is escaped, stay in string
                    i += 1
                    continue
                in_string = None
            i += 1
            continue

        # Check for comment start (inline comment with *)
        if c == "*":
            # GAMS inline comments start with * and go to end of line
            return False

        # Check for string start
        if c in ('"', "'"):
            in_string = c
            i += 1
            continue

        # Check for semicolon outside string/comment
        if c == ";":
            return True

        i += 1

    return False


def strip_unsupported_directives(source: str) -> str:
    """Remove unsupported GAMS compiler directives from source text.

    This function strips out compiler directives that are not yet supported
    by the parser, replacing them with comments to preserve line numbers.
    This allows parsing of GAMS files that contain these directives.

    Supported (stripped) directives:
    - $title: Model title (documentation only)
    - $ontext/$offtext: Comment blocks (documentation only)
    - $eolcom: End-of-line comment character definition
    - if() execution control statements: Runtime conditionals (not needed for model structure)
    - abort/display: Execution statements (not needed for model structure)

    Args:
        source: GAMS source code text

    Returns:
        Source code with unsupported directives replaced by comments

    Example:
        >>> source = "$title My Model\\nVariables x;\\n"
        >>> result = strip_unsupported_directives(source)
        >>> # Result: "* [Stripped: $title My Model]\\nVariables x;\\n"

    Notes:
        - Line numbers are preserved by replacing directives with comments
        - $include directives are NOT stripped (handled by preprocess_includes)
        - Case-insensitive matching for all directives
    """
    lines = source.split("\n")
    filtered = []
    in_ontext_block = False

    for line in lines:
        stripped = line.strip()
        stripped_lower = stripped.lower()

        # Handle $ontext/$offtext comment blocks
        if stripped_lower.startswith("$ontext"):
            filtered.append(f"* [Stripped: {stripped}]")
            in_ontext_block = True
            continue

        if stripped_lower.startswith("$offtext"):
            filtered.append(f"* [Stripped: {stripped}]")
            in_ontext_block = False
            continue

        # If inside comment block, convert to regular comment
        if in_ontext_block:
            filtered.append(f"* {line}")
            continue

        # Strip $title directive
        if stripped_lower.startswith("$title"):
            filtered.append(f"* [Stripped: {line}]")
            continue

        # Strip $eolcom directive
        if stripped_lower.startswith("$eolcom"):
            filtered.append(f"* [Stripped: {line}]")
            continue

        # Sprint 9 Day 6: if/elseif/else, abort, and compile-time constants now fully supported
        # No longer stripping these statements - they are parsed by the grammar

        # Keep all other lines unchanged
        filtered.append(line)

    return "\n".join(filtered)


def extract_conditional_sets(source: str) -> dict[str, str]:
    """Extract default values from $if not set directives.

    Parses lines like: $if not set varname $set varname "default_value"
    Returns a dictionary mapping variable names to their default values.

    This implements the mock preprocessing approach from Task 3 research
    (preprocessor_directives.md). We extract defaults without evaluating
    the conditional - we always use the default value.

    Args:
        source: GAMS source code text

    Returns:
        Dictionary mapping variable names to default values

    Example:
        >>> source = '$if not set size $set size "10"\\nSet i /1*%size%/;'
        >>> macros = extract_conditional_sets(source)
        >>> macros
        {'size': '10'}

    Notes:
        - Case-insensitive matching for GAMS directives ($if, $set) and backreference
        - Backreference \\1 matches case-insensitively (e.g., SIZE matches size)
        - Variable name case from first occurrence is preserved in output
        - Handles both quoted and unquoted default values
        - Unquoted values: [\\w.-]+ pattern captures identifiers, numbers with
          dots/hyphens (e.g., 1e-6, 3.14) but stops at semicolons and dollar signs
        - If multiple $if not set directives set the same variable,
          the last one wins
    """
    macros = {}

    # Pattern: $if not set varname $set varname value
    # Matches: $if not set size $set size 10
    #          $if not set size $set size "10"
    #          $if not set tol $set tol 1e-6
    # Case-insensitive for directives, preserves case for variable names
    # Unquoted values: [\w.-]+ allows identifiers, numbers, dots, and hyphens
    # This avoids capturing semicolons, dollar signs, and other special characters
    pattern = r'\$if\s+not\s+set\s+(\w+)\s+\$set\s+\1\s+(?:"([^"]*)"|([\w.-]+))'

    for match in re.finditer(pattern, source, re.IGNORECASE):
        var_name = match.group(1)
        # Get value from either quoted (group 2) or unquoted (group 3)
        value = match.group(2) if match.group(2) is not None else match.group(3)
        macros[var_name] = value

    return macros


def expand_macros(source: str, macros: dict[str, str]) -> str:
    """Expand %macro% references with their values.

    Replaces %varname% with the corresponding value from the macros dict.
    Unknown macros are left unchanged.

    This implements the mock preprocessing approach from Task 3 research.
    We support user-defined macros from $set directives and can be extended
    to support system macros like %modelStat.optimal% if needed.

    Args:
        source: GAMS source code text with %macro% references
        macros: Dictionary mapping macro names to values

    Returns:
        Source code with macros expanded

    Example:
        >>> source = "Set i /1*%size%/;"
        >>> macros = {'size': '10'}
        >>> expand_macros(source, macros)
        'Set i /1*10/;'

    Notes:
        - Case-sensitive macro name matching (GAMS convention)
        - Unknown macros are left as-is (e.g., %unknown% unchanged)
        - System macros like %gams.user1% can be added to macros dict
    """
    result = source

    for var_name, value in macros.items():
        # Replace %varname% with value
        # The % delimiters prevent partial matches
        # Use lambda to prevent interpreting special regex replacement sequences
        pattern = f"%{re.escape(var_name)}%"
        result = re.sub(pattern, lambda m: value, result)

    return result


def strip_conditional_directives(source: str) -> str:
    """Strip $if not set directives, replacing with comments.

    Removes $if not set directives from the source while preserving
    line numbers by replacing them with comment lines.

    Args:
        source: GAMS source code text

    Returns:
        Source code with $if not set directives replaced by comments

    Example:
        >>> source = '$if not set size $set size "10"\\nSet i /1*10/;'
        >>> result = strip_conditional_directives(source)
        >>> # Result: '* [Stripped: $if not set size $set size "10"]\\nSet i /1*10/;'

    Notes:
        - Preserves line numbers for accurate error reporting
        - Other lines remain unchanged
    """
    lines = source.split("\n")
    filtered = []

    for line in lines:
        stripped = line.strip()

        # Check if this line contains $if not set directive (more precise)
        if re.match(r"^\$if\s+not\s+set\b", stripped, re.IGNORECASE):
            # Replace with comment to preserve line number, preserving original indentation
            leading_ws = line[: len(line) - len(line.lstrip())]
            filtered.append(f"{leading_ws}* [Stripped: {stripped}]")
        else:
            # Keep line unchanged
            filtered.append(line)

    return "\n".join(filtered)


def normalize_multi_line_continuations(source: str) -> str:
    """Add missing commas for implicit line continuations in data blocks.

    GAMS allows multi-line set/parameter declarations without trailing commas.
    For example:
        Set i /
            a
            b
            c
        /;

    This function normalizes such declarations by inserting commas at line ends,
    making them parseable by the grammar which requires explicit separators.

    Args:
        source: GAMS source code text

    Returns:
        Source code with commas inserted at appropriate line ends

    Example:
        >>> source = "Set i /\\n    a\\n    b\\n/;"
        >>> result = normalize_multi_line_continuations(source)
        >>> # Result: "Set i /\\n    a,\\n    b\\n/;"

    Notes:
        - Only processes lines within /.../ data blocks
        - Skips lines that already end with comma, slash, or semicolon
        - Skips lines that are comments or empty
        - Preserves original whitespace and indentation
    """
    lines = source.split("\n")
    result = []
    in_data_block = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track if we're inside a /.../ data block
        if "/" in line and not in_data_block:
            # Entering a data block
            # Check if it also closes on the same line (e.g., Set i / a, b /;)
            slash_count = line.count("/")
            if slash_count >= 2:
                # Both opening and closing slash on same line
                result.append(line)
                continue

            # Opening slash - check if there's data after it
            slash_idx = line.find("/")
            after_slash = line[slash_idx + 1 :].strip()

            if after_slash:
                # Data on same line as opening /, e.g., "Set i / i-1"
                # Need to check if this needs a comma (if more data follows)
                in_data_block = True

                # Look ahead to see if next line has more data
                needs_comma = False
                if i + 1 < len(lines):
                    next_stripped = lines[i + 1].strip()
                    # If next line has data (not just closing /), we need comma
                    if next_stripped and not next_stripped.startswith("*"):
                        if "/" in next_stripped:
                            # Check if there's data before the /
                            next_slash_idx = next_stripped.find("/")
                            before_slash = next_stripped[:next_slash_idx].strip()
                            if before_slash:
                                # Next line has data before /, so current line needs comma
                                needs_comma = True
                        else:
                            # Next line has data without /, so current line needs comma
                            needs_comma = True

                if needs_comma:
                    result.append(line + ",")
                else:
                    result.append(line)
                continue
            else:
                # Just opening slash on this line
                in_data_block = True
                result.append(line)
                continue

        # If we're in a data block, process the line
        if in_data_block and stripped:
            # Skip if line is a comment
            if stripped.startswith("*"):
                result.append(line)
                continue

            # Check if this line contains the closing /
            if "/" in stripped:
                # This line closes the block
                # It may have data before the / (e.g., "i-2  /") or just be "/" alone
                # Don't add comma - the closing / indicates this is the last element
                result.append(line)
                in_data_block = False
                continue

            # Regular data line within block
            # Skip if line already ends with a comma or semicolon
            if stripped.endswith((",", ";")):
                result.append(line)
                continue

            # Check if next line closes the block or has more data
            needs_comma = True
            if i + 1 < len(lines):
                next_stripped = lines[i + 1].strip()
                # If next line starts with / or only contains /, this is last element
                if next_stripped == "/" or next_stripped.startswith("/;"):
                    needs_comma = False
                # If next line has data followed by /, this is not the last element
                elif "/" in next_stripped:
                    slash_idx = next_stripped.find("/")
                    before_slash = next_stripped[:slash_idx].strip()
                    if before_slash:
                        # Next line has data before /, so current line needs comma
                        needs_comma = True
                    else:
                        # Next line is just /, current line is last element
                        needs_comma = False

            if needs_comma:
                result.append(line + ",")
            else:
                result.append(line)
        else:
            result.append(line)

    return "\n".join(result)


def normalize_special_identifiers(source: str) -> str:
    """Quote identifiers containing special characters (-, +) in data blocks.

    GAMS allows hyphens and plus signs in identifiers (e.g., light-ind, food+agr).
    To avoid ambiguity with arithmetic operators, we quote these identifiers when
    they appear in /.../ data blocks or table headers.

    Args:
        source: GAMS source code text

    Returns:
        Source code with special identifiers quoted

    Example:
        Set i / light-ind, food+agr /;
        →
        Set i / 'light-ind', 'food+agr' /;

    Notes:
        - Processes identifiers within /.../ data blocks
        - Processes identifiers in table headers (after Table keyword)
        - Preserves already-quoted strings
        - Detects identifiers with - or + that aren't arithmetic operators
        - Uses context: no surrounding whitespace = identifier
    """
    import re

    lines = source.split("\n")
    result = []
    in_data_block = False
    in_table = False
    table_header_seen = False

    for line in lines:
        stripped = line.strip()

        # Check if we're starting a table
        if re.match(r"^Table\b", stripped, re.IGNORECASE):
            in_table = True
            table_header_seen = False
            result.append(line)
            continue

        # If in a table, process header and data rows
        if in_table:
            # Table ends with a semicolon
            if stripped.endswith(";"):
                in_table = False
                # Still process this line (could be data row)
                processed = _quote_special_in_line(line)
                result.append(processed)
                continue

            # First non-empty line after Table declaration is the header
            if not table_header_seen and stripped:
                table_header_seen = True
                processed = _quote_special_in_line(line)
                result.append(processed)
                continue

            # All table rows (data rows with row labels and values)
            if stripped:
                processed = _quote_special_in_line(line)
                result.append(processed)
                continue

        # Track if we're inside a /.../ data block
        if "/" in line and not in_data_block:
            # Check if entering a data block
            slash_count = line.count("/")
            if slash_count == 1:
                # Opening a data block
                in_data_block = True
            elif slash_count >= 2:
                # Inline block - process it
                processed = _quote_special_in_line(line)
                result.append(processed)
                continue
        elif "/" in line and in_data_block:
            # Check if closing the data block
            if line.strip().endswith("/") or line.strip().endswith("/;"):
                in_data_block = False

        # Process line if in data block
        if in_data_block:
            processed = _quote_special_in_line(line)
            result.append(processed)
        else:
            result.append(line)

    return "\n".join(result)


def _quote_special_in_line(line: str) -> str:
    """Quote identifiers with special chars in a single line.

    Detects patterns like:
    - word-word (no spaces around -)
    - word+word (no spaces around +)

    And wraps them in quotes if not already quoted.
    """
    import re

    # Skip if line is a comment
    if line.strip().startswith("*"):
        return line

    # Pattern: identifier with - or + that's NOT surrounded by whitespace
    # This distinguishes:
    #   light-ind (identifier) vs x1 - 1 (arithmetic)
    #   food+agr (identifier) vs x + y (arithmetic)
    #
    # Match: Start of identifier, then word chars, then one or more (-/+ followed by word chars)
    # Word boundary at start to ensure we match the full identifier
    pattern = r"\b([a-zA-Z_][a-zA-Z0-9_]*(?:[-+][a-zA-Z0-9_]+)+)\b"

    def replace_if_not_quoted(match):
        """Replace match with quoted version if not already in quotes."""
        matched_text = match.group(1)
        start_pos = match.start()

        # Check if already inside a quoted string
        # Count quotes before this position
        before = line[:start_pos]
        single_quotes = before.count("'")
        double_quotes = before.count('"')

        # If odd number of quotes, we're inside a string
        if single_quotes % 2 == 1 or double_quotes % 2 == 1:
            return matched_text

        # Check if there's whitespace around -/+ to distinguish from operators
        # Look at the context around the identifier
        # If the identifier is preceded/followed by whitespace around the operator, skip it
        # This is already handled by the pattern requiring word boundaries

        # Quote the identifier
        return f"'{matched_text}'"

    # Apply the replacement
    processed = re.sub(pattern, replace_if_not_quoted, line)
    return processed


def preprocess_gams_file(file_path: Path | str) -> str:
    """Preprocess a GAMS file, expanding all $include directives.

    This is the main entry point for preprocessing GAMS files.
    It performs preprocessing in the following order:
    1. Expand $include directives recursively
    2. Extract macro defaults from $if not set directives
    3. Expand %macro% references
    4. Strip conditional directives ($if not set)
    5. Strip other unsupported directives ($title, $ontext, etc.)
    6. Normalize multi-line continuations (add missing commas)

    Args:
        file_path: Path to the GAMS file (Path object or string)

    Returns:
        Preprocessed file content ready for parsing

    Raises:
        FileNotFoundError: If the file or any included file doesn't exist
        CircularIncludeError: If a circular include is detected
        IncludeDepthExceededError: If nesting exceeds 100 levels

    Example:
        >>> content = preprocess_gams_file("model.gms")
        >>> # All preprocessing complete
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    # Step 1: Expand all $include directives recursively
    content = preprocess_includes(file_path)

    # Step 2: Extract macro defaults from $if not set directives
    macros = extract_conditional_sets(content)

    # Step 3: Expand %macro% references with their values
    content = expand_macros(content, macros)

    # Step 4: Strip $if not set directives (replaced with comments)
    content = strip_conditional_directives(content)

    # Step 5: Strip other unsupported directives ($title, $ontext, etc.)
    content = strip_unsupported_directives(content)

    # Step 6: Normalize multi-line continuations (add missing commas)
    content = normalize_multi_line_continuations(content)

    # Step 7: Quote identifiers with special characters (-, +) in data blocks
    return normalize_special_identifiers(content)
