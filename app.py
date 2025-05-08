from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse
import os

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()

    # Use a direct fast-hosted URL to avoid Twilio timeouts
    greeting_url = "https://your-cdn-or-fast-hosting.com/greeting.mp3"

    resp.play(greeting_url)
    return str(resp)

# Optional: serve static files from your app if needed
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route("/")
def index():
    return "Voice assistant is live!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
