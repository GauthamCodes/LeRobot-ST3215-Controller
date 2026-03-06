# ST3215 Serial Bus Servo Controller

A Python-based control system for the **Feetech ST3215 Serial Bus Servo** using the **Waveshare Bus Servo Adapter (A)**. Includes real-time position feedback, teach & replay mode with multithreading, and movement logging.

---

## 📦 Hardware Requirements

| Component | Details |
|---|---|
| **Servo** | Feetech ST3215 Series Serial Bus Servo |
| **Driver Board** | Waveshare Bus Servo Adapter (A) V1.1 |
| **Power Supply** | 9V–12.6V DC (12V recommended for full 30kg.cm torque) |
| **Connection** | USB (PC) → Adapter Board → Servo chain |

---

## 🔌 Wiring Guide

### Servo Wire Colors → Adapter Board

```
⚫ BLACK  →  G  (Ground)
🔴 RED    →  V  (Voltage / Power)
⚪ WHITE  →  D  (Data / Signal)
```

### Board Switch Position

Make sure the switch on the Waveshare adapter is set to:
```
B  USB-SERVO   ✅
```

### Daisy Chain Setup

```
PC (USB) → Adapter Board → Servo ID1 → Servo ID2 → Servo ID3 → ...
```

---

## 🎥 Demo

[![Demo Video](media/photos/connected%20and%20controlled%20by%20python.jpg)](media/videos/demo%20vid.mp4)

> Click the image above to watch the demo video.

---

## 📸 Photos

### Waveshare Serial Bus Servo Driver Board
![Waveshare Serial Bus Servo Driver Board](media/photos/Waveshare%20Serial%20Bus%20Servo%20Driver%20Board.jpg)

### Connected and Controlled by Python
![Connected and controlled by Python](media/photos/connected%20and%20controlled%20by%20python.jpg)

### Daisy Chained Manipulator with ST3215 Servo
![Daisy chained manipulator with ST3215 Servo](media/photos/Daisy%20chained%20manipulator%20with%20STM3215%20SERVO.jpg)

## 🛠️ Software Requirements

- Python 3.x
- pyserial library
- Waveshare STServo Python SDK

### Installation

**1. Install pyserial:**
```bash
pip install pyserial
```

**2. Download the STServo Python SDK from Waveshare:**
```
https://www.waveshare.com/wiki/Bus_Servo_Adapter_(A)
```

**3. Extract and set up the virtual environment:**
```bash
cd STServo_Python
stservo-env\Scripts\activate      # Windows
source stservo-env/bin/activate   # Linux/Mac
```

**4. Copy all scripts from this repo into the `sms_sts` folder:**
```
STServo_Python/
  stservo-env/
    sms_sts/          ← place all scripts here
    scservo_sdk/      ← SDK library (already there)
```

---

## 📁 Project Structure

```
ST3215_servo_controller/
│
├── README.md                    ← You are here
├── requirements.txt             ← Python dependencies
│
├── scripts/
│   ├── ping.py                  ← Test servo connection
│   ├── scan_ids.py              ← Scan and find all servo IDs
│   ├── set_id.py                ← Assign a new ID to a servo
│   ├── realtime_feedback.py     ← Live position monitoring
│   ├── teach_mode.py            ← Record movements by hand
│   └── teach_replay.py          ← Full teach & replay system
│
├── docs/
│   ├── WIRING.md                ← Detailed wiring instructions
│   ├── SERVO_IDS.md             ← How to manage servo IDs
│   └── TROUBLESHOOTING.md       ← Common errors and fixes
│
└── logs/                        ← Auto-generated movement logs saved here
```

---

## 🚀 Quick Start

### Step 1 — Find Your COM Port
Open **Device Manager → Ports (COM & LPT)** and note your port (e.g. COM15).
Update `DEVICENAME = 'COM15'` in whichever script you are running.

### Step 2 — Test Connection
```bash
python ping.py
```
Expected output:
```
✅ Port opened successfully
✅ Baudrate set successfully
[ID:001] ping Succeeded. SC Servo model number : 777
```

### Step 3 — Scan All Servo IDs
```bash
python scan_ids.py
```
Expected output:
```
✅ Found servo!  ID: 1  |  Model: 777
✅ Found servo!  ID: 2  |  Model: 777
...
```

### Step 4 — Monitor Live Positions
```bash
python realtime_feedback.py
```

### Step 5 — Teach & Replay Mode
```bash
python teach_replay.py
```

---

## 📜 Script Reference

### `ping.py`
Tests whether the servo with a given ID is connected and responding.

**Key settings:**
```python
SCS_ID     = 1        # Servo ID to ping
DEVICENAME = 'COM15'  # Your COM port
```

---

### `scan_ids.py`
Scans all 253 possible servo IDs and reports which ones are connected.
Useful when you don't know what IDs your servos have been assigned.

**Key settings:**
```python
DEVICENAME = 'COM15'
```

---

