import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


COMMON_PORTS = [
    20, 21, 22, 23, 25, 53, 67, 68,
    80, 110, 123, 135, 137, 138, 139,
    143, 161, 389, 443, 445, 465, 587,
    993, 995, 1433, 1521, 3306, 3389,
    5432, 5900, 8080, 8443
]


def scan_port(target, port, timeout=0.5):
    """
    Attempts a TCP connection to one port.

    Returns the port number if the port is open.
    Returns None otherwise.
    """

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    sock.settimeout(timeout)

    try:
        result = sock.connect_ex(
            (target, port)
        )

        if result == 0:
            return port

    except (
        socket.timeout,
        socket.error,
        OSError
    ):
        pass

    finally:
        sock.close()

    return None


def get_service_name(port):
    """
    Returns the registered TCP service name
    associated with a port when available.
    """

    try:
        return socket.getservbyport(
            port,
            "tcp"
        )

    except OSError:
        return "unknown"


def scan_ports(
    target,
    ports,
    timeout=0.5,
    max_workers=100
):
    """
    Scans multiple TCP ports concurrently.

    A bounded thread pool is used to improve
    performance without creating one thread
    manually for every port.

    Returns a sorted list of open ports.
    """

    ports = list(ports)
    open_ports = []

    print(
        f"\n[*] Starting TCP port scan "
        f"on {target}..."
    )

    print(
        f"[*] Scanning {len(ports)} "
        f"TCP port(s)..."
    )

    start_time = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        future_to_port = {
            executor.submit(
                scan_port,
                target,
                port,
                timeout
            ): port
            for port in ports
        }

        for future in as_completed(
            future_to_port
        ):
            try:
                result = future.result()

                if result is not None:
                    open_ports.append(result)

            except Exception:
                continue

    open_ports.sort()

    for port in open_ports:
        service = get_service_name(port)

        print(
            f"[+] Port {port:<5} "
            f"OPEN    {service}"
        )

    elapsed = (
        time.perf_counter()
        - start_time
    )

    print(
        f"\n[*] Port scan complete. "
        f"{len(open_ports)} open port(s) found."
    )

    print(
        f"[*] Scan duration: "
        f"{elapsed:.2f} seconds"
    )

    return open_ports