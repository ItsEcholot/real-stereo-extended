"""Stores network configurations in the wpa_supplicant.conf file"""
from os import system
from shlex import quote


WPA_SUPPLICANT_CONF = '/etc/wpa_supplicant/wpa_supplicant.conf'


class WpaSupplicant:
    """Stores network configurations in the wpa_supplicant.conf file"""

    def store_network(self, ssid: str, psk: str = None) -> None:
        """Stores a new network.

        :param str ssid: Network SSID
        :param str psk: Network password if it has one
        """
        self.remove_network(ssid)

        if psk is not None and len(psk) > 0:
            # encrypt the password and store it to the file
            system('wpa_passphrase {} {} >> {}'.format(
                quote(ssid), quote(psk), WPA_SUPPLICANT_CONF))
        else:
            # add the network without a password to the file
            with open(WPA_SUPPLICANT_CONF, 'a') as write_handle:
                write_handle.writelines([
                    'network={\n',
                    '\tssid="{}"\n'.format(ssid),
                    '\tkey_mgmt=NONE\n',
                    '}\n',
                ])

    def remove_network(self, ssid: str) -> None:
        """Removes a network.

        :param str ssid: Network SSID
        """
        with open(WPA_SUPPLICANT_CONF, 'r') as read_handle:
            lines = read_handle.readlines()
            ssid_search = 'ssid="{}"'.format(ssid.lower())
            network_definition_start = -1
            network_definition_end = 0

            for index, line in enumerate(lines):
                if line.strip().lower() == ssid_search:
                    # definition starts one line above
                    network_definition_start = index - 1
                elif line.strip() == '}' and network_definition_start > 0:
                    network_definition_end = index
                    break
            else:
                # network does not exist
                return

            with open(WPA_SUPPLICANT_CONF, 'w') as write_handle:
                write_handle.writelines(lines[:network_definition_start] +
                                        lines[network_definition_end + 1:])
