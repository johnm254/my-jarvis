"""Error handling and fallback mechanisms for JARVIS.

This module provides graceful error handling and fallback strategies for:
- Voice failures → fall back to text input
- External API failures → return cached data when available
- LLM failures → retry with exponential backoff
- Database failures → queue operations for retry

Validates: Requirements 3.7
"""

import logging
import time
from typing import Any, Callable, Optional, TypeVar, Dict
from functools import wraps
from collections import deque

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 10.0
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            backoff_factor: Multiplier for exponential backoff
            max_delay: Maximum delay between retries
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay


def retry_with_exponential_backoff(
    config: Optional[RetryConfig] = None,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        config: RetryConfig object (default: 3 attempts, 1s initial delay)
        exceptions: Tuple of exceptions to catch and retry
        
    Returns:
        Decorated function with retry logic
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = config.initial_delay
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {config.max_attempts} attempts: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{config.max_attempts}): {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    
                    time.sleep(delay)
                    delay = min(delay * config.backoff_factor, config.max_delay)
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


class CacheManager:
    """Simple cache manager for fallback data."""
    
    def __init__(self, max_size: int = 100):
        """
        Initialize cache manager.
        
        Args:
            max_size: Maximum number of cached items
        """
        self._cache: Dict[str, Any] = {}
        self._access_order = deque(maxlen=max_size)
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set cached value.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Remove oldest item if cache is full
        if len(self._cache) >= self.max_size and key not in self._cache:
            if self._access_order:
                oldest_key = self._access_order.popleft()
                self._cache.pop(oldest_key, None)
        
        self._cache[key] = value
        
        # Update access order
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
    
    def clear(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        self._access_order.clear()


class OperationQueue:
    """Queue for operations that failed and need to be retried."""
    
    def __init__(self):
        """Initialize operation queue."""
        self._queue = deque()
    
    def enqueue(self, operation: Callable, *args, **kwargs) -> None:
        """
        Add an operation to the queue.
        
        Args:
            operation: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        self._queue.append((operation, args, kwargs))
        logger.info(f"Queued operation: {operation.__name__}")
    
    def process_queue(self) -> int:
        """
        Process all queued operations.
        
        Returns:
            Number of successfully processed operations
        """
        success_count = 0
        failed_operations = deque()
        
        while self._queue:
            operation, args, kwargs = self._queue.popleft()
            
            try:
                operation(*args, **kwargs)
                success_count += 1
                logger.info(f"Successfully processed queued operation: {operation.__name__}")
            except Exception as e:
                logger.warning(f"Queued operation {operation.__name__} failed: {e}")
                failed_operations.append((operation, args, kwargs))
        
        # Re-queue failed operations
        self._queue = failed_operations
        
        return success_count
    
    def size(self) -> int:
        """Get the number of queued operations."""
        return len(self._queue)


# Global instances
_cache_manager = CacheManager()
_operation_queue = OperationQueue()


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    return _cache_manager


def get_operation_queue() -> OperationQueue:
    """Get the global operation queue instance."""
    return _operation_queue


def with_fallback_cache(cache_key_func: Callable[..., str]):
    """
    Decorator that provides cached fallback data on failure.
    
    Args:
        cache_key_func: Function to generate cache key from arguments
        
    Returns:
        Decorated function with cache fallback
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            cache_key = cache_key_func(*args, **kwargs)
            cache = get_cache_manager()
            
            try:
                result = func(*args, **kwargs)
                # Cache successful result
                cache.set(cache_key, result)
                return result
            except Exception as e:
                logger.warning(f"{func.__name__} failed: {e}. Attempting to use cached data...")
                
                cached_result = cache.get(cache_key)
                if cached_result is not None:
                    logger.info(f"Using cached data for {func.__name__}")
                    return cached_result
                
                logger.error(f"No cached data available for {func.__name__}")
                raise
        
        return wrapper
    return decorator


def with_queue_on_failure(queue_func: Optional[Callable] = None):
    """
    Decorator that queues operations for retry on failure.
    
    Args:
        queue_func: Optional function to call instead of the original on failure
        
    Returns:
        Decorated function with queue fallback
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"{func.__name__} failed: {e}. Queuing for retry...")
                
                queue = get_operation_queue()
                operation = queue_func if queue_func else func
                queue.enqueue(operation, *args, **kwargs)
                
                return None
        
        return wrapper
    return decorator


class FallbackHandler:
    """Handler for managing fallback strategies."""
    
    @staticmethod
    def voice_to_text_fallback(error: Exception) -> str:
        """
        Handle voice input failure by falling back to text input.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Message to display to user
        """
        logger.warning(f"Voice input failed: {error}")
        return "Voice input failed. Please type your request instead."
    
    @staticmethod
    def llm_failure_fallback(error: Exception) -> str:
        """
        Handle LLM API failure.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Message to display to user
        """
        logger.error(f"LLM API failed: {error}")
        return "I'm having trouble connecting to my reasoning engine. Please try again in a moment."
    
    @staticmethod
    def database_failure_fallback(error: Exception) -> str:
        """
        Handle database connection failure.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Message to display to user
        """
        logger.error(f"Database connection failed: {error}")
        return "I'm experiencing database connectivity issues. Your request has been queued and will be processed when the connection is restored."
    
    @staticmethod
    def external_api_failure_fallback(api_name: str, error: Exception) -> str:
        """
        Handle external API failure.
        
        Args:
            api_name: Name of the API that failed
            error: The exception that occurred
            
        Returns:
            Message to display to user
        """
        logger.warning(f"{api_name} API failed: {error}")
        return f"The {api_name} service is currently unavailable. I'll try to provide cached information if available."


# Convenience function for common retry scenarios
def retry_llm_call(func: Callable[..., T]) -> Callable[..., T]:
    """Retry LLM API calls with exponential backoff (3 attempts)."""
    return retry_with_exponential_backoff(
        config=RetryConfig(max_attempts=3, initial_delay=1.0, backoff_factor=2.0),
        exceptions=(Exception,)
    )(func)


def retry_database_operation(func: Callable[..., T]) -> Callable[..., T]:
    """Retry database operations with exponential backoff (3 attempts)."""
    return retry_with_exponential_backoff(
        config=RetryConfig(max_attempts=3, initial_delay=0.5, backoff_factor=2.0),
        exceptions=(Exception,)
    )(func)
