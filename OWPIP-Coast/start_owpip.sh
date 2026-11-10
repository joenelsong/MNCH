#!/bin/bash
cd "$(dirname "$0")" || exit 1
LOG=/var/log/owpip.log
if ! touch "$LOG" 2>/dev/null; then
    LOG="$HOME/owpip.log"
fi
{
    echo "###############"
    date
    echo "WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-unset} DISPLAY=${DISPLAY:-unset}"
} >> "$LOG"
# A desktop login has no terminal. Wait until the screen session is up.
if [[ ! -t 0 ]]; then
    sleep 5
fi
exec python3 -u owpip-coast.py >> "$LOG" 2>&1
