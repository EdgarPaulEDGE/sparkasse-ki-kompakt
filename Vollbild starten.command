#!/bin/bash
# Öffnet den Vortrag in einem Chrome-Fenster ganz ohne Bedienleisten.
# Doppelklick genügt. Beenden mit cmd+Q.
open -na "Google Chrome" --args \
  --kiosk \
  --start-fullscreen \
  --disable-session-crashed-bubble \
  --disable-infobars \
  "https://aufgeweckt.edge-digital.ai/"
