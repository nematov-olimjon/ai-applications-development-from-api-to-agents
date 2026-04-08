import json
from datetime import datetime

import requests

from commons.constants import OPENAI_API_KEY, OPENAI_HOST


class Voice:
    alloy: str = 'alloy'
    ash: str = 'ash'
    ballad: str = 'ballad'
    coral: str = 'coral'
    echo: str = 'echo'
    fable: str = 'fable'
    nova: str = 'nova'
    onyx: str = 'onyx'
    sage: str = 'sage'
    shimmer: str = 'shimmer'


# https://developers.openai.com/api/docs/guides/text-to-speech
# Request:
# curl https://api.openai.com/v1/audio/speech \
#   -H "Authorization: Bearer $OPENAI_API_KEY" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "model": "gpt-4o-mini-tts",
#     "input": "Why can't we say that black is white?",
#     "voice": "coral",
#     "instructions": "Speak in a cheerful and positive tone."
#   }' \
# Response:
#   bytes with audio

#TODO:
# You need to convert text to speech:
#   - Create Client that will go to speech OpenAI API
#   - Call API
#   - Get response and save as .mp3 file
# ---
# Hints:
#   - Use /v1/audio/speech endpoint
#   - Use gpt-4o-mini-tts model

if __name__ == "__main__":
    import os

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "gpt-4o-mini-tts",
        "input": "Why can't we say that black is white?",
        # "voice": Voice.coral,
        # "voice": Voice.shimmer,
        "voice": Voice.nova,
        "instructions": "Speak in a cheerful and positive tone.",
    }

    response = requests.post(
        f"{OPENAI_HOST}/v1/audio/speech",
        headers=headers,
        json=payload,
    )

    if response.status_code == 200:
        output_dir = os.path.dirname(__file__)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"speech_{timestamp}.mp3")

        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"\n--- Speech saved to {output_path} ---")
    else:
        print(f"Error: {response.status_code} - {response.text}")
