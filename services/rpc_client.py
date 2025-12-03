import asyncio
import logging
from typing import Optional, Dict, Any

from substrateinterface import SubstrateInterface

logger = logging.getLogger(__name__)


class PolkadotRPCClient:
    """RPC client for Polkadot blockchain."""

    def __init__(self, rpc_url: str, timeout: int = 10):
        """
        Args:
            rpc_url: WebSocket URL of RPC endpoint.
            timeout: Request timeout in seconds.
        """
        self.rpc_url = rpc_url
        self.timeout = timeout
        self.substrate: Optional[SubstrateInterface] = None

    async def connect(self) -> bool:
        """Connect to Polkadot RPC endpoint. Returns True if successful."""
        try:
            # asyncio.to_thread prevents blocking the event loop
            self.substrate = await asyncio.to_thread(
                SubstrateInterface,
                url=self.rpc_url
            )
            logger.info(f"Connected to {self.rpc_url}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to {self.rpc_url}: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from RPC endpoint."""
        if self.substrate:
            self.substrate.close()
            logger.info("Disconnected from RPC")

    async def get_chain_head(self) -> Optional[Dict[str, Any]]:
        """Get current block height and hash. Returns None if fails."""
        if not self.substrate:
            logger.warning("Not connected to RPC")
            return None

        try:
            block_number = await asyncio.to_thread(
                self._query_block_number
            )

            block_hash = await asyncio.to_thread(
                self._query_block_hash,
                block_number
            )

            return {
                "block_height": block_number,
                "block_hash": block_hash
            }

        except Exception as e:
            logger.error(f"Failed to get chain head: {e}")
            return None

    def _query_block_number(self) -> int:
        """Query current block number from storage."""
        result = self.substrate.query("System", "Number")
        return result.value

    def _query_block_hash(self, block_number: int) -> str:
        """Query block hash by block number."""
        result = self.substrate.query("System", "BlockHash", [block_number])
        return result.value

    async def get_peers_count(self) -> Optional[int]:
        """Get number of connected peers. Returns None if fails."""
        if not self.substrate:
            logger.warning("Not connected to RPC")
            return None

        try:
            peers = await asyncio.to_thread(
                self._get_peers_rpc
            )
            return peers

        except Exception as e:
            logger.error(f"Failed to get peers count: {e}")
            return None

    def _get_peers_rpc(self) -> int:
        """Get peers count via RPC. Returns 0 if unavailable."""
        try:
            result = self.substrate.rpc_request(
                method="system_peers",
                params=[]
            )

            if "result" in result:
                return len(result["result"])

            return 0

        except Exception as e:
            logger.debug(f"system_peers unavailable (expected on public RPC): {e}")
            return 0

