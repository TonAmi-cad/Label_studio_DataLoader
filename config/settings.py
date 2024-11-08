"""Main application settings"""
from dataclasses import dataclass

@dataclass
class LabelStudioSettings:
    """Label Studio connection settings"""
    URL: str = "http://localhost:8080/api"
    TOKEN: str = "ad896bb9df35b118f6d2644b3d1fba5d19f56aaa"
    TIMEOUT: int = 30
    
    # Параметры многопоточной загрузки
    NUM_WORKERS: int = 15
    WORKER_START_DELAY: float = 0.6
    UPLOAD_MIN_DELAY: float = 0.05
    UPLOAD_MAX_DELAY: float = 0.25
    
    # Параметры повторных попыток
    MAX_RETRIES: int = 50
    RETRY_DELAY: int = 50
    RETRY_BACKOFF: int = 2
    
    # Параметры пакетной обработки
    BATCH_SIZE: int = 100

@dataclass
class LoggingSettings:
    """Logging settings"""
    LOG_FILE: str = "label_studio_tool.log"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
