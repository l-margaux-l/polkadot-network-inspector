from models.node import Node
from models.metrics import HealthMetrics
from datetime import datetime, timezone 

def test():
    # Create a Node
    n = Node(name="Polkadot Mainnet", rpc_url="wss://rpc.polkadot.io")
    print(n)

    # Create HealthMetrics with proper timezone-aware datetime
    metric = HealthMetrics(
        node_name=n.name,
        block_height=123456,
        current_block_height=123460,
        peers_count=12,
        finality_lag=4,
        time_since_last_block=10,
        rpc_response_time=95.2,
        status="healthy",
        timestamp=datetime.now(timezone.utc)  
    )
    print(metric)

if __name__ == "__main__":
    test()
