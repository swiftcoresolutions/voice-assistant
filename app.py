from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/voice", methods=["POST"])
def voice():
    speech = request.form.get("SpeechResult", "").strip()
    resp = VoiceResponse()

    if not speech:
        gather = resp.gather(
            input="speech",
            timeout=5,
            speech_timeout="auto",
            action="/voice",
            method="POST"
        )
        gather.say("Hi there! Go ahead, I'm listening.", voice="Polly.Joanna", language="en-US")
        return str(resp)

    try:
        gpt_reply = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a warm, friendly, human-sounding AI assistant for SwiftCore. Keep your responses short, helpful, and natural."},
                {"role": "user", "content": speech}
            ]
        )
        reply = gpt_reply['choices'][0]['message']['content']
    except Exception as e:
        reply = "Sorry, I’m having trouble understanding you right now. Please try again later."

    resp.say(reply, voice="Polly.Joanna", language="en-US")
    resp.pause(length=1)
    resp.redirect("/voice")  # allows follow-up question

    return str(resp)
