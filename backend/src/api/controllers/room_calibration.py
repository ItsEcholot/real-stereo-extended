"""Controller for the /room-calibration namespace."""

from socketio import AsyncNamespace
from config import Config
from models.acknowledgment import Acknowledgment
from models.room import Room
from models.room_calibration_point import RoomCalibrationPoint
from api.validate import Validate
from balancing.sonos import Sonos
from balancing.sonos_command import SonosPlayCalibrationSoundCommand, SonosStopCalibrationSoundCommand, SonosVolumeCommand
from balancing.sonos_command import SonosEnsureSpeakersInGroupCommand, SonosRestoreSpeakerGroupsCommand
from tracking.manager import TrackingManager
from protocol.master import ClusterMaster

CALIBRATION_SOUND_VOLUME = 25


class RoomCalibrationController(AsyncNamespace):
    """Controller for the /room-calibration namespace.

    :param Config config: The application config object.
    :param Sonos sonos: The sonos control instance
    :param TrackingManager tracking_manager: The instance of an active tracking manager.
    """

    def __init__(self, config: Config, sonos: Sonos, tracking_manager: TrackingManager,
                 cluster_master: ClusterMaster):
        super().__init__(namespace='/room-calibration')
        self.config: Config = config
        self.cluster_master: ClusterMaster = cluster_master
        self.sonos: Sonos = sonos
        self.tracking_manager = tracking_manager
        self.config.tracking_repository.register_listener(self.position_update)

    def validate_update(self, data: dict) -> Acknowledgment:
        """Validates the input data.

        :param dict data: Input data
        :returns: Acknowledgment with the status and possible error messages.
        :rtype: models.acknowledgment.Acknowledgment
        """
        ack = Acknowledgment()
        validate = Validate(ack)
        start = data.get('start')
        start_volume = data.get('startVolume')
        finish = data.get('finish')
        repeat_point = data.get('repeatPoint')
        confirm_point = data.get('confirmPoint')
        next_point = data.get('nextPoint')
        next_speaker = data.get('nextSpeaker')

        if data.get('room') is None or isinstance(data.get('room'), dict) is False:
            ack.add_error('Room id must not be empty')
        elif validate.integer(data.get('room').get('id'), label='Room id', min_value=1):
            room = self.config.room_repository.get_room(data.get('room').get('id'))
            if room is None:
                ack.add_error('A room with this id does not exist')
            elif len(room.nodes) != 2:
                ack.add_error('A room needs exactly two nodes')
        if start is not None:
            validate.boolean(start, label='Start')
            if start and self.config.room_repository.get_room(data.get('room').get('id')).calibrating:
                ack.add_error('The room is already calibrating currently')
            elif start and start_volume is None:
                ack.add_error('Calibration start volume is required')
            elif start:
                validate.integer(start_volume, label='Calibration Start Volume')

        if finish is not None:
            validate.boolean(finish, label='Finish')
            if finish and not self.config.room_repository.get_room(data.get('room').get('id')).calibrating:
                ack.add_error('The room wasn\'t beeing calibrated')
        if repeat_point is not None:
            validate.boolean(repeat_point, label='Repeat Point')
        if confirm_point is not None:
            validate.boolean(confirm_point, label='Confirm Point')
        if next_point is not None:
            validate.boolean(next_point, label='Next Point')
        if next_speaker is not None:
            validate.boolean(next_speaker, label='Next Speaker')

        return ack

    def validate_result(self, data: dict) -> Acknowledgment:
        """Validates the input data

        :param dict data: Input data
        :returns: Acknowledgment with the status and possible error messages.
        :rtype: models.acknowledgment.Acknowledgment
        """
        ack = Acknowledgment()
        validate = Validate(ack)
        volume = data.get('volume')

        if data.get('room') is None or isinstance(data.get('room'), dict) is False:
            ack.add_error('Room id must not be empty')
        elif validate.integer(data.get('room').get('id'), label='Room id', min_value=1):
            room = self.config.room_repository.get_room(data.get('room').get('id'))
            if room is None:
                ack.add_error('A room with this id does not exist')
            elif len(room.nodes) != 2:
                ack.add_error('A room needs exactly two nodes')
        validate.float(volume, label="Volume", min_value=0.0)

        return ack

    async def position_update(self) -> None:
        """Gets called when the tracking repository contains new coordinates."""
        room: Room
        for room in list(filter(lambda room: room.calibrating == True, self.config.rooms)):
            if not room.calibration_point_freeze:
                room.calibration_point_x = room.coordinates[0]
                room.calibration_point_y = room.coordinates[1]
                await self.send_response(room)

    async def send_response(self, room: Room) -> None:
        """Sends the room calibration response to all clients.

        :param models.room.Room room: Room
        """
        await self.emit('get', {
            'room': {
                'id': room.room_id
            },
            'calibrating': room.calibrating,
            'positionX': room.calibration_point_x,
            'positionY': room.calibration_point_y,
            'positionFreeze': room.calibration_point_freeze,
            'currentSpeakerIndex': room.calibration_current_speaker_index,
            'currentPoints': list(map(lambda point: point.to_json(), room.calibration_points_current_point)),
            'previousPoints': list(map(lambda point: point.to_json(), room.calibration_points)),
        })

    async def on_update(self, _: str, data: dict) -> None:
        """Starts the room calibration process.

        :param str sid: Session id
        :param dict data: Event data
        """
        ack = self.validate_update(data)

        if ack.successful:
            room = self.config.room_repository.get_room(data.get('room').get('id'))
            if data.get('start'):
                self.config.balance = False
                room.calibration_volume = data.get('startVolume')
                room.calibration_points = []
                room.calibration_current_speaker_index = 0
                await self.config.setting_repository.call_listeners()
                room.calibrating = True
                await self.config.room_repository.call_listeners()

                # make sure all room speakers are in a group together
                room_speakers = list(filter(lambda speaker: speaker.room.room_id == room.room_id,
                                            self.config.speakers))
                self.sonos.send_command(SonosEnsureSpeakersInGroupCommand(room_speakers))

                # set node coordinate types
                if not room.nodes[0].has_coordinate_type() or not room.nodes[1].has_coordinate_type() \
                        or room.nodes[0].coordinate_type == room.nodes[1].coordinate_type:
                    room.nodes[0].coordinate_type = 'x'
                    room.nodes[1].coordinate_type = 'y'
                    await self.config.node_repository.call_listeners()

                # send service update to all nodes of this room
                for node in room.nodes:
                    self.cluster_master.send_service_update(node.ip_address, True)

                print('[Room Calibration] Starting for room {}'.format(room.name))
            elif data.get('finish'):
                # Reset states and stop calibrating
                room.calibrating = False
                room.calibration_points_current_point = []
                room.calibration_current_speaker_index = 0
                room.calibration_point_freeze = False
                await self.config.room_repository.call_listeners()

                # restore the speaker group state from before calibration
                room_speakers = list(filter(lambda speaker: speaker.room.room_id == room.room_id,
                                            self.config.speakers))
                self.sonos.send_command(SonosRestoreSpeakerGroupsCommand(room_speakers))

                # send service update to all nodes of this room
                for node in room.nodes:
                    self.cluster_master.send_service_update(node.ip_address, False)

                await self.send_response(room)
                print('[Room Calibration] Finishing for room {}'.format(room.name))
            elif data.get('repeatPoint'):
                # Delete current unsaved points and reset speaker index state to repeat current coordinates
                room.calibration_points_current_point = []
                room.calibration_current_speaker_index = 0
                await self.config.room_repository.call_listeners()
                await self.send_response(room)
            elif data.get('confirmPoint'):
                # Save current unsaved points to permanent calibration points
                room.calibration_points.extend(room.calibration_points_current_point)
                room.calibration_points_current_point = []
                room.calibration_current_speaker_index = 0
                room.calibration_point_freeze = False
                await self.config.room_repository.call_listeners()
                await self.send_response(room)
            elif data.get('nextPoint'):
                # Stop updating the tracking coordinates
                room.calibration_point_freeze = True
                await self.config.room_repository.call_listeners()
                await self.send_response(room)
                print('[Room Calibration] Next point for room {} has been selected: x{}, y{}'
                      .format(room.name, room.calibration_point_x, room.calibration_point_y))
            elif data.get('nextSpeaker'):
                # If first time for current position --> Start playing the calibration sound
                # Sets balances for current speaker index
                # If last time for current position --> Stop playing the calibration sound
                room_speakers = list(filter(lambda speaker: speaker.room.room_id == room.room_id,
                                            self.config.speakers))
                room_speaker_count = len(room_speakers)
                if room.calibration_current_speaker_index == room_speaker_count:
                    self.sonos.send_command(SonosStopCalibrationSoundCommand([room_speakers[0]]))
                    await self.send_response(room)
                    return ack.to_json()

                room_volumes = [0] * len(room_speakers)
                room_volumes[room.calibration_current_speaker_index] = room.calibration_volume
                if room.calibration_current_speaker_index == 0:
                    self.sonos.send_command(SonosPlayCalibrationSoundCommand([room_speakers[0]]))
                self.sonos.send_command(SonosVolumeCommand(room_speakers, room_volumes))

                print('[Room Calibration] Next speaker ({}) has been selected for noise'.format(
                    room_speakers[room.calibration_current_speaker_index].name))
                await self.send_response(room)
                room.calibration_current_speaker_index += 1
                await self.config.room_repository.call_listeners()
            else:
                await self.send_response(room)

        return ack.to_json()

    async def on_result(self, _: str, data: dict) -> None:
        """Receives the calibration result.

        :param str sid: Session id
        :param dict data: Event data
        """
        ack = self.validate_result(data)
        if ack.successful:
            room = self.config.room_repository.get_room(data.get('room').get('id'))
            room_speakers = list(filter(lambda speaker: speaker.room.room_id == room.room_id,
                                        self.config.speakers))
            speaker = room_speakers[room.calibration_current_speaker_index - 1]
            calibration_point = RoomCalibrationPoint(
                speaker, room.calibration_point_x, room.calibration_point_y, data.get('volume'))
            room.calibration_points_current_point.append(calibration_point)
            await self.config.room_repository.call_listeners()
            await self.send_response(room)

        return ack.to_json()
