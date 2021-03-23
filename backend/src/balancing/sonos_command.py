"""Contains information of the command to be sent to a Sonos speaker"""
from abc import ABC, abstractmethod
from models.speaker import Speaker


class SonosCommand(ABC):
    """Contains information of the command to be sent to a Sonos speaker

    :param list[Speaker] speakers: Speakers where the command should be sent to
    """

    def __init__(self, speakers: list[Speaker]):
        self.speakers = speakers

    @abstractmethod
    def run(self):
        """Executes the command"""


class SonosVolumeCommand(SonosCommand):
    """Contains information of the volume command to be sent to a Sonos speaker

    :param list[Speaker] speakers: Speakers where the command should be sent to
    :param list[int] volume: The volumes to be set, values between 0 and 100
    :param bool ramp_to_volume: If the volume should be changed smoothly by the
                                Sonos speaker (ramp rate is 1.25 steps per second)
    """

    def __init__(self, speakers: list[Speaker], volumes: list[int], ramp_to_volume: bool = False):
        super().__init__(speakers)
        self.volumes = volumes
        self.ramp_to_volume = ramp_to_volume
