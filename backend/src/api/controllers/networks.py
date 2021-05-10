"""Controller for the /networks namespace."""

from socketio import AsyncNamespace
from models.acknowledgment import Acknowledgment
from api.validate import Validate
from networking.wpa_supplicant import WpaSupplicant


class NetworksController(AsyncNamespace):
    """Controller for the /networks namespace."""

    def __init__(self):
        super().__init__(namespace='/networks')
        self.wpa_supplicant = WpaSupplicant()

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

            self.wpa_supplicant.store_network(ssid, psk)

        return ack.to_json()
