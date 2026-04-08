import base64
from datetime import datetime

from commons.constants import OPENAI_HOST
from t3_content_generation._openai_client import OpenAIClientT3


# https://developers.openai.com/api/reference/resources/images/methods/generate
# ---
# Request:
# curl -X POST "https://api.openai.com/v1/images/generations" \
#     -H "Authorization: Bearer $OPENAI_API_KEY" \
#     -H "Content-type: application/json" \
#     -d '{
#         "model": "gpt-image-1",
#         "prompt": "smiling catdog."
#     }'
# Response:
# {
#   "created": 1699900000,
#   "data": [
#     {
#       "b64_json": Qt0n6ArYAEABGOhEoYgVAJFdt8jM79uW2DO...,
#     }
#   ]
# }

#TODO:
# You need to create some images with `gpt-image-1` model:
#   - Generate an image with 'Smiling dog'
#   - Decode and save it locally
# ---
# Hints:
#   - Use OpenAIClientT3 to connect to OpenAI API
#   - Use /v1/images/generations endpoint
#   - The image will be returned in base64 format

if __name__ == "__main__":
    import os

    client = OpenAIClientT3(endpoint=f"{OPENAI_HOST}/v1/images/generations")

    response = client.call(
        model="gpt-image-1",
        prompt="Smiling catdog",
        print_response=False,
    )

    # Decode base64 image and save locally
    b64_json = response["data"][0]["b64_json"]
    image_bytes = base64.b64decode(b64_json)

    output_dir = os.path.dirname(__file__)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"generated_image_{timestamp}.png")

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print(f"\n--- Image saved to {output_path} ---")

