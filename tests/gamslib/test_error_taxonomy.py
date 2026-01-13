"""Unit tests for error_taxonomy module.

Tests the categorization functions for parse, translate, and solve outcomes.
Covers all 47 outcome categories with 96 test cases including variants and edge cases.
"""

from __future__ import annotations

from scripts.gamslib.error_taxonomy import (
    ALL_CATEGORIES,
    CODEGEN_EQUATION_ERROR,
    CODEGEN_NUMERICAL_ERROR,
    CODEGEN_VARIABLE_ERROR,
    COMPARE_BOTH_INFEASIBLE,
    COMPARE_MCP_FAILED,
    COMPARE_NLP_FAILED,
    COMPARE_OBJECTIVE_MATCH,
    COMPARE_OBJECTIVE_MISMATCH,
    COMPARE_STATUS_MISMATCH,
    DIFF_CHAIN_RULE_ERROR,
    DIFF_NUMERICAL_ERROR,
    # Translate categories
    DIFF_UNSUPPORTED_FUNC,
    INCLUDE_CIRCULAR,
    INCLUDE_FILE_NOT_FOUND,
    INTERNAL_ERROR,
    LEXER_ENCODING_ERROR,
    # Parse categories
    LEXER_INVALID_CHAR,
    LEXER_INVALID_NUMBER,
    LEXER_UNCLOSED_STRING,
    MODEL_DOMAIN_MISMATCH,
    MODEL_INFEASIBLE,
    MODEL_LOCALLY_OPTIMAL,
    MODEL_MISSING_BOUNDS,
    MODEL_NO_OBJECTIVE_DEF,
    MODEL_OPTIMAL,
    MODEL_UNBOUNDED,
    # Lists
    PARSE_ERROR_CATEGORIES,
    PARSER_INVALID_DECLARATION,
    PARSER_INVALID_EXPRESSION,
    PARSER_MISSING_SEMICOLON,
    PARSER_UNEXPECTED_EOF,
    PARSER_UNEXPECTED_TOKEN,
    PARSER_UNMATCHED_PAREN,
    PATH_SOLVE_EVAL_ERROR,
    PATH_SOLVE_ITERATION_LIMIT,
    PATH_SOLVE_LICENSE,
    # Solve categories
    PATH_SOLVE_NORMAL,
    PATH_SOLVE_TERMINATED,
    PATH_SOLVE_TIME_LIMIT,
    SEMANTIC_DOMAIN_ERROR,
    SEMANTIC_DUPLICATE_DEF,
    SEMANTIC_TYPE_MISMATCH,
    SEMANTIC_UNDEFINED_SYMBOL,
    SOLVE_OUTCOME_CATEGORIES,
    # Generic
    TIMEOUT,
    TRANSLATE_ERROR_CATEGORIES,
    UNSUP_DOLLAR_COND,
    UNSUP_EXPRESSION_TYPE,
    UNSUP_INDEX_OFFSET,
    UNSUP_SPECIAL_ORDERED,
    categorize_model_status,
    # Functions
    categorize_parse_error,
    categorize_path_solver_status,
    categorize_solve_outcome,
    categorize_translate_error,
    migrate_parse_category,
    migrate_translate_category,
)

# =============================================================================
# Parse Error Categorization Tests
# =============================================================================


