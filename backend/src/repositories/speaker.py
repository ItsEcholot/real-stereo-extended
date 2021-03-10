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

    def get_speaker(self, speaker_id: int) -> Speaker:
        """Returns the speaker with the specified id.

        :param int speaker_id: Speaker id
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

    def remove_speaker(self, speaker_id: int) -> bool:
        """Removes a speaker and stores the config file.

        :param int speaker_id: Speaker id
        :returns: False if no speaker could be found with this id and so no removal was possible,
                  otherwise True.
        :rtype: bool
        """
        speaker = self.get_speaker(speaker_id)

        if speaker is not None:
            # remove speaker
            self.config.speakers.remove(speaker)
            self.call_listeners()

            return True

        return False

    def to_json(self) -> dict:
        """Returns the list of all speakers in JSON serializable objects.

        :returns: JSON serializable object
        :rtype: dict
        """
        return list(map(lambda speaker: speaker.to_json(True), self.config.speakers))
