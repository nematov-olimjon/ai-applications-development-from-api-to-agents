import json

import requests

from commons.constants import OPENAI_API_KEY, OPENAI_HOST


# https://developers.openai.com/api/docs/guides/speech-to-text

#TODO:
# You need to transcribe 'audio_sample.mp3':
#   - Create Client that will go to transcriptions OpenAI API
#   - Call API and provide file (pay attention that you work with 'multipart/form-data')
#   - Get response with transcription
# ---
# Hints:
#   - Use /v1/audio/transcriptions endpoint
#   - Use whisper-1 or gpt-4o-transcribe model

if __name__ == "__main__":
    import os

    audio_path = os.path.join(os.path.dirname(__file__), "audio_sample.mp3")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }

    with open(audio_path, "rb") as audio_file:
        files = {
            "file": ("audio_sample.mp3", audio_file, "audio/mpeg"),
        }
        data = {
            "model": "whisper-1",
        }

        response = requests.post(
            f"{OPENAI_HOST}/v1/audio/transcriptions",
            headers=headers,
            files=files,
            data=data,
        )

    if response.status_code == 200:
        result = response.json()
        print("\n--- Transcription ---")
        print(json.dumps(result, indent=2))
        print("\nText:", result.get("text", ""))
    else:
        print(f"Error: {response.status_code} - {response.text}")
