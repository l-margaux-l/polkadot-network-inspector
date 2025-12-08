import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Handles errors and timeouts gracefully."""

    @staticmethod
    async def execute_with_timeout(
        coro_func: Callable,
        timeout: float = 5.0,
        fallback_value: Any = None,
        operation_name: str = "operation",
    ) -> Any:
        """
        Execute async function with timeout and error handling.

        Args:
            coro_func: Async function to execute
            timeout: Timeout in seconds
            fallback_value: Value to return if operation fails
            operation_name: Name for logging

        Returns:
            Result from function or fallback_value if operation fails
        """
        try:
            result = await asyncio.wait_for(coro_func(), timeout=timeout)
            return result

        except asyncio.TimeoutError:
            logger.warning(
                f"Timeout ({timeout}s) while executing {operation_name}"
            )
            return fallback_value

        except Exception as e:
            logger.error(f"Error in {operation_name}: {type(e).__name__}: {e}")
            return fallback_value

    @staticmethod
    async def execute_with_retry(
        coro_func: Callable,
        max_retries: int = 2,
        timeout: float = 5.0,
        fallback_value: Any = None,
        operation_name: str = "operation",
    ) -> Any:
        """
        Execute async function with retry logic.

        Args:
            coro_func: Async function to execute
            max_retries: Number of retries (total attempts = max_retries + 1)
            timeout: Timeout per attempt in seconds
            fallback_value: Value to return if all retries fail
            operation_name: Name for logging

        Returns:
            Result or fallback_value if all attempts fail
        """
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                result = await asyncio.wait_for(coro_func(), timeout=timeout)
                if attempt > 0:
                    logger.info(
                        f"{operation_name} succeeded on attempt {attempt + 1}"
                    )
                return result

            except asyncio.TimeoutError as e:
                last_error = e
                logger.warning(
                    f"Timeout in {operation_name} (attempt {attempt + 1}/{max_retries + 1})"
                )
                if attempt < max_retries:
                    await asyncio.sleep(1)  

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Error in {operation_name} (attempt {attempt + 1}/{max_retries + 1}): {e}"
                )
                if attempt < max_retries:
                    await asyncio.sleep(1)  

        logger.error(
            f"All retries failed for {operation_name}. Using fallback value."
        )
        return fallback_value
