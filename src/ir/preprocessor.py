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

# Regex pattern for GAMS declaration keywords (both singular and plural forms)
DECLARATION_KEYWORDS_PATTERN = r"\b(Set|Sets|Parameter|Parameters|Scalar|Scalars|Alias)\b"

# Block keywords that start a new declaration block and require previous block to be terminated
# These keywords, when appearing at the start of a line, indicate a new block
BLOCK_KEYWORDS = [
    "set",
    "sets",
    "parameter",
    "parameters",
    "scalar",
    "scalars",
    "variable",
    "variables",
    "equation",
    "equations",
    "alias",
    "table",
    "model",
    "positive",
    "negative",
    "binary",
    "integer",
]


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


def process_conditionals(source: str, macros: dict[str, str]) -> str:
    """Process $if/$else/$endif conditional compilation directives.

    Evaluates conditional blocks and includes/excludes code based on conditions.
    Supports nested conditionals.

    Supported conditions:
    - $if set varname: Include if variable is defined
    - $if not set varname: Include if variable is NOT defined
    - $if varname: Include if variable is defined (same as "set varname")
    - $if expr: Include if expression evaluates to true (basic support)
    - $else: Alternative block when condition is false
    - $elseif: Alternative condition (processed as $else $if)
    - $endif: End conditional block

    Args:
        source: GAMS source code text
        macros: Dictionary of defined variables (from $set directives)

    Returns:
        Source code with conditionals evaluated and inactive blocks removed

    Example:
        >>> source = '''$if set debug
        ... Parameter debugMode;
        ... $else
        ... Parameter prodMode;
        ... $endif'''
        >>> macros = {'debug': '1'}
        >>> result = process_conditionals(source, macros)
        >>> # Result includes "Parameter debugMode;" and excludes "Parameter prodMode;"

    Notes:
        - Conditions are evaluated at compile time
        - Nested conditionals are supported
        - Unknown variables in "set" checks are treated as undefined
        - Expression evaluation is basic (comparisons, logical ops)
        - Excluded blocks are replaced with comments to preserve line numbers
    """
    lines = source.split("\n")
    result = []

    # Stack to track conditional nesting
    # Each entry: (condition_met, else_seen, include_lines)
    # condition_met: Was the $if condition true?
    # else_seen: Have we seen an $else yet?
    # include_lines: Should we include lines at this level?
    conditional_stack: list[tuple[bool, bool, bool]] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        stripped_lower = stripped.lower()

        # Check for $if directive
        if stripped_lower.startswith("$if"):
            # Special case: Single-line $if not set ... $set ... is handled by
            # extract_conditional_sets() and strip_conditional_directives()
            # Skip it here to avoid double-processing
            if re.match(
                r"\$if\s+not\s+set\s+(\w+)\s+\$set\s+\1\b",
                stripped,
                re.IGNORECASE,
            ):
                # This is a single-line default pattern - pass through unchanged
                result.append(line)
                i += 1
                continue

            # Parse the condition
            condition_met = _evaluate_if_condition(stripped, macros)

            # Push new conditional context
            # Include lines if: no parent conditional OR parent is including
            parent_including = True if not conditional_stack else conditional_stack[-1][2]
            include_lines = parent_including and condition_met

            conditional_stack.append((condition_met, False, include_lines))

            # Add comment showing the directive
            result.append(f"* [Conditional: {stripped}]")
            i += 1
            continue

        # Check for $elseif directive (treat as $else + $if)
        elif stripped_lower.startswith("$elseif"):
            if not conditional_stack:
                # $elseif without $if - skip with warning
                result.append(f"* [Warning: {stripped} without $if]")
                i += 1
                continue

            # Pop the current $if context
            condition_met, else_seen, _ = conditional_stack.pop()

            if else_seen:
                # Already saw $else, can't have $elseif
                result.append(f"* [Warning: {stripped} after $else]")
                conditional_stack.append((condition_met, True, False))
                i += 1
                continue

            # Evaluate new condition (only if previous condition was false)
            new_condition = _evaluate_if_condition(stripped.replace("$elseif", "$if", 1), macros)

            # Include this block if: previous condition was false AND new condition is true
            parent_including = True if not conditional_stack else conditional_stack[-1][2]
            include_lines = parent_including and not condition_met and new_condition

            # Push back with else_seen=False (allows more $elseif)
            conditional_stack.append((condition_met or new_condition, False, include_lines))

            result.append(f"* [Conditional: {stripped}]")
            i += 1
            continue

        # Check for $else directive
        elif stripped_lower.startswith("$else"):
            if not conditional_stack:
                # $else without $if - skip with warning
                result.append(f"* [Warning: {stripped} without $if]")
                i += 1
                continue

            condition_met, else_seen, _ = conditional_stack.pop()

            if else_seen:
                # Already saw $else - this is an error
                result.append(f"* [Warning: duplicate {stripped}]")
                conditional_stack.append((condition_met, True, False))
                i += 1
                continue

            # Include else block if condition was false
            parent_including = True if not conditional_stack else conditional_stack[-1][2]
            include_lines = parent_including and not condition_met

            conditional_stack.append((condition_met, True, include_lines))

            result.append(f"* [Conditional: {stripped}]")
            i += 1
            continue

        # Check for $endif directive
        elif stripped_lower.startswith("$endif"):
            if not conditional_stack:
                # $endif without $if - skip with warning
                result.append(f"* [Warning: {stripped} without $if]")
                i += 1
                continue

            # Pop the conditional context
            conditional_stack.pop()

            result.append(f"* [Conditional: {stripped}]")
            i += 1
            continue

        # Regular line - include or exclude based on conditional stack
        if conditional_stack:
            # We're inside a conditional block
            _, _, include_lines = conditional_stack[-1]
            if include_lines:
                # Include this line
                result.append(line)
            else:
                # Exclude this line (replace with comment to preserve line numbers)
                leading_ws = line[: len(line) - len(line.lstrip())]
                if stripped:  # Only comment non-empty lines
                    result.append(f"{leading_ws}* [Excluded: {stripped}]")
                else:
                    result.append(line)  # Keep empty lines
        else:
            # Not inside a conditional - include the line
            result.append(line)

        i += 1

    # Check for unclosed conditionals
    if conditional_stack:
        # Warning: unclosed $if directives
        result.append(f"* [Warning: {len(conditional_stack)} unclosed $if directive(s)]")

    return "\n".join(result)


def _evaluate_if_condition(condition_line: str, macros: dict[str, str]) -> bool:
    """Evaluate a $if condition.

    Args:
        condition_line: The $if directive line (e.g., "$if set n", "$if %n% > 5")
        macros: Dictionary of defined variables

    Returns:
        True if condition is met, False otherwise

    Examples:
        >>> _evaluate_if_condition("$if set n", {"n": "10"})
        True
        >>> _evaluate_if_condition("$if not set n", {"n": "10"})
        False
        >>> _evaluate_if_condition("$if not set missing", {})
        True
    """
    stripped = condition_line.strip()

    # Pattern: $if set varname
    match = re.match(r"\$if\s+set\s+(\w+)", stripped, re.IGNORECASE)
    if match:
        var_name = match.group(1)
        return var_name in macros

    # Pattern: $if not set varname
    match = re.match(r"\$if\s+not\s+set\s+(\w+)", stripped, re.IGNORECASE)
    if match:
        var_name = match.group(1)
        return var_name not in macros

    # Pattern: $if varname (same as "set varname")
    match = re.match(r"\$if\s+(\w+)\s*$", stripped, re.IGNORECASE)
    if match:
        var_name = match.group(1)
        return var_name in macros

    # Pattern: $if expression (e.g., $if %n% > 5)
    # For now, basic support: expand macros and try to evaluate
    # This is complex and would need a full expression parser
    # For Phase 4, we'll support basic patterns

    # Expand any %variable% references in the condition
    expanded = stripped
    for var_name, value in macros.items():
        pattern = f"%{re.escape(var_name)}%"
        expanded = re.sub(pattern, value, expanded)

    # Try to evaluate simple comparisons
    # Pattern: $if value1 OP value2 where OP is >=, <=, >, <, ==, !=, =
    # Note: Must check >= and <= before > and < to avoid partial matches
    match = re.match(
        r"\$if\s+([^\s]+)\s*(>=|<=|>|<|==|!=|=)\s*([^\s]+)",
        expanded,
        re.IGNORECASE,
    )
    if match:
        left = match.group(1).strip()
        op = match.group(2).strip()
        right = match.group(3).strip()

        # Try to convert to numbers for comparison
        try:
            left_num = float(left)
            right_num = float(right)

            if op == ">=":
                return left_num >= right_num
            elif op == "<=":
                return left_num <= right_num
            elif op == ">":
                return left_num > right_num
            elif op == "<":
                return left_num < right_num
            elif op == "==" or op == "=":
                return left_num == right_num
            elif op == "!=":
                return left_num != right_num
        except ValueError:
            # Not numeric - do string comparison
            if op == "==" or op == "=":
                return left == right
            elif op == "!=":
                return left != right
            # Other ops don't make sense for strings
            return False

    # Default: if we can't parse it, assume false (conservative)
    return False


