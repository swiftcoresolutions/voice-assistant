from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse
import openai
import os
import requests
import uuid

app = Flask(__name__)

# Load API keys from environment
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

# Voice route
@app.route("/voice", methods=["POST"])
def voice():
    speech_text = request.form.get("SpeechResult", "")
    if not speech_text:
        resp = VoiceResponse()
        resp.say("Sorry, I didn’t catch that.")
        return str(resp)

    print("Caller said:", speech_text)

    # Step 1: Get OpenAI response
    reply = get_openai_response(speech_text)

    # Step 2: Convert to speech with ElevenLabs
    audio_file = generate_elevenlabs_mp3(reply)

    # Step 3: Return TwiML that plays the audio file
    resp = VoiceResponse()
    resp.play(f"{HOSTNAME}/static/{audio_file}")
    return str(resp)

# Serve MP3s from static folder
@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

# Optional root
@app.route("/")
def index():
    return "Voice assistant is live!"

# Generate AI response
def get_openai_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a helpful and professional customer service assistant for SwiftCore Solutions."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message["content"]

# Convert reply to MP3
def generate_elevenlabs_mp3(text):
    filename = f"{uuid.uuid4().hex}.mp3"
    filepath = os.path.join("static", filename)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.75}
    }

    response = requests.post(url, headers=headers, json=data)
    with open(filepath, "wb") as f:
        f.write(response.content)

    return filename

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
