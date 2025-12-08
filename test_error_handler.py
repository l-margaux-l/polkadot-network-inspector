import asyncio
from services.error_handler import ErrorHandler


async def test_error_handler():
    """Test error handling and timeout mechanisms."""

    print("Testing ErrorHandler...\n")

    # Test 1: Successful execution
    print("Test 1: Successful execution")
    async def success_func():
        await asyncio.sleep(0.1)
        return "success"

    result = await ErrorHandler.execute_with_timeout(
        success_func,
        timeout=1.0,
        fallback_value="fallback",
        operation_name="test_success",
    )
    print(f"  Result: {result}")
    assert result == "success", "Expected success"

    # Test 2: Timeout handling
    print("\nTest 2: Timeout handling")
    async def slow_func():
        await asyncio.sleep(5.0)  # Sleep longer than timeout
        return "this won't execute"

    result = await ErrorHandler.execute_with_timeout(
        slow_func,
        timeout=0.5,
        fallback_value="fallback",
        operation_name="test_timeout",
    )
    print(f"  Result: {result}")
    assert result == "fallback", "Expected fallback on timeout"

    # Test 3: Exception handling
    print("\nTest 3: Exception handling")
    async def error_func():
        raise ValueError("Intentional error")

    result = await ErrorHandler.execute_with_timeout(
        error_func,
        timeout=1.0,
        fallback_value="fallback",
        operation_name="test_error",
    )
    print(f"  Result: {result}")
    assert result == "fallback", "Expected fallback on error"

    # Test 4: Retry logic
    print("\nTest 4: Retry logic (success on 2nd attempt)")
    attempt_count = 0

    async def flaky_func():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 2:
            raise ConnectionError("Temporary error")
        return "success after retry"

    attempt_count = 0
    result = await ErrorHandler.execute_with_retry(
        flaky_func,
        max_retries=3,
        timeout=1.0,
        fallback_value="fallback",
        operation_name="test_retry",
    )
    print(f"  Attempts: {attempt_count}")
    print(f"  Result: {result}")
    assert result == "success after retry", "Expected success after retry"

    # Test 5: Retry exhaustion
    print("\nTest 5: Retry exhaustion (all attempts fail)")
    async def always_fails():
        raise RuntimeError("Always fails")

    result = await ErrorHandler.execute_with_retry(
        always_fails,
        max_retries=2,
        timeout=1.0,
        fallback_value="fallback",
        operation_name="test_retry_fail",
    )
    print(f"  Result: {result}")
    assert result == "fallback", "Expected fallback after all retries fail"

    print("\n✓ All ErrorHandler tests passed!")


if __name__ == "__main__":
    asyncio.run(test_error_handler())
