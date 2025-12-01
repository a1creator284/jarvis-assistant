from flask import Flask, request, jsonify, render_template
from main import handle_command, get_status, speak

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask_jarvis():
    data = request.get_json(force=True)
    message = data.get("message", "")
    print("[/ask] Message:", message)

    reply = handle_command(message)
    print("[/ask] Reply:", reply)

    # Frontend calls /speak to avoid double speaking
    return jsonify({"reply": reply})


@app.route("/status")
def status():
    return jsonify(get_status())


@app.route("/speak", methods=["POST"])
def speak_route():
    data = request.get_json(force=True)
    text = data.get("text", "")
    print("[/speak] Request:", text)
    if text:
        speak(text)
    return jsonify({"ok": True})


if __name__ == "__main__":
    # 0.0.0.0 so phone on same Wi-Fi can open the UI
    app.run(host="0.0.0.0", port=5001, debug=True)
