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

    @abstractmethod
    def set_volume(self, speaker: Speaker, volume: int):
        """Sets volume for passed Sonos speaker

        :param models.speaker.Speaker speaker: Speaker to control
        :param int volume: Volume to set
        """
        raise NotImplementedError()

    def ramp_to_volume(self, speaker: Speaker, volume: int):
        """Ramps volume to target volume for the passed Sonos speaker

        :param models.speaker.Speaker speaker: Speaker to control
        :param int volume: Volume to ramp up or down to
        """
        raise NotImplementedError()
