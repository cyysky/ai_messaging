"""
Logging initialization module.
Configures loggers for the application.
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


# Initialize all application loggers
auth_logger = setup_logger("auth", "auth.log")
twilio_logger = setup_logger("twilio_webhook", "twilio_webhook.log")
messages_logger = setup_logger("messages", "messages.log")