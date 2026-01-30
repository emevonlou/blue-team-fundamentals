#!/bin/bash

echo "=============================="
echo " Blue Team Daily Security Run "
echo "=============================="
echo ""

echo "[1/2] Running File Integrity Check..."
sudo ./file_integrity_check.sh

echo ""
echo "[2/2] Running Auth Log Monitor..."
sudo ./auth_log_monitor.sh

echo ""
echo "Security routine completed at $(date)"
echo "=============================="
