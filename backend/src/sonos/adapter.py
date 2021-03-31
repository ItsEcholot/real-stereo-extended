"""Defines methods to send commands to Sonos speakers"""
from abc import ABC, abstractmethod
from typing import Set
from pathlib import Path
from socket import gethostname, gethostbyname
from models.speaker import Speaker


class SonosAdapter(ABC):
    """Defines methods to send commands to Sonos speakers"""

    def __init__(self):
        self.calibration_sound_uri = 'http://{}:{}/backend-assets/white_noise.mp3'.format(
            gethostbyname(gethostname()), 8080)

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

    @abstractmethod
    def ramp_to_volume(self, speaker: Speaker, volume: int):
        """Ramps volume to target volume for the passed Sonos speaker

        :param models.speaker.Speaker speaker: Speaker to control
        :param int volume: Volume to ramp up or down to
        """
        raise NotImplementedError()

    @abstractmethod
    def play_calibration_sound(self, speaker: Speaker):
        """Plays the calibration sound on all speakers which are part
        of the passed speakers group.

        :param models.speaker.Speaker speaker: Speaker
        """
        raise NotImplementedError()
