from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse
import os

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()
    resp.play(f"{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/static/greeting.mp3")
    return str(resp)

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
