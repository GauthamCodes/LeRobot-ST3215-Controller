#!/usr/bin/env python
"""
teach_mode.py
-------------
Disables torque on all servos so they can be moved freely by hand.
Records every movement above the threshold to the screen, and saves
a timestamped .txt log file automatically when you press CTRL+C.

Workflow:
    1. Run script  → torque disables on all servos
    2. Move servos by hand freely
    3. Press CTRL+C → log is saved, torque re-enables

Usage:
    python teach_mode.py
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
    print("✅ Port opened successfully")
else:
    print("❌ Failed to open port")
    quit()

portHandler.setBaudRate(BAUDRATE)

# ── Disable torque on all servos ──────────────────────────
print("\n🔓 Disabling torque on all servos...")
for scs_id in SERVO_IDS:
    result, error = packetHandler.write1ByteTxRx(scs_id, SMS_STS_TORQUE_ENABLE, 0)
    if result == COMM_SUCCESS:
        print(f"   ID {scs_id} → torque OFF ✅")
    else:
        print(f"   ID {scs_id} → failed ❌")

print("\n✋ You can now move all servos freely by hand!")
print("📝 Every movement will be recorded below.")
print("💾 Press CTRL+C to stop and save to file.\n")
print("─" * 65)
print(f"{'Timestamp':<20} | {'Servo ID':<10} | {'Angle':>8} | {'Position':>8}")
print("─" * 65)

prev_angles = {scs_id: None for scs_id in SERVO_IDS}
log = []  # Stores all recorded movements

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
                    log.append({
                        "timestamp": timestamp,
                        "servo_id":  scs_id,
                        "angle":     angle,
                        "position":  pos
                    })
                    prev_angles[scs_id] = angle

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n" + "─" * 65)
    print(f"\n🛑 Stopped. {len(log)} movements recorded.")

    # ── Save to file ──────────────────────────────────────
    filename = f"teach_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{'Timestamp':<20} | {'Servo ID':<10} | {'Angle':>8} | {'Position':>8}\n")
        f.write("─" * 65 + "\n")
        for entry in log:
            f.write(f"{entry['timestamp']:<20} | ID {entry['servo_id']:<7} | "
                    f"{entry['angle']:>7}° | {entry['position']:>8}\n")

    print(f"💾 Log saved to: {filename}")

    # ── Re-enable torque on all servos ───────────────────
    print("\n🔒 Re-enabling torque on all servos...")
    for scs_id in SERVO_IDS:
        packetHandler.write1ByteTxRx(scs_id, SMS_STS_TORQUE_ENABLE, 1)
        print(f"   ID {scs_id} → torque ON ✅")

    portHandler.closePort()
    print("\n✅ Done!")
