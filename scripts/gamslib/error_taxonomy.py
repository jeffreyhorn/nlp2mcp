#!/usr/bin/env python3
"""Comprehensive error taxonomy for nlp2mcp pipeline stages.

This module defines 47 outcome categories for the parse, translate, and solve
pipeline stages. It provides categorization functions to classify error messages
and solve outcomes into specific categories.

Categories:
- 16 parse error categories (4 lexer, 6 parser, 4 semantic, 2 include)
- 13 translation error categories (3 diff, 3 model, 4 unsupported, 3 codegen)
- 16 solve outcome categories (6 PATH status, 4 model status, 6 comparison)
- 2 generic categories (timeout, internal_error)

Usage:
    from scripts.gamslib.error_taxonomy import (
        categorize_parse_error,
        categorize_translate_error,
        categorize_solve_outcome,
    )

    category = categorize_parse_error("Error: Parse error at line 18...")
    category = categorize_translate_error("Differentiation not implemented...")
    category = categorize_solve_outcome(1, 1, 1, 1, True)

Reference:
    docs/planning/EPIC_3/SPRINT_15/prep-tasks/error_taxonomy.md
"""

from __future__ import annotations

import re

# =============================================================================
# Parse Error Categories (16 total)
# =============================================================================

# Lexer errors (tokenization)
LEXER_INVALID_CHAR = "lexer_invalid_char"
LEXER_UNCLOSED_STRING = "lexer_unclosed_string"
LEXER_INVALID_NUMBER = "lexer_invalid_number"
LEXER_ENCODING_ERROR = "lexer_encoding_error"

# Parser errors (grammar)
PARSER_UNEXPECTED_TOKEN = "parser_unexpected_token"
PARSER_MISSING_SEMICOLON = "parser_missing_semicolon"
PARSER_UNMATCHED_PAREN = "parser_unmatched_paren"
PARSER_INVALID_DECLARATION = "parser_invalid_declaration"
PARSER_INVALID_EXPRESSION = "parser_invalid_expression"
PARSER_UNEXPECTED_EOF = "parser_unexpected_eof"

# Semantic errors (meaning)
SEMANTIC_UNDEFINED_SYMBOL = "semantic_undefined_symbol"
SEMANTIC_TYPE_MISMATCH = "semantic_type_mismatch"
SEMANTIC_DOMAIN_ERROR = "semantic_domain_error"
SEMANTIC_DUPLICATE_DEF = "semantic_duplicate_def"

# Include/file errors
INCLUDE_FILE_NOT_FOUND = "include_file_not_found"
INCLUDE_CIRCULAR = "include_circular"

# =============================================================================
# Translation Error Categories (13 total)
# =============================================================================

# Differentiation errors
DIFF_UNSUPPORTED_FUNC = "diff_unsupported_func"
DIFF_CHAIN_RULE_ERROR = "diff_chain_rule_error"
DIFF_NUMERICAL_ERROR = "diff_numerical_error"

# Model structure errors
MODEL_NO_OBJECTIVE_DEF = "model_no_objective_def"
MODEL_DOMAIN_MISMATCH = "model_domain_mismatch"
MODEL_MISSING_BOUNDS = "model_missing_bounds"

# Unsupported construct errors
UNSUP_INDEX_OFFSET = "unsup_index_offset"
UNSUP_DOLLAR_COND = "unsup_dollar_cond"
UNSUP_EXPRESSION_TYPE = "unsup_expression_type"
UNSUP_SPECIAL_ORDERED = "unsup_special_ordered"

# Code generation errors
CODEGEN_EQUATION_ERROR = "codegen_equation_error"
CODEGEN_VARIABLE_ERROR = "codegen_variable_error"
CODEGEN_NUMERICAL_ERROR = "codegen_numerical_error"

# =============================================================================
# Solve Outcome Categories (16 total)
# =============================================================================

# PATH solver status outcomes
PATH_SOLVE_NORMAL = "path_solve_normal"
PATH_SOLVE_ITERATION_LIMIT = "path_solve_iteration_limit"
PATH_SOLVE_TIME_LIMIT = "path_solve_time_limit"
PATH_SOLVE_TERMINATED = "path_solve_terminated"
PATH_SOLVE_EVAL_ERROR = "path_solve_eval_error"
PATH_SOLVE_LICENSE = "path_solve_license"

