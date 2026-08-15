# NetRecon User's Manual

**Version:** 1.0.0  
**Project:** Custom Network Scanner  
**Purpose:** Educational and Authorized Network Testing

---

## 1. Introduction

**NetRecon** is a custom Python-based network scanner designed for use in controlled and authorized laboratory environments. It provides basic network reconnaissance capabilities inspired by tools such as Nmap.

NetRecon includes the following features:

- Host discovery using ping sweeps
- TCP port scanning
- Service detection
- Version detection through banner grabbing
- Basic operating system fingerprinting
- Quick, Standard, and Custom scan profiles
- Complete Scan mode
- Scan report generation

> **Important:** NetRecon is intended for educational use and authorized network testing only. It should only be used on systems and networks that the user owns or has explicit permission to test.

---

## 2. System Requirements

NetRecon can be executed using either:

1. Python source code
2. The compiled Windows executable

### Python Requirements

- Python 3.x
- Windows or Linux
- Network connectivity to the target system

NetRecon uses Python standard-library modules only. No third-party runtime packages are required.

### Windows Executable

The compiled executable can be found at:

```text
executable/NetRecon.exe
```

---

## 3. Repository Structure

```text
NetRecon/
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
│
├── src/
│   ├── main.py
│   ├── scanner/
│   │   ├── __init__.py
│   │   ├── discovery.py
│   │   ├── port_scanner.py
│   │   ├── service_detector.py
│   │   └── os_fingerprint.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── validator.py
│       ├── formatter.py
│       └── reporter.py
│
├── executable/
│   └── NetRecon.exe
│
├── documentation/
│   └── USER_MANUAL.md
│
├── presentation/
├── screenshots/
├── reports/
└── tests/
```

---

# 4. Starting NetRecon

## Option A — Run Using Python

From the repository root:

```bash
py src/main.py
```

Alternatively:

```bash
python src/main.py
```

## Option B — Run the Windows Executable

Run:

```powershell
.\executable\NetRecon.exe
```

The following main menu will appear:

```text
============================================================
                        NETRECON
                 Custom Network Scanner
============================================================
 Educational & Authorized Network Testing Tool
============================================================
 Version: 1.0.0

[1] Host Discovery
[2] Port Scan
[3] Service & Version Detection
[4] OS Fingerprinting
[5] Complete Scan
[6] Exit
```

---

# 5. Host Discovery

Host Discovery performs a **ping sweep** across an IPv4 network to identify hosts that respond to ICMP Echo Requests.

## How to Use

Select:

```text
[1] Host Discovery
```

Enter a network using CIDR notation.

Example:

```text
192.168.56.0/24
```

NetRecon will enumerate the usable addresses within the network and test each host.

Example output:

```text
[*] Performing host discovery on 192.168.56.0/24...

[+] 192.168.56.101  UP    2.43 ms
[+] 192.168.56.102  UP    3.02 ms

[*] Host discovery complete. 2 active host(s) found.
```

## How It Works

NetRecon uses Python's `ipaddress` module to enumerate the usable IPv4 addresses inside the supplied network.

The operating system's `ping` utility is then used to send ICMP-based ping requests to each address.

A host that successfully responds is classified as:

```text
UP
```

## Limitation

A host may be active but still appear offline if its firewall blocks ICMP Echo Requests.

---

# 6. Port Scanning

Port scanning determines which TCP ports are accepting connections on a target system.

Select:

```text
[2] Port Scan
```

Enter a target IP address or hostname.

Example:

```text
192.168.56.102
```

or:

```text
localhost
```

NetRecon provides three scan profiles.

---

## 6.1 Quick Scan

Select:

```text
[1] Quick Scan
```

Quick Scan checks a predefined list of commonly used TCP ports.

Examples include:

| Port | Common Service |
|---:|---|
| 21 | FTP |
| 22 | SSH |
| 25 | SMTP |
| 53 | DNS |
| 80 | HTTP |
| 135 | RPC Endpoint Mapper |
| 139 | NetBIOS |
| 443 | HTTPS |
| 445 | SMB |
| 3306 | MySQL |
| 3389 | RDP |
| 5432 | PostgreSQL |
| 8080 | Alternate HTTP |

Quick Scan is useful when a fast overview of commonly used services is required.

---

## 6.2 Standard Scan

Select:

```text
[2] Standard Scan
```

Standard Scan checks TCP ports:

```text
1-1024
```

This provides broader coverage than Quick Scan.

---

## 6.3 Custom Scan

Select:

```text
[3] Custom Scan
```

The user can specify a starting and ending TCP port.

Example:

```text
Start port: 8000
End port: 8100
```

NetRecon will scan every port within the selected range.

---