class TestCategorizeParseError:
    """Tests for categorize_parse_error function."""

    # Lexer errors
    def test_lexer_invalid_char(self) -> None:
        """Test detection of invalid character errors."""
        msg = "Error: Parse error at line 18, column 24: Unexpected character: '-'"
        assert categorize_parse_error(msg) == LEXER_INVALID_CHAR

    def test_lexer_invalid_char_variant(self) -> None:
        """Test another invalid character pattern."""
        msg = "Unexpected character: '3' at position 16"
        assert categorize_parse_error(msg) == LEXER_INVALID_CHAR

    def test_lexer_unclosed_string(self) -> None:
        """Test detection of unclosed string errors."""
        msg = "Error: Parse error at line 5, column 10: Unclosed string literal"
        assert categorize_parse_error(msg) == LEXER_UNCLOSED_STRING

    def test_lexer_unterminated_string(self) -> None:
        """Test unterminated string variant."""
        msg = "Unterminated string at line 42"
        assert categorize_parse_error(msg) == LEXER_UNCLOSED_STRING

    def test_lexer_invalid_number(self) -> None:
        """Test detection of invalid number errors."""
        msg = "Invalid number format: 1.2.3"
        assert categorize_parse_error(msg) == LEXER_INVALID_NUMBER

    def test_lexer_malformed_number(self) -> None:
        """Test malformed number variant."""
        msg = "Malformed number literal at line 10"
        assert categorize_parse_error(msg) == LEXER_INVALID_NUMBER

    def test_lexer_encoding_error(self) -> None:
        """Test detection of encoding errors."""
        msg = "Character encoding error: invalid UTF-8 sequence"
        assert categorize_parse_error(msg) == LEXER_ENCODING_ERROR

    def test_lexer_decode_error(self) -> None:
        """Test decode error variant."""
        msg = "Failed to decode file: UnicodeDecodeError"
        assert categorize_parse_error(msg) == LEXER_ENCODING_ERROR

    # Parser errors
    def test_parser_missing_semicolon(self) -> None:
        """Test detection of missing semicolon errors."""
        msg = "Missing semicolon at end of line 42"
        assert categorize_parse_error(msg) == PARSER_MISSING_SEMICOLON

    def test_parser_unexpected_eof(self) -> None:
        """Test detection of unexpected EOF errors."""
        msg = "Unexpected EOF while parsing model"
        assert categorize_parse_error(msg) == PARSER_UNEXPECTED_EOF

    def test_parser_unexpected_end(self) -> None:
        """Test unexpected end variant."""
        msg = "Unexpected end of file"
        assert categorize_parse_error(msg) == PARSER_UNEXPECTED_EOF

    def test_parser_unmatched_paren(self) -> None:
        """Test detection of unmatched parenthesis errors."""
        msg = "Unmatched parenthesis '(' at line 15"
        assert categorize_parse_error(msg) == PARSER_UNMATCHED_PAREN

    def test_parser_unmatched_bracket(self) -> None:
        """Test unmatched bracket variant."""
        msg = "Unmatched bracket ']' found"
        assert categorize_parse_error(msg) == PARSER_UNMATCHED_PAREN

    def test_parser_invalid_declaration(self) -> None:
        """Test detection of invalid declaration errors."""
        msg = "Invalid declaration of parameter 'p'"
        assert categorize_parse_error(msg) == PARSER_INVALID_DECLARATION

    def test_parser_malformed_declaration(self) -> None:
        """Test malformed declaration variant."""
        msg = "Malformed declaration at line 20"
        assert categorize_parse_error(msg) == PARSER_INVALID_DECLARATION

    def test_parser_invalid_expression(self) -> None:
        """Test detection of invalid expression errors."""
        msg = "Invalid expression in equation 'eq1'"
        assert categorize_parse_error(msg) == PARSER_INVALID_EXPRESSION

    def test_parser_malformed_expression(self) -> None:
        """Test malformed expression variant."""
        msg = "Malformed expression at line 30"
        assert categorize_parse_error(msg) == PARSER_INVALID_EXPRESSION

    def test_parser_unexpected_token(self) -> None:
        """Test detection of unexpected token errors."""
        msg = "Unexpected token 'model' - expected ';'"
        assert categorize_parse_error(msg) == PARSER_UNEXPECTED_TOKEN

    def test_parser_expected_got(self) -> None:
        """Test expected/got pattern."""
        msg = "Expected 'identifier' but got 'number'"
        assert categorize_parse_error(msg) == PARSER_UNEXPECTED_TOKEN

    # Semantic errors
    def test_semantic_undefined_symbol(self) -> None:
        """Test detection of undefined symbol errors."""
        msg = "Symbol 'x' is not defined"
        assert categorize_parse_error(msg) == SEMANTIC_UNDEFINED_SYMBOL

    def test_semantic_undefined_variant(self) -> None:
        """Test undefined variant."""
        msg = "Variable 'cost' is undefined"
        assert categorize_parse_error(msg) == SEMANTIC_UNDEFINED_SYMBOL

    def test_semantic_not_equation_exclusion(self) -> None:
        """Test that 'not defined by any equation' is NOT a parse error."""
        # This should fall through to internal_error for parse stage
        # (it's actually a translation error)
        msg = "Objective variable 'f' is not defined by any equation"
        assert categorize_parse_error(msg) == INTERNAL_ERROR

    def test_semantic_type_mismatch(self) -> None:
        """Test detection of type mismatch errors."""
        msg = "Type mismatch in assignment of variable 'x'"
        assert categorize_parse_error(msg) == SEMANTIC_TYPE_MISMATCH

    def test_semantic_type_mismatch_incompatible(self) -> None:
        """Test incompatible types variant."""
        msg = "Incompatible types: scalar and vector cannot be combined"
        assert categorize_parse_error(msg) == SEMANTIC_TYPE_MISMATCH

    def test_semantic_domain_error(self) -> None:
        """Test detection of domain errors."""
        msg = "Incompatible domains for summation"
        assert categorize_parse_error(msg) == SEMANTIC_DOMAIN_ERROR

    def test_semantic_domain_error_variant(self) -> None:
        """Test domain error variant."""
        msg = "Domain error in expression evaluation"
        assert categorize_parse_error(msg) == SEMANTIC_DOMAIN_ERROR

    def test_semantic_duplicate_def(self) -> None:
        """Test detection of duplicate definition errors."""
        msg = "Duplicate definition of set 'i'"
        assert categorize_parse_error(msg) == SEMANTIC_DUPLICATE_DEF

    def test_semantic_already_defined(self) -> None:
        """Test already defined variant."""
        msg = "Symbol 'cost' is already defined"
        assert categorize_parse_error(msg) == SEMANTIC_DUPLICATE_DEF

    # Include errors
    def test_include_file_not_found(self) -> None:
        """Test detection of include file not found errors."""
        msg = "Include file 'data.gms' not found"
        assert categorize_parse_error(msg) == INCLUDE_FILE_NOT_FOUND

    def test_include_could_not(self) -> None:
        """Test could not include variant."""
        msg = "Could not include file 'params.inc'"
        assert categorize_parse_error(msg) == INCLUDE_FILE_NOT_FOUND

    def test_include_circular(self) -> None:
        """Test detection of circular include errors."""
        msg = "Circular include detected: a.gms -> b.gms -> a.gms"
        assert categorize_parse_error(msg) == INCLUDE_CIRCULAR

    # Edge cases
    def test_timeout(self) -> None:
        """Test timeout detection."""
        msg = "Parse timeout after 60 seconds"
        assert categorize_parse_error(msg) == TIMEOUT

    def test_empty_message(self) -> None:
        """Test empty error message."""
        assert categorize_parse_error("") == INTERNAL_ERROR

    def test_unknown_error(self) -> None:
        """Test unknown error falls back to internal_error."""
        msg = "Some completely unknown error type"
        assert categorize_parse_error(msg) == INTERNAL_ERROR


