"""Implements Sonos discovery and control"""

import asyncio
from config import Config
from models.speaker import Speaker
import soco


class Sonos:
    """Performs discovery for Sonos speakers and sends messages to control them."""

    def __init__(self, config: Config):
        self.discover_loop_exiting = False
        self.config = config

    async def discover_loop(self):
        """Starts the discover loop which runs every 15 seconds until stopped"""
        self.discover_loop_exiting = False

        while not self.discover_loop_exiting:
            players: set[soco.SoCo] = soco.discover()
            if players is not None:
                for player in players:
                    existing_speaker = self.config.speaker_repository.get_speaker(player.uid)
                    if existing_speaker is not None and existing_speaker.name == player.player_name:
                        continue
                    elif existing_speaker is not None:
                        existing_speaker.name = player.player_name
                        await self.config.speaker_repository.call_listeners()
                        continue
                    print('[Balancing] Discovered new Sonos player {} with uid {} at {}, Coordinator: {}'
                          .format(
                              player.player_name,
                              player.uid,
                              player.ip_address,
                              player.is_coordinator
                          ))
                    speaker = Speaker(speaker_id=player.uid, name=player.player_name)
                    await self.config.speaker_repository.add_speaker(speaker)
            await asyncio.sleep(15)

    def stop_discover_loop(self):
        """Sets the flag to stop the discover loop"""
        self.discover_loop_exiting = True
