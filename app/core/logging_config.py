"""
Logging Configuration
Centralized logging setup with file rotation
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Configure application logging with:
    - Console output (INFO level)
    - File output with rotation (app.log)
    - Error file output (error.log)
    """
    
    # Create logs directory if not exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler - app.log (rotating by size: 10MB, keep 5 backups)
    app_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10_000_000,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)
    logger.addHandler(app_handler)
    
    # Error File Handler - error.log (only errors)
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10_000_000,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module
    
    Args:
        name: Usually __name__ of the module
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
