import asyncio
from services.rpc_utils import RpcUtils
from models.node import Node
from services.metrics_collector import MetricsCollector


def test_rpc_health_evaluation():
    """Test RPC health evaluation based on response time."""
    
    print("Testing RPC health evaluation...\n")
    
    test_cases = [
        (100, "healthy"),      # 100ms - fast
        (500, "healthy"),      # 500ms - still fast
        (1000, "warning"),     # 1s - getting slow
        (2000, "warning"),     # 2s - slow
        (3000, "critical"),    # 3s - very slow
        (5000, "critical"),    # 5s - timeout-like
    ]
    
    print("Response time -> Health status:")
    for response_time_ms, expected_status in test_cases:
        actual_status = RpcUtils.evaluate_rpc_health(response_time_ms)
        formatted = RpcUtils.format_response_time(response_time_ms)
        icon = "✓" if actual_status == expected_status else "✗"
        print(f"  {icon} {formatted:10s} -> {actual_status:8s} (expected: {expected_status})")


async def test_with_real_node():
    """Test RPC measurement with actual node."""
    
    print("\n" + "="*60)
    print("Testing RPC response time measurement...\n")
    
    collector = MetricsCollector()
    
    node = Node(
        name="polkadot_main",
        rpc_url="wss://rpc.polkadot.io"
    )
    
    metrics = await collector.collect_metrics(node)
    
    if metrics:
        rpc_health = RpcUtils.evaluate_rpc_health(metrics.rpc_response_time)
        rpc_formatted = RpcUtils.format_response_time(metrics.rpc_response_time)
        
        print(f"✓ Node: {metrics.node_name}")
        print(f"  Block height: {metrics.block_height}")
        print(f"  Time since block: {metrics.time_since_last_block}s")
        print(f"  RPC response time: {rpc_formatted}")
        print(f"  RPC health: {rpc_health}")
        print(f"  Overall status: {metrics.status}")
    else:
        print("✗ Failed to collect metrics")
    
    await collector.disconnect_all()


if __name__ == "__main__":
    test_rpc_health_evaluation()
    asyncio.run(test_with_real_node())
