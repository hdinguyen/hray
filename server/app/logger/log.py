import logging
import sys
from typing import Optional


class CustomFormatter(logging.Formatter):
    """Custom formatter with color coding for log levels"""

    COLORS = {
        logging.DEBUG: '\033[0;36m',    # CYAN
        logging.INFO: '\033[0;32m',     # GREEN
        logging.WARNING: '\033[0;33m',  # YELLOW
        logging.ERROR: '\033[0;31m',    # RED
        logging.CRITICAL: '\033[0;35m', # MAGENTA
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelno)
        if color:
            record.levelname = f"{color}{record.levelname}{self.RESET}"
            record.msg = f"{color}{record.msg}{self.RESET}"
        return super().format(record)

def setup_logger(
    name: str = "app",
    level: int = logging.DEBUG,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Configure and return a logger instance with the specified settings.

    Args:
        name: The name of the logger
        level: The logging level (default: DEBUG)
        log_format: Custom log format string (optional)

    Returns:
        logging.Logger: Configured logger instance
    """
    if log_format is None:
        log_format = '%(asctime)s %(levelname)s [%(name)s] %(message)s'

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers if they already exist
    if not logger.handlers:
        # Console handler with color formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CustomFormatter(log_format))
        logger.addHandler(console_handler)

    return logger

# Create a default logger instance
logger = setup_logger()

# Convenience functions
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return setup_logger(name)

def set_log_level(level: int) -> None:
    """Set the log level for the root logger."""
    logging.getLogger().setLevel(level)
