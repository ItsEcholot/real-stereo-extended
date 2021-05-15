"""Some networking helper functions."""
import netifaces


def get_hostname() -> str:
    """Returns the hostname of the machine.

    :returns: Hostname
    :rtype: str
    """
    with open('/etc/hostname', 'r') as file:
        return file.readline().strip()


def get_ip_address() -> str:
    """Returns the ip address of the machine.

    :returns: Ip address
    :rtype: str
    """
    if 'wlan0' not in netifaces.interfaces():
        return None

    addresses = netifaces.ifaddresses('wlan0')
    if netifaces.AF_INET not in addresses or len(addresses[netifaces.AF_INET]) < 1:
        return None

    return addresses[netifaces.AF_INET][0]['addr']
