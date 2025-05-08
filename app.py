from flask import Flask, request, send_from_directory, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai, os, requests, uuid

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
RENDER_URL = os.getenv("RENDER_EXTERNAL_HOSTNAME")

@app.route("/voice", methods=["POST"])
def voice():
    speech = request.form.get("SpeechResult", "")
    resp = VoiceResponse()

    if not speech:
        # Ask for user input via speech
        gather = Gather(input='speech', timeout=3, action='/voice', method='POST')
        gather.say("Hi, this is SwiftCore Solutions. How can I help you today?", voice='alice')
        resp.append(gather)
        return Response(str(resp), mimetype='text/xml')

    # Step 1: Get OpenAI response
    try:
        gpt = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a friendly business assistant."},
                {"role": "user", "content": speech}
            ]
        )
        reply_text = gpt['choices'][0]['message']['content']
    except Exception as e:
        resp.say("Sorry, something went wrong with our system.")
        return Response(str(resp), mimetype='text/xml')

    # Step 2: Convert to MP3 using ElevenLabs
    try:
        filename = f"{uuid.uuid4()}.mp3"
        mp3_path = f"static/{filename}"

        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "text": reply_text,
            "voice_settings": {
                "stability": 0.4,
                "similarity_boost": 0.8
            }
        }

        audio_response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream",
            headers=headers,
            json=payload
        )

        with open(mp3_path, "wb") as f:
            f.write(audio_response.content)

        # Step 3: Play MP3 in call
        mp3_url = f"{RENDER_URL}/static/{filename}"
        resp.play(mp3_url)
        resp.redirect("/voice")  # loop back for next input

    except Exception as e:
        resp.say("Sorry, I couldn't speak the response.")
    
    return Response(str(resp), mimetype='text/xml')

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)

@app.route("/")
def home():
    return "SwiftCore AI Voice Assistant is running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
