import json
import aiohttp
import requests

from commons.models.message import Message
from commons.models.role import Role
from t1_llm_api.base_client import AIClient


class CustomAnthropicAIClient(AIClient):
    """
    Custom HTTP client for Anthropic's Claude API.

    This implementation uses raw HTTP requests (requests/aiohttp) instead of
    the official SDK, demonstrating how to interact with Claude's API directly
    and handle its Server-Sent Events (SSE) streaming format.
    """

    def response(self, messages: list[Message], **kwargs) -> Message:
        """
        Get a synchronous response using raw HTTP POST request.

        Args:
            messages (list[Message]): The conversation history.
            **kwargs: Additional parameters like max_tokens (default: 1024).

        Returns:
            Message: The AI's response message.

        Raises:
            ValueError: If the API response contains no content blocks.
            Exception: If the HTTP request fails (non-200 status code).

        Note:
            Requires 'x-api-key' header and 'anthropic-version' header.
            Claude's API returns content as an array of content blocks.
            The response is printed to stdout before being returned.
        """
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self._model_name,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "system": self._system_prompt,
            "messages": [m.to_dict() for m in messages],
        }

        resp = requests.post(self._endpoint, headers=headers, json=payload)

        if resp.status_code != 200:
            raise Exception(f"API request failed with status {resp.status_code}: {resp.text}")

        data = resp.json()
        content_blocks = data.get("content", [])
        if not content_blocks:
            raise ValueError("API response contains no content blocks")

        response_content = "".join(
            block.get("text", "") for block in content_blocks if block.get("type") == "text"
        )
        print(response_content)
        return Message(role=Role.ASSISTANT, content=response_content)

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        """
        Get a streaming response using raw HTTP with Server-Sent Events (SSE).

        The response is streamed using Anthropic's SSE format, with text deltas
        printed immediately as they arrive.

        Args:
            messages (list[Message]): The conversation history.
            **kwargs: Additional parameters like max_tokens (default: 1024).

        Returns:
            Message: The complete AI response message after all deltas are received.

        Note:
            Uses Server-Sent Events (SSE) format where each line starts with "data: ".
            Listens for 'content_block_delta' events with 'text_delta' type.
            Stops processing when 'message_stop' event is received.
            Each delta is printed to stdout as it arrives.
        """
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self._model_name,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "system": self._system_prompt,
            "messages": [m.to_dict() for m in messages],
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
                    elif decoded_line.startswith("data: "):
                        if current_event == "message_stop":
                            break
                        if current_event == "content_block_delta":
                            data = json.loads(decoded_line[len("data: "):])
                            delta = data.get("delta", {})
                            if delta.get("type") == "text_delta":
                                text = delta.get("text", "")
                                if text:
                                    print(text, end="", flush=True)
                                    full_response += text

        return Message(role=Role.ASSISTANT, content=full_response)

