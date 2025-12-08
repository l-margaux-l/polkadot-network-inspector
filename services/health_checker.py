import logging

from models.metrics import HealthMetrics
from services.time_utils import TimeUtils
from services.rpc_utils import RpcUtils

logger = logging.getLogger(__name__)


class HealthChecker:
    """Evaluates and aggregates node health from multiple metrics."""

    @staticmethod
    def evaluate_metrics(metrics: HealthMetrics) -> str:
        """
        Determine overall health status based on all metrics.

        Evaluates individual metric health and combines them:
        - healthy: all metrics healthy or most are healthy
        - warning: 1-2 metrics warning
        - critical: 3+ metrics warning, or any metric critical

        Args:
            metrics: HealthMetrics object with all collected data.

        Returns:
            Overall health status: "healthy", "warning", or "critical"
        """
        health_statuses = []

        # Evaluate each metric
        peers_health = HealthChecker._eval_peers(metrics.peers_count)
        health_statuses.append(peers_health)

        block_freshness = TimeUtils.evaluate_block_freshness(
            metrics.time_since_last_block
        )
        health_statuses.append(block_freshness)

        rpc_health = RpcUtils.evaluate_rpc_health(metrics.rpc_response_time)
        health_statuses.append(rpc_health)

        finality_health = HealthChecker._eval_finality(metrics.finality_lag)
        health_statuses.append(finality_health)

        # Count statuses
        critical_count = health_statuses.count("critical")
        warning_count = health_statuses.count("warning")

        # Determine overall status
        if critical_count > 0:
            return "critical"
        elif warning_count >= 2:
            return "critical"
        elif warning_count == 1:
            return "warning"
        else:
            return "healthy"

    @staticmethod
    def _eval_peers(peers_count: int) -> str:
        """Evaluate peers health."""
        if peers_count > 20:
            return "healthy"
        elif peers_count > 0:
            return "warning"
        else:
            return "healthy"  # 0 peers on public RPC is expected

    @staticmethod
    def _eval_finality(finality_lag: int) -> str:
        """Evaluate finality lag health."""
        if finality_lag == 0:
            return "critical"
        if finality_lag < 10:
            return "healthy"
        if finality_lag <= 30:
            return "warning"
        return "critical"

    @staticmethod
    def generate_report(metrics: HealthMetrics) -> dict:
        """
        Generate a complete health report for a node.

        Args:
            metrics: HealthMetrics object.

        Returns:
            Dictionary with summary and all metrics.
        """
        overall_status = HealthChecker.evaluate_metrics(metrics)

        return {
            "node_name": metrics.node_name,
            "status": overall_status,
            "timestamp": metrics.timestamp.isoformat(),
            "metrics": {
                "block_height": metrics.block_height,
                "peers": metrics.peers_count,
                "time_since_last_block_seconds": metrics.time_since_last_block,
                "rpc_response_time_ms": metrics.rpc_response_time,
                "finality_lag": metrics.finality_lag,
            },
        }
