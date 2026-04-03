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
    - X-axis -> ADS1115 A2
    - Y-axis -> ADS1115 A1
    - Z-axis -> ADS1115 A0
    - VCC    -> 5V
    - GND    -> GND

Prerequisites:
  Add to /boot/firmware/config.txt:
    dtoverlay=pwm
  Then reboot.  (Defaults: PWM2=GPIO18)
"""

from moglin import Moglin
import requests



def post_mood(mood: str) -> None:
    try:
        requests.post("http://faces:5000/mood", json={"mood": mood}, timeout=2)
    except requests.RequestException:
        pass

def main() -> None:
    print("Hardware controller started.")
    moglin = Moglin()
    mood = "happy"  # Default mood  
    post_mood(mood)

    try:
        while True:
            match mood:
                case "happy":
                    moglin.happy()
                case "sad":
                    moglin.sad()
                case "angry":
                    moglin.neutral()
                case "confused":
                    moglin.neutral()
                case "dead":
                    moglin.sad()
                case "dizzy":
                    moglin.neutral()
                case "scared":
                    moglin.neutral()
                case "sleeping":
                    moglin.neutral()
            
            old_mood = mood
            if moglin.shaken():
                mood = "angry"
            elif moglin.upside_down():
                mood = "dead"

            if mood != old_mood:
                post_mood(mood)
    finally:
        moglin.neutral()  # Ensure tail returns to neutral on exit
        


if __name__ == "__main__":
    main()
