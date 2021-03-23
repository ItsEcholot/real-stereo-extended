"""Defines methods to send commands to Sonos speakers"""
from abc import ABC, abstractmethod
from typing import Set
from models.speaker import Speaker


class SonosAdapter(ABC):
    """Defines methods to send commands to Sonos speakers"""

    def __init__(self):
        pass

    @abstractmethod
    def discover(self) -> Set[Speaker]:
        """Discovers local Sonos speakers

        :returns: Set of discovered speakers
        :rtype: set[models.speaker.Speaker]
        """
        raise NotImplementedError()
