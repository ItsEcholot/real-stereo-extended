"""Controller for the /networks namespace."""

import asyncio
from socketio import AsyncNamespace
from config import Config
from models.acknowledgment import Acknowledgment
from api.validate import Validate
from networking.manager import NetworkingManager


class NetworksController(AsyncNamespace):
    """Controller for the /networks namespace."""

    def __init__(self, config: Config, networking_manager: NetworkingManager):
        super().__init__(namespace='/networks')
        self.config = config
        self.networking_manager = networking_manager

    def validate(self, data: dict) -> Acknowledgment:
        """Validates the input data.

        :param dict data: Input data
        :returns: Acknowledgment with the status and possible error messages.
        :rtype: models.acknowledgment.Acknowledgment
        """
        ack = Acknowledgment()
        validate = Validate(ack)
        ssid = data.get('ssid')
        psk = data.get('psk')

        validate.string(ssid, label='SSID', min_value=1)

        if psk is not None:
            validate.string(psk, label='Password', min_value=8, max_value=63)

        return ack

    async def on_create(self, _: str, data: dict) -> None:
        """Stores a new network.

        :param str sid: Session id
        :param dict data: Event data
        """
        # validate
        ack = self.validate(data)

        if ack.successful:
            ssid = data.get('ssid')
            psk = data.get('psk')

            self.networking_manager.wpa_supplicant.store_network(ssid, psk)

            # if in the ad hoc networking mode, switch to the client again and try to connect
            if self.config.network == 'adhoc':
                asyncio.create_task(self.delayed_ad_hoc_disable())
                asyncio.create_task(self.networking_manager.initial_check())

        return ack.to_json()

    async def delayed_ad_hoc_disable(self) -> None:
        """Disables the ad hoc network after a short delay to allow the ack message to still get delivered."""
        await asyncio.sleep(5)
        self.networking_manager.ad_hoc.disable()
