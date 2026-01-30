#!/bin/bash

REPORT="../reports/auth_alerts_$(date +%Y-%m-%d).txt"

echo "Auth Log Monitor" > "$REPORT"
echo "-----------------" >> "$REPORT"

echo "Failed login attempts:" >> "$REPORT"
journalctl -u sshd | grep "Failed password" >> "$REPORT"

echo "" >> "$REPORT"
echo "Invalid users:" >> "$REPORT"
journalctl -u sshd | grep "Invalid user" >> "$REPORT"

echo "" >> "$REPORT"
echo "Report generated at $(date)" >> "$REPORT"

echo "Auth report saved to $REPORT"

