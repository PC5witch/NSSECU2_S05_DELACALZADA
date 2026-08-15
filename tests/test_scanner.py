import sys
import unittest
from pathlib import Path
from unittest.mock import patch


# Allow tests to import modules from src/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_PATH))


from utils.validator import (
    validate_ip,
    validate_network,
    validate_port,
    validate_port_range,
    resolve_target
)

from scanner.service_detector import (
    get_service_name,
    extract_version
)

from scanner.os_fingerprint import (
    estimate_os
)

from scanner.port_scanner import (
    scan_port
)


class TestValidator(unittest.TestCase):
    """
    Tests NetRecon input validation functions.
    """

    def test_valid_ipv4_address(self):
        self.assertTrue(
            validate_ip("192.168.56.101")
        )

    def test_invalid_ipv4_address(self):
        self.assertFalse(
            validate_ip("999.999.999.999")
        )

    def test_valid_network(self):
        self.assertTrue(
            validate_network("192.168.56.0/24")
        )

    def test_network_accepts_host_bits(self):
        self.assertTrue(
            validate_network("192.168.56.25/24")
        )

    def test_invalid_network(self):
        self.assertFalse(
            validate_network("192.168.999.0/24")
        )

    def test_valid_port(self):
        self.assertTrue(
            validate_port(80)
        )

    def test_lowest_valid_port(self):
        self.assertTrue(
            validate_port(1)
        )

    def test_highest_valid_port(self):
        self.assertTrue(
            validate_port(65535)
        )

    def test_port_zero_invalid(self):
        self.assertFalse(
            validate_port(0)
        )

    def test_port_above_range_invalid(self):
        self.assertFalse(
            validate_port(65536)
        )

    def test_non_numeric_port_invalid(self):
        self.assertFalse(
            validate_port("hello")
        )

    def test_valid_port_range(self):
        self.assertTrue(
            validate_port_range(1, 1024)
        )

    def test_invalid_reversed_port_range(self):
        self.assertFalse(
            validate_port_range(500, 100)
        )

    def test_invalid_port_range_value(self):
        self.assertFalse(
            validate_port_range("abc", 100)
        )

    def test_localhost_resolution(self):
        result = resolve_target("localhost")

        self.assertIsNotNone(result)


class TestServiceDetection(unittest.TestCase):
    """
    Tests service-name and version parsing.
    """

    def test_http_service_detection(self):
        self.assertEqual(
            get_service_name(80),
            "HTTP"
        )

    def test_https_service_detection(self):
        self.assertEqual(
            get_service_name(443),
            "HTTPS"
        )

    def test_ssh_service_detection(self):
        self.assertEqual(
            get_service_name(22),
            "SSH"
        )

    def test_http_version_extraction(self):
        banner = (
            "HTTP/1.1 200 OK\r\n"
            "Server: Apache/2.4.58\r\n"
            "Content-Type: text/html\r\n"
        )

        version = extract_version(
            "HTTP",
            banner
        )

        self.assertEqual(
            version,
            "Apache/2.4.58"
        )

    def test_unknown_banner(self):
        version = extract_version(
            "HTTP",
            ""
        )

        self.assertEqual(
            version,
            "Unknown"
        )

    def test_ssh_banner_extraction(self):
        banner = (
            "SSH-2.0-OpenSSH_9.6p1 Ubuntu"
        )

        version = extract_version(
            "SSH",
            banner
        )

        self.assertEqual(
            version,
            "SSH-2.0-OpenSSH_9.6p1 Ubuntu"
        )


class TestOSFingerprinting(unittest.TestCase):
    """
    Tests NetRecon OS estimation logic.
    """

    def test_windows_ttl(self):
        os_guess, confidence = estimate_os(
            128,
            []
        )

        self.assertEqual(
            os_guess,
            "Windows"
        )

        self.assertEqual(
            confidence,
            "Medium"
        )

    def test_windows_with_supporting_ports(self):
        os_guess, confidence = estimate_os(
            128,
            [135, 445]
        )

        self.assertEqual(
            os_guess,
            "Windows"
        )

        self.assertEqual(
            confidence,
            "High"
        )

    def test_linux_ttl(self):
        os_guess, confidence = estimate_os(
            64,
            []
        )

        self.assertEqual(
            os_guess,
            "Linux / Unix-like"
        )

        self.assertEqual(
            confidence,
            "Medium"
        )

    def test_linux_with_ssh(self):
        os_guess, confidence = estimate_os(
            64,
            [22]
        )

        self.assertEqual(
            os_guess,
            "Linux / Unix-like"
        )

        self.assertEqual(
            confidence,
            "High"
        )

    def test_unknown_os(self):
        os_guess, confidence = estimate_os(
            None,
            []
        )

        self.assertEqual(
            os_guess,
            "Unknown"
        )

        self.assertEqual(
            confidence,
            "Low"
        )

    def test_service_based_windows_estimate(self):
        os_guess, confidence = estimate_os(
            None,
            [135, 445]
        )

        self.assertEqual(
            os_guess,
            "Windows (service-based estimate)"
        )

        self.assertEqual(
            confidence,
            "Low"
        )


class TestPortScanner(unittest.TestCase):
    """
    Tests TCP port-scanning behavior using mocks.

    Mocking allows the scanner logic to be tested
    without depending on a real external host.
    """

    @patch("scanner.port_scanner.socket.socket")
    def test_open_port(self, mock_socket):
        mock_instance = (
            mock_socket.return_value
        )

        mock_instance.connect_ex.return_value = 0

        result = scan_port(
            "127.0.0.1",
            80
        )

        self.assertEqual(
            result,
            80
        )

        mock_instance.close.assert_called_once()

    @patch("scanner.port_scanner.socket.socket")
    def test_closed_port(self, mock_socket):
        mock_instance = (
            mock_socket.return_value
        )

        mock_instance.connect_ex.return_value = 1

        result = scan_port(
            "127.0.0.1",
            80
        )

        self.assertIsNone(result)

        mock_instance.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()