"""Main application settings"""
from dataclasses import dataclass

@dataclass
class LabelStudioSettings:
    """Label Studio connection settings"""
    URL: str = "http://localhost:8080/api"
    TOKEN: str = "ad896bb9df35b118f6d2644b3d1fba5d19f56aaa"
    TIMEOUT: int = 80
    RETRIES: int = 1500
    DELAY: int = 1


@dataclass
class LoggingSettings:
    """Logging settings"""
    LOG_FILE: str = "label_studio_tool.log"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
