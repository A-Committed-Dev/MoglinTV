"""
RPi 5 hardware controller.
SG90 servo on GPIO 18 (hardware PWM), ADXL335 accelerometer via ADS1115 on I2C.

Wiring:
  SG90 Servo:
    - Signal -> GPIO 18 (hardware PWM)
    - VCC    -> 5V (separate supply recommended)
    - GND    -> GND (common with Pi)

  ADS1115 (I2C):
    - SDA -> GPIO 2 (SDA1)
    - SCL -> GPIO 3 (SCL1)
    - VDD -> 5V
    - GND -> GND

  ADXL335 -> ADS1115:
    - X-axis -> ADS1115 A0
    - Y-axis -> ADS1115 A1
    - Z-axis -> ADS1115 A2
    - VCC    -> 5V
    - GND    -> GND

Prerequisites:
  Add to /boot/firmware/config.txt:
    dtoverlay=pwm-2chan
  Then reboot.  (Defaults: PWM0=GPIO18, PWM1=GPIO19)
"""

import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from rpi_hardware_pwm import HardwarePWM

# ── SG90 Servo (hardware PWM) ────────────────────────────────────────────────
# SG90 datasheet specs:
#   Pulse width:  500–2400 µs
#   Pulse cycle:  20 ms (50 Hz)
#   Center (0°):  1500 µs
#   Range:        180° (-90° to +90°)
#   Dead band:    10 µs
#   Speed:        0.10 s/60° at 4.8V
#   Stall torque: 1.8 kgf·cm at 4.8V
#   Voltage:      4.8–6.0V
#
# RPi 5: channel 2 = GPIO 18, chip 2

SERVO_HZ = 50
MIN_PULSE_US = 500      # -90°
MAX_PULSE_US = 2400     # +90°
PERIOD_US = 1_000_000 / SERVO_HZ  # 20000 µs

pwm = HardwarePWM(pwm_channel=2, hz=SERVO_HZ, chip=2)
pwm.start(0)


def set_servo_angle(degrees: float) -> None:
    """Set SG90 to angle in range -90..+90."""
    degrees = max(-90, min(90, degrees))
    pulse_us = MIN_PULSE_US + (degrees + 90) / 180 * (MAX_PULSE_US - MIN_PULSE_US)
    duty_pct = pulse_us / PERIOD_US * 100
    pwm.change_duty_cycle(duty_pct)


# ── ADS1115 + ADXL335 ────────────────────────────────────────────────────────
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
# GY-61 ADXL335 outputs are typically within ~0.3-3.0V; use a tighter ADC range.
ads.gain = 1  # +/-4.096 V full-scale
accel_x = AnalogIn(ads, ADS.P0)
accel_y = AnalogIn(ads, ADS.P1)
accel_z = AnalogIn(ads, ADS.P2)

# On most GY-61 boards, the ADXL335 is regulated internally near 3.3V even when
# module input is 5V, so 0g is around half that internal supply (~1.65V).
ZERO_G_VOLTAGE = 1.65
SENSITIVITY = 0.300     # V/g (300 mV/g)


def voltage_to_g(v: float) -> float:
    return (v - ZERO_G_VOLTAGE) / SENSITIVITY


def read_accel() -> tuple[float, float, float]:
    return (
        voltage_to_g(accel_x.voltage),
        voltage_to_g(accel_y.voltage),
        voltage_to_g(accel_z.voltage),
    )


def main() -> None:
    print("Hardware controller started.")
    angle = -90
    direction = 5

    try:
        while True:
            x, y, z = read_accel()
            print(f"Accel X={x:+.2f}g  Y={y:+.2f}g  Z={z:+.2f}g  | Servo={angle}°")

            set_servo_angle(angle)
            angle += direction
            if angle >= 90 or angle <= -90:
                direction = -direction

            time.sleep(0.05)
    finally:
        pwm.stop()


if __name__ == "__main__":
    main()
