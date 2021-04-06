"""Defines methods for the people detection."""
from abc import ABC, abstractmethod
from numpy import ndarray
from config import Config


class PeopleDetector(ABC):
    """Defines methods for the people detection."""

    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    async def detect(self, detection_frame: ndarray, draw_frame: ndarray = None) -> None:
        """Detects people in a given camera frame.

        :param numpy.ndarray detection_frame: Camera frame which should be used for detection
        :param numpy.ndarray draw_frame: Frame in which recognized people should be drawn.
                                         If none, result should be drawn in detection_frame.
        """
        raise NotImplementedError()

    async def report_coordinate(self, coordinate: int) -> None:
        """Reports the detected coordinate to the master.

        :param int coordinate: Coordinate
        """
        await self.config.tracking_repository.update_coordinate(coordinate)
