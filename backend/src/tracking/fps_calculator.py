"""Calculates the performance in form of frames per seconds."""

from time import time
from collections import deque


class Fps:
    """Calculates the performance in form of frames per seconds.

    :param int size: Number of frames to average
    """

    def __init__(self, size: int = 10):
        self.frames = deque(maxlen=size)

    def frame(self) -> None:
        """Store a new frame."""
        self.frames.append(time())

    def get(self) -> float:
        """Get the average FPS.

        :returns: Average FPS
        :rtype: float
        """
        if len(self.frames) < 2:
            return 0.0

        return len(self.frames) / (self.frames[-1] - self.frames[0])
