"""Controller for the /room-calibration namespace."""

import asyncio
from socketio import AsyncNamespace
from config import Config
from models.acknowledgment import Acknowledgment
from models.room import Room
from models.speaker import Speaker
from api.validate import Validate
from balancing.sonos import Sonos
from models.room_calibration_point import RoomCalibrationPoint
from balancing.sonos_command import SonosPlayCalibrationSoundCommand, SonosStopCalibrationSoundCommand, SonosVolumeCommand

CALIBRATION_SOUND_LENGTH = 5
CALIBRATION_SOUND_VOLUME = 25

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

        return ack

    async def after_calibration_noise(self, room: Room, speaker: Speaker):
        """Inform the client that the calibration noise ended
        
        :param models.room.Room room: Room
        :param models.speaker.Speaker speaker: Speaker
        """
        self.sonos.send_command(SonosStopCalibrationSoundCommand([speaker]))
        await self.send_response(room, room.calibration_point_x, room.calibration_point_y, noise_done=True)

    async def send_response(self, room: Room, position_x: int, 
                     position_y: int, noise_done: bool = False) -> None:
        """Sends the room calibration response to all clients.

        :param models.room.Room room: Room
        :param int position_x: X Coordinate
        :param int position_y: Y Coordinate
        :param bool noise_done: Is the calibration noise done
        """
        await self.emit('get', {
            'room': {
                'id': room.room_id
            },
            'calibrating': room.calibrating,
            'positionX': position_x,
            'positionY': position_y,
            'noiseDone': noise_done
        })

    async def on_update(self, _: str, data: dict) -> None:
        """Starts the room calibration process.

        :param str sid: Session id
        :param dict data: Event data
        """
        ack = self.validate(data)

        if ack.successful:
            room = self.config.room_repository.get_room(
                data.get('room').get('id'))
            if data.get('start'):
                self.config.balance = False
                await self.config.setting_repository.call_listeners()
                room.calibrating = True
                await self.config.room_repository.call_listeners()
                # TODO: Start tracking for room and keep clients updated with self.send_response
                await self.send_response(room, position_x=1, position_y=1) # TODO: Replace with real coordinates
            elif data.get('finish'):
                room.calibrating = False
                await self.config.room_repository.call_listeners()
                await self.send_response(room, position_x=0, position_y=0)
            elif data.get('repeatPoint'):
                room_speaker_count = list(filter(lambda speaker: speaker.room.room_id == room.room_id,
                                                 self.config.speakers)).count()
                del room.calibration_points_temp[-room_speaker_count:]
                room.calibration_current_speaker_index = 0
                await self.config.room_repository.call_listeners()
            elif data.get('nextPoint'):
                room.calibration_point_x = 1 # TODO: Replace with real coordinates
                room.calibration_point_y = 1
                room.calibration_current_speaker_index = 0
                await self.config.room_repository.call_listeners()
                await self.send_response(room, room.calibration_point_x, room.calibration_point_y)
                # TODO: Stop tracking & updating clients
            elif data.get('nextSpeaker'):
                room_speakers = list(filter(lambda speaker: speaker.room.room_id == room.room_id,
                                            self.config.speakers))
                room_volumes = [0] * room_speakers.count
                room_volumes[room.calibration_current_speaker_index] = CALIBRATION_SOUND_VOLUME
                self.sonos.send_command(SonosVolumeCommand(room_speakers, room_volumes))
                self.sonos.send_command(
                    SonosPlayCalibrationSoundCommand([room_speakers[room.calibration_current_speaker_index]]))

                # TODO: Somehow call self.after_calibration_noise with room & speaker as argument after CALIBRATION_SOUND_LENGTH seconds
                #       But don't wait for the timeout... Call the following statements immediately

                room.calibration_current_speaker_index += 1
                await self.config.room_repository.call_listeners()
            else:
                await self.send_response(room, position_x=1, position_y=1) # TODO: Replace with real coordinates

        return ack.to_json()
