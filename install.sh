#!/usr/bin/env bash
# Install morse-code as a background LaunchAgent (auto-starts on login).

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$(which python3)"
PLIST_NAME="com.user.morse-code"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
LOG_DIR="$HOME/Library/Logs"

echo "=== morse-code installer ==="
echo "Script: $SCRIPT_DIR/main.py"
echo "Python: $PYTHON"

# ── LaunchAgent plist ─────────────────────────────────────────────────────────
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${SCRIPT_DIR}/main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/morse-code.log</string>
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/morse-code.err</string>
</dict>
</plist>
PLIST

# ── Load agent ────────────────────────────────────────────────────────────────
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load -w "$PLIST_PATH"

echo ""
echo "✓ Installed and started as LaunchAgent."
echo ""
echo "IMPORTANT — for Option+M hotkey, grant Accessibility permission:"
echo "  System Settings → Privacy & Security → Accessibility → add:"
echo "    $(dirname "$PYTHON")/python3"
echo ""
echo "The converter panel opens automatically on launch."
echo "Option+M toggles show/hide from anywhere."
echo ""
echo "Logs: $LOG_DIR/morse-code.log"
