import sys
import asyncio
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import config
from models.node import Node
from services.metrics_collector import MetricsCollector


async def main():
    """Main entry point for Polkadot Network Inspector."""
    print(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    print(f"Project root: {config.PROJECT_ROOT}")
    print(f"RPC URL: {config.POLKADOT_RPC_URL}\n")

    # Create metrics collector
    collector = MetricsCollector()

    try:
        # Create node object
        polkadot_node = Node(
            name="Polkadot",
            rpc_url=config.POLKADOT_RPC_URL
        )

        print(f"Collecting metrics for {polkadot_node.name}...\n")

        # Collect metrics
        metrics = await collector.collect_metrics(polkadot_node)

        if metrics:
            print(f"✓ Block height: {metrics.block_height}")
            print(f"✓ Peers: {metrics.peers_count}")
            print(f"✓ Status: {metrics.status}")
            print(f"✓ Timestamp: {metrics.timestamp}")
        else:
            print("✗ Failed to collect metrics")

    finally:
        # Clean up
        await collector.disconnect_all()
        print("\n✓ Done")


if __name__ == "__main__":
    asyncio.run(main())