# =============================================================================
# Translate Error Categorization Tests
# =============================================================================


class TestCategorizeTranslateError:
    """Tests for categorize_translate_error function."""

    # Differentiation errors
    def test_diff_unsupported_func(self) -> None:
        """Test detection of unsupported function errors."""
        msg = "Differentiation not yet implemented for function 'card'"
        assert categorize_translate_error(msg) == DIFF_UNSUPPORTED_FUNC

    def test_diff_unsupported_func_gamma(self) -> None:
        """Test gamma function variant."""
        msg = "Differentiation not yet implemented for function 'gamma'"
        assert categorize_translate_error(msg) == DIFF_UNSUPPORTED_FUNC

    def test_diff_chain_rule_error(self) -> None:
        """Test detection of chain rule errors."""
        msg = "Error applying chain rule to nested expression"
        assert categorize_translate_error(msg) == DIFF_CHAIN_RULE_ERROR

    def test_diff_numerical_error(self) -> None:
        """Test detection of numerical errors in differentiation."""
        msg = "Numerical error during differentiation: NaN result"
        assert categorize_translate_error(msg) == DIFF_NUMERICAL_ERROR

    # Model structure errors
    def test_model_no_objective_def(self) -> None:
        """Test detection of missing objective definition."""
        msg = "Objective variable 'f' is not defined by any equation"
        assert categorize_translate_error(msg) == MODEL_NO_OBJECTIVE_DEF

    def test_model_domain_mismatch(self) -> None:
        """Test detection of domain mismatch errors."""
        msg = "Incompatible domains for variable indexing"
        assert categorize_translate_error(msg) == MODEL_DOMAIN_MISMATCH

    def test_model_missing_bounds(self) -> None:
        """Test detection of missing bounds errors."""
        msg = "Variable 'x' has missing bounds specification"
        assert categorize_translate_error(msg) == MODEL_MISSING_BOUNDS

    def test_model_bounds_missing_variant(self) -> None:
        """Test bounds missing variant."""
        msg = "Error: bounds missing for variable 'y'"
        assert categorize_translate_error(msg) == MODEL_MISSING_BOUNDS

    # Unsupported construct errors
    def test_unsup_index_offset(self) -> None:
        """Test detection of index offset errors."""
        msg = "IndexOffset not yet supported in this context"
        assert categorize_translate_error(msg) == UNSUP_INDEX_OFFSET

    def test_unsup_dollar_cond(self) -> None:
        """Test detection of dollar conditional errors."""
        msg = "DollarConditional in equation not supported"
        assert categorize_translate_error(msg) == UNSUP_DOLLAR_COND

    def test_unsup_dollar_cond_variant(self) -> None:
        """Test dollar conditional variant."""
        msg = "Dollar conditional $(...) not supported"
        assert categorize_translate_error(msg) == UNSUP_DOLLAR_COND

    def test_unsup_expression_type(self) -> None:
        """Test detection of unknown expression type errors."""
        msg = "Unknown expression type: FunctionCall"
        assert categorize_translate_error(msg) == UNSUP_EXPRESSION_TYPE

    def test_unsup_special_ordered(self) -> None:
        """Test detection of SOS errors."""
        msg = "Special Ordered Sets (SOS) not supported"
        assert categorize_translate_error(msg) == UNSUP_SPECIAL_ORDERED

    def test_unsup_sos_variant(self) -> None:
        """Test SOS variant."""
        msg = "SOS1 constraints not implemented"
        assert categorize_translate_error(msg) == UNSUP_SPECIAL_ORDERED

    # Code generation errors
    def test_codegen_equation_error(self) -> None:
        """Test detection of equation generation errors."""
        msg = "Failed during equation generation: invalid index"
        assert categorize_translate_error(msg) == CODEGEN_EQUATION_ERROR

    def test_codegen_variable_error(self) -> None:
        """Test detection of variable generation errors."""
        msg = "Error in variable generation: unknown type"
        assert categorize_translate_error(msg) == CODEGEN_VARIABLE_ERROR

    def test_codegen_numerical_error(self) -> None:
        """Test detection of numerical errors in codegen."""
        msg = "Numerical error in parameter: Invalid value"
        assert categorize_translate_error(msg) == CODEGEN_NUMERICAL_ERROR

    def test_codegen_nan(self) -> None:
        """Test NaN detection."""
        msg = "Parameter value is NaN"
        assert categorize_translate_error(msg) == CODEGEN_NUMERICAL_ERROR

    def test_codegen_inf(self) -> None:
        """Test Inf detection."""
        msg = "Value is -Inf which is invalid"
        assert categorize_translate_error(msg) == CODEGEN_NUMERICAL_ERROR

    # Edge cases
    def test_timeout(self) -> None:
        """Test timeout detection."""
        msg = "Translation timeout after 60 seconds"
        assert categorize_translate_error(msg) == TIMEOUT

    def test_empty_message(self) -> None:
        """Test empty error message."""
        assert categorize_translate_error("") == INTERNAL_ERROR

    def test_unknown_error(self) -> None:
        """Test unknown error falls back to internal_error."""
        msg = "Some completely unknown translation error"
        assert categorize_translate_error(msg) == INTERNAL_ERROR


