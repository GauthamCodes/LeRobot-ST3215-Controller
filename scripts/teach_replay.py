#!/usr/bin/env python
"""
teach_replay.py
---------------
Full teach & replay system with multithreading.

Records human hand movements across all servos, then replays
those exact movements back on command. Uses 3 background threads
running simultaneously so reading, recording, and replaying never
block each other.

Threading Architecture:
    Thread 1 (read_thread)   → Reads all servo positions at 50Hz continuously
    Thread 2 (record_thread) → Captures snapshots while recording is active
    Thread 3 (replay_thread) → Sends positions to servos during replay
    Main Thread              → Handles keyboard commands

Commands:
    R → Start recording  (torque OFF, move arm by hand)
    S → Stop recording   (torque ON)
    P → Replay recorded movements
    C → Clear recording
    V → View current live positions
    W → Save recording to .txt file
    Q → Quit cleanly

Usage:
    python teach_replay.py
"""

import sys
import time
import threading
from datetime import datetime
sys.path.append("..")
from scservo_sdk import *

# ── Settings ──────────────────────────────────────────────
DEVICENAME  = 'COM15'                 # Change to your COM port
BAUDRATE    = 1000000
SERVO_IDS   = [1, 2, 3, 4, 5, 6]     # IDs of all connected servos
SAMPLE_RATE = 0.05                     # Record a snapshot every 50ms (20/sec)
THRESHOLD   = 1.0                      # Degrees of movement to trigger a snapshot
# ──────────────────────────────────────────────────────────

portHandler   = PortHandler(DEVICENAME)
packetHandler = sms_sts(portHandler)

if portHandler.openPort():
    print("✅ Port opened successfully")
else:
    print("❌ Failed to open port")
    quit()

portHandler.setBaudRate(BAUDRATE)

# ── Shared State (protected by lock) ──────────────────────
lock          = threading.Lock()
current_pos   = {scs_id: 2048  for scs_id in SERVO_IDS}   # live raw positions
current_angle = {scs_id: 180.0 for scs_id in SERVO_IDS}   # live angles in degrees
recording     = []        # list of position snapshots [{id: pos, ..., _time: ts}]
is_recording  = False     # True while human is moving the arm
is_replaying  = False     # True while replay is running
stop_all      = False     # Set to True to shut down all threads
# ──────────────────────────────────────────────────────────


def set_torque(enable: bool):
    """Enable or disable torque on all servos."""
    state = 1 if enable else 0
    label = "ON  🔒" if enable else "OFF 🔓"
    for scs_id in SERVO_IDS:
        packetHandler.write1ByteTxRx(scs_id, SMS_STS_TORQUE_ENABLE, state)
    print(f"\n⚙️  Torque {label} on all servos")


# ── Thread 1: Continuously read all servo positions ───────
def read_thread():
    """
    Runs forever in the background.
    Reads each servo's position sequentially and updates shared state.
    Note: Reading is sequential (not parallel) because all servos
    share one physical serial bus — only one can talk at a time.
    """
    global stop_all
    while not stop_all:
        for scs_id in SERVO_IDS:
            pos, spd, result, error = packetHandler.ReadPosSpeed(scs_id)
            if result == COMM_SUCCESS:
                with lock:
                    current_pos[scs_id]   = pos
                    current_angle[scs_id] = round(pos / 4095 * 360, 1)
        time.sleep(0.02)   # Read at ~50Hz


# ── Thread 2: Record snapshots while human moves servos ───
def record_thread():
    """
    Runs forever in the background.
    When is_recording is True, captures a snapshot whenever any servo
    moves more than the threshold. Snapshots are appended to recording[].
    """
    global is_recording, stop_all
    prev = {scs_id: None for scs_id in SERVO_IDS}

    while not stop_all:
        if is_recording:
            with lock:
                snapshot = {scs_id: current_pos[scs_id]   for scs_id in SERVO_IDS}
                angles   = {scs_id: current_angle[scs_id] for scs_id in SERVO_IDS}

            # Check if any servo moved beyond threshold
            moved = False
            for scs_id in SERVO_IDS:
                if prev[scs_id] is None or abs(angles[scs_id] - prev[scs_id]) > THRESHOLD:
                    moved = True
                    prev[scs_id] = angles[scs_id]

            if moved:
                timestamp        = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                snapshot["_time"] = timestamp
                recording.append(snapshot)

                # Print live movement log to screen
                print(f"  📍 [{timestamp}] " +
                      "  ".join([f"ID{s}:{angles[s]}°" for s in SERVO_IDS]))

        time.sleep(SAMPLE_RATE)