### `set_id.py`
Changes the ID of a servo permanently (stored in EEPROM).

> ⚠️ Connect **only one servo at a time** when using this script.

**Key settings:**
```python
CURRENT_ID = 1   # Servo's current ID
NEW_ID     = 2   # ID you want to assign
DEVICENAME = 'COM15'
```

---

### `realtime_feedback.py`
Reads and displays live position, angle, and speed of all servos.
Logs a new line every time a servo moves more than 1°. Never clears the screen — full history stays visible.

**Key settings:**
```python
SERVO_IDS  = [1, 2, 3, 4, 5, 6]   # List of connected servo IDs
DEVICENAME = 'COM15'
THRESHOLD  = 1.0                    # Degrees of movement to trigger a log
```

**Output format:**
```
Timestamp            | Servo ID   |    Angle | Position
────────────────────────────────────────────────────────
14:32:01.123         | ID 1       |   182.5° |     2079
14:32:02.001         | ID 3       |    45.0° |      512
```

---

### `teach_mode.py`
Disables torque on all servos so they can be moved freely by hand.
Records every movement above the threshold to screen and saves a `.txt` log file when you press CTRL+C.

**Key settings:**
```python
SERVO_IDS  = [1, 2, 3, 4, 5, 6]
DEVICENAME = 'COM15'
THRESHOLD  = 1.0
```

**Workflow:**
```
1. Run script → torque disables automatically
2. Move servos by hand → movements are logged
3. Press CTRL+C → log saved, torque re-enables
```

---

### `teach_replay.py` ⭐ Main Script
Full teach & replay system with **multithreading**. Records human movements and replays them exactly.

**Key settings:**
```python
SERVO_IDS   = [1, 2, 3, 4, 5, 6]
DEVICENAME  = 'COM15'
SAMPLE_RATE = 0.05    # Snapshot every 50ms (20 per second)
THRESHOLD   = 1.0     # Degrees to trigger a recording snapshot
```

**Commands:**
| Key | Action |
|-----|--------|
| `R` | Start recording — torque disables, move arm by hand |
| `S` | Stop recording — torque re-enables |
| `P` | Replay recorded movements |
| `C` | Clear current recording |
| `V` | View current live positions of all servos |
| `W` | Save recording to `.txt` file |
| `Q` | Quit cleanly |

**Threading Architecture:**
```
Thread 1 (read_thread)    → Reads all servo positions at 50Hz continuously
Thread 2 (record_thread)  → Captures snapshots while recording is active
Thread 3 (replay_thread)  → Sends positions to servos during replay
Main Thread               → Handles keyboard commands
```

> ℹ️ Servo reading is sequential (not parallel) because all servos share one serial bus. However all 3 threads run truly in parallel — reading never blocks recording or replaying.

---

## 📐 Position & Angle Reference

The ST3215 uses a **12-bit magnetic encoder**:

```
Position range : 0 – 4095
Angle range    : 0° – 360°

Formula: Angle = (Position / 4095) × 360

Examples:
  0    →   0.0°
  1024 →  90.0°
  2048 → 180.0°  (centre)
  3072 → 270.0°
  4095 → 360.0°
```

---

## ⚙️ SC vs ST Series — Key Differences

| | ST Series (yours) | SC Series |
|---|---|---|
| **Voltage** | 9–12.6V | 4.8–8.4V |
| **Rotation** | 360° | 180° |
| **Encoder bits** | 12-bit (0–4095) | 10-bit (0–1023) |
| **SDK Class** | `SMS_STS` | `SCSCL` |
| **Example models** | ST3215, ST3025 | SC15, SC09 |

> ⚠️ Never mix ST and SC servos on the same power supply — voltage difference will damage SC servos.

---

## 🔧 Troubleshooting

### `No such file or directory: SCServo.h`
→ SCServo library not installed correctly. See installation steps above.

### `Access is denied` on COM port
→ Close Arduino IDE or any other program using the port, then retry.

### `There is no status packet!`
→ Check 12V power is connected. Check White→D, Red→V, Black→G wiring. Confirm switch is set to `B USB-SERVO`.

### Servo not found during scan
→ Try `ping.py` with ID 1 first. If that fails, check power and wiring before scanning.

### `UnicodeEncodeError` when saving log
→ Make sure file is opened with `encoding='utf-8'` — see `teach_mode.py`.

---

## 📌 Important Notes

- Always **turn off 12V power** before plugging or unplugging servo wires
- The default factory ID for all ST3215 servos is **1**
- When assigning IDs with `set_id.py`, connect **only one servo at a time**
- USB alone cannot power the servo — always use external 12V supply
- The Waveshare Bus Servo Adapter (A) is a **pass-through adapter only** — it has no onboard processor and cannot run Arduino code

---

## 📄 License

MIT License — free to use and modify.

---

## 🙏 Credits

- [Waveshare](https://www.waveshare.com) — Hardware and Python SDK
- [Feetech](http://www.feetechrc.com) — ST3215 Servo
