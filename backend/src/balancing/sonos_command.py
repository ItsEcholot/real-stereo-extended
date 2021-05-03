"""Contains information of the command to be sent to a Sonos speaker"""
from abc import ABC, abstractmethod
from typing import List
from models.speaker import Speaker
from sonos.adapter import SonosAdapter


class SonosCommand(ABC):
    """Contains information of the command to be sent to a Sonos speaker

    :param list[Speaker] speakers: Speakers where the command should be sent to
    """

    def __init__(self, speakers: List[Speaker]):
        self.speakers = speakers

    @abstractmethod
    def run(self, sonos_adapter: SonosAdapter):
        """Executes the command"""


class SonosVolumeCommand(SonosCommand):
    """Contains information of the volume command to be sent to a Sonos speaker

    :param list[Speaker] speakers: Speakers where the command should be sent to
    :param list[int] volume: The volumes to be set, values between 0 and 100
    :param bool ramp_to_volume: If the volume should be changed smoothly by the
                                Sonos speaker (ramp rate is 1.25 steps per second)
    """

    def __init__(self, speakers: List[Speaker], volumes: List[int], ramp_to_volume: bool = False):
        super().__init__(speakers)
        self.volumes = volumes
        self.ramp_to_volume = ramp_to_volume

    def run(self, sonos_adapter: SonosAdapter):
        """Executes the command"""
        for index, speaker in enumerate(self.speakers):
            if not self.ramp_to_volume:
                sonos_adapter.set_volume(speaker=speaker, volume=self.volumes[index])
            else:
                sonos_adapter.ramp_to_volume(speaker=speaker, volume=self.volumes[index])


class SonosPlayCalibrationSoundCommand(SonosCommand):
    """Contains information of the play calibration sound command to
    be sent to a Sonos speaker

    :param list[Speaker] speakers: Speakers where the command should be sent to
    """

    def run(self, sonos_adapter: SonosAdapter):
        """Executes the command"""
        for speaker in self.speakers:
            sonos_adapter.save_snapshot(speaker)
            sonos_adapter.play_calibration_sound(speaker)


class SonosStopCalibrationSoundCommand(SonosCommand):
    """Contains information of the stop calibration sound command to
    be sent to a Sonos speaker

    :param list[Speaker] speakers: Speakers where the command should be sent to
    """

    def run(self, sonos_adapter: SonosAdapter):
        """Executes the command"""
        for speaker in self.speakers:
            sonos_adapter.restore_snapshot(speaker)


class SonosEnsureSpeakersInGroupCommand(SonosCommand):
    """Contains information about the speakers which should be ensured
    to be in a group.

    :param list[Speaker] speakers: Speakers which should be in a group together
    """

    def run(self, sonos_adapter: SonosAdapter):
        """Executes the command"""
        sonos_adapter.ensure_speakers_in_group(self.speakers)