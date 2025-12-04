import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class TimeUtils:
    """Utilities for working with blockchain timestamps."""

    @staticmethod
    def calculate_time_since_last_block(block_timestamp_ms: int) -> int:
        """
        Calculate seconds elapsed since block was produced.

        Args:
            block_timestamp_ms: Block timestamp in milliseconds.

        Returns:
            Seconds elapsed since block timestamp.
        """
        current_time_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        elapsed_ms = current_time_ms - block_timestamp_ms
        elapsed_seconds = elapsed_ms // 1000
        
        return max(0, elapsed_seconds)

    @staticmethod
    def evaluate_block_freshness(seconds_since_block: int) -> str:
        """
        Evaluate block freshness health status.

        Args:
            seconds_since_block: Seconds since last block.

        Returns:
            Health status: "healthy", "warning", or "critical"
        """
        if seconds_since_block <= 12:
            return "healthy"
        elif seconds_since_block <= 30:
            return "warning"
        else:
            return "critical"
