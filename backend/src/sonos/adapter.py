"""Defines methods to send commands to Sonos speakers"""
from abc import ABC, abstractmethod
from typing import Set
from pathlib import Path
from models.speaker import Speaker

ASSETS_PATH: Path = (Path(__file__).resolve().parent / '..' / '..' / 'assets').resolve()
CALIBRATION_SOUND_PATH: Path = ASSETS_PATH / 'white_noise.mp3'

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
