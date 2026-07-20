"""
shared/logger.py

Centralized logger factory for the AMS Incident Agent.

Format: <timestamp> | <level> | <logger_name> | <message>

Usage:
    from shared.logger import get_logger
    logger = get_logger("module.name")
"""
import logging
import sys


def get_logger(name: str) -> logging.Logger:

    # Reuse existing logger if already configured for this name
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    # Minimum log level — INFO and above will be shown
    logger.setLevel(logging.INFO)

    # Consistent format across all modules
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Write to stdout so logs appear in Render / container logs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # Prevent duplicate output from root logger
    logger.propagate = False

    return logger
