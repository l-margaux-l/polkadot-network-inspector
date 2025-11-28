class Node:
    """
    Represents a blockchain node with an assigned name and RPC URL.
    """

    def __init__(self, name: str, rpc_url: str):
        """
        Initialize a new Node instance.

        Args:
            name (str): Human-readable name for the node.
            rpc_url (str): RPC endpoint used to connect to the node.
        """
        self.name = name
        self.rpc_url = rpc_url

    def __repr__(self):
        return f"<Node name={self.name} rpc_url={self.rpc_url}>"
