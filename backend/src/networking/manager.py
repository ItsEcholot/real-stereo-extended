"""Controls the networking functionality."""
from asyncio import sleep
import netifaces
from config import Config, NodeType
from .ad_hoc_network import AdHocNetwork
from .wpa_supplicant import WpaSupplicant


class NetworkingManager:
    """Controls the networking functionality."""

    def __init__(self, config: Config):
        self.config = config
        self.ad_hoc = AdHocNetwork(config)
        self.wpa_supplicant = WpaSupplicant()

        if self.config.type == NodeType.UNCONFIGURED and not self.ad_hoc.is_enabled():
            self.ad_hoc.enable()

        if self.ad_hoc.is_enabled():
            self.config.network = 'adhoc'
        else:
            self.config.network = 'client'

    async def initial_check(self) -> None:
        """Initially checks if a network connection could be established.
        If not, it starts the adhoc network to allow the user to configure a new network.
        """
        if self.config.type == NodeType.UNCONFIGURED or self.config.network == 'adhoc':
            return

        await sleep(30)

        if not self.has_assigned_ip():
            self.ad_hoc.enable()

    def has_assigned_ip(self) -> bool:
        """Checks whether an ip address is assigned to the network interface.

        :returns: True if the network interface has an ip address assigned
        :rtype: bool
        """
        if 'wlan0' not in netifaces.interfaces():
            return False

        addresses = netifaces.ifaddresses('wlan0')
        return netifaces.AF_INET in addresses
