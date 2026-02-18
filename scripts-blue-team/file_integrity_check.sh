#!/bin/bash

INTEGRITY_DB="integrity_db.sha256"
TARGET_DIR="/etc"
WHITELIST="integrity_whitelist.txt"

# Must be run as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: this script must be run as root."
    exit 1
fi

# Check required command
if ! command -v sha256sum &> /dev/null; then
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

# Verify integrity
RESULT=$(sha256sum -c "$INTEGRITY_DB" 2>/dev/null || true)
CHANGES=$(printf "%s\n" "$RESULT" | grep -v "OK$" || true)

if [ -z "$CHANGES" ]; then
    echo "All monitored files are intact."
    exit 0
fi

echo "Integrity changes detected!"
echo "--------------------------------"

nonwhitelisted=0

while IFS= read -r line; do
    [ -z "$line" ] && continue
    FILE="${line%%:*}"

    if [ -f "$WHITELIST" ] && grep -Fxq "$FILE" "$WHITELIST"; then
        echo "Ignored (whitelisted): $FILE"
    else
        echo "Modified file: $FILE"
        nonwhitelisted=1
    fi
done <<< "$CHANGES"

if [ "$nonwhitelisted" -eq 1 ]; then
    echo "[CRIT] Integrity changes found (non-whitelisted)."
    exit 10
else
    echo "[OK] Integrity changes were only whitelisted."
    exit 0
fi

