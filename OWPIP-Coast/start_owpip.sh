#!/bin/bash
cd "$(dirname "$0")" || exit 1
LOG=/var/log/owpip.log
if ! touch "$LOG" 2>/dev/null; then
    LOG="$HOME/owpip.log"
fi
echo "###############" >> "$LOG"
date >> "$LOG"
exec python3 owpip-coast.py >> "$LOG" 2>&1
