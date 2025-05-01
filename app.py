from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()
    resp.say("Hey! This is SwiftCore’s AI Assistant test run. If you can hear me, the call setup is working!", voice="alice")
    return str(resp)

@app.route("/")
def home():
    return "SwiftCore Voice Assistant is live."

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
