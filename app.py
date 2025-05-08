from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse
import os

app = Flask(__name__)

# Voice route for Twilio webhook
@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()
    # Ensure this URL points to your deployed static MP3
    greeting_url = f"{os.environ['RENDER_EXTERNAL_HOSTNAME']}/static/greeting.mp3"
    resp.play(greeting_url)
    return str(resp)

# Serve static MP3 files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Optional root route
@app.route("/")
def index():
    return "Voice assistant is live!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
