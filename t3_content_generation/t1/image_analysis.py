import base64
import os

from commons.constants import OPENAI_HOST
from t3_content_generation._openai_client import OpenAIClientT3


# https://developers.openai.com/api/docs/guides/images-vision?format=url&lang=curl
# https://developers.openai.com/api/docs/guides/images-vision?format=base64-encoded

#TODO:
# You need to analyse these 2 images:
#   - https://a-z-animals.com/media/2019/11/Elephant-male-1024x535.jpg
#   - in this folder we have 'logo.png', load it as encoded data (see documentation)
# ---
# Hints:
#   - Use OpenAIClientT3 to connect to OpenAI API
#   - Use /v1/chat/completions endpoint
#   - Function to encode image to base64 you can find in documentation
# ---
# In the end load both images (url and base64 encoded 'logo.png'), ask "Generate poem based on images" and se what will happen?

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


if __name__ == "__main__":
    client = OpenAIClientT3(endpoint=f"{OPENAI_HOST}/v1/chat/completions")

    # Encode local logo.png to base64
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    base64_image = encode_image_to_base64(logo_path)

    response = client.call(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Generate poem based on images. What is written in both images"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://a-z-animals.com/media/2019/11/Elephant-male-1024x535.jpg"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )

    # Print the generated poem
    print("\n--- Generated Poem ---")
    print(response["choices"][0]["message"]["content"])
