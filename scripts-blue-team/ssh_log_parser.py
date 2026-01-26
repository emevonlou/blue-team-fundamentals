#!/usr/bin/env python3

"""
Simple SSH log parser
Counts failed SSH login attempts by IP address
"""

from collections import Counter

log_file = "/var/log/auth.log"

failed_ips = Counter()

try:
    with open(log_file, "r") as file:
        for line in file:
            if "Failed password" in line:
                parts = line.split()
                ip = parts[-4]
                failed_ips[ip] += 1
except FileNotFoundError:
    print("Log file not found. Adjust path for your system.")
    exit(1)

print("Failed SSH login attempts by IP:\n")

for ip, count in failed_ips.most_common():
    print(f"{ip}: {count}")