# Model status outcomes
MODEL_OPTIMAL = "model_optimal"
MODEL_LOCALLY_OPTIMAL = "model_locally_optimal"
MODEL_INFEASIBLE = "model_infeasible"
MODEL_UNBOUNDED = "model_unbounded"

# Solution comparison outcomes
COMPARE_OBJECTIVE_MATCH = "compare_objective_match"
COMPARE_OBJECTIVE_MISMATCH = "compare_objective_mismatch"
COMPARE_STATUS_MISMATCH = "compare_status_mismatch"
COMPARE_NLP_FAILED = "compare_nlp_failed"
COMPARE_MCP_FAILED = "compare_mcp_failed"
COMPARE_BOTH_INFEASIBLE = "compare_both_infeasible"

# =============================================================================
# Generic Categories
# =============================================================================

TIMEOUT = "timeout"
INTERNAL_ERROR = "internal_error"

# =============================================================================
# Category Lists
# =============================================================================

PARSE_ERROR_CATEGORIES = [
    LEXER_INVALID_CHAR,
    LEXER_UNCLOSED_STRING,
    LEXER_INVALID_NUMBER,
    LEXER_ENCODING_ERROR,
    PARSER_UNEXPECTED_TOKEN,
    PARSER_MISSING_SEMICOLON,
    PARSER_UNMATCHED_PAREN,
    PARSER_INVALID_DECLARATION,
    PARSER_INVALID_EXPRESSION,
    PARSER_UNEXPECTED_EOF,
    SEMANTIC_UNDEFINED_SYMBOL,
    SEMANTIC_TYPE_MISMATCH,
    SEMANTIC_DOMAIN_ERROR,
    SEMANTIC_DUPLICATE_DEF,
    INCLUDE_FILE_NOT_FOUND,
    INCLUDE_CIRCULAR,
]

TRANSLATE_ERROR_CATEGORIES = [
    DIFF_UNSUPPORTED_FUNC,
    DIFF_CHAIN_RULE_ERROR,
    DIFF_NUMERICAL_ERROR,
    MODEL_NO_OBJECTIVE_DEF,
    MODEL_DOMAIN_MISMATCH,
    MODEL_MISSING_BOUNDS,
    UNSUP_INDEX_OFFSET,
    UNSUP_DOLLAR_COND,
    UNSUP_EXPRESSION_TYPE,
    UNSUP_SPECIAL_ORDERED,
    CODEGEN_EQUATION_ERROR,
    CODEGEN_VARIABLE_ERROR,
    CODEGEN_NUMERICAL_ERROR,
]

SOLVE_OUTCOME_CATEGORIES = [
    PATH_SOLVE_NORMAL,
    PATH_SOLVE_ITERATION_LIMIT,
    PATH_SOLVE_TIME_LIMIT,
    PATH_SOLVE_TERMINATED,
    PATH_SOLVE_EVAL_ERROR,
    PATH_SOLVE_LICENSE,
    MODEL_OPTIMAL,
    MODEL_LOCALLY_OPTIMAL,
    MODEL_INFEASIBLE,
    MODEL_UNBOUNDED,
    COMPARE_OBJECTIVE_MATCH,
    COMPARE_OBJECTIVE_MISMATCH,
    COMPARE_STATUS_MISMATCH,
    COMPARE_NLP_FAILED,
    COMPARE_MCP_FAILED,
    COMPARE_BOTH_INFEASIBLE,
]

ALL_CATEGORIES = (
    PARSE_ERROR_CATEGORIES
    + TRANSLATE_ERROR_CATEGORIES
    + SOLVE_OUTCOME_CATEGORIES
    + [TIMEOUT, INTERNAL_ERROR]
)

# =============================================================================
# Legacy Category Mapping (Sprint 14 -> Sprint 15)
# =============================================================================

LEGACY_PARSE_MAPPING = {
    "syntax_error": None,  # Needs re-categorization based on message
    "validation_error": None,  # Needs re-categorization based on message
    "missing_include": INCLUDE_FILE_NOT_FOUND,
    "internal_error": INTERNAL_ERROR,
    "timeout": TIMEOUT,
    "unsupported_feature": None,  # Move to translation stage
}