## Example Port Scan Output

```text
[*] Starting TCP port scan on 127.0.0.1...
[*] Scanning 32 TCP port(s)...

[+] Port 135   OPEN    epmap
[+] Port 445   OPEN    microsoft-ds
[+] Port 8080  OPEN    unknown

[*] Port scan complete. 3 open port(s) found.
[*] Scan duration: 0.48 seconds
```

---

## How Port Scanning Works

NetRecon uses a **TCP Connect Scan**.

For every selected port, NetRecon creates a TCP socket and attempts to establish a connection with the target.

Conceptually:

```text
NetRecon
   |
   | TCP connection attempt
   v
Target:Port
   |
   +---- Connection succeeds ----> OPEN
   |
   +---- Connection fails -------> Closed/Unavailable
```

A successful TCP connection indicates that a service is accepting connections on the port.

---

## Concurrent Port Scanning

NetRecon uses Python's:

```python
ThreadPoolExecutor
```

to perform multiple TCP connection attempts concurrently.

The initial implementation scanned ports sequentially:

```text
Port 1
  ↓
Port 2
  ↓
Port 3
  ↓
...
Port 1024
```

This resulted in long scan times when connections had to wait for timeouts.

The improved implementation uses a bounded worker pool:

```text
               ┌── Port 1
               ├── Port 2
               ├── Port 3
NetRecon ──────┤
               ├── Port 4
               ├── ...
               └── Port N
```

This significantly improves scanning performance while keeping the number of concurrent workers controlled.

---

# 7. Service and Version Detection

Service detection attempts to identify the application or protocol associated with an open TCP port.

Version detection attempts to collect additional identifying information from the service.

Select:

```text
[3] Service & Version Detection
```

Enter the target IP address or hostname.

NetRecon first performs a scan of common ports.

The open ports are then passed to the service detection module.

Example:

```text
PORT      SERVICE        VERSION
------------------------------------------------------------
135/tcp   EPMAP          Unknown
445/tcp   SMB            Unknown
8080/tcp  HTTP           SimpleHTTP/0.6 Python/3.11.9
```

---

## How Service Detection Works

NetRecon initially determines the likely service using the TCP port number.

For example:

```text
22  → SSH
80  → HTTP
443 → HTTPS
445 → SMB
```

The scanner then attempts to gather additional information from the service.

---

# 8. Banner Grabbing and Version Detection

Some network services expose identifying information when a client connects.

NetRecon attempts to collect this information through **banner grabbing**.

For HTTP services, NetRecon sends an HTTP request and examines the response headers.

Example:

```text
Server: SimpleHTTP/0.6 Python/3.11.9
```

NetRecon can then display:

```text
8080/tcp  HTTP  SimpleHTTP/0.6 Python/3.11.9
```

Other services may automatically send information after a connection is established.

Example:

```text
220 VMware Authentication Daemon Version 1.10
```

This allows NetRecon to detect useful service information even when the port is not associated with a known service name.

---

## Unknown Versions

Some services intentionally hide or suppress version information.

In these situations NetRecon displays:

```text
Unknown
```

This does not necessarily indicate a scanning failure.

It means that NetRecon was unable to retrieve usable version information from the service.

---

# 9. OS Fingerprinting

NetRecon performs **basic operating system estimation** using:

1. Observed TTL values
2. Selected open-port clues

Select:

```text
[4] OS Fingerprinting
```

Enter the target.

Example:

```text
[*] Performing OS fingerprinting on 127.0.0.1...

[+] TTL          : 128
[+] OS Guess     : Windows
[+] Confidence   : High
```

---

## TTL-Based Estimation

TTL stands for:

**Time To Live**

Different operating systems commonly use different initial TTL values.

NetRecon uses the observed TTL as a clue.

| Observed TTL | Possible OS Family |
|---:|---|
| 1–64 | Linux / Unix-like |
| 65–128 | Windows |
| 129–255 | Network device / Unix-like |

For example:

```text
TTL = 128
```

may indicate:

```text
Windows
```

while:

```text
TTL = 64
```

may indicate:

```text
Linux / Unix-like
```

---

## Supporting Port Clues

NetRecon also considers selected open ports.

Possible Windows-related clues include:

```text
135  RPC
139  NetBIOS
445  SMB
3389 RDP
```

Port:

```text
22 SSH
```

may provide a supporting Linux/Unix clue.

For example:

```text
TTL = 128
Port 445 = OPEN
```

provides stronger evidence for a Windows system than TTL alone.

NetRecon therefore provides a confidence value such as:

```text
Low
Medium
High
```

---

## OS Fingerprinting Limitation

NetRecon's OS fingerprinting is **heuristic**.