def preprocess_bat_includes(
    file_path: Path,
    source: str,
    max_depth: int = 100,
    _include_stack: list[Path] | None = None,
) -> str:
    """Process $batInclude directives with argument substitution.

    $batInclude allows passing arguments to included files, where arguments
    are referenced as %1%, %2%, %3%, etc. in the included file.

    Args:
        file_path: Path to the GAMS file being processed
        source: Source code containing $batInclude directives
        max_depth: Maximum allowed include nesting depth (default: 100)
        _include_stack: Internal parameter for tracking include chain

    Returns:
        Source code with $batInclude directives expanded

    Example:
        >>> # In main.gms:
        >>> # $batInclude helper.inc foo bar
        >>> # In helper.inc:
        >>> # Set s%1% /%2%/;
        >>> # After expansion:
        >>> # Set sfoo /bar/;

    Notes:
        - Arguments are whitespace-separated
        - %1% refers to first argument, %2% to second, etc.
        - If included file doesn't exist, directive is commented out
        - Paths are resolved relative to the containing file
    """
    # Initialize include stack on first call
    if _include_stack is None:
        _include_stack = []

    # Normalize path for consistent comparison
    file_path = file_path.resolve()

    # Check depth limit
    current_depth = len(_include_stack)
    if current_depth >= max_depth:
        raise IncludeDepthExceededError(current_depth, max_depth, file_path)

    # Pattern matches: $batInclude filename arg1 arg2 ...
    # Case-insensitive, allows optional whitespace
    bat_include_pattern = r'\$batInclude\s+(?:"([^"]+)"|(\S+))(.*)$'

    # Track position for building result
    result_parts = []
    last_end = 0

    # Add current file to include stack
    new_stack = _include_stack + [file_path]

    # Process all $batInclude directives
    for match in re.finditer(bat_include_pattern, source, re.IGNORECASE | re.MULTILINE):
        # Add content before this include
        result_parts.append(source[last_end : match.start()])

        # Get the included filename (either from quoted or unquoted group)
        included_filename = match.group(1) or match.group(2)

        # Get arguments (everything after filename, split by whitespace)
        args_str = match.group(3).strip()
        args = args_str.split() if args_str else []

        # Resolve path relative to the file containing the $batInclude
        included_path = (file_path.parent / included_filename).resolve()

        # Check if file exists
        if not included_path.exists():
            # File doesn't exist - comment out the directive
            result_parts.append(
                f"\n* [Stripped: $batInclude {included_filename} {args_str} - file not found]\n"
            )
            last_end = match.end()
            continue

        # Check for circular includes
        if included_path in new_stack:
            chain = new_stack + [included_path]
            raise CircularIncludeError(chain)

        # Read the included file
        included_content = included_path.read_text()

        # Substitute %1, %2, etc. with arguments
        # Note: GAMS $batInclude uses %1, %2, etc. (not %1%, %2%)
        for i, arg in enumerate(args, 1):
            # Use regex to match %N where N is the argument number
            # Must use word boundary or lookahead to avoid matching %10 when looking for %1
            # Pattern matches %N followed by non-digit or end of string
            arg_pattern = rf"%{i}(?!\d)"
            included_content = re.sub(arg_pattern, arg, included_content)

        # Add debug comment showing include boundary
        result_parts.append(f"\n* BEGIN BATINCLUDE: {included_filename} {args_str}\n")

        # Recursively process the included file for nested $batInclude directives
        included_content = preprocess_bat_includes(
            included_path,
            included_content,
            max_depth=max_depth,
            _include_stack=new_stack,
        )

        result_parts.append(included_content)

        # Add end marker
        result_parts.append(f"\n* END BATINCLUDE: {included_filename}\n")

        last_end = match.end()

    # Add remaining content after last include
    result_parts.append(source[last_end:])

    return "".join(result_parts)


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
    """Check if a line has a semicolon that ends a statement (not in string).

    This handles:
    - Semicolons inside single or double quoted strings are ignored
    - Escaped quotes within strings (e.g., "test\\"quote" or 'test\\'quote')

    Note on comment/non-code handling in the surrounding preprocessor:
    - `*` is treated as a line comment only when it appears in column 1; such
      full-line comments are removed before this function is called.
    - Anything after a statement-terminating `;` is treated as non-code and is
      ignored for scanning (including any `*` that might appear there).

    This helper only detects a semicolon that is outside of string literals. It
    assumes that full-line comments and trailing non-code after `;` have already
    been stripped. It does not handle nested quotes, but works for typical GAMS
    code.
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

        # Check for string start
        if c in ('"', "'"):
            in_string = c
            i += 1
            continue

        # Check for semicolon outside string
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


def extract_set_directives(
    source: str, existing_macros: dict[str, str] | None = None
) -> dict[str, str]:
    """Extract variable assignments from $set directives.

    Parses lines like: $set varname value
    Returns a dictionary mapping variable names to their values.

    This extends the preprocessor to support general $set directives,
    not just $if not set patterns. Values can be quoted strings,
    numbers, or unquoted identifiers.

    Args:
        source: GAMS source code text
        existing_macros: Optional dict of already-defined macros to expand within values

    Returns:
        Dictionary mapping variable names to values

    Example:
        >>> source = '$set n 10\\n$set np %n%+1\\nSet ip /1*%np%/;'
        >>> macros = extract_set_directives(source, {'n': '10'})
        >>> macros
        {'n': '10', 'np': '10+1'}

    Notes:
        - Case-insensitive matching for $set directive
        - Variable name case from first occurrence is preserved
        - Handles both quoted and unquoted values
        - If multiple $set directives set the same variable, later ones override
        - Unquoted values can contain: identifiers, numbers, dots, hyphens, plus signs
        - Expands %macros% within values using existing_macros
    """
    if existing_macros is None:
        existing_macros = {}

    macros: dict[str, str] = {}

    # Pattern: $set varname value
    # Matches: $set n 10
    #          $set path "c:\data\models"
    #          $set tol 1e-6
    #          $if set n $set np %n%  (extracts the $set np %n% part)
    # Case-insensitive for $set directive, preserves case for variable names
    # The pattern looks for $set followed by variable name and value
    # It can appear anywhere in the line (e.g., after $if directives)
    # For unquoted values, match everything except semicolon and newline
    pattern = r'\$set\s+(\w+)\s+(?:"([^"]*)"|([^;\n]+))'

    for match in re.finditer(pattern, source, re.IGNORECASE):
        var_name = match.group(1)
        # Get value from either quoted (group 2) or unquoted (group 3)
        value = match.group(2) if match.group(2) is not None else match.group(3)
        # Strip whitespace from unquoted values
        if match.group(2) is None:
            value = value.strip()

        # Expand any %macro% references within the value using existing macros
        # This handles cases like: $set np %n%+1
        expanded_value = expand_macros(value, {**existing_macros, **macros})

        macros[var_name] = expanded_value

    return macros


def extract_macro_definitions(source: str) -> dict[str, tuple[list[str], str]]:
    """Extract $macro function definitions.

    Parses lines like: $macro name(param1, param2) body
    Returns a dictionary mapping macro names to (parameters, body) tuples.

    Args:
        source: GAMS source code text

    Returns:
        Dictionary mapping macro names to (parameter_list, body) tuples

    Example:
        >>> source = '$macro fx(t) %scale%*t\\nx =e= fx(y);'
        >>> macros = extract_macro_definitions(source)
        >>> macros
        {'fx': (['t'], '%scale%*t')}

    Notes:
        - Case-insensitive matching for $macro directive
        - Macro name and parameter names are case-preserving
        - Body can contain %variable% references
        - Parameters are whitespace-trimmed
    """
    macros: dict[str, tuple[list[str], str]] = {}

    # Pattern: $macro name(param1, param2, ...) body
    # Matches: $macro fx(t) %scale%*t
    #          $macro sum2(i,j,expr) sum(i, sum(j, expr))
    # Case-insensitive for $macro directive
    # Body extends to end of line
    pattern = r"\$macro\s+(\w+)\(([^)]*)\)\s+(.+)"

    for match in re.finditer(pattern, source, re.IGNORECASE):
        name = match.group(1)
        params_str = match.group(2)
        body = match.group(3).strip()

        # Parse parameter list (comma-separated, whitespace-trimmed)
        params = [p.strip() for p in params_str.split(",")] if params_str.strip() else []

        macros[name] = (params, body)

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


def expand_macro_calls(source: str, macro_defs: dict[str, tuple[list[str], str]]) -> str:
    """Expand macro function calls with argument substitution.

    Replaces macro calls like fx(arg1, arg2) with the macro body,
    substituting parameters with the provided arguments.

    Args:
        source: GAMS source code text with macro calls
        macro_defs: Dictionary mapping macro names to (parameters, body) tuples

    Returns:
        Source code with macro calls expanded

    Example:
        >>> source = "x =e= fx(t('1'));"
        >>> macro_defs = {'fx': (['t'], 'sin(t) * cos(t-t*t)')}
        >>> expand_macro_calls(source, macro_defs)
        "x =e= sin(t('1')) * cos(t('1')-t('1')*t('1'));"

    Notes:
        - Performs textual substitution of parameters with arguments
        - Arguments can contain parentheses (e.g., t('1'))
        - Multiple macro calls can appear in the same line
        - Macro calls are case-sensitive (GAMS convention)
    """
    result = source

    for name, (params, body) in macro_defs.items():
        # Pattern: name(args)
        # Need to handle nested parentheses in arguments (e.g., fx(t('1')))
        # Use a more sophisticated approach: find all occurrences and parse carefully

        # Build regex pattern for this macro call
        # Match: name followed by (
        pattern = rf"\b{re.escape(name)}\("

        # Process all matches from end to start to avoid offset issues
        matches = list(re.finditer(pattern, result))

        # Process in reverse order to maintain string positions
        for match in reversed(matches):
            start_pos = match.start()
            # Find the matching closing parenthesis
            paren_start = match.end() - 1  # Position of opening (
            paren_count = 1
            pos = paren_start + 1
            args_str = ""

            while pos < len(result) and paren_count > 0:
                if result[pos] == "(":
                    paren_count += 1
                elif result[pos] == ")":
                    paren_count -= 1
                    if paren_count == 0:
                        # Found matching closing paren
                        args_str = result[paren_start + 1 : pos]
                        break
                pos += 1

            if paren_count != 0:
                # Unmatched parentheses - skip this match
                continue

            # Parse arguments (comma-separated, but respect nested parens)
            args = _parse_macro_arguments(args_str)

            # Check if argument count matches parameter count
            if len(args) != len(params):
                # Argument count mismatch - skip this expansion
                # This could be a different function with the same name
                continue

            # Substitute parameters with arguments in the body
            expanded = body
            for param, arg in zip(params, args, strict=True):
                # Use word boundaries to avoid partial replacements
                # But also handle cases where param is followed by non-word chars
                param_pattern = rf"\b{re.escape(param)}\b"
                expanded = re.sub(param_pattern, arg, expanded)

            # Replace the macro call with the expanded body
            call_end = pos + 1  # Position after closing )
            result = result[:start_pos] + expanded + result[call_end:]

    return result


def _parse_macro_arguments(args_str: str) -> list[str]:
    """Parse comma-separated macro arguments, respecting nested parentheses.

    Args:
        args_str: String containing comma-separated arguments

    Returns:
        List of argument strings (whitespace-trimmed)

    Example:
        >>> _parse_macro_arguments("t('1'), x+y")
        ["t('1')", "x+y"]
    """
    if not args_str.strip():
        return []

    args = []
    current_arg = ""
    paren_depth = 0

    for char in args_str:
        if char == "," and paren_depth == 0:
            # Argument separator at top level
            args.append(current_arg.strip())
            current_arg = ""
        else:
            if char == "(":
                paren_depth += 1
            elif char == ")":
                paren_depth -= 1
            current_arg += char

    # Add the last argument
    if current_arg.strip():
        args.append(current_arg.strip())

    return args


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


def strip_set_directives(source: str) -> str:
    """Strip $set directives, replacing with comments.

    Removes $set directives from the source while preserving
    line numbers by replacing them with comment lines.
    Also strips lines containing $if ... $set patterns.

    Args:
        source: GAMS source code text

    Returns:
        Source code with $set directives replaced by comments

    Example:
        >>> source = '$set n 10\\nSet i /1*%n%/;'
        >>> result = strip_set_directives(source)
        >>> # Result: '* [Stripped: $set n 10]\\nSet i /1*%n%/;'

    Notes:
        - Preserves line numbers for accurate error reporting
        - Should be called after expand_macros() to avoid losing values
        - Also strips $if set/not set lines containing $set
    """
    lines = source.split("\n")
    filtered = []

    for line in lines:
        stripped = line.strip()

        # Check if this line contains a $set directive (standalone or after $if)
        # Matches: $set n 10
        #          $if set n $set np %n%
        #          $if not set n $set n 10
        if re.search(r"\$set\b", stripped, re.IGNORECASE):
            # Replace with comment to preserve line number, preserving original indentation
            leading_ws = line[: len(line) - len(line.lstrip())]
            filtered.append(f"{leading_ws}* [Stripped: {stripped}]")
        else:
            # Keep line unchanged
            filtered.append(line)

    return "\n".join(filtered)


def strip_macro_directives(source: str) -> str:
    """Strip $macro directives, replacing with comments.

    Removes $macro definitions from the source while preserving
    line numbers by replacing them with comment lines.

    Args:
        source: GAMS source code text

    Returns:
        Source code with $macro directives replaced by comments

    Example:
        >>> source = '$macro fx(t) %fx%\\nx =e= fx(y);'
        >>> result = strip_macro_directives(source)
        >>> # Result: '* [Stripped: $macro fx(t) %fx%]\\nx =e= sin(y) * cos(y);'

    Notes:
        - Preserves line numbers for accurate error reporting
        - Should be called after expand_macro_calls() to avoid losing expansions
    """
    lines = source.split("\n")
    filtered = []

    for line in lines:
        stripped = line.strip()

        # Check if this line contains a $macro directive
        if re.search(r"\$macro\b", stripped, re.IGNORECASE):
            # Replace with comment to preserve line number, preserving original indentation
            leading_ws = line[: len(line) - len(line.lstrip())]
            filtered.append(f"{leading_ws}* [Stripped: {stripped}]")
        else:
            # Keep line unchanged
            filtered.append(line)

    return "\n".join(filtered)


def normalize_table_continuations(source: str) -> str:
    """Remove table continuation markers (+) from multi-line table data.

    GAMS uses + at the start of a line to indicate table continuation.
    This function removes these markers so the table data can be parsed correctly.

    Args:
        source: GAMS source code text

    Returns:
        Source code with + continuation markers removed

    Example:
        Table data(i,j)
               col1  col2
           +   col3  col4
           row1  1     2

        Becomes:
        Table data(i,j)
               col1  col2
               col3  col4
           row1  1     2
    """
    lines = source.split("\n")
    result = []
    in_table = False

    for line in lines:
        stripped = line.strip()

        # Check if we're starting a table
        if re.match(r"^Table\b", stripped, re.IGNORECASE):
            in_table = True
            result.append(line)
            continue

        # If in table and line starts with +, remove it
        if in_table:
            if stripped.startswith("+"):
                # Remove the + and preserve indentation
                # Find the + and replace it with spaces to maintain column alignment
                plus_idx = line.find("+")
                # Replace + with space
                fixed_line = line[:plus_idx] + " " + line[plus_idx + 1 :]
                result.append(fixed_line)
                continue

            # Check if table ends
            if stripped.endswith(";"):
                in_table = False

        result.append(line)

    return "\n".join(result)


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
    in_declaration = False  # Track if we're in a Set/Parameter/Scalar/Alias block

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Sprint 17 Day 6: Skip comment lines early - they should never trigger
        # data block detection or have commas added. This fixes issues where
        # comments containing "/" (e.g., "* Primal/Dual Variables") were being
        # treated as data block openings.
        if stripped.startswith("*"):
            result.append(line)
            continue

        # Track if we're entering a declaration block
        if re.match(f"^\\s*{DECLARATION_KEYWORDS_PATTERN}", stripped, re.IGNORECASE):
            in_declaration = True

        # Track if we're inside a /.../ data block
        # Only treat / as data block delimiter if it appears in a declaration context
        if "/" in line and not in_data_block:
            # If line ends with ; and has only 1 slash, it's likely division (e.g., "x = a/2;")
            # not a data block
            if stripped.endswith(";") and line.count("/") == 1:
                result.append(line)
                continue

            # Check if / appears after a declaration keyword (Set, Parameter, Scalar, Alias)
            # OR if we're currently in a declaration block (keyword was on a previous line)
            has_keyword_before_slash = re.search(
                DECLARATION_KEYWORDS_PATTERN, line[: line.find("/")], re.IGNORECASE
            )
            if not has_keyword_before_slash and not in_declaration:
                # No declaration keyword before / and not in declaration block
                result.append(line)
                continue

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

                # Look ahead (skipping comment lines) to see if next data line has more
                needs_comma = False
                for j in range(i + 1, len(lines)):
                    next_stripped = lines[j].strip()
                    if not next_stripped or next_stripped.startswith("*"):
                        continue  # skip empty lines and comments
                    # If next data line has data (not just closing /), we need comma
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
                    break

                # Issue #618: Make idempotent - don't add comma if line already ends with one
                if needs_comma and not after_slash.endswith(","):
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
            # Skip comment lines in look-ahead (comments between data items are valid GAMS)
            needs_comma = True
            for j in range(i + 1, len(lines)):
                next_stripped = lines[j].strip()
                if not next_stripped or next_stripped.startswith("*"):
                    continue  # skip empty lines and comments
                # If next data line starts with / or only contains /, this is last element
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
                break

            if needs_comma:
                result.append(line + ",")
            else:
                result.append(line)
        else:
            result.append(line)

        # Reset declaration state if we hit a semicolon (end of declaration)
        if in_declaration and ";" in line:
            in_declaration = False

    return "\n".join(result)


def normalize_special_identifiers(source: str) -> str:
    """Quote identifiers containing special characters (-, +) in data blocks.

    GAMS allows hyphens and plus signs in identifiers (e.g., light-ind, food+agr).
    To avoid ambiguity with arithmetic operators, we quote these identifiers when
    they appear in /.../ data blocks or table row labels/data.

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
        - For tables: column headers are kept unquoted (parsed via DESCRIPTION
          terminal), but row labels and data values are quoted if needed
        - Preserves already-quoted strings
        - Detects identifiers with - or + that aren't arithmetic operators
        - Uses context: no surrounding whitespace = identifier
    """
    lines = source.split("\n")
    result = []
    in_data_block = False
    in_table = False
    table_header_seen = False
    in_multi_line_declaration = False  # Track multi-line Set/Parameter/Scalar/Alias

    for line in lines:
        stripped = line.strip()

        # Check if we're starting a multi-line declaration
        if re.match(r"^\s*(Set|Parameter|Scalar|Alias)\b", stripped, re.IGNORECASE):
            in_multi_line_declaration = True
            # Check if this line also has a semicolon (single-line declaration)
            if ";" in line:
                in_multi_line_declaration = False

        # Check if we're starting a table
        if re.match(r"^Table\b", stripped, re.IGNORECASE):
            in_table = True
            table_header_seen = False
            # Detect whether the Table declaration line has a description
            # after the domain. The grammar allows both quoted and unquoted
            # DESCRIPTION text, for example:
            #   Table t(i,j) 'production rate'
            #   Table t(i,j) production rate
            # We therefore treat any non-empty text after the closing ')'
            # that is not just a bare semicolon as a description.
            closing_paren_idx = stripped.find(")")
            if closing_paren_idx != -1:
                after_paren = stripped[closing_paren_idx + 1 :].strip()
                table_has_description = bool(after_paren and not after_paren.startswith(";"))
            else:
                table_has_description = False
            result.append(line)
            continue

        # If in a table, skip column header line but process data rows
        if in_table:
            # Table ends with a semicolon
            if stripped.endswith(";"):
                in_table = False
                # Still process this line (could be data row)
                processed = _quote_special_in_line(line)
                result.append(processed)
                continue

            # First non-empty line after Table declaration is the column header.
            # Issue #673: Column headers with hyphens need special handling:
            # - If the Table declaration has a description after the domain
            #   (either a quoted STRING, e.g., 'production rate', or unquoted
            #   DESCRIPTION text, e.g., production rate), we MUST quote column
            #   headers to prevent `machine-1` from being parsed as row label
            #   `machine` + value `-1`.
            # - If Table declaration has NO description, we must NOT quote column
            #   headers so the DESCRIPTION terminal can match them.
            # Issue #668: Column headers with + MUST always be quoted because + triggers
            # table_continuation parsing.
            if not table_header_seen and stripped:
                table_header_seen = True
                # Check if line contains identifier with + (always quote these)
                has_plus_identifier = bool(
                    re.search(r"\b[0-9A-Za-z_][0-9A-Za-z_+-]*\+[0-9A-Za-z_+-]+\b", stripped)
                )
                if table_has_description or has_plus_identifier:
                    # Quote all special identifiers in column headers
                    processed = _quote_special_in_line(line)
                    result.append(processed)
                else:
                    # Don't quote - let DESCRIPTION terminal match
                    result.append(line)
                continue

            # All table rows (data rows with row labels and values)
            if stripped:
                processed = _quote_special_in_line(line)
                result.append(processed)
                continue

        # Track if we're inside a /.../ data block
        # Data blocks can appear on lines starting with declaration keywords
        # OR on continuation lines within a multi-line declaration
        if "/" in line and not in_data_block:
            # Check if this is actually a data block (not division in equations)
            # Data blocks appear after Set, Parameter, Scalar, Alias keywords
            is_declaration = re.match(r"^\s*(Set|Parameter|Scalar|Alias)\b", line, re.IGNORECASE)
            if is_declaration or in_multi_line_declaration:
                # Check if entering a data block
                slash_count = line.count("/")
                if slash_count == 1:
                    # Opening a data block
                    in_data_block = True
                elif slash_count >= 2:
                    # Inline block - process it
                    processed = _quote_special_in_line(line)
                    result.append(processed)
                    # Check if declaration ends
                    if ";" in line:
                        in_multi_line_declaration = False
                    continue
        elif "/" in line and in_data_block:
            # Check if closing the data block
            if line.strip().endswith("/") or line.strip().endswith("/;"):
                in_data_block = False

        # Check if multi-line declaration ends (semicolon outside data block)
        if in_multi_line_declaration and ";" in line and not in_data_block:
            in_multi_line_declaration = False

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
    # Skip if line is a comment
    if line.strip().startswith("*"):
        return line

    # Pattern: identifier with - or + that's NOT surrounded by whitespace
    # This distinguishes:
    #   light-ind (identifier) vs x1 - 1 (arithmetic)
    #   food+agr (identifier) vs x + y (arithmetic)
    #   20-bond-wt (identifier starting with number)
    #
    # Match: Start of identifier, then word chars, then one or more (-/+ followed by word chars)
    # Word boundary at start to ensure we match the full identifier
    # Note: This function is only called for lines in data blocks (Set/Parameter/etc.),
    # so we don't need to worry about matching arithmetic in equations
    #
    # Issue #665: Also match number-starting identifiers like 20-bond-wt
    # Pattern has two alternatives:
    # 1. Letter/underscore start: [a-zA-Z_][a-zA-Z0-9_]*(?:[-+][a-zA-Z0-9_]+)+
    # 2. Number start with hyphen or plus: [0-9]+[-+][a-zA-Z0-9_]+(?:[-+][a-zA-Z0-9_]+)*
    pattern = r"\b((?:[a-zA-Z_][a-zA-Z0-9_]*(?:[-+][a-zA-Z0-9_]+)+)|(?:[0-9]+[-+][a-zA-Z0-9_]+(?:[-+][a-zA-Z0-9_]+)*))\b"

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


def strip_eol_comments(source: str) -> str:
    """Strip end-of-line comments defined by $eolCom directive.

    GAMS supports user-defined end-of-line comment markers via the $eolCom
    directive. For example, ``$eolCom //`` makes ``//`` an end-of-line comment
    marker, so everything from ``//`` to end of line is a comment.

    This must run BEFORE multiline joining (join_multiline_equations) because
    the joiner concatenates continuation lines into a single line, which would
    embed the comment text into the middle of an expression where the grammar's
    end-of-line ignore pattern cannot match it.

    The function respects quoted strings — comment markers inside single or
    double quotes are not treated as comments.

    Args:
        source: GAMS source code text

    Returns:
        Source code with end-of-line comments stripped
    """
    lines = source.split("\n")
    eol_marker: str | None = None
    result: list[str] = []

    for line in lines:
        stripped_lower = line.strip().lower()

        # Detect $eolCom directive and extract the marker
        if stripped_lower.startswith("$eolcom"):
            parts = line.strip().split(None, 1)
            if len(parts) >= 2:
                eol_marker = parts[1].strip()
            result.append(line)
            continue

        # If no eol marker defined yet, pass through
        if eol_marker is None:
            result.append(line)
            continue

        # Strip eol comment, respecting quoted strings
        # Walk character by character to find the marker outside quotes
        in_single_quote = False
        in_double_quote = False
        marker_len = len(eol_marker)
        i = 0
        found_at = -1
        while i <= len(line) - marker_len:
            ch = line[i]
            # Handle single quotes, including GAMS-style escaped quotes ('')
            if ch == "'" and not in_double_quote:
                if in_single_quote and i + 1 < len(line) and line[i + 1] == "'":
                    # Escaped single quote inside single-quoted string
                    i += 2
                    continue
                in_single_quote = not in_single_quote
                i += 1
                continue
            # Handle double quotes, including GAMS-style escaped quotes ("")
            if ch == '"' and not in_single_quote:
                if in_double_quote and i + 1 < len(line) and line[i + 1] == '"':
                    # Escaped double quote inside double-quoted string
                    i += 2
                    continue
                in_double_quote = not in_double_quote
                i += 1
                continue
            # Only look for the marker when not inside any quoted string
            if not in_single_quote and not in_double_quote:
                if line[i : i + marker_len] == eol_marker:
                    found_at = i
                    break
            i += 1

        if found_at >= 0:
            result.append(line[:found_at].rstrip())
        else:
            result.append(line)

    return "\n".join(result)


def join_multiline_equations(source: str) -> str:
    """Join multi-line equation definitions into single logical lines.

    GAMS allows equations to span multiple lines without explicit continuation
    characters. This function detects equation definitions (identified by `..`)
    and joins continuation lines until the equation ends with a semicolon.

    The function handles:
    - Equations spanning multiple lines (common in GAMS models)
    - Continuation lines starting with operators (+, -, *, /)
    - Continuation lines starting with relational operators (=e=, =l=, =g=)
    - Column-1 comment lines (line starts with * at position 0) are preserved
      as standalone lines without terminating the equation being joined
    - Indented lines starting with * (e.g., "   * expr") are treated as
      multiplication continuations, not comments

    Args:
        source: GAMS source code text

    Returns:
        Source code with multi-line equations joined into single lines

    Example:
        >>> source = '''labc(tm)..     sum((p,s), labor(p,tm)*xcrop(p,s))
        ...             +  sum(r, llab(tm,r)*xliver(r))
        ...            =l= flab(tm) + tlab(tm) + dpm*plab;'''
        >>> result = join_multiline_equations(source)
        >>> # Result: 'labc(tm).. sum((p,s), labor(p,tm)*xcrop(p,s)) + sum(r, llab(tm,r)*xliver(r)) =l= flab(tm) + tlab(tm) + dpm*plab;'

    Notes:
        - Only processes lines within equation definitions (after ..)
        - Stops joining when a semicolon is encountered
        - Column-1 comment lines (starting with * at position 0) are preserved
          as standalone lines but do not terminate the equation being joined
        - Indented * lines are treated as multiplication, not comments
        - Preserves line structure for non-equation code
        - Comment reordering: Column-1 comments that appear between continuation
          lines are emitted immediately while the equation is still being
          buffered, so they may appear BEFORE the joined equation in the output.
          This is acceptable because comments in the middle of equations are
          rare in practice, and the comment content is preserved.
    """
    lines = source.split("\n")
    result: list[str] = []
    in_equation = False
    equation_buffer: list[str] = []

    for line in lines:
        stripped = line.strip()

        # Skip empty lines - preserve them as-is
        if not stripped:
            result.append(line)
            continue

        # Handle GAMS comment lines - these start with * at column 1 (no leading whitespace)
        # Lines with leading whitespace before * are multiplication continuations, not comments
        # This distinction is important: "* comment" vs "   * expr" (multiplication)
        if line.startswith("*"):
            # True comment line - preserve as-is but do NOT terminate ongoing equation.
            # Comments can appear between continuation lines in GAMS. We emit the comment
            # immediately but keep buffering the equation so it doesn't get split.
            result.append(line)
            continue

        # Check if this line starts an equation definition (contains ..)
        # Must have identifier followed by optional domain, then ..
        if not in_equation and ".." in stripped:
            # Check if this is actually an equation definition (not string or comment)
            # Pattern: identifier with optional domain, followed by ..
            # Avoid matching things like "foo.bar" or strings containing ".."
            dot_dot_idx = stripped.find("..")
            if dot_dot_idx > 0:
                before_dots = stripped[:dot_dot_idx].rstrip()
                # Should end with ) for domain or identifier char
                if before_dots and (
                    before_dots[-1] == ")" or before_dots[-1].isalnum() or before_dots[-1] == "_"
                ):
                    # This looks like an equation definition
                    # Check if it has a semicolon (complete on one line)
                    if _has_statement_ending_semicolon(stripped):
                        # Complete equation on one line
                        result.append(line)
                    else:
                        # Multi-line equation starts
                        in_equation = True
                        equation_buffer = [stripped]
                    continue

        # If we're inside an equation, check for continuation
        if in_equation:
            # Check if this line continues the equation
            # Continuation lines typically start with:
            # - Operators: +, -, *, /
            # - Relational operators: =e=, =l=, =g=, =n=
            # - Opening parenthesis or other expression parts
            # Or they can be any expression that doesn't start a new statement

            # Check if line ends the equation (has semicolon)
            if _has_statement_ending_semicolon(stripped):
                # End of equation - join and output
                equation_buffer.append(stripped)
                joined = " ".join(equation_buffer)
                result.append(joined)
                in_equation = False
                equation_buffer = []
            else:
                # Check if this is a continuation or a new statement
                # A new statement would start with a keyword or identifier followed by specific patterns
                # For now, we consider lines starting with operators as continuations
                first_char = stripped[0] if stripped else ""
                first_word = stripped.split()[0].lower() if stripped.split() else ""

                # Check for common continuation patterns
                is_continuation = (
                    first_char in ("+", "-", "*", "/", "(", ")", ",")
                    or stripped.lower().startswith("=e=")
                    or stripped.lower().startswith("=l=")
                    or stripped.lower().startswith("=g=")
                    or stripped.lower().startswith("=n=")
                    # Check if it looks like an expression continuation (not a new statement)
                    # New statements typically start with keywords
                    # Only check keyword membership if first_word exists to avoid false positives
                    or (
                        first_word
                        and first_word
                        not in (
                            BLOCK_KEYWORDS
                            + [
                                "model",
                                "solve",
                                "display",
                                "abort",
                                "option",
                                "if",
                                "loop",
                                "while",
                                "for",
                                "equation",
                                "equations",
                            ]
                        )
                    )
                )

                if is_continuation:
                    equation_buffer.append(stripped)
                else:
                    # This looks like a new statement - output buffered equation and process this line
                    if equation_buffer:
                        joined = " ".join(equation_buffer)
                        result.append(joined)
                    in_equation = False
                    equation_buffer = []
                    result.append(line)
        else:
            result.append(line)

    # Handle case where equation wasn't closed (missing semicolon at end of file)
    if equation_buffer:
        joined = " ".join(equation_buffer)
        result.append(joined)

    return "\n".join(result)


def join_multiline_assignments(source: str) -> str:
    """Join multi-line parameter/scalar assignments into single logical lines.

    GAMS allows assignments to span multiple lines without explicit continuation
    characters. This function detects assignment statements that have unbalanced
    parentheses at end of line and joins them with subsequent lines until
    parentheses are balanced and the statement ends with a semicolon.

    This handles cases like (Issue #636):
        at(it) = xd0(it)/(gamma(it)*e0(it)**rhot(it) + (1 - gamma(it))
               * xxd0(it)**rhot(it))**(1/rhot(it));

    Which the parser would otherwise fail on because line 1 has unbalanced
    parentheses (8 open, 7 close).

    Args:
        source: GAMS source code text

    Returns:
        Source code with multi-line assignments joined into single lines

    Notes:
        - Only joins lines where parentheses are unbalanced
        - Preserves comment lines (starting with *), but may reorder them
        - Column-1 comment lines that appear between continuation lines are emitted
          immediately while the assignment is still being buffered, so they can
          appear before the final joined assignment line in the output (same
          behavior as join_multiline_equations)
        - Stops joining when parentheses are balanced AND line ends with semicolon
        - Does not process lines that look like equation definitions (contain ..)
    """
    lines = source.split("\n")
    result: list[str] = []
    in_continuation = False
    # Store tuples of (original_line, stripped_line) so we can join stripped
    # content for successful continuations but preserve original formatting in flush paths
    continuation_buffer: list[tuple[str, str]] = []
    paren_depth = 0

    for line in lines:
        stripped = line.strip()

        # Skip empty lines - preserve them as-is
        if not stripped:
            result.append(line)
            continue

        # Handle GAMS comment lines - these start with * at column 1 (no leading whitespace)
        # Lines with leading whitespace before * are multiplication continuations, not comments
        # This distinction is important: "* comment" vs "   * expr" (multiplication)
        if line.startswith("*"):
            # True comment line - preserve as-is but do NOT terminate ongoing continuation.
            # Comments can appear between continuation lines in GAMS. We emit the comment
            # immediately but keep buffering the assignment so it doesn't get split.
            result.append(line)
            continue

        # Skip lines that are equation definitions (handled by join_multiline_equations)
        if ".." in stripped and not in_continuation:
            result.append(line)
            continue

        if not in_continuation:
            # Check if this line has an assignment and unbalanced parentheses
            # Look for pattern: identifier(domain) = expression or identifier = expression
            has_assignment = "=" in stripped and not stripped.startswith("=")

            if has_assignment:
                # Count parentheses
                open_parens = stripped.count("(")
                close_parens = stripped.count(")")
                paren_depth = open_parens - close_parens

                # Check if line ends with semicolon (complete statement)
                ends_with_semi = _has_statement_ending_semicolon(stripped)

                if paren_depth != 0 and not ends_with_semi:
                    # Unbalanced parentheses and no semicolon - start continuation
                    in_continuation = True
                    continuation_buffer = [(line, stripped)]
                else:
                    # Balanced or complete - output as-is
                    result.append(line)
            else:
                result.append(line)
        else:
            # We're in a continuation - add this line to buffer
            continuation_buffer.append((line, stripped))

            # Update parenthesis count
            paren_depth += stripped.count("(") - stripped.count(")")

            # Check if statement is complete (balanced parens and ends with semicolon)
            ends_with_semi = _has_statement_ending_semicolon(stripped)

            if paren_depth == 0 and ends_with_semi:
                # Statement is complete - join stripped content and output
                joined = " ".join(s for _, s in continuation_buffer)
                result.append(joined)
                in_continuation = False
                continuation_buffer = []
                paren_depth = 0
            elif paren_depth < 0:
                # More closing than opening - something is wrong, output original lines as-is
                for orig, _ in continuation_buffer:
                    result.append(orig)
                in_continuation = False
                continuation_buffer = []
                paren_depth = 0

    # Handle case where continuation wasn't closed at end of file
    if continuation_buffer:
        for orig, _ in continuation_buffer:
            result.append(orig)

    return "\n".join(result)


def insert_missing_semicolons(source: str) -> str:
    """Insert missing semicolons before block keywords.

    GAMS allows omitting semicolons at the end of declaration blocks when
    the next block starts with a keyword. This function inserts semicolons
    before block keywords (Set, Parameter, Variable, Equation, etc.) when
    the previous non-empty, non-comment line doesn't end with a semicolon.

    This fixes issue #418 where variables declared in include files were
    not being recognized because the parser consumed them as part of a
    preceding block (e.g., parameters or sets) that was missing a semicolon.

    Args:
        source: GAMS source code text

    Returns:
        Source code with missing semicolons inserted

    Example:
        >>> source = '''parameters p(i) test
        ...
        ... variables x(i) test;'''
        >>> result = insert_missing_semicolons(source)
        >>> # Result has semicolon inserted before 'variables'
    """
    lines = source.split("\n")
    result = []

    # Build regex pattern for block keywords at start of line (case-insensitive)
    # Pattern matches: optional whitespace, then keyword, then word boundary
    block_keyword_pattern = re.compile(r"^\s*(" + "|".join(BLOCK_KEYWORDS) + r")\b", re.IGNORECASE)

    # Track if we need to insert a semicolon
    last_content_line_idx = -1  # Index of last non-empty, non-comment line

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("*"):
            result.append(line)
            continue

        # Check if this line starts with a block keyword
        if block_keyword_pattern.match(stripped):
            # Check if we need to insert a semicolon before this line
            if last_content_line_idx >= 0:
                last_line = result[last_content_line_idx]
                last_stripped = last_line.rstrip()

                # If the last content line doesn't end with semicolon, insert one
                if not last_stripped.endswith(";"):
                    result[last_content_line_idx] = last_stripped + ";"

        result.append(line)
        last_content_line_idx = i

    return "\n".join(result)


def expand_tuple_only_table_rows(source: str) -> str:
    """Expand (a,b,c) tuple-only row labels in tables to individual rows.

    GAMS allows a parenthesized list as a table row label when multiple
    elements share the same row values. For example:

        Table t(i,j)
                  c1  c2
        (a,b,c)    1   2

    expands to three rows: a 1 2 / b 1 2 / c 1 2.

    This preprocessor step rewrites such rows before grammar parsing, since
    the grammar cannot distinguish (i,j) in "Table t(i,j)" from (i,j) as a
    row label without line-position context.

    Note: The regex group 3 captures all trailing content after the closing ')',
    including any dot-suffix (e.g. '(a,b).c  1 2' → 'a.c  1 2' and 'b.c  1 2').
    This means the preprocessor also expands dot-suffixed tuple labels — functionally
    equivalent to the grammar's tuple_label rule, and avoids the grammar ambiguity
    with Table domain declarations like 'Table t(i,j)'.
    """
    # Pattern: optional whitespace, then ( elem1, elem2, ... ), then rest of line
    # elem can be SET_ELEMENT_ID (alphanumeric + hyphens) or GAMS STRING ('...' with '' escapes)
    # GAMS uses '' (double single-quote) as the escape for a literal single-quote inside strings.
    _ELEM = r"(?:'(?:[^']|'')*'|[A-Za-z0-9_][A-Za-z0-9_\-]*)"
    _TUPLE_ROW = re.compile(
        r"^(\s*)"  # group 1: leading indent
        r"\(("  # literal ( then group 2: element list
        + _ELEM
        + r"(?:\s*,\s*"
        + _ELEM
        + r")*"
        + r")\)"  # end group 2 and )
        r"(\s*.*)$",  # group 3: rest of line (values)
        re.IGNORECASE,
    )
    # Quote-aware element splitter: splits on commas outside of single-quoted strings
    _SPLIT_ELEM = re.compile(r"'(?:[^']|'')*'|[^,]+")

    def _split_elements(elem_list_str: str) -> list[str]:
        """Split a comma-separated element list, respecting GAMS quoted strings."""
        parts = []
        for m in _SPLIT_ELEM.finditer(elem_list_str):
            token = m.group(0).strip()
            if token and token != ",":
                parts.append(token)
        return parts

    lines = source.split("\n")
    result = []
    in_table = False
    table_header_seen = False
    is_first_line_after_decl = False

    for line in lines:
        stripped = line.strip()

        if re.match(r"^Table\b", stripped, re.IGNORECASE):
            in_table = True
            table_header_seen = False
            is_first_line_after_decl = True
            result.append(line)
            continue

        if in_table:
            # Skip column header line (first non-empty line after Table decl)
            if is_first_line_after_decl:
                if stripped:
                    is_first_line_after_decl = False
                    table_header_seen = True
                result.append(line)
                continue

            # If a new block keyword starts without a semicolon, terminate the table.
            # This prevents subsequent declaration lines from being misread as table rows.
            if stripped and re.match(
                r"^(?:" + "|".join(BLOCK_KEYWORDS) + r")\b", stripped, re.IGNORECASE
            ):
                in_table = False
                result.append(line)
                continue

            # Handle table termination: check for tuple expansion BEFORE ending
            is_last_line = stripped.endswith(";")
            if is_last_line:
                in_table = False
                # Strip the trailing semicolon for tuple expansion check
                line_no_semi = line.rstrip()
                if line_no_semi.endswith(";"):
                    line_no_semi = line_no_semi[:-1]
                stripped_no_semi = line_no_semi.strip()
            else:
                line_no_semi = line
                stripped_no_semi = stripped

            if table_header_seen and stripped_no_semi:
                m = _TUPLE_ROW.match(line_no_semi)
                if m:
                    indent = m.group(1)
                    elem_list_str = m.group(2)
                    rest = m.group(3)
                    # Parse elements: use quote-aware splitter to handle 'a,b' strings
                    raw_elems = _split_elements(elem_list_str)
                    for i_elem, elem in enumerate(raw_elems):
                        # Only append semicolon to the last expanded row if this was last line
                        if is_last_line and i_elem == len(raw_elems) - 1:
                            result.append(f"{indent}{elem}{rest};")
                        else:
                            result.append(f"{indent}{elem}{rest}")
                    continue

            if is_last_line and not (
                table_header_seen and stripped_no_semi and _TUPLE_ROW.match(line_no_semi)
            ):
                result.append(line)
                continue

        result.append(line)

    return "\n".join(result)


def normalize_double_commas(source: str) -> str:
    """Replace double commas with single commas in data blocks.

    Issue #565: GAMS allows double commas in set/parameter data as visual
    alignment or placeholder. This function normalizes them to single commas.

    Args:
        source: GAMS source code text

    Returns:
        Source code with double commas replaced by single commas

    Example:
        Set l / b 'base',, c 'competitive' /;
        →
        Set l / b 'base', c 'competitive' /;

    Notes:
        - Replaces all occurrences of two-or-more consecutive commas with a single comma
          when they appear outside of quoted strings
        - Leaves commas inside single-quoted strings unchanged
        - Runs before full parsing, using a simple single-quote aware scan to respect
          string boundaries
    """
    # Perform a single-pass scan, collapsing comma runs only outside of strings.
    result: list[str] = []
    in_string = False
    i = 0
    length = len(source)

    while i < length:
        ch = source[i]

        if ch == "'":
            # Handle GAMS-style escaped quote inside strings: '' -> literal '
            if in_string and i + 1 < length and source[i + 1] == "'":
                result.append("''")
                i += 2
                continue
            in_string = not in_string
            result.append(ch)
            i += 1
            continue

        if not in_string and ch == ",":
            # Collapse any run of commas outside strings to a single comma.
            result.append(",")
            i += 1
            while i < length and source[i] == ",":
                i += 1
            continue

        result.append(ch)
        i += 1

    return "".join(result)


def _is_include_directive(line: str) -> bool:
    """Check if a line contains an actual $include/$batInclude directive.

    Returns True only if the directive appears as actual code, not inside
    quoted strings or comments. Handles:
    - Standalone directives: `$include "file.gms"`
    - Inline after conditionals: `$if set X $include "file.gms"`

    Args:
        line: A single line of GAMS source code

    Returns:
        True if the line contains an actual include directive to strip
    """
    # Check if line is already a comment
    stripped = line.lstrip()
    if stripped.startswith("*"):
        return False

    # Scan through the line, tracking whether we're inside quotes
    in_single_quote = False
    in_double_quote = False
    i = 0
    line_lower = line.lower()
    length = len(line)

    while i < length:
        char = line[i]

        # Handle quote state changes with escaped quote handling ('' and "")
        if char == "'" and not in_double_quote:
            # Check for escaped single quote ('') inside single-quoted string
            if in_single_quote and i + 1 < length and line[i + 1] == "'":
                # Skip both quotes - this is an escaped literal quote
                i += 2
                continue
            in_single_quote = not in_single_quote
        elif char == '"' and not in_single_quote:
            # Check for escaped double quote ("") inside double-quoted string
            if in_double_quote and i + 1 < length and line[i + 1] == '"':
                # Skip both quotes - this is an escaped literal quote
                i += 2
                continue
            in_double_quote = not in_double_quote
        elif not in_single_quote and not in_double_quote:
            # Only treat '*' as starting an inline comment in valid comment
            # positions: first non-whitespace character, or after a statement
            # terminator ';'. In other positions (e.g., 'a*b'), it's a
            # multiplication operator and we must continue scanning.
            if char == "*":
                # Look backwards for the previous non-whitespace character
                j = i - 1
                while j >= 0 and line[j].isspace():
                    j -= 1
                # Comment start if: first token (j < 0) or after ';'
                if j < 0 or line[j] == ";":
                    break
            # Check for $ directive when not inside quotes or comments
            if char == "$":
                # Check if this is $include or $batinclude
                remaining = line_lower[i:]
                if remaining.startswith("$include") or remaining.startswith("$batinclude"):
                    # Verify it's a word boundary (not $includefoo or $include_foo)
                    directive_len = 8 if remaining.startswith("$include") else 11
                    if len(remaining) == directive_len:
                        return True
                    next_char = remaining[directive_len]
                    # Treat '_' as an identifier character to avoid misdetecting $include_foo
                    if not (next_char.isalnum() or next_char == "_"):
                        return True
        i += 1

    return False


def _strip_include_directives(source: str) -> str:
    """Strip $include and $batInclude directives to comments.

    This preserves line numbers while preventing parse errors when these
    directives appear in source strings passed to preprocess_text().

    Handles both standalone include directives and inline includes (e.g.,
    after $if conditionals like `$if set X $include "file.gms"`).

    Only strips actual directive usage - ignores matches inside quoted strings
    or comments.

    Args:
        source: GAMS source code

    Returns:
        Source with lines containing $include/$batInclude directives replaced by comments
    """
    lines = source.split("\n")
    result = []
    for line in lines:
        if _is_include_directive(line):
            # Replace with comment to preserve line numbers, preserving original indentation
            stripped = line.strip()
            leading_ws = line[: len(line) - len(line.lstrip())]
            result.append(f"{leading_ws}* [Stripped: {stripped}]")
        else:
            result.append(line)
    return "\n".join(result)


def _preprocess_content(content: str) -> str:
    """Shared preprocessing pipeline for GAMS content.

    This is the core preprocessing logic used by both preprocess_gams_file()
    and preprocess_text(). It performs all preprocessing steps except for
    file-based operations ($include, $batInclude).

    Preprocessing steps:
    1. Extract macro defaults from $if not set directives
    2. Extract general $set directives
    3. Process $if/$else/$endif conditional blocks
    4. Expand %variable% references
    5. Extract $macro definitions
    6. Expand macro function calls
    7. Strip conditional directives ($if not set)
    8. Strip $set directives
    9. Strip $macro directives
    10. Strip other unsupported directives ($title, $ontext, etc.)
    11. Join multi-line equations into single lines
    11b. Join multi-line assignments into single lines (Issue #636)
    12. Remove table continuation markers (+)
    13. Normalize multi-line continuations (add missing commas)
    14. Insert missing semicolons before block keywords
    15. Quote identifiers with special characters (-, +) in data blocks
    15b. Expand tuple-only table rows: (a,b,c) vals → individual rows
    16. Normalize double commas to single commas

    Args:
        content: GAMS source code (after $include expansion if applicable)

    Returns:
        Preprocessed source code ready for parsing
    """
    # Step 1: Extract macro defaults from $if not set directives
    macros = extract_conditional_sets(content)

    # Step 2: Extract general $set directives (merge with conditional sets)
    # Pass existing macros so that $set can reference earlier macros
    set_macros = extract_set_directives(content, macros)
    macros.update(set_macros)  # $set directives override conditional defaults

    # Step 3: Process $if/$else/$endif conditional blocks
    # This must happen after extracting macros so conditionals can test variable definitions
    # but before expanding %variable% so conditional blocks are removed first
    content = process_conditionals(content, macros)

    # Step 4: Expand %variable% references with their values
    content = expand_macros(content, macros)

    # Step 5: Extract $macro function definitions
    # This must happen after %variable% expansion so that macro bodies have variables expanded
    # For example: $macro fx(t) %fx% becomes $macro fx(t) sin(t) * cos(t-t*t)
    macro_defs = extract_macro_definitions(content)

    # Step 6: Expand macro function calls
    # Replace fx(t('1')) with sin(t('1')) * cos(t('1')-t('1')*t('1'))
    content = expand_macro_calls(content, macro_defs)

    # Step 7: Strip $if not set directives (replaced with comments)
    content = strip_conditional_directives(content)

    # Step 8: Strip $set directives (replaced with comments)
    content = strip_set_directives(content)

    # Step 9: Strip $macro directives (replaced with comments)
    content = strip_macro_directives(content)

    # Step 9b: Strip end-of-line comments defined by $eolCom directive (Issue #722)
    # This must happen BEFORE strip_unsupported_directives (which strips the
    # $eolCom directive itself) and BEFORE multiline joining (which would embed
    # comment text into the middle of joined expressions).
    content = strip_eol_comments(content)

    # Step 10: Strip other unsupported directives ($title, $ontext, etc.)
    content = strip_unsupported_directives(content)

    # Step 11: Join multi-line equations into single lines
    # This must happen before table continuation normalization to avoid
    # confusing equation continuation with table continuation markers
    content = join_multiline_equations(content)

    # Step 11b: Join multi-line assignments into single lines (Issue #636)
    # This handles parameter/scalar assignments that span multiple lines
    # due to unbalanced parentheses, like:
    #   at(it) = xd0(it)/(gamma(it)*e0(it)**rhot(it) + (1 - gamma(it))
    #          * xxd0(it)**rhot(it))**(1/rhot(it));
    content = join_multiline_assignments(content)

    # Step 12: Remove table continuation markers (+)
    content = normalize_table_continuations(content)

    # Step 13: Normalize multi-line continuations (add missing commas)
    content = normalize_multi_line_continuations(content)

    # Step 14: Insert missing semicolons before block keywords
    # This fixes issue #418 where variables from include files weren't recognized
    # because previous blocks (sets, parameters) were missing semicolons
    content = insert_missing_semicolons(content)

    # Step 15: Quote identifiers with special characters (-, +) in data blocks
    content = normalize_special_identifiers(content)

    # Step 15b: Expand (a,b,c) tuple-only row labels in tables
    # Must run after normalize_special_identifiers (which quotes hyphenated IDs)
    content = expand_tuple_only_table_rows(content)

    # Step 16: Normalize double commas to single commas (Issue #565)
    # This must happen after all other data normalization
    return normalize_double_commas(content)


def preprocess_gams_file(file_path: Path | str) -> str:
    """Preprocess a GAMS file, expanding all $include directives.

    This is the main entry point for preprocessing GAMS files.
    It performs preprocessing in the following order:
    1. Expand $include directives recursively
    2. Expand $batInclude directives with argument substitution
    3. Run _preprocess_content() (macro/conditional expansion, stripping, normalization)

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

    # Step 2: Expand $batInclude directives with argument substitution
    # This must happen after regular includes so that $batInclude can reference
    # files that were themselves included via $include
    content = preprocess_bat_includes(file_path, content)

    # Step 3: Shared preprocessing pipeline (macro/conditional expansion, stripping, normalization)
    return _preprocess_content(content)


def preprocess_text(source: str) -> str:
    """Preprocess GAMS source text without file-based operations.

    This function performs the same preprocessing as preprocess_gams_file()
    but skips file-based operations ($include, $batInclude). Use this for
    preprocessing raw GAMS source strings that don't require file inclusion.

    Any $include or $batInclude directives in the source will be stripped
    (converted to comments) to prevent parse errors. If you need to process
    files with includes, use preprocess_gams_file() instead.

    Args:
        source: GAMS source code to preprocess

    Returns:
        Preprocessed source code ready for parsing

    Example:
        >>> code = "$set N 5\\nSet i / i1*i%N% /;"
        >>> result = preprocess_text(code)
        >>> # %N% is expanded to 5
    """
    # Apply shared preprocessing pipeline first (macro/conditional expansion, etc.)
    content = _preprocess_content(source)

    # Strip $include/$batInclude directives (convert to comments) after conditionals
    # This prevents double-wrapping of lines (e.g., Excluded: Stripped: ...) while
    # still ensuring unresolved include directives don't reach the parser.
    return _strip_include_directives(content)
