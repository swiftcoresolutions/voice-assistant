import os
import requests

# Load environment variables
api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("ELEVENLABS_VOICE_ID")

text = "This is SwiftCore Solutions. How can I help you today?"

headers = {
    "xi-api-key": api_key,
    "Content-Type": "application/json"
}

data = {
    "text": text,
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
    }
}

response = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
    headers=headers,
    json=data,
    stream=True
)

if response.status_code == 200:
    with open("static/greeting.mp3", "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    print("✅ Greeting MP3 generated successfully.")
else:
    print("❌ Failed to generate greeting:", response.status_code, response.text)
