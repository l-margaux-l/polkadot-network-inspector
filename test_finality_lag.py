import asyncio
from models.node import Node
from services.metrics_collector import MetricsCollector


async def test_finality_lag():
    collector = MetricsCollector()

    node = Node(
        name="polkadot_main",
        rpc_url="wss://rpc.polkadot.io",
    )

    print("Collecting metrics with finality lag...\n")
    metrics = await collector.collect_metrics(node)

    if metrics:
        print(f"Node:            {metrics.node_name}")
        print(f"Block height:    {metrics.block_height}")
        print(f"Finality lag:    {metrics.finality_lag}")
        print(f"Time since block:{metrics.time_since_last_block}s")
        print(f"RPC time:        {metrics.rpc_response_time:.0f}ms")
        print(f"Status:          {metrics.status}")
    else:
        print("✗ Failed to collect metrics")

    await collector.disconnect_all()


if __name__ == "__main__":
    asyncio.run(test_finality_lag())
