from substrateinterface import SubstrateInterface

try:
    substrate = SubstrateInterface(url="wss://rpc.polkadot.io")
    print("✓ Connected to Polkadot")
    print(f"Chain: {substrate.chain}")
    
    # get block info
    block_info = substrate.query("System", "Number")
    print(f"Current block height: {block_info.value}")
    
except Exception as e:
    print(f"✗ Error: {e}")