# =============================================================================
# Solve Outcome Categorization Tests
# =============================================================================


class TestCategorizeSolveOutcome:
    """Tests for categorize_solve_outcome function."""

    def test_objective_match(self) -> None:
        """Test successful objective match."""
        result = categorize_solve_outcome(1, 1, 1, 1, True)
        assert result == COMPARE_OBJECTIVE_MATCH

    def test_objective_mismatch(self) -> None:
        """Test objective mismatch."""
        result = categorize_solve_outcome(1, 1, 1, 1, False)
        assert result == COMPARE_OBJECTIVE_MISMATCH

    def test_locally_optimal_match(self) -> None:
        """Test locally optimal solutions matching."""
        result = categorize_solve_outcome(1, 2, 1, 2, True)
        assert result == COMPARE_OBJECTIVE_MATCH

    def test_nlp_failed(self) -> None:
        """Test NLP solver failure detection."""
        result = categorize_solve_outcome(5, 1, 1, 1, None)
        assert result == COMPARE_NLP_FAILED

    def test_nlp_none(self) -> None:
        """Test missing NLP data."""
        result = categorize_solve_outcome(None, None, 1, 1, None)
        assert result == COMPARE_NLP_FAILED

    def test_mcp_none(self) -> None:
        """Test missing MCP data."""
        result = categorize_solve_outcome(1, 1, None, None, None)
        assert result == COMPARE_MCP_FAILED

    def test_path_iteration_limit(self) -> None:
        """Test PATH iteration limit."""
        result = categorize_solve_outcome(1, 1, 2, 1, None)
        assert result == PATH_SOLVE_ITERATION_LIMIT

    def test_path_time_limit(self) -> None:
        """Test PATH time limit."""
        result = categorize_solve_outcome(1, 1, 3, 1, None)
        assert result == PATH_SOLVE_TIME_LIMIT

    def test_path_terminated(self) -> None:
        """Test PATH terminated."""
        result = categorize_solve_outcome(1, 1, 4, 1, None)
        assert result == PATH_SOLVE_TERMINATED

    def test_path_eval_error(self) -> None:
        """Test PATH evaluation error."""
        result = categorize_solve_outcome(1, 1, 5, 1, None)
        assert result == PATH_SOLVE_EVAL_ERROR

    def test_path_license(self) -> None:
        """Test PATH license error."""
        result = categorize_solve_outcome(1, 1, 7, 1, None)
        assert result == PATH_SOLVE_LICENSE

    def test_mcp_failed_unknown_status(self) -> None:
        """Test unknown MCP solver status."""
        result = categorize_solve_outcome(1, 1, 99, 1, None)
        assert result == COMPARE_MCP_FAILED

    def test_both_infeasible(self) -> None:
        """Test both models infeasible."""
        result = categorize_solve_outcome(1, 4, 1, 4, None)
        assert result == COMPARE_BOTH_INFEASIBLE

    def test_both_locally_infeasible(self) -> None:
        """Test both models locally infeasible."""
        result = categorize_solve_outcome(1, 5, 1, 5, None)
        assert result == COMPARE_BOTH_INFEASIBLE

    def test_mcp_infeasible(self) -> None:
        """Test MCP infeasible when NLP optimal."""
        result = categorize_solve_outcome(1, 1, 1, 4, None)
        assert result == MODEL_INFEASIBLE

    def test_mcp_unbounded(self) -> None:
        """Test MCP unbounded."""
        result = categorize_solve_outcome(1, 1, 1, 3, None)
        assert result == MODEL_UNBOUNDED

    def test_status_mismatch_nlp_optimal_mcp_not(self) -> None:
        """Test status mismatch: NLP optimal, MCP not."""
        result = categorize_solve_outcome(1, 1, 1, 6, None)
        assert result == COMPARE_STATUS_MISMATCH

    def test_no_comparison_performed(self) -> None:
        """Test when comparison is None but both optimal."""
        result = categorize_solve_outcome(1, 1, 1, 1, None)
        assert result == COMPARE_STATUS_MISMATCH


