import time

from scanner.discovery import ping_sweep
from scanner.port_scanner import scan_ports, COMMON_PORTS
from scanner.service_detector import detect_services
from scanner.os_fingerprint import fingerprint_os

from utils.validator import (
    validate_network,
    validate_port_range,
    resolve_target
)

from utils.reporter import create_report

from utils.formatter import (
    print_banner,
    print_section,
    print_success,
    print_info,
    print_warning
)


VERSION = "1.0.0"


def display_menu():
    """
    Displays the main NetRecon menu.
    """

    print_banner()
    print(f" Version: {VERSION}")

    print("\n[1] Host Discovery")
    print("[2] Port Scan")
    print("[3] Service & Version Detection")
    print("[4] OS Fingerprinting")
    print("[5] Complete Scan")
    print("[6] Exit")


def main():
    """
    Main program loop for NetRecon.
    """

    while True:
        display_menu()

        choice = input(
            "\nSelect an option: "
        ).strip()

        # -------------------------------------------------
        # OPTION 1 - HOST DISCOVERY
        # -------------------------------------------------

        if choice == "1":
            print_info("Host Discovery selected.")

            network = input(
                "Enter network "
                "(example: 192.168.56.0/24): "
            ).strip()

            if not validate_network(network):
                print_warning(
                    "Invalid network address."
                )
                continue

            ping_sweep(network)

        # -------------------------------------------------
        # OPTION 2 - PORT SCAN
        # -------------------------------------------------

        elif choice == "2":
            print_info("Port Scan selected.")

            target = input(
                "Enter target IP or hostname: "
            ).strip()

            resolved_ip = resolve_target(target)

            if resolved_ip is None:
                print_warning(
                    "Unable to resolve target."
                )
                continue

            print_success(
                f"Target resolved to {resolved_ip}"
            )

            print("\nScan Type")
            print("[1] Quick Scan")
            print("[2] Standard Scan")
            print("[3] Custom Scan")

            scan_type = input(
                "\nSelect scan type: "
            ).strip()

            if scan_type == "1":
                ports = COMMON_PORTS

            elif scan_type == "2":
                ports = range(1, 1025)

            elif scan_type == "3":
                start_port = input(
                    "Start port: "
                ).strip()

                end_port = input(
                    "End port: "
                ).strip()

                if not validate_port_range(
                    start_port,
                    end_port
                ):
                    print_warning(
                        "Invalid port range."
                    )
                    continue

                ports = range(
                    int(start_port),
                    int(end_port) + 1
                )

            else:
                print_warning(
                    "Invalid scan type."
                )
                continue

            scan_ports(
                resolved_ip,
                ports
            )

        # -------------------------------------------------
        # OPTION 3 - SERVICE & VERSION DETECTION
        # -------------------------------------------------

        elif choice == "3":
            print_info(
                "Service & Version Detection selected."
            )

            target = input(
                "Enter target IP or hostname: "
            ).strip()

            resolved_ip = resolve_target(target)

            if resolved_ip is None:
                print_warning(
                    "Unable to resolve target."
                )
                continue

            print_success(
                f"Target resolved to {resolved_ip}"
            )

            print_info(
                "Scanning common ports first..."
            )

            open_ports = scan_ports(
                resolved_ip,
                COMMON_PORTS
            )

            if not open_ports:
                print_warning(
                    "No open ports found for "
                    "service detection."
                )
                continue

            detect_services(
                resolved_ip,
                open_ports
            )

        # -------------------------------------------------
        # OPTION 4 - OS FINGERPRINTING
        # -------------------------------------------------

        elif choice == "4":
            print_info(
                "OS Fingerprinting selected."
            )

            target = input(
                "Enter target IP or hostname: "
            ).strip()

            resolved_ip = resolve_target(target)

            if resolved_ip is None:
                print_warning(
                    "Unable to resolve target."
                )
                continue

            print_success(
                f"Target resolved to {resolved_ip}"
            )

            print_info(
                "Scanning common ports for "
                "additional OS clues..."
            )

            open_ports = scan_ports(
                resolved_ip,
                COMMON_PORTS
            )

            fingerprint_os(
                resolved_ip,
                open_ports
            )

        # -------------------------------------------------
        # OPTION 5 - COMPLETE SCAN
        # -------------------------------------------------

        elif choice == "5":
            complete_start = time.perf_counter()

            print_info(
                "Complete Scan selected."
            )

            target = input(
                "Enter target IP or hostname: "
            ).strip()

            resolved_ip = resolve_target(target)

            if resolved_ip is None:
                print_warning(
                    "Unable to resolve target."
                )
                continue

            print_success(
                f"Target resolved to {resolved_ip}"
            )

            print_section(
                "COMPLETE SCAN"
            )

            # ---------------------------------------------
            # Select scan profile
            # ---------------------------------------------

            print("\nComplete Scan Profile")
            print("[1] Quick    - Common ports")
            print("[2] Standard - Ports 1-1024")

            profile = input(
                "\nSelect profile: "
            ).strip()

            if profile == "1":
                ports = COMMON_PORTS

            elif profile == "2":
                ports = range(1, 1025)

            else:
                print_warning(
                    "Invalid scan profile."
                )
                continue

            # ---------------------------------------------
            # STEP 1 - PORT SCANNING
            # ---------------------------------------------

            print("\n[1/3] PORT SCANNING")

            open_ports = scan_ports(
                resolved_ip,
                ports
            )

            # ---------------------------------------------
            # STEP 2 - SERVICE & VERSION DETECTION
            # ---------------------------------------------

            print(
                "\n[2/3] "
                "SERVICE & VERSION DETECTION"
            )

            if open_ports:
                service_results = detect_services(
                    resolved_ip,
                    open_ports
                )

            else:
                service_results = []

                print_warning(
                    "No open ports detected."
                )

            # ---------------------------------------------
            # STEP 3 - OS FINGERPRINTING
            # ---------------------------------------------

            print(
                "\n[3/3] "
                "OS FINGERPRINTING"
            )

            os_result = fingerprint_os(
                resolved_ip,
                open_ports
            )

            # ---------------------------------------------
            # FINAL SUMMARY
            # ---------------------------------------------

            print_section(
                "SCAN SUMMARY"
            )

            print(
                f"Target       : {target}"
            )

            print(
                f"IP Address   : {resolved_ip}"
            )

            print(
                f"Open Ports   : "
                f"{len(open_ports)}"
            )

            print(
                f"OS Guess     : "
                f"{os_result['os']}"
            )

            print(
                f"Confidence   : "
                f"{os_result['confidence']}"
            )

            if service_results:
                print(
                    "\nDetected Services:"
                )

                for result in service_results:
                    print(
                        f"  "
                        f"{result['port']}/tcp - "
                        f"{result['service']} - "
                        f"{result['version']}"
                    )

            complete_elapsed = (
                time.perf_counter()
                - complete_start
            )

            print(
                f"\n[*] Complete scan finished "
                f"in {complete_elapsed:.2f} seconds."
            )

            # ---------------------------------------------
            # REPORT GENERATION
            # ---------------------------------------------

            save_choice = input(
                "\nSave scan report? (y/n): "
            ).strip().lower()

            if save_choice in (
                "y",
                "yes"
            ):

                report_path = create_report(
                    target,
                    resolved_ip,
                    open_ports,
                    service_results,
                    os_result
                )

                print_success(
                    "Report saved successfully:"
                )

                print(
                    f"    {report_path}"
                )

            else:
                print_info(
                    "Report not saved."
                )

        # -------------------------------------------------
        # OPTION 6 - EXIT
        # -------------------------------------------------

        elif choice == "6":
            print_info(
                "Exiting NetRecon."
            )

            break

        # -------------------------------------------------
        # INVALID MENU OPTION
        # -------------------------------------------------

        else:
            print_warning(
                "Invalid option. "
                "Please select 1-6."
            )


if __name__ == "__main__":
    main()