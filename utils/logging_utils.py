"""Logging utilities"""
import logging
import sys
from config.settings import LoggingSettings

def setup_logging():
    """Setup logging configuration"""
    # Настраиваем кодировку для файла лога
    kwargs = {
        'filename': LoggingSettings.LOG_FILE,
        'level': LoggingSettings.LOG_LEVEL,
        'format': LoggingSettings.LOG_FORMAT,
        'encoding': 'utf-8'
    }
    
    logging.basicConfig(**kwargs)
    
    # Добавляем вывод в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(LoggingSettings.LOG_FORMAT))
    logging.getLogger().addHandler(console_handler)
    
    return logging.getLogger(__name__)

logger = setup_logging()


