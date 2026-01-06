"""Shared utility functions for GAMSLIB scripts."""

from __future__ import annotations

import logging
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent

logger = logging.getLogger(__name__)


def get_nlp2mcp_version() -> str:
    """Get the current nlp2mcp version from package metadata.

    Returns:
        Version string (e.g., "0.1.0") or "unknown" if not found
    """
    try:
        # Try importlib.metadata first (Python 3.8+)
        from importlib.metadata import version

        return version("nlp2mcp")
    except Exception as e:
        logger.debug(f"importlib.metadata version lookup failed: {e}")

    # Fallback: try reading from pyproject.toml
    try:
        pyproject = PROJECT_ROOT / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text()
            for line in content.splitlines():
                if line.strip().startswith("version"):
                    # Parse: version = "0.1.0"
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        ver = parts[1].strip().strip('"').strip("'")
                        return ver
    except Exception as e:
        logger.debug(f"pyproject.toml version lookup failed: {e}")

    return "unknown"
