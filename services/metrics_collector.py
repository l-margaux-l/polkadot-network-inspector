import logging
from datetime import datetime, timezone
from typing import Optional

from models.node import Node
from models.metrics import HealthMetrics
from services.rpc_client import PolkadotRPCClient
from services.time_utils import TimeUtils
from services.error_handler import ErrorHandler


logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects health metrics from blockchain nodes."""

    def __init__(self):
        """Initialize metrics collector."""
        self.clients: dict[str, PolkadotRPCClient] = {}

    async def collect_metrics(self, node: Node) -> Optional[HealthMetrics]:
        """
        Collect health metrics for a single node.

        Args:
            node: Node object with name and RPC URL.

        Returns:
            HealthMetrics object with collected data, or None if collection fails.
        """
        if node.name not in self.clients:
            self.clients[node.name] = PolkadotRPCClient(node.rpc_url)

        client = self.clients[node.name]

        if client.substrate is None:
            connected = await client.connect()
            if not connected:
                logger.error(f"Could not connect to {node.name}")
                return None

        chain_head = await ErrorHandler.execute_with_timeout(
            client.get_chain_head,
            timeout=client.timeout,
            fallback_value=None,
            operation_name=f"get_chain_head for {node.name}",
        )
        if not chain_head:
            logger.error(f"Could not get chain head for {node.name}")
            return None

        block_height = chain_head["block_height"]
        current_block_height = block_height

        finalized_block_number = await ErrorHandler.execute_with_timeout(
            client.get_finalized_block_number,
            timeout=client.timeout,
            fallback_value=0,
            operation_name=f"get_finalized_block_number for {node.name}",
        )
        finality_lag = max(0, block_height - finalized_block_number) if finalized_block_number else 0

        peers_count = await ErrorHandler.execute_with_timeout(
            client.get_peers_count,
            timeout=client.timeout,
            fallback_value=0,
            operation_name=f"get_peers_count for {node.name}",
        )

        block_timestamp_ms = await ErrorHandler.execute_with_timeout(
            client.get_finalized_block_timestamp,
            timeout=client.timeout,
            fallback_value=None,
            operation_name=f"get_finalized_block_timestamp for {node.name}",
        )
        if block_timestamp_ms is not None:
            time_since_last_block = TimeUtils.calculate_time_since_last_block(
                block_timestamp_ms
            )
        else:
            time_since_last_block = 0

        rpc_response_time = await ErrorHandler.execute_with_timeout(
            client.measure_rpc_response_time,
            timeout=client.timeout,
            fallback_value=-1.0,
            operation_name=f"measure_rpc_response_time for {node.name}",
        )
        if rpc_response_time is None:
            rpc_response_time = -1.0

        metrics = HealthMetrics(
            node_name=node.name,
            block_height=block_height,
            current_block_height=current_block_height,
            peers_count=peers_count,
            finality_lag=finality_lag,
            time_since_last_block=time_since_last_block,
            rpc_response_time=rpc_response_time,
            status="",
            timestamp=datetime.now(timezone.utc),
        )

        from services.health_checker import HealthChecker
        overall_status = HealthChecker.evaluate_metrics(metrics)
        metrics.status = overall_status

        logger.info(
            f"Collected metrics for {node.name}: "
            f"block_height={block_height}, peers={peers_count}, "
            f"time_since_block={time_since_last_block}s, "
            f"rpc_response={rpc_response_time:.0f}ms, status={overall_status}"
        )

        return metrics

    @staticmethod
    def _evaluate_peers_health(peers_count: int) -> str:
        """Evaluate health status based on peer count."""
        if peers_count > 20:
            return "healthy"
        elif peers_count >= 1:
            return "warning"
        else:
            return "warning"
        
    @staticmethod
    def _evaluate_finality_health(finality_lag: int) -> str:
        """Evaluate health status based on finality lag."""
        if finality_lag == 0:
            return "critical"
        if finality_lag < 10:
            return "healthy"
        if finality_lag <= 30:
            return "warning"
        return "critical"

    @staticmethod
    def _determine_overall_status(
        peers_health: str,
        block_freshness: str,
        rpc_health: str,
        finality_health: str,
    ) -> str:
        """
        Determine overall node status based on multiple metrics.

        Uses worst status (critical > warning > healthy).
        """
        status_priority = {"critical": 3, "warning": 2, "healthy": 1}

        worst_status = max(
            [peers_health, block_freshness, rpc_health, finality_health],
            key=lambda s: status_priority.get(s, 1),
        )
        return worst_status

    async def disconnect(self, node_name: str) -> None:
        """Disconnect from a specific node."""
        if node_name in self.clients:
            self.clients[node_name].disconnect()
            del self.clients[node_name]

    async def disconnect_all(self) -> None:
        """Disconnect from all nodes."""
        for client in self.clients.values():
            client.disconnect()
        self.clients.clear()
