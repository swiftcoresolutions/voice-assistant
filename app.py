from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/voice", methods=["POST"])
def voice():
    speech = request.form.get("SpeechResult", "")
    resp = VoiceResponse()

    if not speech:
        gather = Gather(input="speech", action="/voice", method="POST", timeout=3)
        gather.say("Hi there! How can I help you today?", voice="Polly.Joanna")
        resp.append(gather)
        resp.say("I didn’t catch that. Let’s try again.", voice="Polly.Joanna")
        resp.redirect("/voice")
        return str(resp)

    try:
        gpt_reply = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful, friendly phone assistant."},
                {"role": "user", "content": speech}
            ]
        )
        reply = gpt_reply["choices"][0]["message"]["content"]

        gather = Gather(input="speech", action="/voice", method="POST", timeout=3)
        gather.say(reply, voice="Polly.Joanna")
        resp.append(gather)
        return str(resp)

    except Exception as e:
        resp.say("Oops. Something went wrong. Try again later.", voice="Polly.Joanna")
        return str(resp)

@app.route("/", methods=["GET"])
def home():
    return "Voice assistant running."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
