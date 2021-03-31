"""Tracking repository."""

from .repository import Repository


class TrackingRepository(Repository):
    """Tracking repository.

    :param config.Config config: Config instance
    """

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.coordinate = 0

    async def update_coordinate(self, coordinate: int) -> None:
        """Update the coordinate and call all listeners.

        :param int coordinate: New coordinate
        """
        self.coordinate = coordinate
        await self.call_listeners()
