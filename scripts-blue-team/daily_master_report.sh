#!/bin/bash

REPORT_DIR="../reports"
DATE_TAG=$(date +%F)
MASTER="$REPORT_DIR/master_report_$DATE_TAG.txt"

mkdir -p "$REPORT_DIR"

echo "Blue Team Master Report" > "$MASTER"
echo "======================" >> "$MASTER"
echo "Date: $(date)" >> "$MASTER"
echo "" >> "$MASTER"

echo "[1] File Integrity Check" >> "$MASTER"
echo "------------------------" >> "$MASTER"
sudo ./file_integrity_check.sh >> "$MASTER" 2>&1
echo "" >> "$MASTER"

echo "[2] Auth Log Monitor" >> "$MASTER"
echo "--------------------" >> "$MASTER"
sudo ./auth_log_monitor.sh >> "$MASTER" 2>&1
echo "" >> "$MASTER"

echo "[3] Service Health Check" >> "$MASTER"
echo "------------------------" >> "$MASTER"
sudo ./service_health_check.sh >> "$MASTER" 2>&1
echo "" >> "$MASTER"

echo "End of report." >> "$MASTER"
echo "Master report saved to $MASTER"
