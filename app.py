from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse
import os, openai, requests, uuid

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

@app.route("/voice", methods=["POST"])
def voice():
    speech = request.form.get("SpeechResult", "")
    if not speech:
        response = VoiceResponse()
        response.say("I didn’t catch that. Could you say it again?", voice="alice")
        return str(response)

    # Generate reply from GPT
    gpt_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a helpful phone assistant."},
            {"role": "user", "content": speech}
        ]
    )
    reply = gpt_response['choices'][0]['message']['content']

    # Generate ElevenLabs MP3
    output_filename = f"{uuid.uuid4()}.mp3"
    mp3_path = f"static/{output_filename}"

    audio_response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        },
        json={"text": reply, "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}
    )

    with open(mp3_path, "wb") as f:
        f.write(audio_response.content)

    # Twilio will <Play> the MP3
    public_url = f"{os.getenv('RENDER_URL')}/static/{output_filename}"
    response = VoiceResponse()
    response.play(public_url)
    response.redirect("/voice")  # Loop back for continued convo
    return str(response)

@app.route("/")
def home():
    return "Voice assistant is running."

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)
