from flask import Flask, request, send_file
from twilio.twiml.voice_response import VoiceResponse
import openai, os, requests
from tempfile import NamedTemporaryFile

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("ELEVENLABS_VOICE_ID")

@app.route("/voice", methods=["POST"])
def voice():
    speech = request.form.get("SpeechResult", "")
    resp = VoiceResponse()

    if not speech:
        resp.say("Sorry, I didn’t catch that. Please try again.", voice="alice")
        return str(resp)

    try:
        gpt_reply = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a friendly AI phone assistant."},
                {"role": "user", "content": speech}
            ]
        )
        reply = gpt_reply['choices'][0]['message']['content']

        # Generate voice with ElevenLabs
        audio = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": elevenlabs_api_key,
                "Content-Type": "application/json"
            },
            json={
                "text": reply,
                "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}
            }
        )

        # Save to temp file
        with NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(audio.content)
            f.flush()

        # Stream audio to caller
        resp.play(f"https://yourdomain.com/audio/{os.path.basename(f.name)}")

    except Exception as e:
        print("Error:", e)
        resp.say("Sorry, something went wrong on my end.", voice="alice")

    return str(resp)

@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_file(f"/tmp/{filename}", mimetype="audio/mpeg")

@app.route("/")
def home():
    return "SwiftCore Voice Assistant Live."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