LEGACY_TRANSLATE_MAPPING = {
    "unsupported_feature": None,  # Needs re-categorization based on message
    "validation_error": None,  # Needs re-categorization based on message
    "syntax_error": None,  # Needs re-categorization based on message
    "internal_error": INTERNAL_ERROR,
    "timeout": TIMEOUT,
}


# =============================================================================
# Parse Error Categorization
# =============================================================================


def categorize_parse_error(error_message: str) -> str:
    """Categorize a parse error into the refined taxonomy.

    This function analyzes the error message to determine the specific
    error category from the 16 parse error categories.

    Args:
        error_message: The error message string from the parser

    Returns:
        Error category string from PARSE_ERROR_CATEGORIES or INTERNAL_ERROR

    Examples:
        >>> categorize_parse_error("Error: Parse error at line 18: Unexpected character: '-'")
        'lexer_invalid_char'
        >>> categorize_parse_error("Missing semicolon at end of line 42")
        'parser_missing_semicolon'
    """
    if not error_message:
        return INTERNAL_ERROR

    msg_lower = error_message.lower()

    # Lexer errors - check first as they are tokenization-level
    if "unexpected character:" in msg_lower:
        return LEXER_INVALID_CHAR
    if "unclosed string" in msg_lower or "unterminated string" in msg_lower:
        return LEXER_UNCLOSED_STRING
    if "invalid number" in msg_lower or "malformed number" in msg_lower:
        return LEXER_INVALID_NUMBER
    if "encoding" in msg_lower or "decode" in msg_lower:
        return LEXER_ENCODING_ERROR

    # Parser errors - grammar-level issues
    if "missing semicolon" in msg_lower:
        return PARSER_MISSING_SEMICOLON
    if "unexpected eof" in msg_lower or "unexpected end" in msg_lower:
        return PARSER_UNEXPECTED_EOF
    if "unmatched" in msg_lower and any(
        c in msg_lower for c in ["(", ")", "[", "]", "paren", "bracket"]
    ):
        return PARSER_UNMATCHED_PAREN
    if "invalid declaration" in msg_lower or "malformed declaration" in msg_lower:
        return PARSER_INVALID_DECLARATION
    if "invalid expression" in msg_lower or "malformed expression" in msg_lower:
        return PARSER_INVALID_EXPRESSION
    # Note: "expected...got" pattern is checked after more specific patterns above
    # to avoid false positives from generic messages containing these words
    if "unexpected token" in msg_lower or ("expected" in msg_lower and "got" in msg_lower):
        return PARSER_UNEXPECTED_TOKEN

    # Semantic errors - meaning-level issues
    if "incompatible domains" in msg_lower or "domain error" in msg_lower:
        return SEMANTIC_DOMAIN_ERROR
    if "duplicate definition" in msg_lower or "already defined" in msg_lower:
        return SEMANTIC_DUPLICATE_DEF
    if "type mismatch" in msg_lower or "incompatible types" in msg_lower:
        return SEMANTIC_TYPE_MISMATCH
    if (
        "not defined" in msg_lower or "undefined" in msg_lower
    ) and "not defined by any equation" not in msg_lower:
        return SEMANTIC_UNDEFINED_SYMBOL

    # Include errors
    if "include" in msg_lower:
        if "circular" in msg_lower:
            return INCLUDE_CIRCULAR
        if "not found" in msg_lower or "could not" in msg_lower:
            return INCLUDE_FILE_NOT_FOUND

    # Timeout
    if "timeout" in msg_lower:
        return TIMEOUT

    # Fallback for generic syntax/parse errors that don't match specific patterns
    # These should be categorized as internal_error since they don't fit the schema categories
    return INTERNAL_ERROR


# =============================================================================
# Translation Error Categorization
# =============================================================================


