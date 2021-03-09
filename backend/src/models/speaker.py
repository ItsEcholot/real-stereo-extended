import models.room


class Speaker:
    def __init__(self, speaker_id: int = None, name: str = '', room=None):
        if len(name) == 0:
            raise ValueError('Speaker name cannot be empty')

        self.speaker_id: int = speaker_id
        self.name: str = name
        self.room: models.room.Room = room

    def to_json(self, recursive: bool = False) -> dict:
        json = {
            'id': self.speaker_id,
            'name': self.name,
        }

        if self.room is not None:
            if recursive:
                json['room'] = self.room
            else:
                json['room_id'] = self.room.room_id

        return json
