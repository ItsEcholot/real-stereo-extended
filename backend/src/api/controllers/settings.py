"""Controller for the /settings namespace."""

import asyncio
from socketio import AsyncNamespace
from config import Config, NodeType
from models.acknowledgment import Acknowledgment
from api.validate import Validate
from .networks import NetworksController
from balancing.sonos import Sonos
from balancing.sonos_command import SonosPlayCalibrationSoundCommand, SonosStopCalibrationSoundCommand


class SettingsController(AsyncNamespace):
    """Controller for the /settings namespace.
    
    :param Config config: The application config object.
    :param Sonos sonos: The sonos control instance
    """

    def __init__(self, config: Config, sonos: Sonos, networks_controller: NetworksController):
        super().__init__(namespace='/settings')
        self.config: Config = config
        self.sonos: Sonos = sonos
        self.networks_controller = networks_controller

        # add settings repository change listener
        config.setting_repository.register_listener(self.send_settings)
        config.tracking_repository.register_listener(self.position_update)

    def build_settings(self) -> dict:
        """Builds the settings.

        :returns: Settings
        :rtype: dict
        """
        return {
            'configured': self.config.type != NodeType.UNCONFIGURED,
            'balance': self.config.balance,
            'network': self.config.network,
            'test_mode': self.config.test_mode,
        }

    async def send_settings(self, sid: str = None) -> None:
        """Sends the current settings to all clients or only a specific one.

        :param str sid: If specified, settings will only be sent to this session id. Otherwise, all
                        clients will receive the settings.
        """
        await self.emit('get', self.build_settings(), room=sid)

    async def position_update(self) -> None:
        """Gets called when the tracking repository contains new coordinates."""
        if not self.config.test_mode:
            return
        
        result = []
        room: Room
        for room in self.config.rooms:
            result.append({'room': room.to_json(), 'positionX': room.coordinates[0], 'positionY': room.coordinates[1]})
        await self.emit('testModeResult', result)

    def validate(self, data: dict) -> Acknowledgment:  # pylint: disable=no-self-use
        """Validates the input data.

        :param dict data: Input data
        :returns: Acknowledgment with the status and possible error messages.
        :rtype: models.acknowledgment.Acknowledgment
        """
        ack = Acknowledgment()
        validate = Validate(ack)
        balance = data.get('balance')
        node_type = data.get('nodeType')
        test_mode = data.get('testMode')

        if balance is not None:
            validate.boolean(balance, label='Balance')
        if test_mode is not None:
            validate.boolean(test_mode, label='Test Mode')

        if node_type is not None and node_type != 'master' and node_type != 'tracking':
            ack.add_error('nodeType must be either master or tracking')

        if data.get('network') is not None:
            network_ack = self.networks_controller.validate(data.get('network'))
            if not network_ack.successful:
                for error in network_ack.errors:
                    ack.add_error(error)

        return ack

    async def on_get(self, _: str) -> dict:
        """Returns the current settings.

        :param str sid: Session id
        :param dict data: Event data
        """
        return self.build_settings()

    async def on_update(self, _: str, data: dict) -> None:
        """Updates the settings.

        :param str sid: Session id
        :param dict data: Event data
        """
        # validate
        ack = self.validate(data)

        # update the settings
        if ack.successful:
            if data.get('testMode') and not self.config.test_mode:
                self.sonos.send_command(SonosPlayCalibrationSoundCommand(self.config.speakers))
                self.config.test_mode = True
            elif data.get('testMode') == False and self.config.test_mode:
                self.sonos.send_command(SonosStopCalibrationSoundCommand(self.config.speakers))
                self.config.test_mode = False
            
            # check if the balance setting has changed
            if data.get('balance') is not None and self.config.balance != data.get('balance'):
                # check if all rooms are calibrated
                uncalibrated_rooms = list(filter(lambda room: len(room.calibration_points) == 0,
                                                 self.config.rooms))
                if len(uncalibrated_rooms) > 0:
                    ack.add_error('The following rooms must be calibrated: {}'.format(', '.join(
                        map(lambda room: room.name, uncalibrated_rooms))))
                else:
                    self.config.balance = data['balance']
                    await self.config.setting_repository.call_listeners()

            # check if node type has changed
            if data.get('nodeType') is not None:
                node_type = data.get('nodeType')
                if self.config.type == NodeType.UNCONFIGURED or \
                    (node_type == 'master' and self.config.type != NodeType.MASTER) or \
                        (node_type == 'tracking' and self.config.type != NodeType.TRACKING):
                    self.config.type = NodeType.MASTER if node_type == 'master' else NodeType.TRACKING
                    await self.config.setting_repository.call_listeners()
                    asyncio.create_task(self.delayed_restart(data.get('network')))

        return ack.to_json()

    async def delayed_restart(self, network_data: dict = None) -> None:
        """Restarts real stereo after a short delay to allow the ack message to still get delivered.
        """
        # check if a network should get configured in the same set
        if network_data is not None:
            await self.networks_controller.on_create('', network_data)

        await asyncio.sleep(5)
        exit(0)
