#!/bin/bash

# Simple File Integrity Checker
# Compares current file hashes against a baseline

BASELINE="baseline_hashes.txt"
FILES="/etc/passwd /etc/shadow /etc/group"

if [ ! -f "$BASELINE" ]; then
  echo "Baseline not found. Creating baseline..."
  for file in $FILES; do
    sha256sum "$file" >> "$BASELINE" 2>/dev/null
  done
  echo "Baseline created."
  exit 0
fi

echo "Checking file integrity..."
echo

sha256sum -c "$BASELINE" 2>/dev/null

echo
echo "Integrity check completed."
