import logging

logger = logging.getLogger(__name__)


class RpcUtils:
    """Utilities for RPC performance analysis."""

    @staticmethod
    def evaluate_rpc_health(response_time_ms: float) -> str:
        """
        Evaluate RPC health based on response time.

        Args:
            response_time_ms: Response time in milliseconds.

        Returns:
            Health status: "healthy", "warning", or "critical"
        """
        if response_time_ms <= 500:
            return "healthy"
        elif response_time_ms <= 2000:
            return "warning"
        else:
            return "critical"

    @staticmethod
    def format_response_time(response_time_ms: float) -> str:
        """
        Format response time for display.

        Args:
            response_time_ms: Response time in milliseconds.

        Returns:
            Formatted string with appropriate units.
        """
        if response_time_ms < 1000:
            return f"{response_time_ms:.0f}ms"
        else:
            return f"{response_time_ms / 1000:.2f}s"
