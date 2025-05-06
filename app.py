import os
import openai
import requests
from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID")

app = Flask(__name__)

@app.route("/voice", methods=["POST"])
def voice():
    speech = request.form.get("SpeechResult", "")
    if not speech:
        resp = VoiceResponse()
        resp.say("I didn’t catch that. Could you say it again?", voice="alice")
        resp.redirect("/voice")
        return str(resp)

    # Generate text reply from OpenAI
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a helpful assistant for small businesses."},
            {"role": "user", "content": speech}
        ]
    )
    reply_text = completion["choices"][0]["message"]["content"]

    # Generate audio from ElevenLabs
    audio_response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{elevenlabs_voice_id}",
        headers={
            "xi-api-key": elevenlabs_api_key,
            "Content-Type": "application/json"
        },
        json={
            "text": reply_text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8
            }
        }
    )

    audio_path = f"static/reply.mp3"
    with open(audio_path, "wb") as f:
        f.write(audio_response.content)

    # Serve MP3 to Twilio
    resp = VoiceResponse()
    resp.play(f"{request.url_root}static/reply.mp3")
    resp.redirect("/voice")
    return str(resp)

@app.route("/")
def home():
    return "AI Voice Assistant is live!"

# Required to serve static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
