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
from tracking.manager import TrackingManager

CALIBRATION_SOUND_LENGTH = 5
CALIBRATION_SOUND_VOLUME = 25

class RoomCalibrationController(AsyncNamespace):
    """Controller for the /room-calibration namespace.
    
    :param Config config: The application config object.
    :param Sonos sonos: The sonos control instance 
    :param TrackingManager tracking_manager: The instance of an active tracking manager.
    """

    def __init__(self, config: Config, sonos: Sonos, tracking_manager: TrackingManager):
        super().__init__(namespace='/room-calibration')
        self.config: Config = config
        self.sonos: Sonos = sonos
        self.tracking_manager = tracking_manager
        self.config.tracking_repository.register_listener(self.position_update)

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

    async def position_update(self) -> None:
        """Gets called when the tracking repository contains new coordinates."""
        room: Room
        for room in list(filter(lambda room: room.calibrating == True, self.config.rooms)):
            if not room.calibration_point_freeze:
                room.calibration_point_x = self.config.tracking_repository.coordinate
                room.calibration_point_y = self.config.tracking_repository.coordinate # TODO: Get X & Y coordinates
                await self.config.room_repository.call_listeners()
            await self.send_response(room)

    async def after_calibration_noise(self, room: Room, speaker: Speaker):
        """Inform the client that the calibration noise ended
        
        :param models.room.Room room: Room
        :param models.speaker.Speaker speaker: Speaker
        """
        self.sonos.send_command(SonosStopCalibrationSoundCommand([speaker]))
        await self.send_response(room, noise_done=True)

    async def send_response(self, room: Room, noise_done: bool = False) -> None:
        """Sends the room calibration response to all clients.

        :param models.room.Room room: Room
        :param bool noise_done: Is the calibration noise done
        """
        await self.emit('get', {
            'room': {
                'id': room.room_id
            },
            'calibrating': room.calibrating,
            'positionX': room.calibration_point_x,
            'positionY': room.calibration_point_y,
            'noiseDone': noise_done
        })

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
                self.tracking_manager.acquire_camera()
                self.tracking_manager.start_detector()
            elif data.get('finish'):
                room.calibrating = False
                await self.config.room_repository.call_listeners()
                self.tracking_manager.release_camera()
                self.tracking_manager.stop_detector()
                await self.send_response(room)
            elif data.get('repeatPoint'):
                room.calibration_points_current_point = []
                room.calibration_current_speaker_index = 0
                await self.config.room_repository.call_listeners()
            elif data.get('nextPoint'):
                # Save last point to permanent calibration points
                room.calibration_points.extend(room.calibration_points_current_point)
                # Stop updating the tracking coordinates
                room.calibration_point_freeze = True
                room.calibration_current_speaker_index = 0
                await self.config.room_repository.call_listeners()
                await self.send_response(room)
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

                # TODO: After last speaker unfreeze room calibration point using room.calibration_point_freeze

                room.calibration_current_speaker_index += 1
                await self.config.room_repository.call_listeners()
            else:
                await self.send_response(room) # TODO: Replace with real coordinates

        return ack.to_json()
