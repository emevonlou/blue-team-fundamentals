#!/bin/bash

# Colors (only for terminal output)
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m"

ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
crit() { echo -e "${RED}[CRIT]${NC} $1"; }

echo "=============================="
echo " Blue Team Daily Security Run "
echo "=============================="
echo ""

STEP_FAIL=0

echo "[1/3] Running File Integrity Check..."
OUT1=$(sudo ./file_integrity_check.sh 2>&1)
echo "$OUT1"
if echo "$OUT1" | grep -q "Modified file:"; then
  crit "Integrity changes found (non-whitelisted)."
  STEP_FAIL=1
else
  ok "Integrity check clean (or only whitelisted changes)."
fi

echo ""
echo "[2/3] Running Auth Log Monitor..."
OUT2=$(sudo ./auth_log_monitor.sh 2>&1)
echo "$OUT2"
if echo "$OUT2" | grep -qi "Auth report saved"; then
  ok "Auth monitoring completed."
else
  warn "Auth monitor ran but output looked unusual."
fi

echo ""
echo "[3/3] Running Service Health Check..."
OUT3=$(sudo ./service_health_check.sh 2>&1)
echo "$OUT3"
if echo "$OUT3" | grep -qi "saved to"; then
  ok "Service health report generated."
else
  warn "Service health check ran but output looked unusual."
fi

echo ""
if [ "$STEP_FAIL" -eq 1 ]; then
  crit "Security routine completed with CRITICAL findings."
else
  ok "Security routine completed successfully."
fi

echo ""
echo "[BONUS] Generating Master Report..."
sudo ./daily_master_report.sh

echo "Completed at $(date)"
echo "=============================="

