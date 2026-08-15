# NetRecon

Custom Network Scanning and Reconnaissance Tool

## Overview

NetRecon is a custom Python-based network scanning tool designed
for authorized cybersecurity testing and simulated laboratory
environments.

The tool provides host discovery, port scanning, service and
version detection, and basic operating system fingerprinting.

## Features

- Host Discovery / Ping Sweep
- TCP Port Scanning
- Service Detection
- Version Detection
- OS Fingerprinting
- Quick, Standard, and Custom Scan Modes
- Scan Report Generation
- Input Validation and Error Handling

## Repository Contents

- `/src` - Python source code
- `/executable` - Compiled Windows executable
- `/documentation` - User's Manual
- `/presentation` - Final PowerPoint presentation with Tool Demonstration Video
- `/screenshots` - Testing screenshots
- `/reports` - Sample scan reports
- `/tests` - Program tests

## Usage

Run using Python:

python src/main.py

Or run:

executable/NetRecon.exe

## Test Environment

The tool was tested only against authorized virtual machines
in a controlled laboratory environment.

Example environment:

Scanner:
Kali Linux

Targets:
Windows VM
Linux VM

## Disclaimer

NetRecon was developed for educational purposes and authorized
network testing. Users should only scan systems and networks
they own or have explicit permission to test.