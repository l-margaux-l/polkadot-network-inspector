import logging
from datetime import datetime, timezone
from typing import Optional

from models.node import Node
from models.metrics import HealthMetrics
from services.rpc_client import PolkadotRPCClient

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

        chain_head = await client.get_chain_head()
        if not chain_head:
            logger.error(f"Could not get chain head for {node.name}")
            return None

        block_height = chain_head["block_height"]
        current_block_height = block_height
        finality_lag = 0

        peers_count = await client.get_peers_count()
        if peers_count is None:
            peers_count = 0

        peers_health = self._evaluate_peers_health(peers_count)
        overall_status = self._determine_overall_status(peers_health)

        metrics = HealthMetrics(
            node_name=node.name,
            block_height=block_height,
            current_block_height=current_block_height,
            peers_count=peers_count,
            finality_lag=finality_lag,
            time_since_last_block=0,
            rpc_response_time=0.0,
            status=overall_status,
            timestamp=datetime.now(timezone.utc)
        )

        logger.info(
            f"Collected metrics for {node.name}: "
            f"block_height={block_height}, peers={peers_count}, status={overall_status}"
        )

        return metrics

    @staticmethod
    def _evaluate_peers_health(peers_count: int) -> str:
        """
        Evaluate health status based on peer count.

        Args:
            peers_count: Number of connected peers.

        Returns:
            Health status: "healthy", "warning", or "critical"
        """
        if peers_count > 20:
            return "healthy"
        elif peers_count > 5:
            return "warning"
        else:
            return "critical"

    @staticmethod
    def _determine_overall_status(peers_health: str) -> str:
        """
        Determine overall node status based on metrics.

        Args:
            peers_health: Health status from peer evaluation.

        Returns:
            Overall status string.
        """
        return peers_health

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
