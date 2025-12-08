import sys
import asyncio
import argparse
from pathlib import Path
from services.rpc_utils import RpcUtils

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import config
from models.node import Node
from services.metrics_collector import MetricsCollector
from services.config_loader import ConfigLoader


async def collect_and_print_metrics(node: Node, collector: MetricsCollector) -> None:
    """Collect metrics for a node and print results."""
    print(f"\n{'='*60}")
    print(f"Monitoring: {node.name}")
    print(f"RPC URL: {node.rpc_url}")
    print('='*60)

    metrics = await collector.collect_metrics(node)

    if metrics:
        peers_icon = "✓" if metrics.peers_count > 0 else "⚠"
        block_icon = "✓" if metrics.time_since_last_block <= 12 else "⚠" if metrics.time_since_last_block <= 30 else "✗"
        
        # RPC time: -1 means measurement failed
        if metrics.rpc_response_time < 0:
            rpc_display = "N/A (timeout)"
            rpc_icon = "⚠"
        else:
            rpc_display = RpcUtils.format_response_time(metrics.rpc_response_time)
            rpc_icon = "✓" if metrics.rpc_response_time <= 500 else "⚠" if metrics.rpc_response_time <= 2000 else "✗"
        
        status_icon = "✓" if metrics.status == "healthy" else "⚠" if metrics.status == "warning" else "✗"

        print(f"\n{status_icon} Metrics collected (with graceful degradation):")
        print(f"  Block height:      {metrics.block_height}")
        print(f"  {peers_icon} Peers:             {metrics.peers_count}")
        print(f"  {block_icon} Time since block:  {metrics.time_since_last_block}s")
        print(f"  {rpc_icon} RPC response time: {rpc_display}")
        print(f"  Finality lag:      {metrics.finality_lag}")
        print(f"  Status:            {metrics.status.upper()}")
        print(f"  Timestamp:         {metrics.timestamp}")
    else:
        print(f"\n✗ Failed to collect metrics for {node.name}")


async def main():
    """Main entry point with CLI support."""
    parser = argparse.ArgumentParser(
        description=config.APP_DESCRIPTION,
        prog=config.APP_NAME
    )

    parser.add_argument(
        "--node",
        type=str,
        help="Monitor specific node by name"
    )

    parser.add_argument(
        "--all-nodes",
        action="store_true",
        help="Monitor all configured nodes"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available nodes"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"{config.APP_NAME} v{config.APP_VERSION}"
    )

    args = parser.parse_args()

    print(f"\n{config.APP_NAME} v{config.APP_VERSION}")
    print(f"{config.APP_DESCRIPTION}\n")

    # If --list, show available nodes and exit
    if args.list:
        ConfigLoader.list_available_nodes()
        return

    collector = MetricsCollector()

    try:
        # Determine which nodes to monitor
        nodes_to_monitor = []

        if args.all_nodes:
            nodes_to_monitor = ConfigLoader.get_all_nodes()
        elif args.node:
            node = ConfigLoader.get_node_by_name(args.node)
            if node:
                nodes_to_monitor = [node]
            else:
                print(f"Error: Node '{args.node}' not found")
                ConfigLoader.list_available_nodes()
                return
        else:
            # Default: monitor first node
            default_node = ConfigLoader.get_node_by_name("polkadot_main")
            if default_node:
                nodes_to_monitor = [default_node]
            else:
                print("Error: No nodes configured")
                return

        # Collect metrics for each node
        for node in nodes_to_monitor:
            await collect_and_print_metrics(node, collector)

        print(f"\n{'='*60}")
        print("✓ Monitoring completed")

    finally:
        await collector.disconnect_all()


if __name__ == "__main__":
    asyncio.run(main())
