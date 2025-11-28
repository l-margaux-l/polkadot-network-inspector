from dataclasses import dataclass
from datetime import datetime

@dataclass
class HealthMetrics:
    """
    Data class representing health and performance metrics for a blockchain node.
    """
    node_name: str
    block_height: int
    current_block_height: int   # Current reference block height
    peers_count: int
    finality_lag: int
    time_since_last_block: int  # In seconds
    rpc_response_time: float    # In milliseconds
    status: str                 # "healthy", "warning", or "critical"
    timestamp: datetime