#!/usr/bin/env python
"""
set_id.py
---------
Changes the ID of a servo permanently (stored in EEPROM).

⚠️  IMPORTANT: Connect ONLY ONE servo at a time when running this script.
    If multiple servos share the same ID, they will all respond and
    cause communication conflicts.

Steps:
    1. Disconnect all servos except the one you want to rename
    2. Set CURRENT_ID to the servo's existing ID (factory default: 1)
    3. Set NEW_ID to the ID you want to assign
    4. Run the script
    5. Label the servo with its new ID
    6. Repeat for each servo

Usage:
    python set_id.py
"""

import sys
import os

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

sys.path.append("..")
from scservo_sdk import *

# ── Settings ──────────────────────────────────────────────
CURRENT_ID = 1      # The servo's current ID
NEW_ID     = 2      # The ID you want to assign (1–253)
DEVICENAME = 'COM15'
BAUDRATE   = 1000000
# ──────────────────────────────────────────────────────────

portHandler   = PortHandler(DEVICENAME)
packetHandler = sms_sts(portHandler)

if portHandler.openPort():
    print("✅ Port opened")
else:
    print("❌ Failed to open port")
    quit()

if portHandler.setBaudRate(BAUDRATE):
    print("✅ Baudrate set")
else:
    print("❌ Failed to set baudrate")
    portHandler.closePort()
    quit()

# Unlock EEPROM so we can write to it
scs_comm_result, scs_error = packetHandler.unLockEprom(CURRENT_ID)
if scs_comm_result != COMM_SUCCESS:
    print(f"❌ EEPROM unlock failed: {packetHandler.getTxRxResult(scs_comm_result)}")
    portHandler.closePort()
    quit()

# Write new ID to the servo
scs_comm_result, scs_error = packetHandler.write1ByteTxRx(CURRENT_ID, SMS_STS_ID, NEW_ID)
if scs_comm_result != COMM_SUCCESS:
    print(f"❌ ID write failed: {packetHandler.getTxRxResult(scs_comm_result)}")
else:
    # Lock EEPROM again to protect the new ID
    packetHandler.LockEprom(NEW_ID)
    print(f"✅ Successfully changed ID {CURRENT_ID} → {NEW_ID}")
    print(f"   Label this servo: 'ID {NEW_ID}'")

if scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))

portHandler.closePort()
