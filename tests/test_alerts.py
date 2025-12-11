import sys
from pathlib import Path
from datetime import datetime
import unittest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from models.metrics import HealthMetrics
from services.alerts import AlertSystem


class TestAlertSystem(unittest.TestCase):
    
    def setUp(self):
        """Create baseline healthy metrics for testing."""
        self.baseline_metrics = HealthMetrics(
            timestamp=datetime.now(),
            node_name="test-node",
            block_height=2150000,
            current_block_height=2150005,
            peers_count=50,
            finality_lag=5,
            time_since_last_block=10,
            rpc_response_time=100.0,
            status="healthy"
        )
    
    def test_no_alerts_for_healthy_metrics(self):
        """Test that healthy metrics generate no alerts."""
        alerts = AlertSystem.check_alerts(self.baseline_metrics)
        self.assertEqual(len(alerts), 0)
        print("✓ No alerts for healthy metrics")
    
    def test_alert_high_finality_lag(self):
        """Test alert triggered by high finality lag."""
        metrics = HealthMetrics(
            timestamp=datetime.now(),
            node_name="test-node",
            block_height=2150000,
            current_block_height=2150100,
            peers_count=50,
            finality_lag=75,
            time_since_last_block=10,
            rpc_response_time=100.0,
            status="critical"
        )
        
        alerts = AlertSystem.check_alerts(metrics)
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].level, "critical")
        self.assertEqual(alerts[0].metric_name, "finality_lag")
        self.assertIn("75", alerts[0].message)
        print("✓ Alert triggered for high finality lag")
    
    def test_alert_slow_rpc(self):
        """Test alert triggered by slow RPC response."""
        metrics = HealthMetrics(
            timestamp=datetime.now(),
            node_name="test-node",
            block_height=2150000,
            current_block_height=2150005,
            peers_count=50,
            finality_lag=5,
            time_since_last_block=10,
            rpc_response_time=6000.0,
            status="warning"
        )
        
        alerts = AlertSystem.check_alerts(metrics)
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].level, "critical")
        self.assertEqual(alerts[0].metric_name, "rpc_response_time")
        self.assertIn("6000", alerts[0].message)
        print("✓ Alert triggered for slow RPC")
    
    def test_alert_low_peers(self):
        """Test alert triggered by low peer count."""
        metrics = HealthMetrics(
            timestamp=datetime.now(),
            node_name="test-node",
            block_height=2150000,
            current_block_height=2150005,
            peers_count=3,
            finality_lag=5,
            time_since_last_block=10,
            rpc_response_time=100.0,
            status="warning"
        )
        
        alerts = AlertSystem.check_alerts(metrics)
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].level, "warning")
        self.assertEqual(alerts[0].metric_name, "peers_count")
        self.assertIn("3", alerts[0].message)
        print("✓ Alert triggered for low peers")
    
    def test_alert_stale_block(self):
        """Test alert triggered by stale block (old last block)."""
        metrics = HealthMetrics(
            timestamp=datetime.now(),
            node_name="test-node",
            block_height=2150000,
            current_block_height=2150005,
            peers_count=50,
            finality_lag=5,
            time_since_last_block=90,
            rpc_response_time=100.0,
            status="warning"
        )
        
        alerts = AlertSystem.check_alerts(metrics)
        
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].level, "warning")
        self.assertEqual(alerts[0].metric_name, "block_age")
        self.assertIn("90", alerts[0].message)
        print("✓ Alert triggered for stale block")
    
    def test_multiple_alerts(self):
        """Test that multiple alerts are generated when multiple thresholds exceeded."""
        metrics = HealthMetrics(
            timestamp=datetime.now(),
            node_name="test-node",
            block_height=2150000,
            current_block_height=2150150,
            peers_count=2,
            finality_lag=75,
            time_since_last_block=120,
            rpc_response_time=7000.0,
            status="critical"
        )
        
        alerts = AlertSystem.check_alerts(metrics)
        
        self.assertEqual(len(alerts), 4)
        metric_names = {alert.metric_name for alert in alerts}
        expected = {"finality_lag", "rpc_response_time", "peers_count", "block_age"}
        self.assertEqual(metric_names, expected)
        print("✓ Multiple alerts triggered correctly")
    
    def test_alert_structure(self):
        """Test that Alert dataclass has required fields."""
        metrics = HealthMetrics(
            timestamp=datetime.now(),
            node_name="test-node",
            block_height=2150000,
            current_block_height=2150100,
            peers_count=50,
            finality_lag=75,
            time_since_last_block=10,
            rpc_response_time=100.0,
            status="critical"
        )
        
        alerts = AlertSystem.check_alerts(metrics)
        alert = alerts[0]
        
        self.assertTrue(hasattr(alert, "level"))
        self.assertTrue(hasattr(alert, "message"))
        self.assertTrue(hasattr(alert, "timestamp"))
        self.assertTrue(hasattr(alert, "node_name"))
        self.assertTrue(hasattr(alert, "metric_name"))
        print("✓ Alert structure is correct")


if __name__ == '__main__':
    unittest.main()
