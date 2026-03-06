#!/usr/bin/env python
"""
scan_ids.py
-----------
Scans all 253 possible servo IDs and reports which ones are connected.
Run this when you don't know what IDs your servos have been assigned.

Takes approximately 30 seconds to complete a full scan.

Usage:
    python scan_ids.py
"""

import sys
import time
sys.path.append("..")
from scservo_sdk import *

# ── Settings ──────────────────────────────────────────────
DEVICENAME = 'COM15'    # Change to your COM port
BAUDRATE   = 1000000
# ──────────────────────────────────────────────────────────

portHandler   = PortHandler(DEVICENAME)
packetHandler = sms_sts(portHandler)

if portHandler.openPort():
    print("✅ Port opened successfully\n")
else:
    print("❌ Failed to open port")
    quit()

portHandler.setBaudRate(BAUDRATE)

print("🔍 Scanning all 253 possible servo IDs... please wait\n")

found = []

for servo_id in range(1, 254):
    try:
        model, result, error = packetHandler.ping(servo_id)
        if result == COMM_SUCCESS:
            print(f"✅ Found servo!  ID: {servo_id}  |  Model: {model}")
            found.append(servo_id)
        time.sleep(0.01)
    except KeyboardInterrupt:
        print("\n⚠️  Scan interrupted by user.")
        break

print("\n" + "─" * 45)
if found:
    print(f"📋 Total servos found : {len(found)}")
    print(f"📋 IDs discovered     : {found}")
else:
    print("❌ No servos found at any ID")
    print("   → Check wiring, 12V power, and COM port")

portHandler.closePort()
