"""Speaker repository."""

from models.speaker import Speaker
from .repository import Repository


class SpeakerRepository(Repository):
    """Speaker repository.

    :param config.Config config: Config instance
    """

    def __init__(self, config):
        super().__init__()
        self.config = config

    def get_speaker(self, speaker_id: str) -> Speaker:
        """Returns the speaker with the specified id.

        :param str speaker_id: Speaker id
        :returns: Speaker or None if no speaker could be found with this id
        :rtype: models.speaker.Speaker
        """
        return next(filter(lambda s: s.speaker_id == speaker_id, self.config.speakers), None)

    def get_speaker_by_name(self, name: str) -> Speaker:
        """Returns the speaker with the given name.

        :param str name: Speaker name
        :returns: Speaker or None if no speaker could be found with this name
        :rtype: models.speaker.Speaker
        """
        return next(filter(lambda s: s.name == name, self.config.speakers), None)

    async def remove_speaker(self, speaker_id: str, delete_from_runtime_store: bool = False) -> bool:
        """Removes a speaker and stores the config file.

        :param str speaker_id: Speaker id
        :param bool delete_from_runtime_Store: If True speaker will be completly removed from the
                                               config runtime store. If the speaker is discovered
                                               in the next discovery round, it will be added again.
        :returns: False if no speaker could be found with this id and so no removal was possible,
                  otherwise True.
        :rtype: bool
        """
        speaker = self.get_speaker(speaker_id)

        if speaker is not None:
            # remove speaker
            speaker.room = None
            if delete_from_runtime_store:
                self.config.speakers.remove(speaker)
            await self.call_listeners()

            return True

        return False

    async def add_speaker(self, speaker: Speaker) -> None:
        """Adds a speaker and stores the config file.
        If a speaker with the same id already exists a ValueError is thrown.

        :param str speaker_id: Speaker id
        """
        if self.get_speaker(speaker.speaker_id) is not None:
            raise ValueError('Speaker id already exists in repository')

        self.config.speakers.append(speaker)
        await self.call_listeners()

    def to_json(self) -> dict:
        """Returns the list of all speakers in JSON serializable objects.

        :returns: JSON serializable object
        :rtype: dict
        """
        return list(map(lambda speaker: speaker.to_json(True), self.config.speakers))
