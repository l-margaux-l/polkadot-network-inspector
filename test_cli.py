import asyncio
from services.config_loader import ConfigLoader
from services.metrics_collector import MetricsCollector


async def test_cli():
    """Test CLI configuration loading."""
    
    print("Testing ConfigLoader...\n")
    
    # Test 1: List nodes
    print("Test 1: List available nodes")
    ConfigLoader.list_available_nodes()
    
    # Test 2: Get specific node
    print("\nTest 2: Get specific node")
    node = ConfigLoader.get_node_by_name("polkadot_main")
    if node:
        print(f"✓ Found node: {node.name} -> {node.rpc_url}")
    else:
        print("✗ Node not found")
    
    # Test 3: Get all nodes
    print("\nTest 3: Get all nodes")
    all_nodes = ConfigLoader.get_all_nodes()
    print(f"✓ Found {len(all_nodes)} nodes")
    
    # Test 4: Collect metrics from all nodes
    print("\nTest 4: Collect metrics from all nodes")
    collector = MetricsCollector()
    
    try:
        for node in all_nodes:
            print(f"\nCollecting from {node.name}...")
            metrics = await collector.collect_metrics(node)
            if metrics:
                print(f"  ✓ Block height: {metrics.block_height}")
            else:
                print(f"  ✗ Failed")
    finally:
        await collector.disconnect_all()


if __name__ == "__main__":
    asyncio.run(test_cli())
