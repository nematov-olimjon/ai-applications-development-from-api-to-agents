import json
import aiohttp
import requests

from commons.models.message import Message
from commons.models.role import Role
from t1_llm_api.openai.base import BaseOpenAIClient


class CustomOpenAIResponsesClient(BaseOpenAIClient):
    """
    Custom HTTP client for OpenAI Responses API.

    This implementation uses raw HTTP requests (requests/aiohttp) instead of
    the official SDK, demonstrating how to interact with the Responses API directly
    and handle its unique event-based streaming format.
    """

    def response(self, messages: list[Message], **kwargs) -> Message:
        """
        Get a synchronous response using raw HTTP POST request.

        Args:
            messages (list[Message]): The conversation history.
            **kwargs: Additional parameters for the API (currently unused).

        Returns:
            Message: The AI's response message.

        Raises:
            ValueError: If the API response contains no output text.
            Exception: If the HTTP request fails (non-200 status code).

        Note:
            Uses the Responses API format with 'instructions' and 'input' parameters.
            The response is printed to stdout before being returned.
        """
        #TODO:
        # https://developers.openai.com/api/docs/guides/text?lang=curl
        # - Prepare headers with authorization and content type
        # - Prepare input messages
        # - Execute post request to AI API (use `requests`)
        # - Parse response
        # - Print response to console
        # - Return ASSISTANT message
        headers = {
            "Authorization": self._api_key,
            "Content-Type": "application/json",
        }

        input_messages = [{"role": m.role.value, "content": m.content} for m in messages]

        payload = {
            "model": self._model_name,
            "instructions": self._system_prompt,
            "input": input_messages,
        }

        resp = requests.post(self._endpoint, headers=headers, json=payload)

        if resp.status_code != 200:
            raise Exception(f"API request failed with status {resp.status_code}: {resp.text}")

        data = resp.json()
        response_content = ""
        for item in data.get("output", []):
            if item.get("type") == "message":
                for content_block in item.get("content", []):
                    if content_block.get("type") == "output_text":
                        response_content += content_block.get("text", "")

        if not response_content:
            raise ValueError("API response contains no output text")

        print(response_content)
        return Message(role=Role.ASSISTANT, content=response_content)

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        """
        Get a streaming response using raw HTTP with event-based streaming.

        The Responses API uses a different SSE format than Chat Completions,
        with explicit event types and data fields.

        Args:
            messages (list[Message]): The conversation history.
            **kwargs: Additional parameters for the API (currently unused).

        Returns:
            Message: The complete AI response message after all deltas are received.

        Note:
            Uses event-based Server-Sent Events (SSE) format.
            Listens for 'response.output_text.delta' events to build the response.
            Each line with "event: " specifies the event type, followed by "data: " with the payload.
        """
        #TODO:
        # https://developers.openai.com/api/docs/guides/text?lang=curl
        # - Prepare headers with authorization and content type
        # - Prepare input messages
        # - Execute post request to AI API (use `aiohttp`)
        # - Handle stream with events
        # - Parse response
        # - Print chunks to console
        # - Return ASSISTANT message
        headers = {
            "Authorization": self._api_key,
            "Content-Type": "application/json",
        }

        input_messages = [{"role": m.role.value, "content": m.content} for m in messages]

        payload = {
            "model": self._model_name,
            "instructions": self._system_prompt,
            "input": input_messages,
            "stream": True,
        }

        full_response = ""
        current_event = None
        async with aiohttp.ClientSession() as session:
            async with session.post(self._endpoint, headers=headers, json=payload) as resp:
                async for line in resp.content:
                    decoded_line = line.decode("utf-8").strip()
                    if decoded_line.startswith("event: "):
                        current_event = decoded_line[len("event: "):]
                    elif decoded_line.startswith("data: ") and current_event == "response.output_text.delta":
                        data = json.loads(decoded_line[len("data: "):])
                        delta = data.get("delta", "")
                        if delta:
                            print(delta, end="", flush=True)
                            full_response += delta

        return Message(role=Role.ASSISTANT, content=full_response)
