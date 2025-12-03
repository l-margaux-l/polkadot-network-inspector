import asyncio
from models.node import Node
from services.metrics_collector import MetricsCollector


async def test_metrics_collector():
    """Test metrics collection."""
    
    collector = MetricsCollector()

    try:
        # Create test node
        node = Node(
            name="Polkadot",
            rpc_url="wss://rpc.polkadot.io"
        )

        print("Collecting metrics...")
        metrics = await collector.collect_metrics(node)

        if metrics:
            print(f"✓ Metrics collected successfully")
            print(f"  - Node: {metrics.node_name}")
            print(f"  - Block height: {metrics.block_height}")
            print(f"  - Peers: {metrics.peers_count}")
            print(f"  - Status: {metrics.status}")
            print(f"  - Timestamp: {metrics.timestamp}")
        else:
            print("✗ Failed to collect metrics")

    finally:
        await collector.disconnect_all()


if __name__ == "__main__":
    asyncio.run(test_metrics_collector())
