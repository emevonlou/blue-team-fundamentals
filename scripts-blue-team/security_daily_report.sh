#!/bin/bash

REPORT_DATE=$(date)
HOSTNAME=$(hostname)
REPORT_FILE="security_report_$(date +%F).txt"

echo "Security Daily Report" > "$REPORT_FILE"
echo "=====================" >> "$REPORT_FILE"
echo "Date: $REPORT_DATE" >> "$REPORT_FILE"
echo "Host: $HOSTNAME" >> "$REPORT_FILE"
echo >> "$REPORT_FILE"

echo "Logged-in users:" >> "$REPORT_FILE"
echo "----------------" >> "$REPORT_FILE"
who >> "$REPORT_FILE"
echo >> "$REPORT_FILE"

echo "SSH failed login attempts (last 10):" >> "$REPORT_FILE"
echo "-----------------------------------" >> "$REPORT_FILE"
journalctl -u sshd | grep "Failed password" | tail -n 10 >> "$REPORT_FILE"
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

echo "Report generated: $REPORT_FILE"
