"""Controller for the /room-calibration namespace."""

from socketio import AsyncNamespace
from config import Config
from models.acknowledgment import Acknowledgment
from api.validate import Validate


class RoomCalibrationController(AsyncNamespace):
    """Controller for the /room-calibration namespace."""

    def __init__(self, config: Config):
        super().__init__(namespace='/room-calibration')
        self.config: Config = config

    def validate(self, data: dict) -> Acknowledgment:
        """Validates the input data.

        :param dict data: Input data
        :returns: Acknowledgment with the status and possible error messages.
        :rtype: models.acknowledgment.Acknowledgment
        """
        ack = Acknowledgment()
        validate = Validate(ack)
        start = data.get('start')
        finish = data.get('finish')
        repeat = data.get('repeat')

        if start is not None:
            validate.boolean(start, label='Start')
        if finish is not None:
            validate.boolean(finish, label='Finish')
        if repeat is not None:
            validate.boolean(repeat, label='Repeat')
        if data.get('room') is None or isinstance(data.get('room'), dict) is False:
            ack.add_error('Room id must not be empty')
        elif validate.integer(data.get('room').get('id'), label='Room id', min_value=1):
            if self.config.room_repository.get_room(data.get('room').get('id')) is None:
                ack.add_error('A room with this id does not exist')
            elif self.config.room_repository.get_room(data.get('room').get('id')).calibrating:
                ack.add_error('The room is already calibrating')

    async def on_update(self, _: str, data: dict) -> None:
        """Starts the room calibration process.

        :param str sid: Session id
        :param dict data: Event data
        """
        ack = self.validate(data)

        if ack.successful:
            room = self.config.room_repository.get_room(data.get('room').get('id'))
            if data.get('start'):
                room.calibrating = True
                await self.config.room_repository.call_listeners()
            elif data.get('finish'):
                room.calibrating = False
                await self.config.room_repository.call_listeners()

        return ack.to_json()
