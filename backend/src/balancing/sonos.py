"""Implements Sonos discovery and control"""
import asyncio
from config import Config
from models.speaker import Speaker
from sonos.adapter import SonosAdapter
from sonos.adapter_soco import SonosSocoAdapter
from .sonos_command import SonosCommand


class Sonos:
    """Performs discovery for Sonos speakers and sends messages to control them."""

    def __init__(self, config: Config):
        self.config = config
        self.sonos_adapter: SonosAdapter = SonosSocoAdapter()
        self.discover_loop_exiting = False
        self.control_loop_exiting = False
        self.control_queue = asyncio.Queue()

    async def discover_loop(self):
        """Starts the discover loop which runs every 15 seconds until stopped"""
        self.discover_loop_exiting = False

        while not self.discover_loop_exiting:
            speakers = self.sonos_adapter.discover()
            speaker: Speaker
            if speakers is not None:
                for speaker in speakers:
                    existing_speaker = self.config.speaker_repository.get_speaker(
                        speaker.speaker_id)
                    if existing_speaker is not None and \
                            existing_speaker.name == speaker.name and \
                            existing_speaker.ip_address == speaker.ip_address:
                        existing_speaker.times_discovery_missed = -1
                        continue
                    elif existing_speaker is not None:
                        existing_speaker.name = speaker.name
                        existing_speaker.ip_address = speaker.ip_address
                        existing_speaker.times_discovery_missed = -1
                        await self.config.speaker_repository.call_listeners()
                        continue
                    print('[Balancing] Discovered new Sonos speaker {} with uid {} at {}'
                          .format(
                              speaker.name,
                              speaker.speaker_id,
                              speaker.ip_address,
                          ))
                    await self.config.speaker_repository.add_speaker(speaker)

                for speaker in self.config.speakers:
                    speaker.times_discovery_missed += 1
            else:
                for speaker in self.config.speakers:
                    speaker.times_discovery_missed += 1

            # delete speakers that have missed 2 discovery cycles
            for speaker in self.config.speakers:
                if speaker.times_discovery_missed >= 2:
                    await self.config.speaker_repository.remove_speaker(speaker.speaker_id, delete_from_runtime_store=True)

            await asyncio.sleep(15)

    def stop_discover_loop(self):
        """Sets the flag to stop the discover loop"""
        self.discover_loop_exiting = True

    async def control_loop(self):
        """Starts the control loop which consumes all control commands in the queue"""
        self.control_loop_exiting = False
        while not self.control_loop_exiting:
            command: SonosCommand = await self.control_queue.get()
            command.run(self.sonos_adapter)
            self.control_queue.task_done()

    def stop_control_loop(self):
        """Sets the flag to stop the control loop"""
        self.control_loop_exiting = True

    def send_command(self, command: SonosCommand):
        """Adds the command to the control queue"""
        self.control_queue.put_nowait(command)