def categorize_translate_error(error_message: str) -> str:
    """Categorize a translation error into the refined taxonomy.

    This function analyzes the error message to determine the specific
    error category from the 13 translation error categories.

    Args:
        error_message: The error message string from the translator

    Returns:
        Error category string from TRANSLATE_ERROR_CATEGORIES or INTERNAL_ERROR

    Examples:
        >>> categorize_translate_error("Differentiation not yet implemented for function 'card'")
        'diff_unsupported_func'
        >>> categorize_translate_error("Objective variable 'f' is not defined by any equation")
        'model_no_objective_def'
    """
    if not error_message:
        return INTERNAL_ERROR

    msg_lower = error_message.lower()

    # Timeout first
    if "timeout" in msg_lower:
        return TIMEOUT

    # Differentiation errors
    if "differentiation not yet implemented for function" in msg_lower:
        return DIFF_UNSUPPORTED_FUNC
    if "chain rule" in msg_lower:
        return DIFF_CHAIN_RULE_ERROR
    if "numerical" in msg_lower and "differentiation" in msg_lower:
        return DIFF_NUMERICAL_ERROR

    # Model structure errors
    if "objective variable" in msg_lower and "not defined by any equation" in msg_lower:
        return MODEL_NO_OBJECTIVE_DEF
    if "incompatible domains" in msg_lower:
        return MODEL_DOMAIN_MISMATCH
    if "missing bounds" in msg_lower or "bounds missing" in msg_lower:
        return MODEL_MISSING_BOUNDS

    # Unsupported construct errors
    if "indexoffset not yet supported" in msg_lower:
        return UNSUP_INDEX_OFFSET
    if "dollarconditional" in msg_lower or "dollar conditional" in msg_lower:
        return UNSUP_DOLLAR_COND
    if "unknown expression type" in msg_lower:
        return UNSUP_EXPRESSION_TYPE
    # Use word boundary for "sos" to avoid matching words like "those", "also"
    if re.search(r"\bsos[12]?\b", msg_lower) or "special ordered" in msg_lower:
        return UNSUP_SPECIAL_ORDERED

    # Code generation errors - check specific patterns before general numerical
    if "equation generation" in msg_lower or "generating equation" in msg_lower:
        return CODEGEN_EQUATION_ERROR
    if "variable generation" in msg_lower or "generating variable" in msg_lower:
        return CODEGEN_VARIABLE_ERROR

    # Check for numerical errors with word boundaries to avoid false positives
    # "inf" appears in words like "infeasible", "information", "infinite"
    if "numerical error" in msg_lower:
        return CODEGEN_NUMERICAL_ERROR
    if re.search(r"\bnan\b", msg_lower) and "differentiation" not in msg_lower:
        return CODEGEN_NUMERICAL_ERROR
    if re.search(r"\b-?inf\b", msg_lower) and "differentiation" not in msg_lower:
        return CODEGEN_NUMERICAL_ERROR

    return INTERNAL_ERROR


# =============================================================================
# Solve Outcome Categorization
# =============================================================================


def categorize_solve_outcome(
    nlp_solver_status: int | None,
    nlp_model_status: int | None,
    mcp_solver_status: int | None,
    mcp_model_status: int | None,
    objective_match: bool | None,
) -> str:
    """Categorize solve result based on status codes and comparison.

    This function determines the outcome category based on solver status,
    model status, and objective comparison results.

    GAMS Solver Status Codes:
        1 = Normal completion
        2 = Iteration limit
        3 = Time limit
        4 = Terminated by solver
        5 = Evaluation errors
        7 = License error

    GAMS Model Status Codes:
        1 = Optimal
        2 = Locally optimal
        3 = Unbounded
        4 = Infeasible
        5 = Locally infeasible

    Args:
        nlp_solver_status: NLP solver status code (from convexity verification)
        nlp_model_status: NLP model status code
        mcp_solver_status: MCP solver status code (from PATH)
        mcp_model_status: MCP model status code
        objective_match: True if objectives match within tolerance, False if not,
                        None if comparison not performed

    Returns:
        Outcome category string from SOLVE_OUTCOME_CATEGORIES

    Examples:
        >>> categorize_solve_outcome(1, 1, 1, 1, True)
        'compare_objective_match'
        >>> categorize_solve_outcome(1, 1, 2, 1, None)
        'path_solve_iteration_limit'
    """
    # Handle missing NLP data
    if nlp_solver_status is None or nlp_model_status is None:
        return COMPARE_NLP_FAILED

    # Handle missing MCP data
    if mcp_solver_status is None or mcp_model_status is None:
        return COMPARE_MCP_FAILED

    # Check NLP solver status first
    if nlp_solver_status != 1:
        return COMPARE_NLP_FAILED

    # Check MCP/PATH solver status
    if mcp_solver_status != 1:
        if mcp_solver_status == 2:
            return PATH_SOLVE_ITERATION_LIMIT
        if mcp_solver_status == 3:
            return PATH_SOLVE_TIME_LIMIT
        if mcp_solver_status == 4:
            return PATH_SOLVE_TERMINATED
        if mcp_solver_status == 5:
            return PATH_SOLVE_EVAL_ERROR
        if mcp_solver_status == 7:
            return PATH_SOLVE_LICENSE
        return COMPARE_MCP_FAILED

    # Both solvers completed normally - check model status
    nlp_optimal = nlp_model_status in (1, 2)
    mcp_optimal = mcp_model_status in (1, 2)
    nlp_infeasible = nlp_model_status in (4, 5)
    mcp_infeasible = mcp_model_status in (4, 5)
    mcp_unbounded = mcp_model_status == 3

    # Both optimal - compare objectives
    if nlp_optimal and mcp_optimal:
        if objective_match is True:
            return COMPARE_OBJECTIVE_MATCH
        elif objective_match is False:
            return COMPARE_OBJECTIVE_MISMATCH
        else:
            # objective_match is None - comparison not performed or unavailable
            return COMPARE_STATUS_MISMATCH

    # Both infeasible
    if nlp_infeasible and mcp_infeasible:
        return COMPARE_BOTH_INFEASIBLE

    # MCP-specific model status outcomes
    if mcp_infeasible:
        return MODEL_INFEASIBLE
    if mcp_unbounded:
        return MODEL_UNBOUNDED

    # Status mismatch (different model statuses)
    if nlp_optimal != mcp_optimal:
        return COMPARE_STATUS_MISMATCH

    # Fallback for unexpected combinations
    return COMPARE_STATUS_MISMATCH


