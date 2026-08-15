import ipaddress
import platform
import subprocess
import time


def ping_host(ip, timeout=1000):
    """
    Pings one IPv4 host and returns its status and latency.
    """

    system = platform.system().lower()

    if system == "windows":
        command = [
            "ping",
            "-n", "1",
            "-w", str(timeout),
            str(ip)
        ]
    else:
        command = [
            "ping",
            "-c", "1",
            "-W", str(max(1, timeout // 1000)),
            str(ip)
        ]

    start_time = time.perf_counter()

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=(timeout / 1000) + 1
        )

        elapsed = (time.perf_counter() - start_time) * 1000

        if result.returncode == 0:
            return {
                "ip": str(ip),
                "status": "UP",
                "latency": round(elapsed, 2)
            }

    except subprocess.TimeoutExpired:
        pass

    return {
        "ip": str(ip),
        "status": "DOWN",
        "latency": None
    }


def ping_sweep(network):
    """
    Performs host discovery across an IPv4 network.
    Returns a list of active hosts.
    """

    network = ipaddress.IPv4Network(network, strict=False)
    active_hosts = []

    print(f"\n[*] Performing host discovery on {network}...\n")

    for host in network.hosts():
        result = ping_host(host)

        if result["status"] == "UP":
            active_hosts.append(result)

            print(
                f"[+] {result['ip']:<15} "
                f"UP    {result['latency']} ms"
            )

    print(
        f"\n[*] Host discovery complete. "
        f"{len(active_hosts)} active host(s) found."
    )

    return active_hosts