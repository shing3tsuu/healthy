from typing import Awaitable, Optional, Callable, Any
from functools import wraps
import time as t
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

class DatabaseLoggerHandler:
    def __init__(self, enable_timing: bool = True):
        self.enable_timing = enable_timing
        self.logger = logging.getLogger(__name__)

    def __call__(self, func: Callable | Awaitable[Any]):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = t.monotonic()
            result, error = None, None

            try:
                return await func(*args, **kwargs)

            except Exception as e:
                error = e
                self.logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True, extra={"args": args, "kwargs": kwargs})
                raise

            finally:
                if self.enable_timing:
                    duration = t.monotonic() - start_time
                    self.logger.info(
                        f"Method {func.__name__} executed in {duration:.4f}s",
                        extra={"method": func.__name__,"duration": duration,"success": error is None}
                        )

        return async_wrapper

    async def _send_to_external(self, error: Exception, method_name: str):
        pass  # Реализация для внешнего сервиса