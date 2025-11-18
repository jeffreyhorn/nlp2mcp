"""
Error enhancement for parser errors.

Provides "did you mean?" suggestions and contextual hints for common GAMS parsing mistakes.
"""

import re
from difflib import get_close_matches

from .errors import ParseError

# GAMS keywords for typo detection
GAMS_KEYWORDS = [
    "Set",
    "Sets",
    "Scalar",
    "Scalars",
    "Parameter",
    "Parameters",
    "Variable",
    "Variables",
    "Equation",
    "Equations",
    "Model",
    "Solve",
    "Table",
    "Alias",
    "Display",
    "Option",
    "Free",
    "Positive",
    "Negative",
    "Binary",
    "Integer",
    "Using",
    "Minimizing",
    "Maximizing",
]


class ErrorEnhancer:
    """
    Enhance parser errors with actionable suggestions.

    Analyzes ParseError instances and adds contextual hints, "did you mean?" suggestions,
    and explanations for common mistakes.
    """

    def enhance(self, error: ParseError, source: str | None = None) -> ParseError:
        """
        Enhance a ParseError with suggestions based on error patterns.

        Args:
            error: The original ParseError
            source: Full source code (optional, for multi-line analysis)

        Returns:
            Enhanced ParseError with updated suggestion
        """
        # If error already has a suggestion, keep it but potentially add more
        existing_suggestion = error.suggestion
        new_suggestions = []

        # Extract error message and source line
        message = error.message if hasattr(error, "message") else str(error)
        source_line = error.source_line if hasattr(error, "source_line") else None

        # Rule 1: Keyword typo detection
        if source_line:
            keyword_suggestion = self._detect_keyword_typo(source_line, message)
            if keyword_suggestion:
                new_suggestions.append(keyword_suggestion)

        # Rule 2: Set bracket error detection
        if source_line and "Set" in source_line and "[" in source_line:
            bracket_suggestion = self._detect_set_bracket_error(source_line)
            if bracket_suggestion:
                new_suggestions.append(bracket_suggestion)

        # Rule 3: Missing semicolon detection
        if source and error.line:
            semicolon_suggestion = self._detect_missing_semicolon(source, error.line, message)
            if semicolon_suggestion:
                new_suggestions.append(semicolon_suggestion)

        # Rule 4: Unsupported feature explanation
        if "not supported" in message.lower() or "not yet supported" in message.lower():
            feature_suggestion = self._explain_unsupported_feature(message)
            if feature_suggestion:
                new_suggestions.append(feature_suggestion)

        # Rule 5: Function call error
        if "Call(" in message or "function call" in message.lower():
            function_suggestion = self._explain_function_call_limitation(message)
            if function_suggestion:
                new_suggestions.append(function_suggestion)

        # Combine existing and new suggestions
        if new_suggestions:
            if existing_suggestion:
                combined_suggestion = (
                    existing_suggestion.rstrip() + "\n\n" + "\n".join(new_suggestions)
                )
            else:
                combined_suggestion = "\n".join(new_suggestions)

            # Create a new ParseError with the enhanced suggestion
            return ParseError(
                message=error.message,
                line=error.line,
                column=error.column,
                source_line=error.source_line,
                suggestion=combined_suggestion,
            )

        # No enhancements found, return original error
        return error

    def _detect_keyword_typo(self, source_line: str, message: str) -> str | None:
        """
        Detect keyword typos using fuzzy string matching.

        Args:
            source_line: Source code line with potential typo
            message: Error message

        Returns:
            Suggestion string if typo detected, None otherwise
        """
        # Extract the first capitalized word (likely a keyword)
        # Check if it appears at the start of the line (after whitespace)
        match = re.match(r"^\s*([A-Z][a-zA-Z]*)\b", source_line)
        if not match:
            return None

        word = match.group(1)
        if word not in GAMS_KEYWORDS:
            # Find close matches with 60% similarity threshold
            matches = get_close_matches(word, GAMS_KEYWORDS, n=3, cutoff=0.6)
            if matches:
                return f"Did you mean '{matches[0]}'?"

        return None

    def _detect_set_bracket_error(self, source_line: str) -> str | None:
        """
        Detect use of square brackets instead of slashes in Set declarations.

        Args:
            source_line: Source code line with potential bracket error

        Returns:
            Suggestion string if bracket error detected, None otherwise
        """
        # Ignore comments (lines starting with * or with only whitespace before *)
        if re.match(r"^\s*\*", source_line):
            return None

        # Remove string literals to avoid false positives inside quotes
        line_wo_strings = re.sub(r'(["\']).*?\1', "", source_line)

        # Check for Set declaration with square brackets before semicolon
        # e.g., Set i [A, B, C];
        set_decl_pattern = r"^\s*Sets?\s+\w+\s*\[.*\]"
        if re.search(set_decl_pattern, line_wo_strings):
            # Replace brackets only outside string literals
            def replace_brackets_outside_strings(line):
                # Split by string literals (handles both "..." and '...')
                parts = re.split(r'((?:"[^"]*"|\'[^\']*\'))', line)
                for i in range(len(parts)):
                    # Only replace in non-string-literal parts (even indices)
                    if i % 2 == 0:
                        parts[i] = parts[i].replace("[", "/").replace("]", "/")
                return "".join(parts)

            fixed_line = replace_brackets_outside_strings(source_line)
            return f"GAMS set elements use /.../ not [...]. Try: {fixed_line.strip()}"

        return None

    def _detect_missing_semicolon(self, source: str, error_line: int, message: str) -> str | None:
        """
        Detect missing semicolons when unexpected keyword appears on next line.

        Args:
            source: Full source code
            error_line: Line number where error occurred (1-indexed)
            message: Error message

        Returns:
            Suggestion string if missing semicolon detected, None otherwise
        """
        # Check if error is about unexpected token/keyword
        if "unexpected" not in message.lower():
            return None

        source_lines = source.split("\n")
        # If the error is on the first line, there is no previous line to check for a missing semicolon.
        if error_line < 2 or error_line > len(source_lines):
            return None

        # Check previous line for missing semicolon
        prev_line = source_lines[error_line - 2].strip()
        current_line = source_lines[error_line - 1].strip()

        # If previous line doesn't end with semicolon and current line starts with keyword
        if prev_line and not prev_line.endswith(";"):
            # Skip if previous line ends with a delimiter that indicates continuation
            # (e.g., '/' for set declarations, '..' for equation definitions)
            if prev_line.endswith("/") or prev_line.endswith(".."):
                return None

            # Check if current line starts with a GAMS keyword
            first_word = current_line.split()[0] if current_line.split() else ""
            if first_word in GAMS_KEYWORDS:
                return (
                    f"Missing semicolon at end of line {error_line - 1}. Add ';' after: {prev_line}"
                )

        return None

    def _explain_unsupported_feature(self, message: str) -> str | None:
        """
        Explain unsupported features with roadmap reference.

        Args:
            message: Error message containing unsupported feature info

        Returns:
            Explanation string with roadmap reference
        """
        # Extract feature name if possible
        if "indexed assignment" in message.lower():
            feature = "Indexed assignments"
            sprint = "Sprint 8"
        elif "function call" in message.lower():
            feature = "Function calls in expressions"
            sprint = "a future release"
        elif "lead/lag" in message.lower():
            feature = "Lead/lag indexing"
            sprint = "Sprint 9"
        else:
            feature = "This feature"
            sprint = "a future release"

        return (
            f"{feature} will be available in {sprint}. "
            "See docs/ROADMAP.md for the current feature support status."
        )

    def _explain_function_call_limitation(self, message: str) -> str | None:
        """
        Explain that assignments only support numeric literals currently.

        Args:
            message: Error message about function calls

        Returns:
            Explanation string about literal-only limitation
        """
        return "Assignments currently only support numeric literals (e.g., 5, 3.14, -2.5). Function calls and expressions will be supported in a future release."
