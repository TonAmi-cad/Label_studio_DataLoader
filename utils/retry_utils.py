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
        for attempt in range(LabelStudioSettings.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                delay = LabelStudioSettings.RETRY_DELAY * (LabelStudioSettings.RETRY_BACKOFF ** attempt)
                logger.error(f"Error: {e}. Attempt {attempt + 1} of {LabelStudioSettings.MAX_RETRIES}")
                if attempt < LabelStudioSettings.MAX_RETRIES - 1:
                    logger.info(f"Retrying in {delay} seconds")
                    time.sleep(delay)
                else:
                    raise
        return None
    return wrapper

    
