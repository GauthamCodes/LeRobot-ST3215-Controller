# Troubleshooting Guide

## `Access is denied` on COM port
**Cause:** Another program is already using the port (usually Arduino IDE or Serial Monitor).
**Fix:** Close Arduino IDE completely, then retry.

---

## `There is no status packet!`
**Cause:** Servo is not responding. Usually a power or wiring issue.
**Fix checklist:**
1. Is 12V power connected to the barrel jack?
2. Is the red PWR LED on the board lit?
3. Check White→D, Red→V, Black→G wiring
4. Is the board switch set to `B USB-SERVO`?
5. Try unplugging and replugging the servo connector

---

## `Failed to open port`
**Cause:** Wrong COM port or driver not installed.
**Fix:**
1. Open Device Manager → Ports (COM & LPT)
2. Note the exact COM number shown (e.g. COM15)
3. Update `DEVICENAME = 'COM15'` in your script
4. If no port appears, install the CH340 driver from:
   `https://www.wch-ic.com/downloads/CH341SER_EXE.html`

---

## Servo not found during scan
**Fix:**
1. Run `ping.py` with `SCS_ID = 1` first
2. If ping also fails, check power and wiring
3. If ping succeeds but scan misses it, increase `time.sleep()` in scan loop

---

## `UnicodeEncodeError` when saving log file
**Cause:** File opened without UTF-8 encoding.
**Fix:** Make sure all file writes use `open(filename, 'w', encoding='utf-8')`

---

## All servos have the same ID (ID 1)
**Cause:** Factory default — all servos ship with ID 1.
**Fix:** Use `set_id.py` to assign unique IDs one servo at a time.
See `docs/SERVO_IDS.md` for full instructions.

---

## Servo resists being moved by hand
**Cause:** Torque is still enabled.
**Fix:** Use `teach_mode.py` or `teach_replay.py` which disables torque automatically before recording.

---

## Replay movements are jerky or too fast
**Fix:** Reduce the speed parameter in `WritePosEx`:
```python
packetHandler.WritePosEx(scs_id, pos, 800, 30)
#                                       ↑    ↑
#                                    speed  acceleration
#                           lower = smoother/slower
```
