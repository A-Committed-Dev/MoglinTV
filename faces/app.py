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


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_file(os.path.join(os.path.dirname(__file__), "assets", filename))


@app.route("/")
def index():
    return """<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;overflow:hidden;font-family:sans-serif}
iframe{width:100%;height:100%;border:none}
#overlay{position:fixed;top:0;left:0;width:100%;height:100%;z-index:50}
#popup{
  display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
  background:rgba(30,30,30,0.92);color:#fff;padding:40px 60px;border-radius:20px;
  font-size:2em;box-shadow:0 8px 32px rgba(0,0,0,0.4);z-index:100;
  text-align:center;pointer-events:none;opacity:0;transition:opacity 0.25s ease;
}
#popup.show{display:block;opacity:1}
#popup.hide{opacity:0}
</style>
</head><body>
<iframe id="f" src="/face"></iframe>
<div id="overlay"></div>
<div id="popup"><img src="/assets/charpage.png" alt="Charpage" style="max-width:200px;display:block;margin:0 auto 16px"><span>Charpage</span></div>
<script>
const es=new EventSource("/events");
es.onmessage=e=>{document.getElementById("f").src="/face?t="+Date.now();};

let hideTimer;
document.getElementById("overlay").addEventListener("click",()=>{
  const p=document.getElementById("popup");
  clearTimeout(hideTimer);
  p.classList.remove("hide");
  p.classList.add("show");
  hideTimer=setTimeout(()=>{
    p.classList.add("hide");
    setTimeout(()=>p.classList.remove("show","hide"),300);
  },2000);
});
</script>
</body></html>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
