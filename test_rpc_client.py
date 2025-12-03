import asyncio
from services.rpc_client import PolkadotRPCClient


async def test_rpc():
    """Test RPC client connection and basic queries."""
    
    client = PolkadotRPCClient(rpc_url="wss://rpc.polkadot.io", timeout=10)
    
    print("Connecting to Polkadot RPC...")
    connected = await client.connect()
    
    if not connected:
        print("✗ Failed to connect")
        return
    
    print("✓ Connected successfully")
    
    # Get chain head
    print("\nGetting chain head...")
    chain_head = await client.get_chain_head()
    if chain_head:
        print(f"✓ Block height: {chain_head['block_height']}")
        print(f"✓ Block hash: {chain_head['block_hash'][:20]}...")
    else:
        print("✗ Failed to get chain head")
    
    # Get peers count
    print("\nGetting peers count...")
    peers = await client.get_peers_count()
    if peers is not None:
        if peers > 0:
            print(f"✓ Peers: {peers}")
        else:
            print("⚠ Peers: 0 (system_peers RPC may not be available on public nodes)")
    else:
        print("⚠ Failed to get peers count (method may not be available)")
    
    # Disconnect
    client.disconnect()
    print("\n✓ Test completed")


if __name__ == "__main__":
    asyncio.run(test_rpc())
