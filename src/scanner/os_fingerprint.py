import platform
import re
import subprocess


def get_ttl(target, timeout=1000):
    """
    Sends one ping to the target and attempts to extract
    the TTL value from the response.

    Returns the TTL as an integer or None.
    """

    system = platform.system().lower()

    if system == "windows":
        command = [
            "ping",
            "-n", "1",
            "-w", str(timeout),
            target
        ]
    else:
        command = [
            "ping",
            "-c", "1",
            "-W", str(max(1, timeout // 1000)),
            target
        ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=(timeout / 1000) + 1
        )

        output = result.stdout

        match = re.search(
            r"ttl[=\s](\d+)",
            output,
            re.IGNORECASE
        )

        if match:
            return int(match.group(1))

    except (
        subprocess.TimeoutExpired,
        OSError
    ):
        pass

    return None


def estimate_os(ttl, open_ports=None):
    """
    Estimates the target operating system using TTL
    and selected open-port clues.
    """

    if open_ports is None:
        open_ports = []

    windows_clues = {135, 139, 445, 3389}
    unix_clues = {22}

    windows_score = len(
        windows_clues.intersection(open_ports)
    )

    unix_score = len(
        unix_clues.intersection(open_ports)
    )

    if ttl is None:
        if windows_score >= 2:
            return "Windows (service-based estimate)", "Low"

        if unix_score >= 1:
            return "Linux / Unix-like (service-based estimate)", "Low"

        return "Unknown", "Low"

    if ttl <= 64:
        os_guess = "Linux / Unix-like"
        confidence = "Medium"

        if unix_score > windows_score:
            confidence = "High"

    elif ttl <= 128:
        os_guess = "Windows"
        confidence = "Medium"

        if windows_score > 0:
            confidence = "High"

    else:
        os_guess = "Network device / Unix-like"
        confidence = "Low"

    return os_guess, confidence


def fingerprint_os(target, open_ports=None):
    """
    Performs basic OS fingerprinting and returns
    the result as a dictionary.
    """

    print(f"\n[*] Performing OS fingerprinting on {target}...")

    ttl = get_ttl(target)
    os_guess, confidence = estimate_os(
        ttl,
        open_ports
    )

    print(
        f"[+] TTL          : "
        f"{ttl if ttl is not None else 'Unavailable'}"
    )
    print(f"[+] OS Guess     : {os_guess}")
    print(f"[+] Confidence   : {confidence}")

    return {
        "ttl": ttl,
        "os": os_guess,
        "confidence": confidence
    }