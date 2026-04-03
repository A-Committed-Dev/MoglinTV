from flask import Flask, request, jsonify, send_file
import os

app = Flask(__name__)

VALID_MOODS = {"angry", "confused", "dead", "dizzy", "happy", "sad", "scared", "sleeping"}
current_mood = "happy"


@app.route("/mood", methods=["POST"])
def set_mood():
    global current_mood
    data = request.get_json(force=True)
    mood = data.get("mood", "").lower()
    if mood not in VALID_MOODS:
        return jsonify({"error": f"Invalid mood. Valid: {sorted(VALID_MOODS)}"}), 400
    current_mood = mood
    return jsonify({"mood": current_mood})


@app.route("/mood", methods=["GET"])
def get_mood():
    return jsonify({"mood": current_mood})


@app.route("/")
def face():
    path = os.path.join(os.path.dirname(__file__), "templates", f"{current_mood}.html")
    return send_file(path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