def categorize_path_solver_status(solver_status: int) -> str:
    """Categorize PATH solver status code into outcome category.

    This is a helper function for categorizing just the PATH solver
    status without considering the full comparison context.

    Args:
        solver_status: GAMS solver status code

    Returns:
        Outcome category for the solver status
    """
    status_map = {
        1: PATH_SOLVE_NORMAL,
        2: PATH_SOLVE_ITERATION_LIMIT,
        3: PATH_SOLVE_TIME_LIMIT,
        4: PATH_SOLVE_TERMINATED,
        5: PATH_SOLVE_EVAL_ERROR,
        7: PATH_SOLVE_LICENSE,
    }
    return status_map.get(solver_status, COMPARE_MCP_FAILED)


def categorize_model_status(model_status: int) -> str:
    """Categorize GAMS model status code into outcome category.

    This is a helper function for categorizing just the model status.

    Args:
        model_status: GAMS model status code

    Returns:
        Outcome category for the model status
    """
    if model_status == 1:
        return MODEL_OPTIMAL
    if model_status == 2:
        return MODEL_LOCALLY_OPTIMAL
    if model_status == 3:
        return MODEL_UNBOUNDED
    if model_status in (4, 5):
        return MODEL_INFEASIBLE
    return COMPARE_MCP_FAILED


# =============================================================================
# Migration Helpers
# =============================================================================


def migrate_parse_category(old_category: str, error_message: str) -> tuple[str, str]:
    """Migrate a Sprint 14 parse error category to Sprint 15 taxonomy.

    Args:
        old_category: The Sprint 14 category
        error_message: The original error message

    Returns:
        Tuple of (new_category, old_category) for storing both
    """
    # Direct mappings that don't need message analysis
    direct_map = {
        "missing_include": INCLUDE_FILE_NOT_FOUND,
        "internal_error": INTERNAL_ERROR,
        "timeout": TIMEOUT,
    }

    if old_category in direct_map:
        return direct_map[old_category], old_category

    # Categories that need message re-analysis
    new_category = categorize_parse_error(error_message)
    return new_category, old_category


def migrate_translate_category(old_category: str, error_message: str) -> tuple[str, str]:
    """Migrate a Sprint 14 translation error category to Sprint 15 taxonomy.

    Args:
        old_category: The Sprint 14 category
        error_message: The original error message

    Returns:
        Tuple of (new_category, old_category) for storing both
    """
    # Direct mappings
    direct_map = {
        "internal_error": INTERNAL_ERROR,
        "timeout": TIMEOUT,
    }

    if old_category in direct_map:
        return direct_map[old_category], old_category

    # Categories that need message re-analysis
    new_category = categorize_translate_error(error_message)
    return new_category, old_category
