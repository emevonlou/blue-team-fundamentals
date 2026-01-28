#!/usr/bin/env python3

import subprocess
import re
from collections import Counter

THRESHOLD = 5  # attempts per IP
SERVICE = "sshd"

def get_failed_ssh_logs():
    try:
        result = subprocess.run(
            ["journalctl", "-u", SERVICE, "--no-pager"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except Exception as e:
        print(f"Error reading logs: {e}")
        return ""

def extract_ips(logs):
    ip_pattern = r"Failed password.*from ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)"
    return re.findall(ip_pattern, logs)

def main():
    logs = get_failed_ssh_logs()
    if not logs:
        print("No SSH logs found.")
        return

    ips = extract_ips(logs)
    if not ips:
        print("No failed SSH login attempts detected.")
        return

    counter = Counter(ips)

    print("SSH Failed Login Attempts by IP")
    print("--------------------------------")

    suspicious = False
    for ip, count in counter.items():
        print(f"{ip}: {count} attempts")
        if count >= THRESHOLD:
            suspicious = True

    if suspicious:
        print("\n Possible brute force activity detected.")
    else:
        print("\nNo brute force patterns detected.")

if __name__ == "__main__":
    main()
