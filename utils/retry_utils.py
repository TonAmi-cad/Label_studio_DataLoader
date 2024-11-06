
"""Utilities for retry attempts"""
import time
from functools import wraps
from typing import Callable, Any
from config.settings import LabelStudioSettings
from utils.logging_utils import logger

def retry_request(func: Callable) -> Callable:
    """Decorator for retrying request execution"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        for attempt in range(LabelStudioSettings.RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error: {e}. Attempt {attempt + 1} of {LabelStudioSettings.RETRIES}")
                if attempt < LabelStudioSettings.RETRIES - 1:
                    logger.info(f"Retrying in {LabelStudioSettings.DELAY} seconds")
                    time.sleep(LabelStudioSettings.DELAY)
                else:
                    raise
        return None
    return wrapper
