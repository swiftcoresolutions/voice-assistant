from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Gather
import os

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()

    # Create a Gather verb to listen for speech input
    gather = Gather(input="speech", action="/process", method="POST", timeout=3)
    greeting_url = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME'].lstrip('https://')}/static/greeting.mp3"
    gather.play(greeting_url)
    resp.append(gather)

    # Fallback if no speech is detected
    resp.say("Sorry, I didn't hear anything. Goodbye.", voice="alice")
    return str(resp)

@app.route("/process", methods=["POST"])
def process():
    user_input = request.form.get("SpeechResult", "")
    resp = VoiceResponse()

    if user_input:
        # Replace this with actual OpenAI or ElevenLabs logic if dynamic generation is needed
        response_text = f"You said: {user_input}. Thank you for calling SwiftCore Solutions."
        resp.say(response_text, voice="alice")
    else:
        resp.say("I'm sorry, I didn't catch that.", voice="alice")

    return str(resp)

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

@app.route("/")
def index():
    return "Voice assistant is live!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)