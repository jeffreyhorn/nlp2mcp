"""Logging configuration for nlp2mcp.

Provides structured logging with verbosity levels:
- 0 (quiet): Errors only
- 1 (normal): Important steps and results
- 2 (verbose): Detailed progress information
- 3+ (very verbose): Debug-level details
"""

from __future__ import annotations

import logging
import sys
from typing import TextIO


class VerbosityFilter(logging.Filter):
    """Filter log messages based on verbosity level.

    Maps verbosity levels to logging levels:
    - 0 (quiet): ERROR and above
    - 1 (normal): WARNING and above
    - 2 (verbose): INFO and above
    - 3+ (very verbose): DEBUG and above
    """

    def __init__(self, verbosity: int = 1):
        super().__init__()
        self.verbosity = verbosity

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record based on verbosity setting.

        Args:
            record: Log record to filter

        Returns:
            True if record should be logged, False otherwise
        """
        if self.verbosity == 0:
            # Quiet mode: errors only
            return record.levelno >= logging.ERROR
        elif self.verbosity == 1:
            # Normal mode: warnings and errors
            return record.levelno >= logging.WARNING
        elif self.verbosity == 2:
            # Verbose mode: info, warnings, and errors
            return record.levelno >= logging.INFO
        else:
            # Very verbose mode: everything including debug
            return record.levelno >= logging.DEBUG


def setup_logging(
    verbosity: int = 1,
    log_file: str | None = None,
    stream: TextIO | None = None,
) -> logging.Logger:
    """Set up logging for nlp2mcp.

    Args:
        verbosity: Verbosity level (0=quiet, 1=normal, 2=verbose, 3+=very verbose)
        log_file: Optional path to log file
        stream: Optional stream for console output (defaults to stderr)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("nlp2mcp")
    logger.setLevel(logging.DEBUG)  # Capture all messages, filter later

    # Remove any existing handlers
    logger.handlers.clear()

    # Console handler
    if stream is None:
        stream = sys.stderr

    console_handler = logging.StreamHandler(stream)
    console_handler.setLevel(logging.DEBUG)

    # Format: simple for normal use, detailed for verbose
    if verbosity >= 3:
        # Very verbose: include timestamp and level
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    elif verbosity >= 2:
        # Verbose: include level
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
    else:
        # Normal/quiet: just the message
        formatter = logging.Formatter("%(message)s")

    console_handler.setFormatter(formatter)
    console_handler.addFilter(VerbosityFilter(verbosity))
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s:%(funcName)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Don't propagate to root logger
    logger.propagate = False

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__ of the calling module)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"nlp2mcp.{name}")
    return logging.getLogger("nlp2mcp")
