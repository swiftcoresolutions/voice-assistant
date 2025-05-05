from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/voice", methods=["POST"])
def voice():
    user_input = request.form.get("SpeechResult", "")
    response = VoiceResponse()

    if not user_input:
        response.say("I didn’t catch that. Could you please repeat?", voice="alice")
        response.redirect("/voice")
        return str(response)

    chat = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are SwiftCore Solutions' AI voice assistant. Answer as if you're helping a customer calling the business."},
            {"role": "user", "content": user_input}
        ]
    )

    bot_reply = chat['choices'][0]['message']['content']
    response.say(bot_reply, voice="alice")
    response.redirect("/voice")
    return str(response)

@app.route("/")
def home():
    return "SwiftCore Voice AI is live."
