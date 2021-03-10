"""Node repository."""

from models.node import Node
from .repository import Repository


class NodeRepository(Repository):
    """Node repository.

    :param config.Config config: Config instance
    """

    def __init__(self, config):
        super().__init__()
        self.config = config

    def get_node(self, node_id: int, fail: bool = False) -> Node:
        """Returns the node with the specified id.

        :param int node_id: Node id
        :param bool fail: If true, a ValueError will be raised if the node could not be found
        :returns: Node or None if no node could be found with this id
        :rtype: models.node.Node
        """
        node = next(filter(lambda r: r.node_id ==
                           node_id, self.config.nodes), None)

        if fail and node is None:
            raise ValueError('Node with id ' + str(node_id) +
                             ' could not be found')

        return node

    def get_node_by_name(self, name: str) -> Node:
        """Returns the node with the given name.

        :param str name: Node name
        :returns: Node or None if no node could be found with this name
        :rtype: models.node.Node
        """
        return next(filter(lambda n: n.name == name, self.config.nodes), None)

    def get_node_by_ip(self, ip_address: str) -> Node:
        """Returns the node with the given ip address.

        :param str ip: Node ip address
        :returns: Node or None if no node could be found with this ip address
        :rtype: models.node.Node
        """
        return next(filter(lambda n: n.ip_address == ip_address, self.config.nodes), None)

    def add_node(self, node: Node) -> None:
        """Adds a new node and stores the config file.

        :param models.node.Node node: Node instance
        """
        # assign a new id if the node does not yet have one
        if node.node_id is None:
            nodes_sorted = sorted(
                self.config.nodes, key=lambda r: r.node_id, reverse=True)
            node.node_id = 1 if nodes_sorted is None or len(
                nodes_sorted) == 0 else nodes_sorted[0].node_id + 1

        # add reference to room if necessary
        if node.room is not None:
            if node.room not in node.room.nodes:
                node.room.nodes.append(node)
            self.config.room_repository.call_listeners()

        self.config.nodes.append(node)
        self.call_listeners()

    def remove_node(self, node_id: int) -> bool:
        """Removes a node and stores the config file.

        :param int node_id: Node id
        :returns: False if no node could be found with this id and so no removal was possible,
                  otherwise True.
        :rtype: bool
        """
        node = self.get_node(node_id)

        if node is not None:
            # remove node
            self.config.nodes.remove(node)

            # remove reference on room
            if node.room is not None:
                node.room.nodes.remove(node)
                self.config.room_repository.call_listeners()

            self.call_listeners()

            return True

        return False

    def to_json(self) -> dict:
        """Returns the list of all nodes in JSON serializable objects.

        :returns: JSON serializable object
        :rtype: dict
        """
        return list(map(lambda node: node.to_json(True, live=True), self.config.nodes))
