import sys
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import unittest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from models.metrics import HealthMetrics
from services.database import MetricsDB


class TestMetricsDB(unittest.TestCase):
    
    def setUp(self):
        """Create a temporary in-memory database for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = MetricsDB(db_path=str(Path(self.temp_dir.name) / "test.db"))
        self.db.create_tables()
    
    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()
    
    def test_create_tables(self):
        """Test that database tables are created successfully."""
        self.assertTrue(Path(self.db.db_path).exists())
        print("✓ Table creation passed")
    
    def test_insert_single_metric(self):
        """Test inserting a single metric record."""
        metric = HealthMetrics(
            timestamp=datetime.now(),
            node_name="polkadot-validator-1",
            block_height=2150000,
            current_block_height=2150005,
            peers_count=42,
            finality_lag=5,
            time_since_last_block=6,
            rpc_response_time=125.5,
            status="healthy"
        )
        
        self.db.insert_metrics(metric)
        count = self.db.count_records("polkadot-validator-1")
        
        self.assertEqual(count, 1)
        print("✓ Single insert passed")
    
    def test_insert_batch(self):
        """Test inserting multiple metrics in batch."""
        metrics = [
            HealthMetrics(
                timestamp=datetime.now() - timedelta(hours=i),
                node_name="polkadot-validator-1",
                block_height=2150000 - i,
                current_block_height=2150005 - i,
                peers_count=42 - i,
                finality_lag=5,
                time_since_last_block=6,
                rpc_response_time=125.5,
                status="healthy"
            )
            for i in range(5)
        ]
        
        self.db.insert_batch(metrics)
        count = self.db.count_records("polkadot-validator-1")
        
        self.assertEqual(count, 5)
        print("✓ Batch insert passed")
    
    def test_get_metrics_for_node(self):
        """Test retrieving metrics for a specific node."""
        now = datetime.now()
        metrics = [
            HealthMetrics(
                timestamp=now - timedelta(hours=i),
                node_name="polkadot-validator-1",
                block_height=2150000 - i,
                current_block_height=2150005 - i,
                peers_count=42,
                finality_lag=5,
                time_since_last_block=6,
                rpc_response_time=125.5,
                status="healthy"
            )
            for i in range(3)
        ]
        
        self.db.insert_batch(metrics)
        retrieved = self.db.get_metrics_for_node("polkadot-validator-1", hours=24)
        
        self.assertEqual(len(retrieved), 3)
        self.assertEqual(retrieved[0].block_height, 2150000)
        print("✓ Get metrics for node passed")
    
    def test_get_latest_for_node(self):
        """Test retrieving the latest metric for a node."""
        now = datetime.now()
        metrics = [
            HealthMetrics(
                timestamp=now - timedelta(hours=i),
                node_name="polkadot-validator-1",
                block_height=2150000 - i,
                current_block_height=2150005 - i,
                peers_count=42,
                finality_lag=5,
                time_since_last_block=6,
                rpc_response_time=125.5,
                status="healthy"
            )
            for i in range(3)
        ]
        
        self.db.insert_batch(metrics)
        latest = self.db.get_latest_for_node("polkadot-validator-1")
        
        self.assertIsNotNone(latest)
        self.assertEqual(latest.block_height, 2150000)
        print("✓ Get latest metric passed")
    
    def test_get_all_nodes(self):
        """Test retrieving all unique nodes."""
        metrics = [
            HealthMetrics(
                timestamp=datetime.now(),
                node_name=f"node-{i}",
                block_height=2150000,
                current_block_height=2150005,
                peers_count=42,
                finality_lag=5,
                time_since_last_block=6,
                rpc_response_time=125.5,
                status="healthy"
            )
            for i in range(3)
        ]
        
        self.db.insert_batch(metrics)
        nodes = self.db.get_all_nodes()
        
        self.assertEqual(len(nodes), 3)
        self.assertIn("node-0", nodes)
        print("✓ Get all nodes passed")


if __name__ == '__main__':
    unittest.main()
