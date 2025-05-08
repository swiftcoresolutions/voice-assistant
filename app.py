from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Gather, Play
import os
import openai
import requests

app = Flask(__name__)

# Load secrets
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

# ========== 1. Initial voice route ==========
@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()
    gather = Gather(input="speech", action="/voice-response", method="POST")
    gather.play(f"{HOSTNAME}/static/greeting.mp3")
    resp.append(gather)
    resp.say("Sorry, I didn't hear anything. Goodbye.", voice="alice")
    return str(resp)

# ========== 2. After user speaks ==========
@app.route("/voice-response", methods=["POST"])
def voice_response():
    user_input = request.form.get("SpeechResult", "")
    if not user_input:
        resp = VoiceResponse()
        resp.say("Sorry, I didn't catch that. Goodbye.", voice="alice")
        return str(resp)

    # Get OpenAI response
    ai_reply = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a helpful AI assistant for SwiftCore Solutions."},
            {"role": "user", "content": user_input}
        ]
    )["choices"][0]["message"]["content"]

    # Get ElevenLabs MP3
    eleven_url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": ai_reply,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }

    audio = requests.post(eleven_url, headers=headers, json=payload)
    with open("static/response.mp3", "wb") as f:
        f.write(audio.content)

    # Return TwiML to play the MP3
    resp = VoiceResponse()
    resp.play(f"{HOSTNAME}/static/response.mp3")
    return str(resp)

# ========== 3. Serve MP3s ==========
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

# ========== 4. Root ==========
@app.route("/")
def index():
    return "SwiftCore Voice Assistant is live!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
