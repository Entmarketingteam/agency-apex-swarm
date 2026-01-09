"""Retry logic with exponential backoff."""

import time
import logging
from functools import wraps
from typing import Callable, TypeVar, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryCallState
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


def exponential_backoff_retry(
    max_attempts: int = 3,
    initial_wait: float = 2.0,
    max_wait: float = 8.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for exponential backoff retry logic.
    
    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        initial_wait: Initial wait time in seconds (default: 2s)
        max_wait: Maximum wait time in seconds (default: 8s)
        exceptions: Tuple of exceptions to catch and retry on
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=initial_wait, max=max_wait),
            retry=retry_if_exception_type(exceptions),
            reraise=True
        )
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                logger.warning(
                    f"Retrying {func.__name__} after exception: {type(e).__name__}"
                )
                raise
        
        return wrapper
    return decorator


def simple_retry(
    func: Callable[..., T],
    max_attempts: int = 3,
    delay: float = 2.0
) -> T:
    """
    Simple retry wrapper for synchronous functions.
    
    Args:
        func: Function to retry
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds
    
    Returns:
        Function result
    
    Raises:
        Last exception if all attempts fail
    """
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_attempts - 1:
                wait_time = delay * (2 ** attempt)  # 2s, 4s, 8s
                logger.warning(
                    f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}. "
                    f"Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)
            else:
                logger.error(
                    f"All {max_attempts} attempts failed for {func.__name__}"
                )
    
    raise last_exception


