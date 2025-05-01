from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()
    resp.say("Hello! This is SwiftCore’s AI Assistant. How can I help you today?", voice='alice')
    return str(resp)

@app.route("/")
def home():
    return "Voice Assistant is running."

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
