def print_banner():
    """
    Displays the NetRecon application banner.
    """

    print("\n" + "=" * 60)
    print("                        NETRECON")
    print("                 Custom Network Scanner")
    print("=" * 60)
    print(" Educational & Authorized Network Testing Tool")
    print("=" * 60)


def print_section(title):
    """
    Displays a formatted section heading.
    """

    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_success(message):
    """
    Displays a success message.
    """

    print(f"[+] {message}")


def print_info(message):
    """
    Displays an informational message.
    """

    print(f"[*] {message}")


def print_warning(message):
    """
    Displays a warning or error message.
    """

    print(f"[!] {message}")