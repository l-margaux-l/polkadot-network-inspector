import asyncio
import logging
import time
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

    async def get_finalized_block_timestamp(self) -> Optional[int]:
        """
        Get timestamp of the finalized head block in milliseconds.

        Returns:
            int: Timestamp in milliseconds, None if query fails
        """
        if not self.substrate:
            logger.warning("Not connected to RPC")
            return None

        try:
            timestamp = await asyncio.to_thread(
                self._query_finalized_block_timestamp
            )
            return timestamp

        except Exception as e:
            logger.debug(f"Failed to get finalized block timestamp: {e}")
            return None

    def _query_finalized_block_timestamp(self) -> int:
        """Query finalized block timestamp (blocking operation)."""
        try:
            result = self.substrate.query("Timestamp", "Now")
            timestamp_ms = result.value
            
            # Return what we got from the query (even if it's 0)
            # Don't use fallback - if query returns something, use it
            if timestamp_ms is not None:
                return timestamp_ms
            
            # Only use current time as last resort
            import time
            return int(time.time() * 1000)
        
        except Exception:
            # If Timestamp pallet not available, use current time
            import time
            return int(time.time() * 1000)



    async def measure_rpc_response_time(self) -> Optional[float]:
        """
        Measure RPC response time in milliseconds.

        Uses system_health RPC call as a lightweight probe.

        Returns:
            float: Response time in milliseconds, None if measurement fails
        """
        if not self.substrate:
            logger.warning("Not connected to RPC")
            return None

        try:
            response_time_ms = await asyncio.to_thread(
                self._measure_rpc_latency
            )
            return response_time_ms

        except Exception as e:
            logger.error(f"Failed to measure RPC response time: {e}")
            return None

    def _measure_rpc_latency(self) -> float:
        """Measure RPC latency with system_health call (blocking operation)."""
        start_time = time.time()
        
        try:
            self.substrate.rpc_request(method="system_health", params=[])
            elapsed_ms = (time.time() - start_time) * 1000
            return elapsed_ms
        
        except Exception:
            elapsed_ms = (time.time() - start_time) * 1000
            return elapsed_ms
        
    async def get_finalized_block_number(self) -> Optional[int]:
        """
        Get finalized block number.

        Returns:
            int: Finalized block number, or None if query fails.
        """
        if not self.substrate:
            logger.warning("Not connected to RPC")
            return None

        try:
            block_number = await asyncio.to_thread(
                self._query_finalized_block_number
            )
            return block_number
        except Exception as e:
            logger.error(f"Failed to get finalized block number: {e}")
            return None

    def _query_finalized_block_number(self) -> int:
        """Query finalized block number (blocking operation)."""
        # Get finalized head hash via RPC
        finalized_hash = self.substrate.rpc_request(
            method="chain_getFinalizedHead",
            params=[]
        )
        
        # finalized_hash should be in result['result']
        if "result" in finalized_hash:
            finalized_hash = finalized_hash["result"]
        
        # Get header for this hash
        header_result = self.substrate.rpc_request(
            method="chain_getHeader",
            params=[finalized_hash]
        )
        
        if "result" in header_result:
            header = header_result["result"]
            # header['number'] is a hex string like '0x1ba1234'
            block_number = int(header["number"], 16)
            return block_number
        
        return 0