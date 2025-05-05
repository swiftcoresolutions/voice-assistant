from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/voice", methods=["POST"])
def voice():
    speech = request.form.get("SpeechResult", "")
    resp = VoiceResponse()

    if not speech:
        resp.say("I didn’t catch that. Could you say that again?", voice="Polly.Joanna")
        resp.redirect("/voice")
        return str(resp)

    try:
        gpt_reply = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a friendly and professional AI phone assistant that helps customers with their questions."},
                {"role": "user", "content": speech}
            ]
        )
        reply = gpt_reply["choices"][0]["message"]["content"]

        resp.say(reply, voice="Polly.Joanna")  # Use a more natural-sounding voice
        resp.pause(length=1)
        resp.redirect("/voice")
        return str(resp)

    except Exception as e:
        resp.say("I'm sorry, something went wrong. Please try again later.", voice="Polly.Joanna")
        return str(resp)

@app.route("/", methods=["GET"])
def home():
    return "Voice assistant is live."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
