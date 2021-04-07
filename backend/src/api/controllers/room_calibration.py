"""Controller for the /room-calibration namespace."""

import asyncio
from socketio import AsyncNamespace
from config import Config
from models.acknowledgment import Acknowledgment
from api.validate import Validate
from balancing.sonos import Sonos
from models.room_calibration_point import RoomCalibrationPoint
from balancing.sonos_command import SonosPlayCalibrationSoundCommand, SonosStopCalibrationSoundCommand

CALIBRATION_SOUND_LENGTH = 5

class RoomCalibrationController(AsyncNamespace):
    """Controller for the /room-calibration namespace."""

    def __init__(self, config: Config, sonos: Sonos):
        super().__init__(namespace='/room-calibration')
        self.config: Config = config
        self.sonos: Sonos = sonos

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
        repeat_point = data.get('repeatPoint')
        next_point = data.get('nextPoint')
        next_speaker = data.get('nextSpeaker')

        if data.get('room') is None or isinstance(data.get('room'), dict) is False:
            ack.add_error('Room id must not be empty')
        elif validate.integer(data.get('room').get('id'), label='Room id', min_value=1):
            if self.config.room_repository.get_room(data.get('room').get('id')) is None:
                ack.add_error('A room with this id does not exist')
        if start is not None:
            validate.boolean(start, label='Start')
            if start and self.config.room_repository.get_room(data.get('room').get('id')).calibrating:
                ack.add_error('The room is already calibrating currently')
        if finish is not None:
            validate.boolean(finish, label='Finish')
            if finish and not self.config.room_repository.get_room(data.get('room').get('id')).calibrating:
                ack.add_error('The room wasn\'t beeing calibrated')
        if repeat_point is not None:
            validate.boolean(repeat_point, label='Repeat Point')
        if next_point is not None:
            validate.boolean(next_point, label='Next Point')
        if next_speaker is not None:
            validate.boolean(next_speaker, label='Next Speaker')

    async def on_update(self, _: str, data: dict) -> None:
        """Starts the room calibration process.

        :param str sid: Session id
        :param dict data: Event data
        """
        ack = self.validate(data)

        if ack.successful:
            room = self.config.room_repository.get_room(data.get('room').get('id'))
            if data.get('start'):
                self.config.balance = False
                await self.config.setting_repository.call_listeners()
                room.calibrating = True
                await self.config.room_repository.call_listeners()
                # TODO: Start tracking for room
            elif data.get('finish'):
                room.calibrating = False
                await self.config.room_repository.call_listeners()
            elif data.get('repeatPoint'):
                room_speaker_count = list(filter(lambda speaker: speaker.room.room_id == room.room_id, 
                                                 self.config.speakers)).count()
                del room.calibration_points_temp[-room_speaker_count:]
                room.calibration_current_speaker_index = 0
                await self.config.room_repository.call_listeners()
            elif data.get('nextPoint'):
                # TODO: Get position and save into room_calibration_point
                room.calibration_current_speaker_index = 0
                await self.config.room_repository.call_listeners()
            elif data.get('nextSpeaker'):
                speaker = list(filter(lambda speaker: speaker.room.room_id == room.room_id, 
                                      self.config.speakers))[room.calibration_current_speaker_index]
                self.sonos.send_command(SonosPlayCalibrationSoundCommand([speaker]))
                running_loop = asyncio.get_running_loop()
                running_loop.call_later(CALIBRATION_SOUND_LENGTH,
                                        lambda: self.sonos.send_command(SonosStopCalibrationSoundCommand([speaker])))

                room.calibration_current_speaker_index += 1
                await self.config.room_repository.call_listeners()

        return ack.to_json()
