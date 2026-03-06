# Wiring Guide

## Servo Wire Colors → Adapter Board

| Wire Color | Terminal | Meaning |
|---|---|---|
| ⚫ BLACK | G | Ground |
| 🔴 RED | V | Voltage (Power) |
| ⚪ WHITE | D | Data (Signal) |

## Board Switch Position

The small switch on the Waveshare Bus Servo Adapter (A) must be set to:
```
B  USB-SERVO   ✅  (for PC control via USB)
A  UART-SERVO  ❌  (for external microcontroller)
```

## Power Supply

- Connect 9–12.6V DC into the barrel jack (5.5×2.1mm)
- 12V recommended for maximum torque (30kg.cm)
- USB alone cannot power the servo — always use external supply
- The red PWR LED on the board should be lit when powered correctly

## Daisy Chain Connection

```
PC (USB)
   ↓
Waveshare Bus Servo Adapter (A)
   ↓ White→D  Red→V  Black→G
Servo ID 1
   ↓ (pass-through connector)
Servo ID 2
   ↓
Servo ID 3
   ↓
Servo ID 4
   ↓
Servo ID 5
   ↓
Servo ID 6
```

## Safety Rules

1. Always **turn off 12V power** before plugging or unplugging any servo wires
2. Never mix ST series (12V) and SC series (7.4V) servos on the same power supply
3. The servo connector only fits one way — do not force it
