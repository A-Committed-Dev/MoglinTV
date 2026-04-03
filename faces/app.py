from flask import Flask, request, jsonify, send_file, Response
import os
import queue
import threading

app = Flask(__name__)

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


@app.route("/")
def index():
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>*{margin:0;padding:0}html,body,iframe{width:100%;height:100%;border:none;overflow:hidden}</style>
</head><body>
<iframe id="f" src="/face"></iframe>
<script>
const es=new EventSource("/events");
es.onmessage=e=>{document.getElementById("f").src="/face?t="+Date.now();};
</script>
</body></html>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
