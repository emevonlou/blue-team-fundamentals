#!/usr/bin/env bash
set -u

# ------------------------------------------------------------
# Blue Team - Run All Security Checks (with severity rollup)
# rc convention:
#   0  = OK (clean or whitelisted-only)
#   2  = WARN (findings but not critical)
#   10 = CRIT (critical findings or script/runtime errors)
# ------------------------------------------------------------

FINAL_RC=0

bump_rc() {
  local rc="${1:-0}"
  if [ "$rc" -ge 10 ]; then
    FINAL_RC=10
  elif [ "$rc" -eq 2 ] && [ "$FINAL_RC" -lt 10 ]; then
    FINAL_RC=2
  fi
}

ok()   { echo "[OK]   $*"; }
warn() { echo "[WARN] $*"; }
crit() { echo "[CRIT] $*"; }

echo "=============================="
echo " Blue Team Daily Security Run "
echo "=============================="
echo ""

# -----------------------------
# [1/3] File Integrity Check
# -----------------------------
echo "[1/3] Running File Integrity Check..."
OUT1="$(sudo ./file_integrity_check.sh 2>&1 || true)"
rc1=$?
echo "$OUT1"

bump_rc "$rc1"

if [ "$rc1" -ge 10 ]; then
  crit "Integrity changes found (non-whitelisted)."
elif [ "$rc1" -eq 2 ]; then
  warn "Integrity warnings detected."
else
  ok "Integrity check clean (or only whitelisted changes)."
fi

echo ""

# -----------------------------
# [2/3] Auth Log Monitor
# -----------------------------
echo "[2/3] Running Auth Log Monitor..."
OUT2="$(sudo ./auth_log_monitor.sh 2>&1 || true)"
rc2=$?
echo "$OUT2"

bump_rc "$rc2"

if [ "$rc2" -ge 10 ]; then
  crit "Auth monitor failed (critical)."
elif [ "$rc2" -eq 2 ]; then
  warn "Auth monitoring produced warnings."
else
  if echo "$OUT2" | grep -qi "Auth report saved"; then
    ok "Auth monitoring completed."
  else
    warn "Auth monitor ran but output looked unusual."
    bump_rc 2
  fi
fi

echo ""

# -----------------------------
# [3/3] Service Health Check
# -----------------------------
echo "[3/3] Running Service Health Check..."
OUT3="$(sudo ./service_health_check.sh 2>&1 || true)"
rc3=$?
echo "$OUT3"

bump_rc "$rc3"

if [ "$rc3" -ge 10 ]; then
  crit "Service health check failed (critical)."
elif [ "$rc3" -eq 2 ]; then
  warn "Service health check produced warnings."
else
  if echo "$OUT3" | grep -qi "saved to"; then
    ok "Service health report generated."
  else
    warn "Service health check ran but output looked unusual."
    bump_rc 2
  fi
fi

echo ""

# -----------------------------
# Final summary + exit code
# -----------------------------
if [ "$FINAL_RC" -eq 0 ]; then
  ok "Security routine completed successfully."
elif [ "$FINAL_RC" -eq 2 ]; then
  warn "Security routine completed with warnings."
else
  crit "Security routine completed with critical findings."
fi

echo "Completed at $(date)"
echo "=============================="

exit "$FINAL_RC"
