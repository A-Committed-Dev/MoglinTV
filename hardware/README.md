# Hardware Controller — Raspberry Pi Docker Container

Controls an **SG90 servo** and reads an **ADXL335 accelerometer** via an **ADS1115** ADC on a **Raspberry Pi 5**, using Adafruit Blinka (CircuitPython on Linux) with `rpi-lgpio` for GPIO access.

## Wiring

| Component | Pin | Raspberry Pi |
|-----------|-----|-------------|
| SG90 Signal | Orange | GPIO 18 |
| SG90 VCC | Red | 5V |
| SG90 GND | Brown | GND |
| ADS1115 SDA | — | GPIO 2 (SDA1) |
| ADS1115 SCL | — | GPIO 3 (SCL1) |
| ADS1115 VDD | — | 3.3V |
| ADS1115 GND | — | GND |
| ADXL335 X | — | ADS1115 A0 |
| ADXL335 Y | — | ADS1115 A1 |
| ADXL335 Z | — | ADS1115 A2 |
| ADXL335 VCC | — | 3.3V |
| ADXL335 GND | — | GND |

## Prerequisites

Enable I2C on the Raspberry Pi:

```bash
sudo raspi-config  # Interface Options → I2C → Enable
```

## Run

```bash
cd hardware
docker compose up --build
```

## Verify I2C (inside container)

```bash
docker compose exec hardware i2cdetect -y 1
```

You should see the ADS1115 at address `0x48`.
