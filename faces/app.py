from flask import Flask, request, jsonify, send_file, Response
import os
import queue
import threading
import requests as http_client
from charpageProxy import charpage

app = Flask(__name__)
app.register_blueprint(charpage)

VALID_MOODS = {"angry", "confused", "dead", "dizzy", "happy", "sad", "scared", "sleeping"}
current_mood = "happy"
listeners: list[queue.Queue] = []
listeners_lock = threading.Lock()


@app.route("/mood", methods=["POST"])
def set_mood():
    global current_mood
    data = request.get_json(force=True)
    mood = data.get("mood", "").lower()
    if mood not in VALID_MOODS:
        return jsonify({"error": f"Invalid mood. Valid: {sorted(VALID_MOODS)}"}), 400
    current_mood = mood
    with listeners_lock:
        for q in listeners:
            q.put(mood)
    return jsonify({"mood": current_mood})


@app.route("/mood", methods=["GET"])
def get_mood():
    return jsonify({"mood": current_mood})


@app.route("/events")
def events():
    def stream():
        q = queue.Queue()
        with listeners_lock:
            listeners.append(q)
        try:
            while True:
                mood = q.get()
                yield f"data: {mood}\n\n"
        finally:
            with listeners_lock:
                listeners.remove(q)
    return Response(stream(), mimetype="text/event-stream")


@app.route("/face")
def face():
    path = os.path.join(os.path.dirname(__file__), "templates", f"{current_mood}.html")
    return send_file(path)


@app.route("/interact", methods=["POST"])
def interact():
    try:
        http_client.post("http://hardware:8080", json={"interact": True}, timeout=2)
    except http_client.RequestException:
        pass
    return jsonify({"status": "ok"})


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_file(os.path.join(os.path.dirname(__file__), "assets", filename))


@app.route("/")
def index():
    return send_file(os.path.join(os.path.dirname(__file__), "index.html"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
