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
RESULT=$(sha256sum -c "$INTEGRITY_DB" 2>/dev/null)

CHANGES=$(echo "$RESULT" | grep -v "OK$")

if [ -z "$CHANGES" ]; then
    echo "All monitored files are intact."
else
    echo "Integrity changes detected!"
    echo "--------------------------------"
    echo "$CHANGES" | while read line; do
        FILE=$(echo "$line" | cut -d ':' -f 1)

        if [ -f "$WHITELIST" ] && grep -qx "$FILE" "$WHITELIST"; then
            echo "Ignored (whitelisted): $FILE"
        else
            echo "Modified file: $FILE"

# Exit code hardening:
# 0 = clean or whitelisted-only changes
# 2 = non-whitelisted changes detected
if echo "$CHANGES" | cut -d ':' -f 1 | while read f; do
    if [ -f "$WHITELIST" ] && grep -qx "$f" "$WHITELIST"; then
        true
    else
        echo "$f"
    fi
done | grep -q .; then
    exit 2
else
    exit 0
fi

     fi
    done
fi

