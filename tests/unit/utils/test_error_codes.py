"""Unit tests for error_codes module."""

from src.utils.error_codes import (
    ERROR_REGISTRY,
    ErrorInfo,
    get_all_error_codes,
    get_error_info,
)


class TestErrorInfo:
    """Test ErrorInfo dataclass."""

    def test_error_info_doc_url(self):
        """Test documentation URL generation."""
        error = ErrorInfo(
            code="E001",
            level="Error",
            title="Undefined variable",
            doc_anchor="e001-undefined-variable",
        )

        url = error.doc_url()
        assert "docs/errors/README.md#e001-undefined-variable" in url
        assert url.startswith("https://")

    def test_warning_info_doc_url(self):
        """Test documentation URL for warnings."""
        warning = ErrorInfo(
            code="W301",
            level="Warning",
            title="Nonlinear equality",
            doc_anchor="w301-nonlinear-equality",
        )

        url = warning.doc_url()
        assert "docs/errors/README.md#w301-nonlinear-equality" in url


class TestErrorRegistry:
    """Test error registry functionality."""

    def test_registry_contains_validation_errors(self):
        """Test that registry contains validation error codes."""
        assert "E001" in ERROR_REGISTRY  # Undefined variable
        assert "E002" in ERROR_REGISTRY  # Undefined equation
        assert "E003" in ERROR_REGISTRY  # Type mismatch

    def test_registry_contains_syntax_errors(self):
        """Test that registry contains syntax error codes."""
        assert "E101" in ERROR_REGISTRY  # General syntax error

    def test_registry_contains_convexity_warnings(self):
        """Test that registry contains convexity warning codes."""
        assert "W301" in ERROR_REGISTRY  # Nonlinear equality
        assert "W302" in ERROR_REGISTRY  # Trigonometric function
        assert "W303" in ERROR_REGISTRY  # Bilinear term
        assert "W304" in ERROR_REGISTRY  # Division/quotient
        assert "W305" in ERROR_REGISTRY  # Odd-power polynomial

    def test_all_registry_entries_have_required_fields(self):
        """Test that all registry entries have complete metadata."""
        for code, info in ERROR_REGISTRY.items():
            assert info.code == code
            assert info.level in ["Error", "Warning", "Info"]
            assert len(info.title) > 0
            assert len(info.doc_anchor) > 0

    def test_error_codes_match_level_prefix(self):
        """Test that error codes match their level prefix."""
        for code, info in ERROR_REGISTRY.items():
            if info.level == "Error":
                assert code.startswith("E")
            elif info.level == "Warning":
                assert code.startswith("W")
            elif info.level == "Info":
                assert code.startswith("I")


class TestGetErrorInfo:
    """Test get_error_info function."""

    def test_get_existing_error(self):
        """Test retrieving an existing error code."""
        info = get_error_info("E001")
        assert info is not None
        assert info.code == "E001"
        assert info.title == "Undefined variable"
        assert info.level == "Error"

    def test_get_existing_warning(self):
        """Test retrieving an existing warning code."""
        info = get_error_info("W301")
        assert info is not None
        assert info.code == "W301"
        assert info.title == "Nonlinear equality may be nonconvex"
        assert info.level == "Warning"

    def test_get_nonexistent_error(self):
        """Test retrieving a non-existent error code."""
        info = get_error_info("E999")
        assert info is None

    def test_get_error_info_returns_same_object(self):
        """Test that get_error_info returns the same registry object."""
        info1 = get_error_info("E001")
        info2 = get_error_info("E001")
        assert info1 is info2  # Same object from registry


class TestGetAllErrorCodes:
    """Test get_all_error_codes function."""

    def test_returns_list(self):
        """Test that function returns a list."""
        codes = get_all_error_codes()
        assert isinstance(codes, list)

    def test_returns_sorted_codes(self):
        """Test that codes are sorted."""
        codes = get_all_error_codes()
        assert codes == sorted(codes)

    def test_includes_all_registry_codes(self):
        """Test that all registry codes are included."""
        codes = get_all_error_codes()
        for code in ERROR_REGISTRY.keys():
            assert code in codes

    def test_minimum_code_count(self):
        """Test that we have at least the Sprint 6 error codes."""
        codes = get_all_error_codes()
        # Sprint 6 should have at least 9 codes
        # E001, E002, E003, E101, W301, W302, W303, W304, W305
        assert len(codes) >= 9


class TestErrorCodeIntegrationWithFormatter:
    """Test integration between error codes and error formatter."""

    def test_error_info_can_be_used_in_formatted_error(self):
        """Test that ErrorInfo integrates with error formatter."""
        from src.utils.error_formatter import FormattedError

        error_info = get_error_info("E001")
        assert error_info is not None

        # Create a formatted error using the error info
        formatted = FormattedError(
            level=error_info.level,
            title=f"{error_info.code}: {error_info.title}",
            context=None,
            explanation="Variable 'x' is used but not declared.",
            action="Add 'x' to the Variables section.",
            doc_link=error_info.doc_url(),
        )

        output = formatted.format()
        assert error_info.code in output
        assert error_info.title in output
        assert error_info.doc_url() in output

    def test_warning_info_can_be_used_in_formatted_warning(self):
        """Test that warning ErrorInfo integrates with error formatter."""
        from src.utils.error_formatter import FormattedError

        warning_info = get_error_info("W301")
        assert warning_info is not None

        # Create a formatted warning using the warning info
        formatted = FormattedError(
            level=warning_info.level,
            title=f"{warning_info.code}: {warning_info.title}",
            context=None,
            explanation="Nonlinear equality may be nonconvex.",
            action="Consider using inequality constraint instead.",
            doc_link=warning_info.doc_url(),
        )

        output = formatted.format()
        assert warning_info.code in output
        assert warning_info.title in output
        assert warning_info.doc_url() in output
