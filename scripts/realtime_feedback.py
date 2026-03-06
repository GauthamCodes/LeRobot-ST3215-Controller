#!/usr/bin/env python
"""
realtime_feedback.py
--------------------
Reads and displays live position, angle, speed, and timestamp of all
connected servos. Logs a new line every time a servo moves more than
the configured threshold. The screen never clears — full history
remains visible. Press CTRL+C to stop.

Usage:
    python realtime_feedback.py
"""

import sys
import time
from datetime import datetime
sys.path.append("..")
from scservo_sdk import *

# ── Settings ──────────────────────────────────────────────
DEVICENAME = 'COM15'                  # Change to your COM port
BAUDRATE   = 1000000
SERVO_IDS  = [1, 2, 3, 4, 5, 6]      # IDs of all connected servos
THRESHOLD  = 1.0                       # Degrees of movement to log
# ──────────────────────────────────────────────────────────

portHandler   = PortHandler(DEVICENAME)
packetHandler = sms_sts(portHandler)

if portHandler.openPort():
    print("✅ Port opened successfully\n")
else:
    print("❌ Failed to open port")
    quit()

portHandler.setBaudRate(BAUDRATE)

# Track previous angles to detect movement
prev_angles = {scs_id: None for scs_id in SERVO_IDS}

print("🔄 Monitoring servos for movement... (Press CTRL+C to stop)")
print("─" * 65)
print(f"{'Timestamp':<20} | {'Servo ID':<10} | {'Angle':>8} | {'Position':>8}")
print("─" * 65)

try:
    while True:
        for scs_id in SERVO_IDS:
            pos, spd, result, error = packetHandler.ReadPosSpeed(scs_id)
            if result == COMM_SUCCESS:
                angle = round(pos / 4095 * 360, 1)

                # First reading — store silently without logging
                if prev_angles[scs_id] is None:
                    prev_angles[scs_id] = angle

                # Log only when movement exceeds threshold
                elif abs(angle - prev_angles[scs_id]) > THRESHOLD:
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    print(f"{timestamp:<20} | ID {scs_id:<7} | {angle:>7}° | {pos:>8}")
                    prev_angles[scs_id] = angle

        time.sleep(0.2)  # 5 reads per second

except KeyboardInterrupt:
    print("\n" + "─" * 65)
    print("🛑 Stopped.")
    portHandler.closePort()
