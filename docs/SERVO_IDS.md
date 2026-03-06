# Managing Servo IDs

## Default Factory ID
All ST3215 servos ship with **ID 1** from the factory.
If you connect multiple servos without changing their IDs, they will all
respond to the same commands simultaneously and cause communication errors.

---

## Step 1 — Check Existing IDs First
Before assigning new IDs, run the scanner to see what IDs are already set:
```bash
python scan_ids.py
```

If each servo already has a unique ID (e.g. 1, 2, 3, 4, 5, 6), skip to Step 3.

---

## Step 2 — Assign Unique IDs (if needed)

⚠️ **Connect only ONE servo at a time for this step.**

| Servo | CURRENT_ID | NEW_ID | Action |
|---|---|---|---|
| Servo 1 | — | — | Skip — keep as ID 1 |
| Servo 2 | 1 | 2 | Run set_id.py |
| Servo 3 | 1 | 3 | Run set_id.py |
| Servo 4 | 1 | 4 | Run set_id.py |
| Servo 5 | 1 | 5 | Run set_id.py |
| Servo 6 | 1 | 6 | Run set_id.py |

For each servo (except servo 1):
```
1. Turn OFF 12V power
2. Disconnect all servos
3. Connect ONLY the servo you are renaming
4. Turn ON 12V power
5. Edit set_id.py: set CURRENT_ID = 1, NEW_ID = (target ID)
6. Run: python set_id.py
7. Confirm: ✅ Successfully changed ID 1 → (target ID)
8. Turn OFF power, label the servo, set it aside
9. Repeat for next servo
```

---

## Step 3 — Reconnect the Full Chain
Once all servos have unique IDs:
```
1. Turn OFF 12V power
2. Reconnect all servos in the daisy chain
3. Turn ON 12V power
4. Run scan_ids.py to confirm all IDs are detected
```

---

## ID Rules
- Valid IDs are 1 to 253
- Each servo on the same bus must have a unique ID
- ID 254 is the broadcast address (all servos respond) — do not assign it
- IDs are stored permanently in EEPROM and survive power cycles
