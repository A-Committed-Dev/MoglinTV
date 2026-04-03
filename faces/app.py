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
let lastMood="";
setInterval(()=>{
  fetch("/mood").then(r=>r.json()).then(d=>{
    if(lastMood&&d.mood!==lastMood)document.getElementById("f").src="/face?t="+Date.now();
    lastMood=d.mood;
  }).catch(()=>{});
},500);
</script>
</body></html>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
