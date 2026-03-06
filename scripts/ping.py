#!/usr/bin/env python
"""
ping.py
-------
Tests whether the servo with a given ID is connected and responding.
Run this first to verify your hardware setup is working correctly.

Usage:
    python ping.py
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
SCS_ID     = 1          # Servo ID to ping (factory default is 1)
BAUDRATE   = 1000000    # ST3215 default baudrate
DEVICENAME = 'COM15'    # Change to your COM port (e.g. COM3, COM15)
# ──────────────────────────────────────────────────────────

portHandler   = PortHandler(DEVICENAME)
packetHandler = sms_sts(portHandler)

# Open port
if portHandler.openPort():
    print("✅ Port opened successfully")
else:
    print("❌ Failed to open port")
    print("Press any key to terminate...")
    getch()
    quit()

# Set baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("✅ Baudrate set successfully")
else:
    print("❌ Failed to set baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

# Ping the servo
scs_model_number, scs_comm_result, scs_error = packetHandler.ping(SCS_ID)
if scs_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))
else:
    print("[ID:%03d] ping Succeeded. SC Servo model number : %d" % (SCS_ID, scs_model_number))

if scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))

portHandler.closePort()
