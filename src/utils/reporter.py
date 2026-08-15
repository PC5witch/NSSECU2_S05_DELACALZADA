from datetime import datetime
from pathlib import Path


def create_report(
    target,
    ip_address,
    open_ports,
    service_results,
    os_result
):
    """
    Creates a text report containing the results
    of a complete NetRecon scan.
    """

    timestamp = datetime.now()

    project_root = Path(__file__).resolve().parents[2]
    reports_directory = project_root / "reports"

    reports_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    safe_ip = ip_address.replace(".", "_")

    filename = (
        f"scan_{safe_ip}_"
        f"{timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
    )

    report_path = reports_directory / filename

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as report:

        report.write("=" * 60 + "\n")
        report.write("                 NETRECON SCAN REPORT\n")
        report.write("=" * 60 + "\n\n")

        report.write(
            f"Scan Date     : "
            f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

        report.write(f"Target        : {target}\n")
        report.write(f"IP Address    : {ip_address}\n")
        report.write(
            f"Open Ports    : {len(open_ports)}\n"
        )

        report.write(
            f"OS Guess      : {os_result['os']}\n"
        )

        report.write(
            f"OS Confidence : "
            f"{os_result['confidence']}\n"
        )

        report.write(
            f"Observed TTL  : "
            f"{os_result['ttl']}\n"
        )

        report.write("\n")
        report.write("-" * 60 + "\n")
        report.write("OPEN PORTS AND SERVICES\n")
        report.write("-" * 60 + "\n\n")

        if service_results:

            report.write(
                f"{'PORT':<12}"
                f"{'SERVICE':<18}"
                f"VERSION\n"
            )

            report.write("-" * 60 + "\n")

            for result in service_results:

                report.write(
                    f"{str(result['port']) + '/tcp':<12}"
                    f"{result['service']:<18}"
                    f"{result['version']}\n"
                )

        else:
            report.write(
                "No open ports or services detected.\n"
            )

        report.write("\n")
        report.write("=" * 60 + "\n")
        report.write("Scan completed by NetRecon.\n")
        report.write("=" * 60 + "\n")

    return report_path