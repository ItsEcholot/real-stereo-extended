"""Controller for the /settings namespace."""

from socketio import AsyncNamespace
from config import Config, NodeType
from models.acknowledgment import Acknowledgment
from api.validate import Validate


class SettingsController(AsyncNamespace):
    """Controller for the /settings namespace."""

    def __init__(self, config: Config):
        super().__init__(namespace='/settings')
        self.config: Config = config

        # add settings repository change listener
        config.setting_repository.register_listener(self.send_settings)

    def build_settings(self) -> dict:
        """Builds the settings.

        :returns: Settings
        :rtype: dict
        """
        return {
            'configured': self.config.type != NodeType.UNCONFIGURED,
            'balance': self.config.balance,
            'network': self.config.network,
        }

    async def send_settings(self, sid: str = None) -> None:
        """Sends the current settings to all clients or only a specific one.

        :param str sid: If specified, settings will only be sent to this session id. Otherwise, all
                        clients will receive the settings.
        """
        await self.emit('get', self.build_settings(), room=sid)

    def validate(self, data: dict) -> Acknowledgment:  # pylint: disable=no-self-use
        """Validates the input data.

        :param dict data: Input data
        :returns: Acknowledgment with the status and possible error messages.
        :rtype: models.acknowledgment.Acknowledgment
        """
        ack = Acknowledgment()
        validate = Validate(ack)
        balance = data.get('balance')

        validate.boolean(balance, label='Balance')

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
            # check if the balance setting has changed
            if self.config.balance != data['balance']:
                # check if all rooms are calibrated
                uncalibrated_rooms = list(filter(lambda room: len(room.calibration_points) == 0,
                                                 self.config.rooms))
                if len(uncalibrated_rooms) > 0:
                    ack.add_error('The following rooms must be calibrated: {}'.format(', '.join(
                        map(lambda room: room.name, uncalibrated_rooms))))
                else:
                    self.config.balance = data['balance']
                    await self.config.setting_repository.call_listeners()

        return ack.to_json()
