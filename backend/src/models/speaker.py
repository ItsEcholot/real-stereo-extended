"""Implements the state of a single speaker."""

import models.room


class Speaker:
    """Implements the state of a single speaker.

    :param int speaker_id: Speaker id
    :param str name: Name of the speaker
    :param models.room.Room room: Room to which the speaker belongs to
    """

    def __init__(self, speaker_id: str, name: str = '', room=None):
        if len(speaker_id) == 0:
            raise ValueError('Speaker id cannot be empty')
        if len(name) == 0:
            raise ValueError('Speaker name cannot be empty')

        self.speaker_id: str = speaker_id
        self.name: str = name
        self.room: models.room.Room = room

    @staticmethod
    def from_json(data: dict, config):
        """Reads data from a JSON object and returns a new speaker instance.

        :param dict data: JSON data
        :param config.Config config: Config instance
        :returns: Speaker
        :rtype: Speaker
        """
        # find room in which the speaker is located
        room = config.room_repository.get_room(data.get('room_id'), fail=True)

        return Speaker(speaker_id=data.get('id'), name=data.get('name'), room=room)

    def to_json(self, recursive: bool = False) -> dict:
        """Creates a JSON serializable object.

        :param bool recursive: If true, all relations will be returned as full objects as well.
                               If false, only the ids of the relations will be returned.
        :returns: JSON serializable object
        :rtype: dict
        """
        json = {
            'id': self.speaker_id,
            'name': self.name,
        }

        if self.room is not None:
            if recursive:
                json['room'] = self.room.to_json()
            else:
                json['room_id'] = self.room.room_id

        return json
