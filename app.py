from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()

    # Hardcoded tested greeting file
    greeting_url = "https://last-try-1jbd.onrender.com/static/greeting.mp3"

    resp.play(greeting_url)
    return Response(str(resp), mimetype='text/xml')

@app.route("/")
def index():
    return "Voice assistant is live!"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
