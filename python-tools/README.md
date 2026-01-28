# Python Security Tools

This directory contains Python scripts used for log analysis and security monitoring.

## Tools

### log_analyzer.py
Analyzes system logs to identify suspicious patterns and anomalies.

## Purpose
- Blue Team automation
- SOC log analysis
- Security data processing

### ssh_bruteforce_detector.py

Detects potential SSH brute force attacks by aggregating failed login attempts per IP.

**Features**
- Parses systemd SSH logs
- Groups failed attempts by source IP
- Flags suspicious activity based on threshold
