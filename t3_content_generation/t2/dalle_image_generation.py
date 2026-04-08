from commons.constants import OPENAI_HOST
from t3_content_generation._openai_client import OpenAIClientT3


class Size:
    """
    The size of the generated image.
    """
    square: str = '1024x1024'
    height_rectangle: str = '1024x1792'
    width_rectangle: str = '1792x1024'


class Style:
    """
    The style of the generated image. Must be one of vivid or natural.
     - Vivid causes the model to lean towards generating hyper-real and dramatic images.
     - Natural causes the model to produce more natural, less hyper-real looking images.
    """
    natural: str = "natural"
    vivid: str = "vivid"


class Quality:
    """
    The quality of the image that will be generated.
     - ‘hd’ creates images with finer details and greater consistency across the image.
    """
    standard: str = "standard"
    hd: str = "hd"


# https://developers.openai.com/api/reference/resources/images/methods/generate
# Request:
# curl https://api.openai.com/v1/images/generations \
#   -H "Content-Type: application/json" \
#   -H "Authorization: Bearer $OPENAI_API_KEY" \
#   -d '{
#     "model": "dall-e-3",
#     "prompt": "smiling catdog",
#     "size": "1024x1024",
#     "style": "natural",
#     "quality": "standard"
#   }'

#TODO:
# You need to create some images with `dall-e-3` model:
#   - Generate an image with 'Smiling catdog'
#   - Play with configurations (size, style, quality)
# ---
# Hints:
#   - Use OpenAIClientT3 to connect to OpenAI API
#   - Use /v1/images/generations endpoint
#   - The link with generated image will be returned in response


if __name__ == "__main__":
    client = OpenAIClientT3(endpoint=f"{OPENAI_HOST}/v1/images/generations")

    response = client.call(
        model="dall-e-3",
        prompt="Smiling catdog",
        # size=Size.square,
        size=Size.width_rectangle,
        # size=Size.height_rectangle,
        # style=Style.natural,
        style=Style.vivid,
        quality=Quality.standard,
        # quality=Quality.hd,
    )

    # Print the URL of the generated image
    print("\n--- Generated Image URL ---")
    print(response["data"][0]["url"])
