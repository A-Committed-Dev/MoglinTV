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
from utility import Timer
import requests
import json
import queue
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

command_queue = queue.Queue()


class CommandHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length)) if length else {}
        command_queue.put(data)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"status": "running"}).encode())

    def log_message(self, format, *args):
        pass  # Suppress request logs


def start_command_server(port=8080):
    server = HTTPServer(("0.0.0.0", port), CommandHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Command server listening on port {port}")


def post_mood(mood: str) -> None:
    try:
        requests.post("http://faces:5000/mood", json={"mood": mood}, timeout=2)
    except requests.RequestException:
        pass

def main() -> None:
    print("Hardware controller started.")
    start_command_server()
    moglin = Moglin()
    default_mood = "happy"
    mood = default_mood
    shake_count = 0
    mood_timer = Timer()
    upside_down_timer = Timer(10)
    wiggle_timer = Timer(30)
    inactivity_timer = Timer(30 * 60)
    inactivity_timer.start()
    post_mood(mood)

    def set_timed_mood(new_mood, seconds):
        nonlocal mood
        mood = new_mood
        mood_timer.start(seconds)

    try:
        while True:
            while not command_queue.empty():
                cmd = command_queue.get_nowait()
                if "interact" in cmd:
                    inactivity_timer.start()
            

            match mood:
                case "happy":
                    if wiggle_timer.expired() or not wiggle_timer.active():
                        moglin.happy()
                        wiggle_timer.start()
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
                inactivity_timer.start()
                if mood not in {"angry", "dizzy"}:
                    shake_count += 1
                    if shake_count >= 2:
                        set_timed_mood("dizzy", 15)
                        shake_count = 0
                    else:
                        set_timed_mood("angry", 15)
                        
            elif moglin.upside_down():
                inactivity_timer.start()
                if not upside_down_timer.active():
                    upside_down_timer.start()
                    mood = "scared"
                elif upside_down_timer.expired():
                    mood = "dead"
                    
            elif inactivity_timer.expired():
                mood = "sleeping"
                
            else:
                upside_down_timer.reset()
                if mood_timer.expired():
                    mood = default_mood
                    mood_timer.reset()

            if mood != old_mood:
                post_mood(mood)
    finally:
        moglin.neutral()  # Ensure tail returns to neutral on exit
        


if __name__ == "__main__":
    main()
