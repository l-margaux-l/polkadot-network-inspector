import asyncio
from services.metrics_collector import MetricsCollector
from models.node import Node


async def test_peers_health():
    """Test peers health evaluation."""
    
    collector = MetricsCollector()
    
    print("Testing peers health evaluation...\n")
    
    test_cases = [
        (0, "critical"),
        (3, "critical"),
        (5, "critical"),
        (10, "warning"),
        (20, "warning"),
        (25, "healthy"),
        (50, "healthy"),
    ]
    
    print("Peers count -> Health status:")
    for peers, expected_status in test_cases:
        actual_status = collector._evaluate_peers_health(peers)
        icon = "✓" if actual_status == expected_status else "✗"
        print(f"  {icon} {peers:3d} peers -> {actual_status:8s} (expected: {expected_status})")
    
    # Real test with actual node
    print("\n" + "="*60)
    print("Testing with real node...\n")
    
    node = Node(
        name="polkadot_main",
        rpc_url="wss://rpc.polkadot.io"
    )
    
    metrics = await collector.collect_metrics(node)
    
    if metrics:
        print(f"✓ Node: {metrics.node_name}")
        print(f"  Peers: {metrics.peers_count}")
        print(f"  Peers health: {MetricsCollector._evaluate_peers_health(metrics.peers_count)}")
        print(f"  Overall status: {metrics.status}")
    else:
        print("✗ Failed to collect metrics")
    
    await collector.disconnect_all()


if __name__ == "__main__":
    asyncio.run(test_peers_health())
