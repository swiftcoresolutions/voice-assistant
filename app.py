from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import openai, os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/voice", methods=["POST"])
def voice():
    speech = request.form.get("SpeechResult", "")
    if not speech:
        resp = VoiceResponse()
        resp.say("I didn’t catch that. Could you say it again?")
        return str(resp)

    gpt_reply = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're a helpful AI phone assistant."},
            {"role": "user", "content": speech}
        ]
    )

    reply = gpt_reply['choices'][0]['message']['content']
    resp = VoiceResponse()
    resp.say(reply, voice="alice")
    resp.redirect("/voice")
    return str(resp)

@app.route("/")
def home():
    return "Voice Assistant Live."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
