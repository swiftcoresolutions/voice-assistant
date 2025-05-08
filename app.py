from flask import Flask, request, send_from_directory
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os
import requests
import uuid

app = Flask(__name__)

# Load API keys and config
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()
    gather = Gather(input="speech", action="/process", method="POST", timeout=3)
    greeting_url = f"https://{HOSTNAME}/static/greeting.mp3"
    gather.play(greeting_url)
    resp.append(gather)
    resp.say("Sorry, I didn't hear anything. Goodbye.", voice="alice")
    return str(resp)

@app.route("/process", methods=["POST"])
def process():
    user_input = request.form.get("SpeechResult", "")
    resp = VoiceResponse()

    if not user_input:
        resp.say("I'm sorry, I didn't catch that.", voice="alice")
        return str(resp)

    # Get OpenAI response
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You're a helpful AI assistant."},
        {"role": "user", "content": user_input}
    ]
)
ai_reply = response.choices[0].message.content

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

    if response.status_code != 200:
        raise Exception("Failed to generate ElevenLabs audio.")

    with open(mp3_path, "wb") as f:
        f.write(response.content)
    eleven_url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"
    response = requests.post(eleven_url, headers=headers, json=payload)

    with open(mp3_path, "wb") as f:
        f.write(response.content)

    # Play the generated response
    resp.play(f"https://{HOSTNAME}/static/{mp3_filename}")
    return str(resp)

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

@app.route("/")
def index():
    return "SwiftCore AI Assistant is live."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
@app.route("/process", methods=["POST"])
def process():
    user_input = request.form.get("SpeechResult", "")
    print("SpeechResult:", user_input)
    resp = VoiceResponse()

    if not user_input:
        print("No input detected.")
        resp.say("I'm sorry, I didn't catch that.", voice="alice")
        return str(resp)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're a helpful AI assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        ai_reply = response.choices[0].message["content"]
        print("AI Reply:", ai_reply)

        # Generate MP3
        mp3_filename = f"{uuid.uuid4().hex}.mp3"
        mp3_path = os.path.join("static", mp3_filename)

        headers = {
            "xi-api-key": os.getenv("ELEVENLABS_API_KEY"),
            "Content-Type": "application/json"
        }
        payload = {
            "text": ai_reply,
            "voice_settings": {
                "stability": 0.4,
                "similarity_boost": 0.8
            }
        }

        eleven_url = f"https://api.elevenlabs.io/v1/text-to-speech/{os.getenv('ELEVENLABS_VOICE_ID')}/stream"
        response = requests.post(eleven_url, headers=headers, json=payload)
        response.raise_for_status()  # <- catch API failures

        with open(mp3_path, "wb") as f:
            f.write(response.content)

        resp.play(f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/static/{mp3_filename}")
        return str(resp)

    except Exception as e:
        print("Error occurred:", e)
        resp.say("An internal error occurred. Goodbye.", voice="alice")
        return str(resp)
