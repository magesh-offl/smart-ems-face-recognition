"""Logger Configuration"""
import logging
import sys
from app.config import get_settings


def setup_logger(name: str) -> logging.Logger:
    """Setup logger with specified name"""
    settings = get_settings()
    
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger
