import socket
import ssl


SERVICE_NAMES = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    8000: "HTTP",
    8080: "HTTP",
    8443: "HTTPS"
}


def get_service_name(port):
    """
    Determines the likely service based on the port number.
    """

    if port in SERVICE_NAMES:
        return SERVICE_NAMES[port]

    try:
        return socket.getservbyport(port, "tcp").upper()
    except OSError:
        return "UNKNOWN"


def grab_banner(target, port, timeout=2):
    """
    Connects to a TCP service and attempts to retrieve
    identifying information from its response.
    """

    service = get_service_name(port)

    try:
        sock = socket.create_connection(
            (target, port),
            timeout=timeout
        )

        sock.settimeout(timeout)

        if service == "HTTP":
            request = (
                f"HEAD / HTTP/1.1\r\n"
                f"Host: {target}\r\n"
                f"Connection: close\r\n\r\n"
            )

            sock.sendall(request.encode())
            banner = sock.recv(4096).decode(
                errors="ignore"
            )

        elif service == "HTTPS":
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            secure_sock = context.wrap_socket(
                sock,
                server_hostname=target
            )

            request = (
                f"HEAD / HTTP/1.1\r\n"
                f"Host: {target}\r\n"
                f"Connection: close\r\n\r\n"
            )

            secure_sock.sendall(request.encode())

            banner = secure_sock.recv(4096).decode(
                errors="ignore"
            )

            secure_sock.close()

            return banner.strip()

        else:
            banner = sock.recv(1024).decode(
                errors="ignore"
            )

        sock.close()

        return banner.strip()

    except (
        socket.timeout,
        ConnectionRefusedError,
        OSError,
        ssl.SSLError
    ):
        return ""


def extract_version(service, banner):
    """
    Extracts useful version information from
    a service banner.
    """

    if not banner:
        return "Unknown"

    if service in ("HTTP", "HTTPS"):
        for line in banner.splitlines():
            if line.lower().startswith("server:"):
                return line.split(":", 1)[1].strip()

        return "HTTP server detected"

    first_line = banner.splitlines()[0].strip()

    if len(first_line) > 80:
        first_line = first_line[:80]

    return first_line


def detect_service(target, port):
    """
    Performs service and basic version detection
    against one open TCP port.
    """

    service = get_service_name(port)
    banner = grab_banner(target, port)
    version = extract_version(service, banner)

    return {
        "port": port,
        "service": service,
        "version": version
    }


def detect_services(target, open_ports):
    """
    Performs service and version detection against
    a list of previously discovered open ports.
    """

    results = []

    print(
        f"\n[*] Detecting services and versions "
        f"on {target}...\n"
    )

    print(
        f"{'PORT':<10}"
        f"{'SERVICE':<15}"
        f"VERSION"
    )

    print("-" * 60)

    for port in open_ports:
        result = detect_service(target, port)
        results.append(result)

        print(
            f"{str(port) + '/tcp':<10}"
            f"{result['service']:<15}"
            f"{result['version']}"
        )

    print(
        f"\n[*] Service detection complete. "
        f"{len(results)} service(s) analyzed."
    )

    return results