# ── Thread 3: Replay recorded movements ───────────────────
def replay_thread():
    """
    Runs forever in the background.
    When is_replaying is True, sends each recorded snapshot to all
    servos in sequence, reproducing the recorded motion.
    """
    global is_replaying, stop_all

    while not stop_all:
        if is_replaying:
            if not recording:
                print("⚠️  Nothing recorded to replay!")
                is_replaying = False
                continue

            print(f"\n▶️  Replaying {len(recording)} snapshots...\n")
            set_torque(True)
            time.sleep(0.5)

            for i, snapshot in enumerate(recording):
                if not is_replaying:
                    break

                # Send all servos to their recorded positions simultaneously
                for scs_id in SERVO_IDS:
                    packetHandler.WritePosEx(scs_id, snapshot[scs_id], 1500, 50)

                print(f"  ▶️  Step {i+1}/{len(recording)} | " +
                      "  ".join([f"ID{s}:{round(snapshot[s]/4095*360,1)}°"
                                 for s in SERVO_IDS]))

                time.sleep(SAMPLE_RATE)

            print("\n✅ Replay complete!")
            is_replaying = False

        time.sleep(0.05)


# ── Save recording to text file ───────────────────────────
def save_recording():
    """Saves all recorded snapshots to a timestamped .txt file."""
    if not recording:
        print("⚠️  Nothing to save!")
        return
    filename = f"teach_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        header = f"{'Timestamp':<20} | " + " | ".join([f"ID{s} Pos" for s in SERVO_IDS])
        f.write(header + "\n")
        f.write("─" * 75 + "\n")
        for snap in recording:
            line = f"{snap['_time']:<20} | " + \
                   " | ".join([f"{snap[s]:>8}" for s in SERVO_IDS])
            f.write(line + "\n")
    print(f"💾 Saved {len(recording)} snapshots → {filename}")


# ── Main: Start threads and handle keyboard commands ──────
def main():
    global is_recording, is_replaying, stop_all, recording

    # Start all 3 background threads
    t1 = threading.Thread(target=read_thread,   daemon=True, name="ReadThread")
    t2 = threading.Thread(target=record_thread, daemon=True, name="RecordThread")
    t3 = threading.Thread(target=replay_thread, daemon=True, name="ReplayThread")
    t1.start()
    t2.start()
    t3.start()

    print("\n" + "═" * 55)
    print("       🤖 TEACH & REPLAY SYSTEM")
    print("═" * 55)
    print("  R  → Start recording (move arm by hand)")
    print("  S  → Stop recording")
    print("  P  → Replay recorded movements")
    print("  C  → Clear recording")
    print("  V  → View current positions")
    print("  W  → Save recording to file")
    print("  Q  → Quit")
    print("═" * 55 + "\n")

    while True:
        cmd = input("Command: ").strip().upper()

        if cmd == 'R':
            if is_replaying:
                print("⚠️  Stop replay first before recording!")
                continue
            recording.clear()
            is_recording = True
            set_torque(False)
            print("\n🔴 RECORDING STARTED — move the robot arm by hand!\n")
            print(f"{'Timestamp':<20}  Servo positions")
            print("─" * 55)

        elif cmd == 'S':
            is_recording = False
            set_torque(True)
            print(f"\n⏹️  RECORDING STOPPED — {len(recording)} snapshots captured")

        elif cmd == 'P':
            if is_recording:
                print("⚠️  Stop recording first!")
                continue
            if not recording:
                print("⚠️  Nothing recorded yet! Press R to start recording.")
                continue
            is_replaying = True

        elif cmd == 'C':
            recording.clear()
            print("🗑️  Recording cleared!")

        elif cmd == 'V':
            with lock:
                print("\n📊 Current Positions:")
                print("─" * 40)
                for scs_id in SERVO_IDS:
                    print(f"  ID {scs_id} | "
                          f"Pos: {current_pos[scs_id]:>5} | "
                          f"Angle: {current_angle[scs_id]:>6}°")
                print("─" * 40)

        elif cmd == 'W':
            save_recording()

        elif cmd == 'Q':
            print("\n🛑 Shutting down...")
            is_recording = False
            is_replaying = False
            stop_all     = True
            set_torque(True)
            save_recording()
            portHandler.closePort()
            print("✅ Goodbye!")
            break

        else:
            print("❓ Unknown command — use R, S, P, C, V, W, or Q")


if __name__ == "__main__":
    main()
