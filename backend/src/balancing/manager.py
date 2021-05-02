"""Handles sonos discovery and control."""

from config import Config
from models.room import Room
from .sonos import Sonos
from .sonos_command import SonosVolumeCommand


class BalancingManager:
    """The BalancingManager controls Sonos speaker discovery and control threads"""

    def __init__(self, config: Config):
        self.config = config
        self.sonos = Sonos(config)
        self.previous_config_value = self.config.balance

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

    def start_balancing(self) -> None:
        """Starts the speaker balancing"""
        print('[Balancing] Starting balancing')

        # get user set volume for all speakers
        room_volumes = {}
        for speaker in self.config.speakers:
            if speaker.room.room_id not in room_volumes:
                room_volumes[speaker.room.room_id] = []
            room_volumes[speaker.room.room_id].append(self.sonos.sonos_adapter.get_volume(speaker))

        # calculate average volume for each room
        for room in self.config.rooms:
            if room.room_id in room_volumes:
                room.user_volume = sum(room_volumes[room.room_id]) / len(room_volumes[room.room_id])

    def stop_balancing(self) -> None:
        """Stopps the speaker balancing"""
        print('[Balancing] Stopping balancing')

        # reset speaker volumes for all rooms
        for room in self.config.rooms:
            speaker_volumes = []
            for _ in room.volume_interpolation.speakers:
                speaker_volumes.append(room.user_volume)

            command = SonosVolumeCommand(room.volume_interpolation.speakers, speaker_volumes)
            self.sonos.send_command(command)

    def balance_room(self, room: Room) -> None:
        """Balances the speakers within a room

        :param models.room.Room room: Room which should be balanced"""
        if not self.config.balance:
            return

        speaker_volumes = []

        for speaker in room.volume_interpolation.speakers:
            perceived_volume = room.volume_interpolation.calculate_perceived_volume(speaker)
            speaker_volume = room.volume_interpolation.calculate_speaker_volume(perceived_volume)
            speaker_volumes.append(speaker_volume)

        command = SonosVolumeCommand(room.volume_interpolation.speakers, speaker_volumes)
        self.sonos.send_command(command)
        print('{}'.format(speaker_volumes))

    async def on_settings_changed(self) -> None:
        """Update the balancing status when the settings have changed."""
        if self.config.balance and self.config.balance != self.previous_config_value:
            self.start_balancing()
        elif not self.config.balance and self.config.balance != self.previous_config_value:
            self.stop_balancing()

        self.previous_config_value = self.config.balance
