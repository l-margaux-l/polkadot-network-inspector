import logging
from typing import Optional
from models.node import Node
import config

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and manage node configurations."""

    @staticmethod
    def get_all_nodes() -> list[Node]:
        """Get all configured nodes."""
        return [
            Node(name=c["name"], rpc_url=c["rpc_url"])
            for c in config.NODES
        ]

    @staticmethod
    def get_node_by_name(name: str) -> Optional[Node]:
        """Get specific node by name."""
        for node_config in config.NODES:
            if node_config["name"] == name:
                return Node(
                    name=node_config["name"],
                    rpc_url=node_config["rpc_url"]
                )
        
        logger.warning(f"Node '{name}' not found in configuration")
        return None

    @staticmethod
    def list_available_nodes() -> None:
        """Print all available nodes to stdout."""
        if not config.NODES:
            print("No nodes configured")
            return

        print("\nAvailable nodes:")
        for i, node_config in enumerate(config.NODES, 1):
            print(f"  {i}. {node_config['name']} ({node_config['chain']})")
            print(f"     RPC: {node_config['rpc_url']}")
