"""Settings repository."""

from .repository import Repository


class SettingsRepository(Repository):
    """Settings repository.

    :param config.Config config: Config instance
    """

    def __init__(self, config):
        super().__init__()
        self.config = config
