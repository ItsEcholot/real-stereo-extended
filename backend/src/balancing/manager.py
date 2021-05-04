"""Handles sonos discovery and control."""

import asyncio
from time import time
from typing import List
from config import Config
from models.room import Room
from models.speaker import Speaker
from .sonos import Sonos
from .sonos_command import SonosVolumeCommand


class BalancingManager:
    """The BalancingManager controls Sonos speaker discovery and control threads"""

    def __init__(self, config: Config):
        self.config = config
        self.sonos = Sonos(config)
        self.previous_config_value = self.config.balance
        self.previous_volumes = {}
        self.master_ip_addresses = {}
        self.room_info = {}
        self.balances_api_controller = None

        self.config.setting_repository.register_listener(self.on_settings_changed)

    async def start_discovery(self) -> None:
        """Start the discovery loop"""
        print('[Balancing] Starting sonos discovery loop')
        await self.sonos.discover_loop()

    def stop_discovery(self) -> None:
        """Stop the discovery loop"""
        print('[Balancing] Stopping sonos discovery loop')
        self.sonos.stop_discover_loop()

    async def start_control(self) -> None:
        """Start the control loop"""
        print('[Balancing] Starting sonos control loop')
        await self.sonos.control_loop()

    def stop_control(self) -> None:
        """Stop the control loop"""
        print('[Balancing] Stopping sonos control loop')
        self.sonos.stop_control_loop()

    async def start_balancing(self) -> None:
        """Starts the speaker balancing"""
        print('[Balancing] Starting balancing')

        # get user set volume for all speakers
        room_volumes = {}
        for speaker in self.config.speakers:
            # subscribe to sonos events once per room
            if speaker.room.room_id not in self.master_ip_addresses:
                (_, master_ip_address) = await self.sonos.sonos_adapter.subscribe(speaker, self.on_sonos_event(speaker.room))
                self.master_ip_addresses[speaker.room.room_id] = master_ip_address

            if speaker.room.room_id not in room_volumes:
                room_volumes[speaker.room.room_id] = []
                self.room_info[speaker.room.room_id] = {
                    'master_ip_address': self.master_ip_addresses[speaker.room.room_id],
                    'master_index': 0,
                    'volume_confirmed': True,
                    'current_volume': None,
                    'next_volume': None,
                    'last_volume_change': 0,
                }
            room_volumes[speaker.room.room_id].append(self.sonos.sonos_adapter.get_volume(speaker))

        # calculate average volume for each room
        for room in self.config.rooms:
            if room.room_id in room_volumes:
                room.user_volume = sum(room_volumes[room.room_id]) / len(room_volumes[room.room_id])

    async def stop_balancing(self) -> None:
        """Stopps the speaker balancing"""
        print('[Balancing] Stopping balancing')

        # reset speaker volumes for all rooms
        for room in self.config.rooms:
            speaker_volumes = []
            for _ in room.volume_interpolation.speakers:
                speaker_volumes.append(room.user_volume)

            # reset volume
            command = SonosVolumeCommand(room.volume_interpolation.speakers, speaker_volumes)
            self.sonos.send_command(command)

            # cleanup balancing info
            if room.room_id in self.room_info:
                del self.room_info[room.room_id]

        self.previous_volumes = {}

    async def balance_room(self, room: Room) -> None:
        """Balances the speakers within a room

        :param models.room.Room room: Room which should be balanced"""
        if not self.config.balance or room.room_id not in self.room_info:
            return

        speaker_volumes = []

        for index, speaker in enumerate(room.volume_interpolation.speakers):
            perceived_volume = room.volume_interpolation.calculate_perceived_volume(speaker)
            speaker_volume = room.volume_interpolation.calculate_speaker_volume(perceived_volume)
            speaker_volumes.append(speaker_volume)
            if self.room_info[speaker.room.room_id]['master_ip_address'] == speaker.ip_address and \
                    index != self.room_info[speaker.room.room_id]['master_index']:
                self.room_info[speaker.room.room_id]['master_index'] = index

        if self.room_info[room.room_id]['current_volume'] is None or \
                self.room_info[room.room_id]['current_volume'] != speaker_volumes:
            # if the volume change is already confirmed by the speaker, set the next one
            if self.room_info[room.room_id]['volume_confirmed'] or \
                    self.room_info[room.room_id]['last_volume_change'] + 3 < time():
                self.send_volume_command(room, room.volume_interpolation.speakers, speaker_volumes)
            # otherwise, queue it until it gets confirmed
            else:
                self.room_info[room.room_id]['next_volume'] = (room.volume_interpolation.speakers,
                                                               speaker_volumes)

            if self.balances_api_controller is not None:
                await self.balances_api_controller.send_balances(room.volume_interpolation.speakers,
                                                                 speaker_volumes)

    async def on_settings_changed(self) -> None:
        """Update the balancing status when the settings have changed."""
        if self.config.balance and self.config.balance != self.previous_config_value:
            await self.start_balancing()
        elif not self.config.balance and self.config.balance != self.previous_config_value:
            await self.stop_balancing()

        self.previous_config_value = self.config.balance

    def send_volume_command(self, room: Room, speakers: List[Speaker], volumes: List[int]) -> None:
        """Sends a volume command to sonos

        :param models.room.Room room: Room in which the volume gets changed
        :param List[Speaker] speakers: List of speakers
        :param List[int] volumes: List of volumes for the speakers at the same indices
        """
        self.room_info[room.room_id]['current_volume'] = volumes
        self.room_info[room.room_id]['volume_confirmed'] = False
        self.room_info[room.room_id]['last_volume_change'] = time()

        command = SonosVolumeCommand(speakers, volumes)
        self.sonos.send_command(command)

    def on_sonos_event(self, room: Room) -> callable:
        """Handles sonos events for the given room

        :param models.room.Room room: Room
        """
        def handle_event(event):
            if room.room_id not in self.room_info or \
                    self.room_info[room.room_id]['current_volume'] is None:
                return

            # check if the event does not contain a volume change
            if 'volume' not in event.variables or 'Master' not in event.variables['volume']:
                return

            # check if this event confirms the last volume change of real stereo
            event_volume = int(event.variables['volume']['Master'])
            last_change_volume = self.room_info[room.room_id]['current_volume']
            last_change_master_volume = last_change_volume[self.room_info[room.room_id]['master_index']]
            if last_change_master_volume == event_volume and \
                    not self.room_info[room.room_id]['volume_confirmed']:
                self.room_info[room.room_id]['volume_confirmed'] = True

                # check if another change is already queued
                if self.room_info[room.room_id]['next_volume'] is not None:
                    speakers, volumes = self.room_info[room.room_id]['next_volume']
                    self.room_info[room.room_id]['next_volume'] = None
                    self.send_volume_command(room, speakers, volumes)
            else:
                room.user_volume = event_volume

                # clear queued volume if there is one
                self.room_info[room.room_id]['next_volume'] = None

                asyncio.create_task(self.balance_room(room))

        return handle_event
