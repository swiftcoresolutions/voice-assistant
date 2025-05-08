from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse
import os

app = Flask(__name__)

# Route that Twilio hits when a call comes in
@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()
    greeting_url = f"{os.environ['RENDER_EXTERNAL_HOSTNAME']}/static/greeting.mp3"
    resp.play(greeting_url)
    return str(resp)

# Serve MP3 file
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

# Root page for browser testing
@app.route("/")
def index():
    return "Voice assistant is live!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
