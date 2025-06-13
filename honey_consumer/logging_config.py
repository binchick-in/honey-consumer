import logging
import os
import sys


def setup_logging():
    """
    Set up logging for the honey_consumer project.
    Console only, with timestamp, log level, module, and message.
    Log level is set via LOG_LEVEL env var (default: INFO).
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    # Validate log level
    if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        log_level = "INFO"

    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)
