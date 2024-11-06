"""Logging utilities"""
import logging
from config.settings import LoggingSettings

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        filename=LoggingSettings.LOG_FILE,
        level=LoggingSettings.LOG_LEVEL,
        format=LoggingSettings.LOG_FORMAT
    )
    
    # Add console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LoggingSettings.LOG_FORMAT))
    logging.getLogger().addHandler(console_handler)
    
    return logging.getLogger(__name__)

logger = setup_logging()


