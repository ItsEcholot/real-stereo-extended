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
