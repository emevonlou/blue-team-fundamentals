#!/bin/bash

# Simple SSH failed login detector
# This script counts failed SSH login attempts from auth logs

LOG_FILE="/var/log/auth.log"

if [ ! -f "$LOG_FILE" ]; then
  echo "Log file not found. Are you running this on a Debian-based system?"
  exit 1
fi

echo "Analyzing SSH failed login attempts..."
echo

grep "Failed password" "$LOG_FILE" | awk '{print $(NF-3)}' | sort | uniq -c | sort -nr | head

echo
echo "Done. Review IPs with high failure counts."