class TestCategorizePathSolverStatus:
    """Tests for categorize_path_solver_status helper function."""

    def test_normal(self) -> None:
        assert categorize_path_solver_status(1) == PATH_SOLVE_NORMAL

    def test_iteration_limit(self) -> None:
        assert categorize_path_solver_status(2) == PATH_SOLVE_ITERATION_LIMIT

    def test_time_limit(self) -> None:
        assert categorize_path_solver_status(3) == PATH_SOLVE_TIME_LIMIT

    def test_terminated(self) -> None:
        assert categorize_path_solver_status(4) == PATH_SOLVE_TERMINATED

    def test_eval_error(self) -> None:
        assert categorize_path_solver_status(5) == PATH_SOLVE_EVAL_ERROR

    def test_license(self) -> None:
        assert categorize_path_solver_status(7) == PATH_SOLVE_LICENSE

    def test_unknown(self) -> None:
        assert categorize_path_solver_status(99) == COMPARE_MCP_FAILED


class TestCategorizeModelStatus:
    """Tests for categorize_model_status helper function."""

    def test_optimal(self) -> None:
        assert categorize_model_status(1) == MODEL_OPTIMAL

    def test_locally_optimal(self) -> None:
        assert categorize_model_status(2) == MODEL_LOCALLY_OPTIMAL

    def test_unbounded(self) -> None:
        assert categorize_model_status(3) == MODEL_UNBOUNDED

    def test_infeasible(self) -> None:
        assert categorize_model_status(4) == MODEL_INFEASIBLE

    def test_locally_infeasible(self) -> None:
        assert categorize_model_status(5) == MODEL_INFEASIBLE

    def test_unknown(self) -> None:
        assert categorize_model_status(99) == COMPARE_MCP_FAILED


