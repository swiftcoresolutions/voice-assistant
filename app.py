from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Play
import os
import openai
import requests
import uuid
import json

app = Flask(__name__)

# Load API keys from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

@app.route("/voice", methods=["POST"])
def voice():
    user_input = request.form.get("SpeechResult", "")
    resp = VoiceResponse()

    if not user_input:
        resp.say("I'm sorry, I didn't catch that.", voice="alice")
        return str(resp)

    # Get OpenAI response (v1+ syntax)
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful AI assistant for SwiftCore Solutions."},
            {"role": "user", "content": user_input}
        ]
    )
    ai_reply = completion.choices[0].message.content

    # Generate MP3 via ElevenLabs
    mp3_filename = f"{uuid.uuid4().hex}.mp3"
    mp3_path = os.path.join("static", mp3_filename)

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": ai_reply,
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.8
        }
    }
    eleven_url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"
    response = requests.post(eleven_url, headers=headers, json=payload)

    with open(mp3_path, "wb") as f:
        f.write(response.content)

    mp3_url = f"{RENDER_EXTERNAL_HOSTNAME}/static/{mp3_filename}"
    resp.play(mp3_url)
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
