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
import time



def post_mood(mood: str) -> None:
    try:
        requests.post("http://faces:5000/mood", json={"mood": mood}, timeout=2)
    except requests.RequestException:
        pass

def main() -> None:
    print("Hardware controller started.")
    moglin = Moglin()
    default_mood = "happy"
    mood = default_mood
    mood_expires = 0
    shake_count = 0
    upside_down_since = 0
    last_happy_wiggle = 0
    post_mood(mood)

    def set_timed_mood(new_mood, seconds):
        nonlocal mood, mood_expires
        mood = new_mood
        mood_expires = time.monotonic() + seconds

    try:
        while True:
            match mood:
                case "happy":
                    if time.monotonic() - last_happy_wiggle >= 30:
                        moglin.happy()
                        last_happy_wiggle = time.monotonic()
                    else:
                        moglin.neutral()
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
            if moglin.shaken(threshold=0.6):
                if mood not in {"angry", "dizzy"}:
                    shake_count += 1
                    if shake_count >= 2:
                        set_timed_mood("dizzy", 15)
                        shake_count = 0
                    else:
                        set_timed_mood("angry", 15)
            elif moglin.upside_down():
                if upside_down_since == 0:
                    upside_down_since = time.monotonic()
                    set_timed_mood("scared", 2)
                elif time.monotonic() - upside_down_since >= 10:
                    set_timed_mood("dead", 15)
            else:
                upside_down_since = 0
                if mood_expires and time.monotonic() >= mood_expires:
                    mood = default_mood
                    mood_expires = 0

            if mood != old_mood:
                post_mood(mood)
    finally:
        moglin.neutral()  # Ensure tail returns to neutral on exit
        


if __name__ == "__main__":
    main()
