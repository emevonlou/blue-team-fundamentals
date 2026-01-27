#!/bin/bash

# Must be run as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: this script must be run as root to access all security data."
    exit 1
fi

# Required commands check
for cmd in journalctl sha256sum who hostname date; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: required command '$cmd' not found."
        exit 1
    fi
done

REPORT_DIR="../reports"
REPORT_DATE=$(date +%F)
HOSTNAME=$(hostname)
REPORT_FILE="$REPORT_DIR/security_report_$REPORT_DATE.txt"

# Ensure report directory exists
mkdir -p "$REPORT_DIR"

echo "Security Daily Report" > "$REPORT_FILE"
echo "=====================" >> "$REPORT_FILE"
echo "Date: $(date)" >> "$REPORT_FILE"
echo "Host: $HOSTNAME" >> "$REPORT_FILE"
echo >> "$REPORT_FILE"

echo "Logged-in users:" >> "$REPORT_FILE"
echo "----------------" >> "$REPORT_FILE"
who >> "$REPORT_FILE"
echo >> "$REPORT_FILE"

echo "SSH failed login attempts (last 10):" >> "$REPORT_FILE"
echo "-----------------------------------" >> "$REPORT_FILE"
journalctl -u sshd --no-pager | grep -i "failed password" | tail -n 10 >> "$REPORT_FILE"
echo >> "$REPORT_FILE"

echo "File integrity status:" >> "$REPORT_FILE"
echo "----------------------" >> "$REPORT_FILE"
if [ -f integrity_db.sha256 ]; then
    sha256sum -c integrity_db.sha256 >> "$REPORT_FILE"
else
    echo "Integrity database not found." >> "$REPORT_FILE"
fi

echo >> "$REPORT_FILE"
echo "End of report." >> "$REPORT_FILE"

# Report retention: keep only last 7 days
find "$REPORT_DIR" -type f -name "security_report_*.txt" -mtime +7 -exec rm -f {} \;

echo "Report saved to $REPORT_FILE"

