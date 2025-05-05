from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
import openai
import boto3
import os
import uuid

app = Flask(__name__)

# Load your API keys (use environment variables or secure config for deployment)
openai.api_key = os.getenv("OPENAI_API_KEY")
polly = boto3.client(
    "polly",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
)

# Save synthesized speech to file
def synthesize_speech(text):
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId="Joanna"
    )
    filename = f"/tmp/{uuid.uuid4()}.mp3"
    with open(filename, "wb") as f:
        f.write(response["AudioStream"].read())
    return filename

# Get GPT-4 response
def generate_gpt_response(prompt):
    messages = [{"role": "system", "content": "You are a helpful, natural-sounding assistant."},
                {"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message["content"]

@app.route("/voice", methods=["POST"])
def voice():
    prompt = request.form.get("SpeechResult", "")
    if not prompt:
        prompt = "Sorry, I didn’t catch that. Could you repeat?"

    gpt_reply = generate_gpt_response(prompt)

    # Convert GPT reply to TwiML (text-to-speech with Polly voice)
    response = VoiceResponse()
    response.say(gpt_reply, voice="Polly.Joanna", language="en-US")
    return Response(str(response), mimetype="application/xml")

if __name__ == "__main__":
    app.run(debug=True)
