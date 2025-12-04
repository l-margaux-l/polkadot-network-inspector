import asyncio
from datetime import datetime, timezone
from services.time_utils import TimeUtils
from models.node import Node
from services.metrics_collector import MetricsCollector


def test_time_calculation():
    """Test time since block calculation."""
    
    print("Testing time calculation...\n")
    
    current_time_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    
    test_cases = [
        (current_time_ms - 5000, 5, "healthy"),           # 5s ago
        (current_time_ms - 12000, 12, "healthy"),         # 12s ago
        (current_time_ms - 20000, 20, "warning"),         # 20s ago
        (current_time_ms - 30000, 30, "warning"),         # 30s ago
        (current_time_ms - 60000, 60, "critical"),        # 60s ago
    ]
    
    print("Block timestamp -> Time elapsed -> Expected health:")
    for block_timestamp_ms, expected_seconds, expected_health in test_cases:
        elapsed = TimeUtils.calculate_time_since_last_block(block_timestamp_ms)
        health = TimeUtils.evaluate_block_freshness(elapsed)
        
        icon = "✓" if (elapsed >= expected_seconds - 1 and elapsed <= expected_seconds + 1 and health == expected_health) else "✗"
        print(f"  {icon} {elapsed:3d}s elapsed -> {health:8s} (expected: {expected_seconds}s, {expected_health})")


async def test_with_real_node():
    """Test with actual blockchain node."""
    
    print("\n" + "="*60)
    print("Testing with real node...\n")
    
    collector = MetricsCollector()
    
    node = Node(
        name="polkadot_main",
        rpc_url="wss://rpc.polkadot.io"
    )
    
    metrics = await collector.collect_metrics(node)
    
    if metrics:
        block_health = TimeUtils.evaluate_block_freshness(metrics.time_since_last_block)
        print(f"✓ Node: {metrics.node_name}")
        print(f"  Block height: {metrics.block_height}")
        print(f"  Time since block: {metrics.time_since_last_block}s")
        print(f"  Block freshness health: {block_health}")
        print(f"  Overall status: {metrics.status}")
    else:
        print("✗ Failed to collect metrics")
    
    await collector.disconnect_all()


if __name__ == "__main__":
    test_time_calculation()
    asyncio.run(test_with_real_node())
