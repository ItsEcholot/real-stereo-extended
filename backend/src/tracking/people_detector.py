"""Defines methods for the people detection."""
from abc import ABC, abstractmethod
from numpy import ndarray
from config import Config


class PeopleDetector(ABC):
    """Defines methods for the people detection."""

    def __init__(self, config: Config):
        self.config = config

    @abstractmethod
    async def detect(self, frame: ndarray) -> None:
        """Detects people in a given camera frame.

        :param numpy.ndarray frame: Camera frame
        """
        raise NotImplementedError()

    async def report_coordinate(self, coordinate: int) -> None:
        """Reports the detected coordinate to the master.

        :param int coordinate: Coordinate
        """
        await self.config.tracking_repository.update_coordinate(coordinate)
