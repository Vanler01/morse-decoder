#!/usr/bin/env bash
# Remove the morse-code LaunchAgent and stop the daemon.

set -euo pipefail
PLIST_NAME="com.user.morse-code"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

echo "=== morse-code uninstaller ==="

if [ -f "$PLIST_PATH" ]; then
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    rm -f "$PLIST_PATH"
    echo "✓ LaunchAgent removed."
else
    echo "LaunchAgent not found — nothing to remove."
fi

# Clean up pid file
PID_FILE="$(cd "$(dirname "$0")" && pwd)/cache/daemon.pid"
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE" 2>/dev/null || true)
    if [ -n "$PID" ]; then
        kill "$PID" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
fi

echo "Done."
