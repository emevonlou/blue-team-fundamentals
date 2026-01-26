# Blue Team Scripts

This folder contains scripts created to support defensive security tasks.

## Examples

- Log parsing and analysis scripts
- User activity monitoring
- File integrity checks
- System hardening automation
- Alert and report generation

> Scripts are for educational purposes and should be tested only in controlled environments.

## SSH Failed Login Detector

**File:** `ssh_failed_logins.sh`

This Bash script parses authentication logs to identify IP addresses with multiple failed SSH login attempts.

### Purpose
- Assist in early detection of brute-force attacks
- Support incident response investigations

### Notes
- Designed for educational use
- Log file path may vary between distributions

## Python SSH Log Parser

**File:** `ssh_log_parser.py`

This Python script parses authentication logs to count failed SSH login attempts by IP.

### Purpose
- Improve log readability
- Demonstrate defensive automation using Python

### Notes
- Designed for educational use
- Log file path may vary between systems

## Logged Users Monitor

**File:** `logged_users_monitor.sh`

This script displays currently logged-in users and session details.

### Purpose
- Identify active sessions
- Support incident investigation and anomaly detection

### Notes
- Uses standard Linux commands
- Intended for monitoring and awareness
