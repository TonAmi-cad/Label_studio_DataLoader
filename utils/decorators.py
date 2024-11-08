from functools import wraps
import time
from .settings import LabelStudioSettings

def retry_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(LabelStudioSettings.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                delay = LabelStudioSettings.RETRY_DELAY * (LabelStudioSettings.RETRY_BACKOFF ** attempt)
                logger.error(f"Error: {str(e)}. Attempt {attempt + 1} of {LabelStudioSettings.MAX_RETRIES}")
                if attempt < LabelStudioSettings.MAX_RETRIES - 1:
                    logger.info(f"Retrying in {delay} seconds")
                    time.sleep(delay)
                else:
                    raise
    return wrapper 