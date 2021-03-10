"""Available node types."""

from enum import Enum


class NodeType(Enum):
    """Available node types."""

    UNCONFIGURED = 0
    MASTER = 1
    TRACKING = 2
