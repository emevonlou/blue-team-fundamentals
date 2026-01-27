#!/bin/bash

SERVICE="sshd"
LOG_CMD="journalctl -u $SERVICE --no-pager"

if ! command -v journalctl &> /dev/null; then
    echo "Error: journalctl not found. This system may not use systemd."
    exit 1
fi

echo "Checking SSH failed login attempts..."
echo "----------------------------------"

FAILED_LOGINS=$($LOG_CMD | grep -i "failed password")

if [ -z "$FAILED_LOGINS" ]; then
    echo "No failed SSH login attempts found."
else
    echo "$FAILED_LOGINS" | tail -n 10
fi