# =============================================================================
# Migration Helper Tests
# =============================================================================


class TestMigrateCategories:
    """Tests for category migration helpers."""

    def test_migrate_parse_direct_mapping(self) -> None:
        """Test direct mapping for internal_error."""
        new_cat, old_cat = migrate_parse_category("internal_error", "Some error")
        assert new_cat == INTERNAL_ERROR
        assert old_cat == "internal_error"

    def test_migrate_parse_missing_include(self) -> None:
        """Test direct mapping for missing_include."""
        new_cat, old_cat = migrate_parse_category("missing_include", "Include not found")
        assert new_cat == INCLUDE_FILE_NOT_FOUND
        assert old_cat == "missing_include"

    def test_migrate_parse_syntax_error(self) -> None:
        """Test re-analysis of syntax_error."""
        msg = "Error: Parse error at line 18: Unexpected character: '-'"
        new_cat, old_cat = migrate_parse_category("syntax_error", msg)
        assert new_cat == LEXER_INVALID_CHAR
        assert old_cat == "syntax_error"

    def test_migrate_translate_direct_mapping(self) -> None:
        """Test direct mapping for timeout."""
        new_cat, old_cat = migrate_translate_category("timeout", "Timeout!")
        assert new_cat == TIMEOUT
        assert old_cat == "timeout"

    def test_migrate_translate_unsupported(self) -> None:
        """Test re-analysis of unsupported_feature."""
        msg = "Differentiation not yet implemented for function 'card'"
        new_cat, old_cat = migrate_translate_category("unsupported_feature", msg)
        assert new_cat == DIFF_UNSUPPORTED_FUNC
        assert old_cat == "unsupported_feature"


# =============================================================================
# Category List Tests
# =============================================================================


class TestCategoryLists:
    """Tests for category list constants."""

    def test_parse_category_count(self) -> None:
        """Test that there are 16 parse error categories."""
        assert len(PARSE_ERROR_CATEGORIES) == 16

    def test_translate_category_count(self) -> None:
        """Test that there are 13 translate error categories."""
        assert len(TRANSLATE_ERROR_CATEGORIES) == 13

    def test_solve_category_count(self) -> None:
        """Test that there are 16 solve outcome categories."""
        assert len(SOLVE_OUTCOME_CATEGORIES) == 16

    def test_all_categories_count(self) -> None:
        """Test that there are 45 + 2 (timeout, internal_error) = 47 total categories."""
        # 16 parse + 13 translate + 16 solve + 2 generic = 47
        assert len(ALL_CATEGORIES) == 47

    def test_no_duplicate_categories(self) -> None:
        """Test that there are no duplicate category names."""
        assert len(ALL_CATEGORIES) == len(set(ALL_CATEGORIES))

    def test_categories_are_strings(self) -> None:
        """Test that all categories are strings."""
        for cat in ALL_CATEGORIES:
            assert isinstance(cat, str)
            assert len(cat) > 0
