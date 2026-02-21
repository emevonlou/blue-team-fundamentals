#!/usr/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INTEGRITY_DB="$SCRIPT_DIR/integrity_db.sha256"
WHITELIST="$SCRIPT_DIR/integrity_whitelist.txt"
TARGET_DIR="/etc"

# Classify changes:
# 0  = OK (no changes or whitelisted-only)
# 2  = WARN (non-whitelisted changes)
# 10 = CRIT (critical files changed)

CRITICAL_FILES=(
  "/etc/sudoers"
  "/etc/sudoers.d"
  "/etc/ssh/sshd_config"
  "/etc/pam.d/system-auth"
  "/etc/pam.d/password-auth"
)

SENSITIVE_FILES=(
  "/etc/shadow"
  "/etc/gshadow"
  "/etc/passwd"
  "/etc/group"
)

# Must be run as root
if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "Error: this script must be run as root."
  exit 1
fi

# Required command
if ! command -v sha256sum >/dev/null 2>&1; then
  echo "Error: sha256sum not found."
  exit 1
fi

echo "File Integrity Check"
echo "--------------------"

# If database does not exist, create it
if [ ! -f "$INTEGRITY_DB" ]; then
  echo "Integrity database not found."
  echo "Creating integrity database for $TARGET_DIR..."
  find "$TARGET_DIR" -type f -exec sha256sum {} \; > "$INTEGRITY_DB"
  chmod 600 "$INTEGRITY_DB"
  echo "Integrity database created and protected."
  exit 0
fi

# Verify integrity (never fail this script because sha256sum -c returns non-zero on mismatch)
RESULT="$(sha256sum -c "$INTEGRITY_DB" 2>/dev/null || true)"
CHANGES="$(printf "%s\n" "$RESULT" | grep -v "OK$" || true)"

FINAL_RC=0

if [ -z "$CHANGES" ]; then
  echo "All monitored files are intact."
  exit 0
fi

echo "Integrity changes detected!"
echo "--------------------------------"

# Collect non-whitelisted changed files (file paths only)
NONWL_FILES="$(
  printf "%s\n" "$CHANGES" \
  | cut -d ':' -f 1 \
  | while read -r f; do
      if [ -f "$WHITELIST" ] && grep -qx "$f" "$WHITELIST"; then
        echo "Ignored (whitelisted): $f"
      else
        echo "$f"
      fi
    done
)"

# If after whitelist there is nothing left, it's OK
if ! printf "%s\n" "$NONWL_FILES" | grep -q '^/'; then
  echo "[OK] Integrity changes were whitelisted (signal > noise)."
  exit 0
fi

# Otherwise classify each non-whitelisted file
printf "%s\n" "$NONWL_FILES" | while read -r FILE; do
  [ -z "$FILE" ] && continue

  SEVERITY=2  # default WARN

  # CRIT if file equals a critical file OR is under a critical directory
  for cf in "${CRITICAL_FILES[@]}"; do
    if [ "$FILE" = "$cf" ] || [[ "$FILE" == "$cf/"* ]]; then
      SEVERITY=10
      break
    fi
  done

  # If not already CRIT, keep WARN for sensitive files (explicit list)
  if [ "$SEVERITY" -ne 10 ]; then
    for sf in "${SENSITIVE_FILES[@]}"; do
      if [ "$FILE" = "$sf" ]; then
        SEVERITY=2
        break
      fi
    done
  fi

  if [ "$SEVERITY" -eq 10 ]; then
    echo "[CRIT] Modified critical file: $FILE"
  else
    echo "[WARN] Modified file: $FILE"
  fi

  if [ "$SEVERITY" -gt "$FINAL_RC" ]; then
    FINAL_RC="$SEVERITY"
  fi
done

if [ "$FINAL_RC" -eq 10 ]; then
  echo "[CRIT] Integrity changes found (non-whitelisted)."
elif [ "$FINAL_RC" -eq 2 ]; then
  echo "[WARN] Integrity changes found (non-whitelisted)."
fi

exit "$FINAL_RC"
