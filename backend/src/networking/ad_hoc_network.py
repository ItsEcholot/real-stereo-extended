"""Handles the Ad Hoc Network used for initial setup and wifi configuration."""
from os import system
from config import Config, NodeType


DHCP_CONFIG = '/etc/dhcpcd.conf'
DISABLED_START_POINTER = '# --ad-hoc-start--\n'
ENABLED_START_POINTER = '# --ad-hoc-start-enabled--\n'
END_POINTER = '# --ad-hoc-end--\n'


class AdHocNetwork:
    """Handles the Ad Hoc Network used for initial setup and wifi configuration."""

    def __init__(self, config: Config):
        self.config = config

    def is_enabled(self) -> bool:
        """Check if the ad hoc network is enabled.

        :returns: True if the ad hoc network is enabled
        :rtype: bool
        """
        with open(DHCP_CONFIG, 'r') as config_file:
            config = config_file.readlines()
            return ENABLED_START_POINTER in config

    def enable(self):
        """Enables the ad hoc network"""
        print('[AdHoc] Enabling the ad hoc network')

        # enable the ad hoc network in the dhcp config
        with open(DHCP_CONFIG, 'r') as config_file:
            config = config_file.readlines()
            if DISABLED_START_POINTER in config:
                start = config.index(DISABLED_START_POINTER)
                config[start] = ENABLED_START_POINTER
                for i in range(start + 1, config.index(END_POINTER)):
                    if config[i][0] == '#':
                        config[i] = config[i][1:]

                with open(DHCP_CONFIG, 'w') as write_handle:
                    write_handle.writelines(config)

                    # reload daemon config
                    system('sudo systemctl daemon-reload')

        if system('sudo service hostapd status > /dev/null') > 0:
            # enable the hostapd service
            system('sudo systemctl enable --now hostapd')

            # restart the network
            self.restart_network()

            # restart the hostapd service to use the new dhcp config
            system('sudo service hostapd restart')

            # enable the dhcp server for the adhoc network
            system('sudo systemctl enable --now dnsmasq')

        self.config.network = 'adhoc'

        if self.config.type != NodeType.UNCONFIGURED:
            # restart service to allow frontend to be served for configuration
            exit(0)

    def disable(self):
        """Disable the ad hoc network"""
        print('[AdHoc] Disabling the ad hoc network')

        # disable the ad hoc network in the dhcp config
        with open(DHCP_CONFIG, 'r') as config_file:
            config = config_file.readlines()
            if ENABLED_START_POINTER in config:
                start = config.index(ENABLED_START_POINTER)
                config[start] = DISABLED_START_POINTER
                for i in range(start + 1, config.index(END_POINTER)):
                    if config[i][0] != '#':
                        config[i] = '#' + config[i]

                with open(DHCP_CONFIG, 'w') as write_handle:
                    write_handle.writelines(config)

                    # reload daemon config
                    system('sudo systemctl daemon-reload')

        if system('sudo service hostapd status > /dev/null') < 1:
            # disable the hostapd service
            system('sudo systemctl disable --now hostapd')

            # disable the dhcp server for the adhoc network
            system('sudo systemctl disable --now dnsmasq')

            # restart the network
            self.restart_network()

        self.config.network = 'client'

    def restart_network(self) -> None:
        """Restarts the dhcp service and network interface."""
        # restart the dhcp service
        system('sudo service dhcpcd restart')

        # restart the network interface
        system('sudo ifconfig wlan0 down')
        system('sudo ifconfig wlan0 up')