It should not be treated as exact operating system identification.

TTL values may decrease as packets travel through routers, and network services can be installed on many different operating systems.

For this reason, NetRecon reports an:

```text
OS Guess
```

rather than claiming definitive OS identification.

---

# 10. Complete Scan

Complete Scan combines NetRecon's major reconnaissance functions into a single workflow.

Select:

```text
[5] Complete Scan
```

Enter the target.

Example:

```text
192.168.56.102
```

The user can then select:

```text
Complete Scan Profile

[1] Quick    - Common ports
[2] Standard - Ports 1-1024
```

NetRecon performs:

```text
Target
   ↓
Port Scanning
   ↓
Service Detection
   ↓
Version Detection
   ↓
OS Fingerprinting
   ↓
Scan Summary
```

---

## Example Complete Scan Summary

```text
============================================================
 SCAN SUMMARY
============================================================

Target       : localhost
IP Address   : 127.0.0.1
Open Ports   : 4
OS Guess     : Windows
Confidence   : High

Detected Services:
  135/tcp - EPMAP - Unknown
  445/tcp - SMB - Unknown
  902/tcp - UNKNOWN - VMware Authentication Daemon
  912/tcp - UNKNOWN - VMware Authentication Daemon

[*] Complete scan finished.
```

Complete Scan is useful when the user wants a general overview of a single target without manually running each individual module.

---

# 11. Saving Scan Reports

After a Complete Scan finishes, NetRecon asks:

```text
Save scan report? (y/n):
```

Enter:

```text
y
```

to save the results.

Reports are automatically stored inside:

```text
reports/
```

Example:

```text
reports/scan_127_0_0_1_20260815_163304.txt
```

---

## Report Contents

Each report contains:

- Scan date and time
- Target
- Resolved IP address
- Number of open ports
- OS estimate
- OS confidence
- Observed TTL
- Detected services
- Available version information

Example:

```text
============================================================
                 NETRECON SCAN REPORT
============================================================

Scan Date     : 2026-08-15 16:33:04
Target        : localhost
IP Address    : 127.0.0.1
Open Ports    : 4
OS Guess      : Windows
OS Confidence : High
Observed TTL  : 128

------------------------------------------------------------
OPEN PORTS AND SERVICES
------------------------------------------------------------

PORT        SERVICE           VERSION
------------------------------------------------------------
135/tcp     EPMAP             Unknown
445/tcp     SMB               Unknown
902/tcp     UNKNOWN           VMware Authentication Daemon
912/tcp     UNKNOWN           VMware Authentication Daemon

============================================================
Scan completed by NetRecon.
============================================================
```

---

# 12. Input Validation

NetRecon validates user input before performing network operations.

The program validates:

- IPv4 addresses
- CIDR network addresses
- TCP port numbers
- TCP port ranges
- Hostname resolution

---

## Invalid Network Example

Input:

```text
999.999.999.999/24
```

Output:

```text
[!] Invalid network address.
```

---

## Invalid Port Range Example

Input:

```text
Start port: 500
End port: 100
```

Output:

```text
[!] Invalid port range.
```

The scanner rejects the input instead of crashing.

---

# 13. Error Handling

NetRecon handles common networking errors including:

- Connection timeouts
- Connection refusals
- Invalid targets
- DNS resolution failures
- Invalid network ranges
- Invalid port ranges
- Closed ports
- Ping timeouts
- Services that do not expose banners

A failure involving one connection or port does not terminate the entire scan.

---

# 14. Testing Environment

NetRecon should be tested inside an authorized simulated environment.

A possible laboratory configuration is:

```text
                    HOST COMPUTER
                          |
                  VMware / VirtualBox
                          |
          --------------------------------
          |               |              |
          v               v              v
      Kali Linux       Windows VM      Linux VM
      Scanner          Target          Target
```

Recommended isolated networking configurations include:

- Host-only networking
- Internal networking
- A private virtual network created specifically for the lab

This helps keep scanning activity within the simulated environment.

---

# 15. Creating a Temporary Test Service

A temporary HTTP service can be created using Python.

Run:

```bash
python -m http.server 8080
```

The terminal should display something similar to:

```text
Serving HTTP on 0.0.0.0 port 8080
```

NetRecon can then detect the service:

```text
8080/tcp  HTTP  SimpleHTTP/0.6 Python/3.x.x
```

Stop the temporary HTTP server using:

```text
Ctrl + C
```

---

# 16. Source Code Architecture

NetRecon uses a modular architecture.

```text
main.py
   |
   +---- discovery.py
   |
   +---- port_scanner.py
   |
   +---- service_detector.py
   |
   +---- os_fingerprint.py
   |
   +---- validator.py
   |
   +---- reporter.py
   |
   +---- formatter.py
```

