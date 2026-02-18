#!/usr/bin/bash
set -u

# -----------------------------
# Blue Team Daily Security Run
# -----------------------------

ok()   { echo "[OK]   $*"; }
warn() { echo "[WARN] $*"; }
crit() { echo "[CRIT] $*"; }

echo "=============================="
echo " Blue Team Daily Security Run "
echo "=============================="
echo ""

# Ensure we are running from scripts-blue-team dir (best effort)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 10

rc1=0
rc2=0
rc3=0

echo "[1/3] Running File Integrity Check..."
OUT1=$(sudo ./file_integrity_check.sh 2>&1)
rc1=$?
echo "$OUT1"

if [ "$rc1" -ge 10 ]; then
  crit "Integrity changes found (non-whitelisted)."
elif [ "$rc1" -eq 2 ]; then
  warn "Integrity warnings detected."
else
  ok "Integrity check clean (or only whitelisted changes)."
fi

echo ""
echo "[2/3] Running Auth Log Monitor..."
OUT2=$(sudo ./auth_log_monitor.sh 2>&1)
rc2=$?
echo "$OUT2"

if [ "$rc2" -ge 10 ]; then
  crit "Auth log monitor failed."
elif [ "$rc2" -eq 2 ]; then
  warn "Auth monitor found warnings."
else
  ok "Auth monitoring completed."
fi

echo ""
echo "[3/3] Running Service Health Check..."
OUT3=$(sudo ./service_health_check.sh 2>&1)
rc3=$?
echo "$OUT3"

if [ "$rc3" -ge 10 ]; then
  crit "Service health check failed."
elif [ "$rc3" -eq 2 ]; then
  warn "Service health check warnings detected."
else
  ok "Service health report generated."
fi

echo ""

# Final RC = worst wins
final_rc=0
if [ "$rc1" -ge 10 ] || [ "$rc2" -ge 10 ] || [ "$rc3" -ge 10 ]; then
  final_rc=10
elif [ "$rc1" -eq 2 ] || [ "$rc2" -eq 2 ] || [ "$rc3" -eq 2 ]; then
  final_rc=2
else
  final_rc=0
fi

if [ "$final_rc" -eq 0 ]; then
  ok "Security routine completed successfully."
elif [ "$final_rc" -eq 2 ]; then
  warn "Security routine completed with warnings."
else
  crit "Security routine completed with CRITICAL findings."
fi

echo ""
echo "[BONUS] Generating Master Report..."
# Best-effort: doesn't change final_rc
sudo ./daily_master_report.sh >/dev/null 2>&1 || true

echo "Completed at $(date)"
echo "=============================="

exit "$final_rc"
