from dataclasses import dataclass
from datetime import datetime
from typing import List

from models.metrics import HealthMetrics
from config import (
    ALERT_THRESHOLD_FINALITY_LAG,
    ALERT_THRESHOLD_RPC_RESPONSE_TIME_MS,
    ALERT_THRESHOLD_PEERS_MIN,
    ALERT_THRESHOLD_BLOCK_AGE_SECONDS,
)


@dataclass
class Alert:
    """Represents a single alert triggered by metric thresholds."""
    
    level: str  # "info", "warning", "critical"
    message: str
    timestamp: datetime
    node_name: str
    metric_name: str


class AlertSystem:
    """Generate alerts based on HealthMetrics thresholds."""
    
    @staticmethod
    def check_alerts(metrics: HealthMetrics) -> List[Alert]:
        """
        Check metrics against alert thresholds and generate alerts.
        
        Args:
            metrics: HealthMetrics object with collected data
            
        Returns:
            List of Alert objects (empty if no alerts)
        """
        alerts = []
        
        if AlertSystem._check_finality_lag(metrics):
            alert = AlertSystem._create_alert_finality_lag(metrics)
            alerts.append(alert)
        
        if AlertSystem._check_rpc_response_time(metrics):
            alert = AlertSystem._create_alert_rpc_response_time(metrics)
            alerts.append(alert)
        
        if AlertSystem._check_peers_count(metrics):
            alert = AlertSystem._create_alert_peers_count(metrics)
            alerts.append(alert)
        
        if AlertSystem._check_block_age(metrics):
            alert = AlertSystem._create_alert_block_age(metrics)
            alerts.append(alert)
        
        return alerts
    
    @staticmethod
    def _check_finality_lag(metrics: HealthMetrics) -> bool:
        """Check if finality lag exceeds threshold."""
        return metrics.finality_lag > ALERT_THRESHOLD_FINALITY_LAG
    
    @staticmethod
    def _check_rpc_response_time(metrics: HealthMetrics) -> bool:
        """Check if RPC response time exceeds threshold."""
        return metrics.rpc_response_time > ALERT_THRESHOLD_RPC_RESPONSE_TIME_MS
    
    @staticmethod
    def _check_peers_count(metrics: HealthMetrics) -> bool:
        """Check if peers count is below minimum threshold."""
        return metrics.peers_count < ALERT_THRESHOLD_PEERS_MIN
    
    @staticmethod
    def _check_block_age(metrics: HealthMetrics) -> bool:
        """Check if time since last block exceeds threshold."""
        return metrics.time_since_last_block > ALERT_THRESHOLD_BLOCK_AGE_SECONDS
    
    @staticmethod
    def _create_alert_finality_lag(metrics: HealthMetrics) -> Alert:
        """Create alert for high finality lag."""
        return Alert(
            level="critical",
            message=f"Finality lag is {metrics.finality_lag} blocks "
                   f"(threshold: {ALERT_THRESHOLD_FINALITY_LAG})",
            timestamp=metrics.timestamp,
            node_name=metrics.node_name,
            metric_name="finality_lag"
        )
    
    @staticmethod
    def _create_alert_rpc_response_time(metrics: HealthMetrics) -> Alert:
        """Create alert for slow RPC response."""
        return Alert(
            level="critical",
            message=f"RPC response time is {metrics.rpc_response_time:.0f}ms "
                   f"(threshold: {ALERT_THRESHOLD_RPC_RESPONSE_TIME_MS}ms)",
            timestamp=metrics.timestamp,
            node_name=metrics.node_name,
            metric_name="rpc_response_time"
        )
    
    @staticmethod
    def _create_alert_peers_count(metrics: HealthMetrics) -> Alert:
        """Create alert for low peer count."""
        return Alert(
            level="warning",
            message=f"Peer count is {metrics.peers_count} "
                   f"(minimum: {ALERT_THRESHOLD_PEERS_MIN})",
            timestamp=metrics.timestamp,
            node_name=metrics.node_name,
            metric_name="peers_count"
        )
    
    @staticmethod
    def _create_alert_block_age(metrics: HealthMetrics) -> Alert:
        """Create alert for stale blocks."""
        return Alert(
            level="warning",
            message=f"Time since last block: {metrics.time_since_last_block}s "
                   f"(threshold: {ALERT_THRESHOLD_BLOCK_AGE_SECONDS}s)",
            timestamp=metrics.timestamp,
            node_name=metrics.node_name,
            metric_name="block_age"
        )
