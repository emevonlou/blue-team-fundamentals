#!/bin/bash

REPORT="../reports/auth_alerts_$(date +%Y-%m-%d).txt"

echo "Auth Log Monitor" > "$REPORT"
echo "-----------------" >> "$REPORT"

echo "Failed login attempts:" >> "$REPORT"
journalctl -u sshd | grep "Failed password" >> "$REPORT"

echo "" >> "$REPORT"
echo "Top Failed IPs:" >> "$REPORT"

journalctl -u sshd \
| grep "Failed password" \
| awk '{print $(NF-3)}' \
| sort \
| uniq -c \
| sort -nr \
| head -5 >> "$REPORT"

echo "" >> "$REPORT"
echo "Invalid users:" >> "$REPORT"
journalctl -u sshd | grep "Invalid user" >> "$REPORT"

echo "" >> "$REPORT"
echo "Report generated at $(date)" >> "$REPORT"

CSV="../reports/auth_summary_$(date +%Y-%m-%d).csv"

echo "date,failed_attempts" > "$CSV"
COUNT=$(journalctl -u sshd | grep "Failed password" | wc -l)
echo "$(date +%Y-%m-%d),$COUNT" >> "$CSV"

echo "CSV summary saved to $CSV"

echo "Auth report saved to $REPORT"

