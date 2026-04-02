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
    dtoverlay=pwm
  Then reboot.  (Defaults: PWM2=GPIO18)
"""

from servo import Servo
from acceleromter import Accelerometer


def main() -> None:
    print("Hardware controller started.")
    servo = Servo()
    servo.start()
    servo.set_servo_angle(0)  # Start at center position
    accelerometer = Accelerometer()

    try:
        while True:
            x, y, z = accelerometer.read()
            print(f"Accelerometer readings: X={x:.3f} V, Y={y:.3f} V, Z={z:.3f} V")
            # Example: Move servo to 45° over 2 seconds
            servo.move_to_angle(45, duration_s=2)
            servo.move_to_angle(0, duration_s=2)
            servo.move_to_angle(-45, duration_s=2)      
            
    finally:
        servo.stop()


if __name__ == "__main__":
    main()
