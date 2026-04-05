import subprocess
import json
import cv2
import numpy as np
import os
import time
from time import sleep
import requests 

# --- CONFIG ---
WINDOW_CLASS = "Artix Game Launcher"
TEMPLATE_PATH = "death_template.png"
DEBUG_OUTPUT = "last_capture.png"  
THRESHOLD = 0.8

MAX_DEATH_COUNT = 3;
DEATH_COUNT = 0;

FIRST_DEATH_TIME = None
RESET_TIME_SECONDS = 600  # 10 minutes

def get_window_geometry():
    try:
        output = subprocess.check_output(["hyprctl", "clients", "-j"])
        clients = json.loads(output)
        for client in clients:
            if client.get("class") == WINDOW_CLASS:
                x, y = client["at"]
                w, h = client["size"]
                return f"{x},{y} {w}x{h}"
    except Exception as e:
        print(f"Error fetching window geometry: {e}")
    return None


def capture_game_window(geometry):
    try:
        process = subprocess.Popen(
            ["grim", "-g", geometry, "-"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, _ = process.communicate()
        nparr = np.frombuffer(out, np.uint8) 
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Capture failed: {e}")
        return None


def check_status():
    global DEATH_COUNT, FIRST_DEATH_TIME

    if not os.path.exists(TEMPLATE_PATH):
        print(f"Error: {TEMPLATE_PATH} missing!")
        return

    geo = get_window_geometry()
    screen = capture_game_window(geo)
    if screen is None: return

    # 1. Convert both to Grayscale
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)

    # 2. Use Canny Edge Detection
    screen_edges = cv2.Canny(screen_gray, 50, 150)
    template_edges = cv2.Canny(template, 50, 150)
    
    w, h = template.shape[::-1]

    # 3. Match the Edges
    res = cv2.matchTemplate(screen_edges, template_edges, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    print(f"Edge Match Confidence: {max_val:.2f}")

    cv2.imwrite("debug_edges.png", screen_edges)

    current_time = time.time()

    # Reset if too much time has passed since first death
    if FIRST_DEATH_TIME is not None and (current_time - FIRST_DEATH_TIME > RESET_TIME_SECONDS):
        DEATH_COUNT = 0
        FIRST_DEATH_TIME = None

    if max_val >= THRESHOLD: 
        print(">>> DEATH DETECTED <<<")
        cv2.rectangle(screen, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 255, 0), 2)
       
        # Start timer on first death
        if FIRST_DEATH_TIME is None:
            FIRST_DEATH_TIME = current_time


        if DEATH_COUNT <= MAX_DEATH_COUNT:
            post_mood("sad")
            DEATH_COUNT += 1
        else:
            DEATH_COUNT = 0
            post_mood("confused")
        
        print("waiting to be alive again")
        sleep(11)
    else:
        print(">>> STILL ALIVE <<<")

    
    cv2.imwrite(DEBUG_OUTPUT, screen)



def post_mood(mood: str) -> None:
    try:
        requests.post("http://moglinpi.local:8080/", json={mood: True}, timeout=2)
    except requests.RequestException:
        pass

if __name__ == "__main__":
    while True:
        geo = get_window_geometry()
        if geo is None:
            print("Game not open start client when game is running!")
            break
        check_status() 
        sleep(0.5)
