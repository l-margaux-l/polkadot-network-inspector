import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
import tempfile
import unittest

from models.metrics import HealthMetrics
from services.csv_exporter import export_metrics_to_csv, load_metrics_from_csv

class TestCsvExporter(unittest.TestCase):
    
    def test_export_and_load(self):
        """Test full cycle: export metrics to CSV and load them back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "metrics.csv"

            original_metrics = [
                HealthMetrics(
                    timestamp=datetime(2025, 12, 10, 10, 30, 0),
                    node_name="polkadot-validator-1",
                    block_height=1000,
                    current_block_height=1005,
                    peers_count=42,
                    finality_lag=5,
                    time_since_last_block=6,
                    rpc_response_time=120.5, # ms
                    status="healthy"
                ),
                HealthMetrics(
                    timestamp=datetime(2025, 12, 10, 10, 35, 0),
                    node_name="polkadot-validator-1",
                    block_height=1001,
                    current_block_height=1006,
                    peers_count=40,
                    finality_lag=5,
                    time_since_last_block=12,
                    rpc_response_time=145.2, # ms
                    status="warning"
                ),
            ]

            export_metrics_to_csv(original_metrics, str(filepath))

            self.assertTrue(filepath.exists(), "CSV file was not created")

            loaded_metrics = load_metrics_from_csv(str(filepath))

            self.assertEqual(len(loaded_metrics), 2)
            
            m1 = loaded_metrics[0]
            self.assertEqual(m1.node_name, "polkadot-validator-1")
            self.assertEqual(m1.block_height, 1000)
            self.assertEqual(m1.peers_count, 42)
            self.assertEqual(m1.time_since_last_block, 6)
            self.assertEqual(m1.rpc_response_time, 120.5)
            self.assertEqual(m1.status, "healthy")
            self.assertEqual(m1.timestamp, datetime(2025, 12, 10, 10, 30, 0))

            print("✓ Export/Import cycle passed")

    def test_export_empty_list(self):
        """Test that exporting empty list does nothing safely."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "metrics.csv"
            export_metrics_to_csv([], str(filepath))
            self.assertFalse(filepath.exists(), "File should not be created for empty list")
            print("✓ Empty list test passed")

if __name__ == '__main__':
    unittest.main()
