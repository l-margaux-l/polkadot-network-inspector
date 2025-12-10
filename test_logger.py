import json
from datetime import datetime, timezone
from pathlib import Path

from models.metrics import HealthMetrics
from services.logger import setup_logger, log_metrics


def test_logger():
    """Test logger setup and metrics logging."""

    print("Testing logger setup...\n")

    # Setup logger
    logger = setup_logger("test-logger", log_dir="test_logs")

    print("✓ Logger created")

    # Create test metrics
    metrics = HealthMetrics(
        node_name="test_node",
        block_height=28978279,
        current_block_height=28978279,
        peers_count=15,
        finality_lag=4,
        time_since_last_block=5,
        rpc_response_time=35.0,
        status="healthy",
        timestamp=datetime.now(timezone.utc),
    )

    # Log metrics
    log_metrics(logger, metrics)

    print("✓ Metrics logged")

    # Read and verify log file
    log_file = Path("test_logs/inspector.log")
    
    if log_file.exists():
        print(f"✓ Log file created: {log_file}")

        with open(log_file, "r") as f:
            lines = f.readlines()

        print(f"✓ Log file contains {len(lines)} lines")

        # Parse last line (should be metrics log)
        if lines:
            last_line = lines[-1]
            try:
                log_entry = json.loads(last_line)
                print(f"✓ Log entry is valid JSON")
                print(f"  Event: {log_entry.get('level', 'unknown')}")
                print(f"  Timestamp: {log_entry.get('timestamp', 'unknown')}")

                # Check if metrics are in the message
                message = log_entry.get('message', '')
                if 'metrics_collected' in message:
                    metrics_data = json.loads(message)
                    print(f"  Node: {metrics_data['node']}")
                    print(f"  Status: {metrics_data['status']}")
                    print(f"  Block height: {metrics_data['metrics']['block_height']}")

            except json.JSONDecodeError:
                print("✗ Failed to parse log entry as JSON")
    else:
        print(f"✗ Log file not created")

    # Cleanup
    import shutil
    if Path("test_logs").exists():
        shutil.rmtree("test_logs")
        print("\n✓ Cleanup completed")


if __name__ == "__main__":
    test_logger()
