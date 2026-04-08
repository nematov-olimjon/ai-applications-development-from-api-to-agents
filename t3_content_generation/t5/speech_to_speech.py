import base64
import json
from datetime import datetime

import requests

from commons.constants import OPENAI_API_KEY, OPENAI_HOST


# https://developers.openai.com/api/docs/guides/audio#add-audio-to-your-existing-application

#TODO:
# You need to generate answer in audio format based on the audio message:
#   - Create Client that is similar with OpenAIClients but extracts from message audio (instead of content)
#   - Call API
#   - Get response as base64 content, decode and save as .mp3 file
# ---
# Hints:
#   - Use /v1/chat/completions endpoint
#   - Use gpt-4o-audio-preview model
#   - Use modalities=["text", "audio"]
#   - Use audio={"voice": "ballad", "format": "mp3"}
#   - Use similar method to encode audio as you have done for images encoding

def encode_audio_to_base64(audio_path: str) -> str:
    with open(audio_path, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode("utf-8")


if __name__ == "__main__":
    import os

    audio_path = os.path.join(os.path.dirname(__file__), "question.mp3")
    base64_audio = encode_audio_to_base64(audio_path)

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-4o-audio-preview",
        "modalities": ["text", "audio"],
        "audio": {"voice": "ballad", "format": "mp3"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": base64_audio,
                            "format": "mp3",
                        }
                    }
                ]
            }
        ]
    }

    response = requests.post(
        f"{OPENAI_HOST}/v1/chat/completions",
        headers=headers,
        json=payload,
    )

    if response.status_code == 200:
        data = response.json()
        print("\n--- Text Response ---")
        message = data["choices"][0]["message"]

        # Print text content if available
        if message.get("content"):
            print(message["content"])

        # Decode and save audio response
        if message.get("audio") and message["audio"].get("data"):
            audio_data = base64.b64decode(message["audio"]["data"])
            output_dir = os.path.dirname(__file__)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"response_{timestamp}.mp3")

            with open(output_path, "wb") as f:
                f.write(audio_data)

            print(f"\n--- Audio response saved to {output_path} ---")

            # Print transcript if available
            if message["audio"].get("transcript"):
                print(f"Transcript: {message['audio']['transcript']}")
        else:
            print("No audio in response")
    else:
        print(f"Error: {response.status_code} - {response.text}")
