"""
Logging initialization module.
Configures loggers for the application.

Usage:
    from init_logs import auth_logger

    auth_logger.info("User logged in")
    auth_logger.error("Login failed")

To add a new logger:
    1. Add a new setup_logger() call below
    2. Export it in the module
    3. Import and use in your module

Log files are stored in: logs/ (configurable via AI_MESSAGE_LOGS_FOLDER env var)
Log format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
Log rotation: 1MB per file, 50 backup files (50MB total)
"""
import os
import logging
from logging.handlers import RotatingFileHandler

# Get the logs folder path from environment or use default
logs_folder = os.getenv("AI_MESSAGE_LOGS_FOLDER", "logs")
backend_dir = os.path.dirname(os.path.abspath(__file__))
logs_path = os.path.join(backend_dir, "..", logs_folder)
os.makedirs(logs_path, exist_ok=True)


def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with a rotating file handler.
    
    Args:
        name: Logger name
        log_file: Name of the log file
        level: Logging level (default: logging.INFO)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Rotating file handler: max 50MB total (50 files x 1MB each)
    handler = RotatingFileHandler(
        os.path.join(logs_path, log_file),
        maxBytes=1 * 1024 * 1024,  # 1MB per file
        backupCount=50  # 50 files = 50MB max
    )
    handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(handler)
    
    return logger


# =============================================================================
# Application Loggers
# =============================================================================
# Format: <name>_logger = setup_logger(<logger_name>, <log_file>.log)
#
# Example adding a new logger:
#   reports_logger = setup_logger("reports", "reports.log")
# =============================================================================

auth_logger = setup_logger("auth", "auth.log")              # Authentication events
twilio_logger = setup_logger("twilio_webhook", "twilio_webhook.log")  # Twilio webhook & reply events
messages_logger = setup_logger("messages", "messages.log")  # Message operations
orchestrator_logger = setup_logger("orchestrator", "orchestrator.log")  # AI orchestration & agent debugging