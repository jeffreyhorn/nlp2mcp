"""Tests for configuration validation."""

import pytest

from src.config import Config


class TestConfigValidation:
    """Test Config class validation."""

    def test_default_config(self):
        """Test that default config is valid."""
        config = Config()
        assert config.smooth_abs is False
        assert config.smooth_abs_epsilon == 1e-6
        assert config.scale == "none"
        assert config.simplification == "advanced"

    def test_valid_simplification_modes(self):
        """Test that all valid simplification modes are accepted."""
        for mode in ["none", "basic", "advanced"]:
            config = Config(simplification=mode)
            assert config.simplification == mode

    def test_invalid_simplification_mode(self):
        """Test that invalid simplification mode raises error."""
        with pytest.raises(ValueError, match="simplification must be"):
            Config(simplification="invalid")

    def test_valid_scale_modes(self):
        """Test that all valid scale modes are accepted."""
        for mode in ["none", "auto", "byvar"]:
            config = Config(scale=mode)
            assert config.scale == mode

    def test_invalid_scale_mode(self):
        """Test that invalid scale mode raises error."""
        with pytest.raises(ValueError, match="scale must be"):
            Config(scale="invalid")

    def test_invalid_smooth_abs_epsilon(self):
        """Test that non-positive epsilon raises error."""
        with pytest.raises(ValueError, match="smooth_abs_epsilon must be positive"):
            Config(smooth_abs_epsilon=0)

        with pytest.raises(ValueError, match="smooth_abs_epsilon must be positive"):
            Config(smooth_abs_epsilon=-0.5)

    def test_combined_config(self):
        """Test config with multiple options set."""
        config = Config(
            smooth_abs=True,
            smooth_abs_epsilon=1e-8,
            scale="auto",
            simplification="basic",
        )
        assert config.smooth_abs is True
        assert config.smooth_abs_epsilon == 1e-8
        assert config.scale == "auto"
        assert config.simplification == "basic"
