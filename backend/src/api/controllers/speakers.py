"""Controller for the /speakers namespace."""

from typing import List
import asyncio
from socketio import AsyncNamespace
from config import Config
from models.speaker import Speaker
from models.acknowledgment import Acknowledgment
from api.validate import Validate


class SpeakersController(AsyncNamespace):
    """Controller for the /speakers namespace."""

    def __init__(self, config: Config):
        super().__init__(namespace='/speakers')
        self.config: Config = config

        # add speaker repository change listener
        config.speaker_repository.register_listener(self.send_speakers)

    def send_speakers(self, sid: str = None) -> None:
        """Sends the current speakers to all clients or only a specific one.

        :param str sid: If specified, speakers will only be sent to this session id. Otherwise, all
                        clients will receive the speakers.
        """
        loop = asyncio.get_event_loop()
        loop.create_task(self.emit('get', self.config.speaker_repository.to_json(), room=sid))

    def validate(self, data: dict, create: bool) -> Acknowledgment:
        """Validates the input data.

        :param dict data: Input data
        :param bool create: If a new speaker will be created from this data or an existing updated.
        :returns: Acknowledgment with the status and possible error messages.
        :rtype: models.acknowledgment.Acknowledgment
        """
        ack = Acknowledgment()
        validate = Validate(ack)
        speaker_id = data.get('id')
        name = data.get('name')

        validate.string(name, label='Name', min_value=1, max_value=50)

        if data.get('room') is None or isinstance(data.get('room'), dict) is False:
            ack.add_error('Room id must not be empty')
        elif validate.integer(data.get('room').get('id'), label='Room id', min_value=1):
            if self.config.room_repository.get_room(data.get('room').get('id')) is None:
                ack.add_error('A room with this id does not exist')

        if create:
            if self.config.speaker_repository.get_speaker(speaker_id) is not None:
                ack.add_error('A speaker with this name already exists')
        elif validate.integer(speaker_id, label='Speaker id', min_value=1):
            existing = self.config.speaker_repository.get_speaker_by_name(name)

            if self.config.speaker_repository.get_speaker(speaker_id) is None:
                ack.add_error('A speaker with this id does not exist')
            elif existing and existing.speaker_id != speaker_id:
                ack.add_error('A speaker with this name already exists')

        return ack

    async def on_get(self, _: str) -> List[Speaker]:
        """Returns the current speakers.

        :param str sid: Session id
        :param dict data: Event data
        """
        return self.config.speaker_repository.to_json()

    async def on_update(self, _: str, data: dict) -> dict:
        """Updates a speaker.

        :param str sid: Session id
        :param dict data: Event data
        """
        # validate
        ack = self.validate(data, False)

        # update the speaker
        if ack.successful:
            room = self.config.room_repository.get_room(data.get('room').get('id'))
            speaker = self.config.speaker_repository.get_speaker(data.get('id'))

            speaker.name = data.get('name')

            # update room reference if necessary
            if speaker.room.room_id != room.room_id:
                speaker.room = room

            # store the update and send the new state to all clients
            self.config.speaker_repository.call_listeners()

        return ack.to_json()

    async def on_delete(self, _: str, speaker_id: int) -> dict:
        """Deletes a speaker.

        :param str sid: Session id
        :param int speaker_id: Speaker id
        """
        ack = Acknowledgment()

        if self.config.speaker_repository.remove_speaker(speaker_id) is False:
            ack.add_error('A speaker with this id does not exist')

        return ack.to_json()
