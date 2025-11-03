"""Configuration loader for nlp2mcp.

Loads default configuration from pyproject.toml [tool.nlp2mcp] section.
Command-line flags override configuration file settings.
"""

from __future__ import annotations

try:
    import tomllib
except ModuleNotFoundError:
    # Python < 3.11: use tomli backport
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]

from pathlib import Path
from typing import Any


def load_config_from_pyproject() -> dict[str, Any]:
    """Load configuration from pyproject.toml.

    Searches for pyproject.toml in the current directory and parent directories.
    Returns the [tool.nlp2mcp] section if found, otherwise returns empty dict.

    Returns:
        Configuration dictionary from [tool.nlp2mcp] section, or empty dict
    """
    # Search for pyproject.toml starting from current directory
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        pyproject_path = parent / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with pyproject_path.open("rb") as f:
                    data = tomllib.load(f)
                    return data.get("tool", {}).get("nlp2mcp", {})
            except (tomllib.TOMLDecodeError, OSError):
                # If we can't parse the file, continue searching
                continue

    # No pyproject.toml found or no [tool.nlp2mcp] section
    return {}


def get_config_value(config: dict[str, Any], key: str, cli_value: Any, default: Any) -> Any:
    """Get configuration value with precedence: CLI > config file > default.

    Args:
        config: Configuration dictionary from pyproject.toml
        key: Configuration key to look up
        cli_value: Value from command-line flag (None if not specified)
        default: Default value if not in CLI or config file

    Returns:
        Configuration value following precedence rules
    """
    # CLI flag takes precedence
    if cli_value is not None:
        return cli_value

    # Then config file
    if key in config:
        return config[key]

    # Finally default
    return default
