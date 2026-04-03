#!/bin/bash
# Start Chromium in kiosk mode pointing at the Flask face server.
# Add this to your desktop autostart or systemd user service.

sleep 5


FLASK_URL="${FLASK_URL:-http://localhost:5000}"

exec chromium --noerrdialogs \
  --disable-infobars \
  --disable-session-crashed-bubble \
  --check-for-update-interval=31536000 \
  --kiosk \
  --incognito \
  --disable-translate \
  --disable-features=TranslateUI \
  --no-sandbox \
  --ozone-platform=wayland \
  --noerrdialogs \
  "$FLASK_URL"
