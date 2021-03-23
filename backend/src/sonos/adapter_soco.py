"""Defines methods to send commands to Sonos speakers using the soco library"""
from typing import Set
from models.speaker import Speaker
import soco
from .adapter import SonosAdapter


class SonosSocoAdapter(SonosAdapter):
    """Defines methods to send commands to Sonos speakers using the soco library"""

    def discover(self) -> Set[Speaker]:
        """Discovers local Sonos speakers

        :returns: Set of discovered speakers
        :rtype: set[models.speaker.Speaker]
        """
        speakers = set()
        speaker: soco.SoCo
        for speaker in soco.discover():
            speakers.add(Speaker(speaker_id=speaker.uid,
                                 name=speaker.player_name, ip_address=speaker.ip_address))
        return speakers

    def set_volume(self, speaker: Speaker, volume: int):
        """Sets volume for passed Sonos speaker

        :param models.speaker.Speaker speaker: Speaker to control
        :param int volume: Volume to set
        """
        soco_instance = soco.SoCo(speaker.ip_address)
        soco_instance.volume = volume

    def ramp_to_volume(self, speaker: Speaker, volume: int):
        """Ramps volume to target volume for the passed Sonos speaker

        :param models.speaker.Speaker speaker: Speaker to control
        :param int volume: Volume to ramp up or down to
        """
        soco_instance = soco.SoCo(speaker.ip_address)
        soco_instance.ramp_to_volume(volume)