Each module has a specific responsibility.

---

## `main.py`

Controls:

- Main menu
- User interaction
- Scan selection
- Overall program workflow
- Complete Scan integration

---

## `discovery.py`

Responsible for:

- Ping requests
- Host discovery
- IPv4 ping sweeps

---

## `port_scanner.py`

Responsible for:

- TCP Connect scanning
- Quick scans
- Standard scans
- Custom port scans
- Concurrent connection attempts
- Basic service-name lookup

---

## `service_detector.py`

Responsible for:

- Service identification
- Banner grabbing
- HTTP requests
- HTTPS connections
- Basic version detection

---

## `os_fingerprint.py`

Responsible for:

- TTL extraction
- TTL interpretation
- Open-port OS clues
- OS estimation
- Confidence calculation

---

## `validator.py`

Responsible for:

- IPv4 validation
- CIDR validation
- Port validation
- Port-range validation
- Hostname resolution

---

## `reporter.py`

Responsible for:

- Creating scan reports
- Generating filenames
- Recording scan information
- Saving reports to the `reports/` directory

---

## `formatter.py`

Responsible for:

- NetRecon banner
- Section headings
- Information messages
- Success messages
- Warning messages

---

# 17. Limitations

NetRecon currently has several limitations.

### OS Fingerprinting

OS fingerprinting is heuristic and may not identify the exact operating system or version.

### Service Version Detection

Version detection depends on information exposed by the target service.

Some services intentionally suppress banners.

### ICMP Blocking

Hosts that block ICMP may appear offline during Host Discovery.

### TCP Connect Scanning

NetRecon uses full TCP connection attempts rather than stealthier scanning techniques.

These connections may be logged by the target.

### UDP

UDP scanning is not currently implemented.

### IPv6

NetRecon currently focuses on IPv4 networks.

### Fingerprint Database

NetRecon does not contain a large operating-system fingerprint database comparable to mature tools such as Nmap.

### Scale

NetRecon is intended primarily for educational laboratory environments rather than large enterprise networks.

---

# 18. Future Improvements

Possible improvements for future versions include:

- TCP SYN scanning
- UDP scanning
- IPv6 support
- Expanded service signature database
- Larger OS fingerprint database
- Improved HTTP fingerprinting
- Improved TLS fingerprinting
- CSV report export
- JSON report export
- HTML reports
- Graphical user interface
- Scan history
- Network topology visualization
- Configurable timeout settings
- Configurable concurrency
- Additional scan profiles

---

# 19. Troubleshooting

## Unable to Resolve Target

If NetRecon displays:

```text
[!] Unable to resolve target.
```

verify that the IP address or hostname was entered correctly.

---

## No Hosts Found During Ping Sweep

Possible causes include:

- Target is offline
- Target is on another virtual network
- Firewall is blocking ICMP
- Incorrect VM network configuration
- Network adapter is disconnected

Verify connectivity manually before scanning.

---

## No Open Ports Found

The target may not have any services listening on the selected ports.

Try:

- Another authorized target
- Standard Scan
- Custom Scan
- Starting a temporary HTTP server

---

## Version Displays as Unknown

This normally means that the target service did not expose usable version information.

It does not necessarily indicate a program error.

---

## Windows Security Warning

`NetRecon.exe` is generated using PyInstaller and is not digitally signed.

Windows may display a warning when opening a newly created unsigned executable.

The complete Python source code is included in the repository for inspection.

---

# 20. Ethical and Authorized Use

NetRecon was created for educational purposes and authorized cybersecurity laboratory testing.

The tool should only be used on:

- Systems owned by the user
- Virtual machines created for testing
- Networks where the user has explicit authorization

Do not scan third-party systems or networks without permission.

Network scanning can generate connection attempts that may be logged or interpreted as suspicious activity.

---

# 21. Closing NetRecon

From the main menu select:

```text
[6] Exit
```

NetRecon will terminate cleanly.

Example:

```text
[*] Exiting NetRecon.
```

---

# 22. Summary

NetRecon provides a modular implementation of several common network reconnaissance capabilities:

```text
Host Discovery
      +
TCP Port Scanning
      +
Service Detection
      +
Version Detection
      +
OS Fingerprinting
      +
Report Generation
```

The project demonstrates practical concepts including:

- Python socket programming
- IPv4 networking
- ICMP-based host discovery
- TCP connections
- Concurrent network scanning
- Service identification
- Banner grabbing
- OS estimation
- Input validation
- Error handling
- Modular software design
- Responsible cybersecurity testing

---

**NetRecon v1.0.0**  
*Custom Network Scanner — Educational & Authorized Network Testing Tool*