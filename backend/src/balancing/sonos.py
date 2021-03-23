"""Implements Sonos discovery and control"""
from time import sleep
from queue import SimpleQueue
import asyncio
from config import Config
from models.speaker import Speaker
from sonos.adapter import SonosAdapter
from sonos.adapter_soco import SonosSocoAdapter


class Sonos:
    """Performs discovery for Sonos speakers and sends messages to control them."""

    def __init__(self, config: Config):
        self.config = config
        self.sonos_adapter: SonosAdapter = SonosSocoAdapter()
        self.discover_loop_exiting = False
        self.control_loop_exiting = False
        self.control_queue = SimpleQueue()

    def discover_loop(self):
        """Starts the discover loop which runs every 15 seconds until stopped"""
        self.discover_loop_exiting = False
        asyncio.set_event_loop(asyncio.new_event_loop())
        while not self.discover_loop_exiting:
            speakers = self.sonos_adapter.discover()
            speaker: Speaker
            for speaker in speakers:
                existing_speaker = self.config.speaker_repository.get_speaker(speaker.speaker_id)
                if existing_speaker is not None and \
                        existing_speaker.name == speaker.name and \
                        existing_speaker.ip_address == speaker.ip_address:
                    continue
                elif existing_speaker is not None:
                    existing_speaker.name = speaker.name
                    existing_speaker.ip_address = speaker.ip_address
                    self.config.speaker_repository.call_listeners()
                    continue
                print('[Balancing] Discovered new Sonos speaker {} with uid {} at {}'
                      .format(
                          speaker.name,
                          speaker.speaker_id,
                          speaker.ip_address,
                      ))
                self.config.speaker_repository.add_speaker(speaker)
            sleep(15)

    def stop_discover_loop(self):
        """Sets the flag to stop the discover loop"""
        self.discover_loop_exiting = True

    def control_loop(self):
        """Starts the control loop which consumes all control commands in the queue"""
        self.control_loop_exiting = False
        while not self.control_loop_exiting:
            command = self.control_queue.get()

    def stop_control_loop(self):
        """Sets the flag to stop the control loop"""
        self.control_loop_exiting = True
