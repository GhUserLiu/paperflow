"""Utility decorators for common patterns"""

import functools
import logging
from typing import Callable, Type, Tuple, Any, Optional
from .errors import ZoteroConnectorError

logger = logging.getLogger(__name__)


def log_and_reraise(
    error_logger: Optional[logging.Logger] = None,
    message: Optional[str] = None,
    reraise: bool = True,
):
    """
    Decorator to log exceptions and optionally re-raise them

    Args:
        error_logger: Logger instance (uses module logger if None)
        message: Custom error message (uses function name if None)
        reraise: Whether to re-raise the exception (default: True)

    Example:
        @log_and_reraise()
        def some_function():
            # Error will be logged with stack trace and re-raised
            pass

        @log_and_reraise(reraise=False)
        def another_function():
            # Error will be logged but not re-raised (returns None)
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log = error_logger or logger
                msg = message or f"Error in {func.__name__}"

                log.error(
                    f"{msg}: {str(e)}",
                    exc_info=True,  # Include stack trace
                    extra={
                        "function": func.__name__,
                        "args": str(args)[:100],  # Truncate long args
                        "kwargs": str(kwargs)[:100],
                    },
                )

                if reraise:
                    raise
                return None

        return wrapper

    return decorator


def handle_api_errors(
    default_return: Any = None, error_types: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator to handle API errors consistently

    Args:
        default_return: Value to return on error (default: None)
        error_types: Tuple of exception types to catch (default: all Exceptions)

    Example:
        @handle_api_errors(default_return=[])
        def fetch_papers():
            # Returns [] on error instead of raising
            pass

        @handle_api_errors(default_return=False, error_types=(ConnectionError, TimeoutError))
        def connect_to_api():
            # Only handles connection/timeout errors
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_types as e:
                logger.warning(
                    f"API error in {func.__name__}: {str(e)}", extra={"function": func.__name__}
                )
                return default_return

        return wrapper

    return decorator


def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Decorator to retry function on failure with exponential backoff

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        delay: Initial delay between retries in seconds (default: 1.0)
        backoff_factor: Multiplier for delay after each retry (default: 2.0)
        exceptions: Tuple of exception types to retry on (default: all Exceptions)

    Example:
        @retry_on_failure(max_attempts=3, delay=2.0)
        def fetch_data():
            # Will retry up to 3 times with 2s, 4s, 8s delays
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Failed after {max_attempts} attempts in {func.__name__}: {str(e)}"
                        )
                        raise

                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )

                    import time

                    time.sleep(current_delay)
                    current_delay *= backoff_factor

        return wrapper

    return decorator


def validate_args(*validators: Callable):
    """
    Decorator to validate function arguments

    Args:
        *validators: Validation functions that take the same args as the decorated function
                      Should raise ValueError if validation fails

    Example:
        def validate_positive(x, y):
            if x < 0 or y < 0:
                raise ValueError("Arguments must be positive")

        @validate_args(validate_positive)
        def calculate(x, y):
            return x + y
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for validator in validators:
                validator(*args, **kwargs)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def measure_time(log_level: int = logging.INFO):
    """
    Decorator to measure and log function execution time

    Args:
        log_level: Logging level to use (default: INFO)

    Example:
        @measure_time()
        def slow_function():
            # Will log execution time
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time

            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time

            logger.log(
                log_level,
                f"{func.__name__} executed in {elapsed_time:.2f}s",
                extra={"function": func.__name__, "execution_time": elapsed_time},
            )

            return result

        return wrapper

    return decorator


def rate_limit(calls_per_second: float):
    """
    Decorator to rate limit function calls

    Args:
        calls_per_second: Maximum number of calls per second

    Example:
        @rate_limit(calls_per_second=10)
        def api_call():
            # Limited to 10 calls per second
            pass
    """
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]  # Use list for mutable state in closure

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time

            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                wait_time = min_interval - elapsed
                logger.debug(f"Rate limiting {func.__name__}: waiting {wait_time:.2f}s")
                time.sleep(wait_time)

            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result

        return wrapper

    return decorator


def cache_result(ttl_seconds: int = 300):
    """
    Simple in-memory cache decorator with TTL

    Args:
        ttl_seconds: Time-to-live for cached results in seconds (default: 300)

    Note:
        This is a simple cache. For production use, consider functools.lru_cache
        or dedicated caching libraries like cachetools.

    Example:
        @cache_result(ttl_seconds=60)
        def expensive_computation(x):
            return x ** 2
    """
    cache = {}

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time

            # Create cache key from args and kwargs
            key = (args, tuple(sorted(kwargs.items())))

            # Check if result is cached and not expired
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < ttl_seconds:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result

            # Compute result and cache it
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            logger.debug(f"Cache miss for {func.__name__}, result cached")

            return result

        # Add method to clear cache
        wrapper.cache_clear = lambda: cache.clear()

        return wrapper

    return decorator


def deprecated(message: Optional[str] = None, version: Optional[str] = None):
    """
    Decorator to mark functions as deprecated

    Args:
        message: Custom deprecation message
        version: Version when the function was deprecated

    Example:
        @deprecated(message="Use new_function() instead", version="2.0.0")
        def old_function():
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            msg = message or f"{func.__name__} is deprecated"
            if version:
                msg += f" (since version {version})"

            logger.warning(f"DEPRECATION WARNING: {msg}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Composite decorators for common patterns


def robust_api_call(max_retries: int = 3, timeout: int = 30):
    """
    Composite decorator for robust API calls with retry, timeout, and logging

    Args:
        max_retries: Maximum retry attempts (default: 3)
        timeout: Timeout in seconds (default: 30)

    Example:
        @robust_api_call(max_retries=3, timeout=60)
        def fetch_from_api():
            # Retries on failure, measures time, logs errors
            pass
    """

    def decorator(func: Callable) -> Callable:
        func = retry_on_failure(max_attempts=max_retries)(func)
        func = measure_time()(func)
        func = log_and_reraise()(func)
        return func

    return decorator


# Example usage demonstrations
if __name__ == "__main__":
    # Setup logging for examples
    logging.basicConfig(level=logging.INFO)

    # Example 1: log_and_reraise
    @log_and_reraise()
    def example_function():
        """Function that logs and re-raises errors"""
        raise ValueError("Test error")

    # Example 2: handle_api_errors
    @handle_api_errors(default_return=[])
    def fetch_papers():
        """Returns empty list on error instead of raising"""
        raise ConnectionError("API unavailable")

    # Example 3: retry_on_failure
    @retry_on_failure(max_attempts=2, delay=0.5)
    def unstable_function():
        """Retries on failure"""
        import random

        if random.random() < 0.7:
            raise ConnectionError("Random failure")
        return "Success!"

    # Example 4: measure_time
    @measure_time()
    def slow_function():
        """Logs execution time"""
        import time

        time.sleep(0.1)
        return "Done"

    # Example 5: rate_limit
    @rate_limit(calls_per_second=2)
    def rate_limited_function():
        """Limited to 2 calls per second"""
        return "Called"

    # Example 6: cache_result
    @cache_result(ttl_seconds=5)
    def expensive_computation(x):
        """Caches result for 5 seconds"""
        import time

        time.sleep(0.1)
        return x**2

    # Example 7: deprecated
    @deprecated(message="Use new_function() instead", version="2.0.0")
    def old_function():
        """Shows deprecation warning"""
        return "Old implementation"

    # Example 8: robust_api_call
    @robust_api_call(max_retries=2, timeout=10)
    def api_endpoint():
        """Robust API call with all features"""
        return "API response"

    # Run examples
    print("\n=== Example 1: log_and_reraise ===")
    try:
        example_function()
    except ValueError:
        print("Error was logged and re-raised")

    print("\n=== Example 2: handle_api_errors ===")
    result = fetch_papers()
    print(f"Result: {result}")

    print("\n=== Example 3: retry_on_failure ===")
    result = unstable_function()
    print(f"Result: {result}")

    print("\n=== Example 4: measure_time ===")
    result = slow_function()

    print("\n=== Example 5: rate_limit ===")
    rate_limited_function()
    rate_limited_function()

    print("\n=== Example 6: cache_result ===")
    print("First call (slow):", expensive_computation(5))
    print("Second call (fast, from cache):", expensive_computation(5))

    print("\n=== Example 7: deprecated ===")
    old_function()

    print("\n=== Example 8: robust_api_call ===")
    api_endpoint()
