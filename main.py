import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import config


def main():
    """
    Main function that starts the Polkadot Network Inspector
    """
    print(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    print(f"Project root: {config.PROJECT_ROOT}")
    print(f"RPC URL: {config.POLKADOT_RPC_URL}")
    print(f"Check interval: {config.CHECK_INTERVAL_SECONDS} seconds")
    print("\n✓ Configuration loaded successfully")
    print("✓ Project structure initialized")
    
    # TODO: Implement monitoring loop in next stages
    print("\nℹ️  Stage 1.1 complete: Project initialized")


if __name__ == "__main__":
    main()
