"""Controller for the /settings namespace."""

import asyncio
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
        }

    def send_settings(self, sid: str = None) -> None:
        """Sends the current settings to all clients or only a specific one.

        :param str sid: If specified, settings will only be sent to this session id. Otherwise, all
                        clients will receive the settings.
        """
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.emit('get', self.build_settings(), room=sid))

        if loop.is_running() is False:
            loop.run_until_complete(task)

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
            self.config.balance = data['balance']
            self.config.setting_repository.call_listeners()

        return ack.to_json()
