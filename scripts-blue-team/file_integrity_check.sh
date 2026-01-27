#!/bin/bash

INTEGRITY_DB="integrity_db.sha256"
TARGET_DIR="/etc"

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
echo "Verifying file integrity..."
RESULT=$(sha256sum -c "$INTEGRITY_DB" 2>/dev/null)

CHANGES=$(echo "$RESULT" | grep -v "OK$")

if [ -z "$CHANGES" ]; then
    echo "All monitored files are intact."
else
    echo "WARNING: File integrity changes detected!"
    echo "-----------------------------------------"
    echo "$CHANGES"
fi

