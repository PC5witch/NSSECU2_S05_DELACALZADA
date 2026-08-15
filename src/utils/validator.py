import ipaddress
import socket


def validate_ip(target):
    """
    Validates an IPv4 address.

    Returns True if the address is valid.
    Returns False otherwise.
    """
    try:
        ipaddress.IPv4Address(target)
        return True
    except ipaddress.AddressValueError:
        return False


def validate_network(network):
    """
    Validates an IPv4 network in CIDR notation.

    Example:
        192.168.56.0/24
    """
    try:
        ipaddress.IPv4Network(network, strict=False)
        return True
    except ValueError:
        return False


def validate_port(port):
    """
    Checks whether a port number is valid.
    Valid TCP/UDP ports range from 1 to 65535.
    """
    try:
        port = int(port)
        return 1 <= port <= 65535
    except (ValueError, TypeError):
        return False


def validate_port_range(start_port, end_port):
    """
    Validates a range of ports.
    """
    if not validate_port(start_port) or not validate_port(end_port):
        return False

    return int(start_port) <= int(end_port)


def resolve_target(target):
    """
    Resolves either an IPv4 address or hostname
    into an IPv4 address.

    Returns the resolved IP address or None.
    """
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        return None
    
### for testing... delete afterwards

if __name__ == "__main__":
    print(validate_ip("192.168.56.101"))
    print(validate_ip("999.999.999.999"))

    print(validate_network("192.168.56.0/24"))
    print(validate_network("hello"))

    print(validate_port(80))
    print(validate_port(70000))

    print(validate_port_range(1, 1024))
    print(validate_port_range(500, 100))

    print(resolve_target("localhost"))