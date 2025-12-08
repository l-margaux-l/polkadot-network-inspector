from datetime import datetime, timezone
from models.metrics import HealthMetrics
from services.health_checker import HealthChecker


def test_health_checker():
    """Test health checker evaluation logic."""

    print("Testing HealthChecker status evaluation...\n")

    # Test case 1: All healthy
    metrics = HealthMetrics(
        node_name="test_node_1",
        block_height=1000,
        current_block_height=1000,
        peers_count=50,
        finality_lag=3,
        time_since_last_block=5,
        rpc_response_time=50.0,
        status="",
        timestamp=datetime.now(timezone.utc),
    )
    status = HealthChecker.evaluate_metrics(metrics)
    print(f"Test 1 (all healthy): {status}")
    assert status == "healthy", f"Expected 'healthy', got '{status}'"

    # Test case 2: One warning (peers)
    metrics.peers_count = 10
    status = HealthChecker.evaluate_metrics(metrics)
    print(f"Test 2 (1 warning - peers): {status}")
    assert status == "warning", f"Expected 'warning', got '{status}'"

    # Test case 3: Two warnings
    metrics.peers_count = 10
    metrics.finality_lag = 25
    status = HealthChecker.evaluate_metrics(metrics)
    print(f"Test 3 (2 warnings): {status}")
    assert status == "critical", f"Expected 'critical', got '{status}'"

    # Test case 4: One critical
    metrics.peers_count = 50
    metrics.finality_lag = 0
    status = HealthChecker.evaluate_metrics(metrics)
    print(f"Test 4 (1 critical - finality): {status}")
    assert status == "critical", f"Expected 'critical', got '{status}'"

    print("\n✓ All HealthChecker tests passed!")


def test_report_generation():
    """Test health report generation."""

    print("\nTesting report generation...\n")

    metrics = HealthMetrics(
        node_name="polkadot_main",
        block_height=28937693,
        current_block_height=28937693,
        peers_count=0,
        finality_lag=5,
        time_since_last_block=6,
        rpc_response_time=45.0,
        status="",
        timestamp=datetime.now(timezone.utc),
    )

    metrics.status = HealthChecker.evaluate_metrics(metrics)
    report = HealthChecker.generate_report(metrics)

    print(f"Node: {report['node_name']}")
    print(f"Status: {report['status']}")
    print(f"Block height: {report['metrics']['block_height']}")
    print(f"Finality lag: {report['metrics']['finality_lag']}")
    print(f"RPC time: {report['metrics']['rpc_response_time_ms']}ms")

    print("\n✓ Report generation works!")


if __name__ == "__main__":
    test_health_checker()
    test_report_generation()
