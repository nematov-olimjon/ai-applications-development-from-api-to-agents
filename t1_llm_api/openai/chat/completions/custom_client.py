import json
import aiohttp
import requests

from commons.models.message import Message
from commons.models.role import Role
from t1_llm_api.openai.base import BaseOpenAIClient


class CustomOpenAIClient(BaseOpenAIClient):
    """
    Custom HTTP client for OpenAI Chat Completions API.

    This implementation uses raw HTTP requests (requests/aiohttp) instead of
    the official SDK, providing more control over the HTTP layer and demonstrating
    how to interact with the API directly.
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
            ValueError: If the API response contains no choices.
            Exception: If the HTTP request fails (non-200 status code).

        Note:
            The system prompt is automatically prepended to the messages.
            The response is printed to stdout before being returned.
        """
        #TODO:
        # https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create
        # - Prepare headers with authorization and content type
        # - Prepare message history with System prompt
        # - Execute post request to AI API (use `requests`)
        # - Parse response
        # - Print response to console
        # - Return ASSISTANT message
        headers = {
            "Authorization": self._api_key,
            "Content-Type": "application/json",
        }

        all_messages = [{"role": Role.SYSTEM.value, "content": self._system_prompt}] + [m.to_dict() for m in messages]

        payload = {
            "model": self._model_name,
            "messages": all_messages,
        }

        resp = requests.post(self._endpoint, headers=headers, json=payload)

        if resp.status_code != 200:
            raise Exception(f"API request failed with status {resp.status_code}: {resp.text}")

        data = resp.json()
        if not data.get("choices"):
            raise ValueError("API response contains no choices")

        response_content = data["choices"][0]["message"]["content"]
        print(response_content)
        return Message(role=Role.ASSISTANT, content=response_content)

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        """
        Get a streaming response using raw HTTP with Server-Sent Events (SSE).

        The response is streamed token-by-token using OpenAI's SSE format,
        with each chunk printed immediately as it arrives.

        Args:
            messages (list[Message]): The conversation history.
            **kwargs: Additional parameters for the API (currently unused).

        Returns:
            Message: The complete AI response message after all chunks are received.

        Note:
            The system prompt is automatically prepended to the messages.
            Each token is printed to stdout as it arrives.
            Uses Server-Sent Events (SSE) format where each line starts with "data: ".
        """
        #TODO:
        # https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create (Streaming tab)
        # - Prepare headers with authorization and content type
        # - Prepare message history with System prompt
        # - Execute post request to AI API (use `aihttp`)
        # - Handle stream with chunks
        # - Parse response
        # - Print chunks to console
        # - Return ASSISTANT message
        headers = {
            "Authorization": self._api_key,
            "Content-Type": "application/json",
        }

        all_messages = [{"role": Role.SYSTEM.value, "content": self._system_prompt}] + [m.to_dict() for m in messages]

        payload = {
            "model": self._model_name,
            "messages": all_messages,
            "stream": True,
        }

        full_response = ""
        async with aiohttp.ClientSession() as session:
            async with session.post(self._endpoint, headers=headers, json=payload) as resp:
                async for line in resp.content:
                    decoded_line = line.decode("utf-8").strip()
                    if not decoded_line.startswith("data: "):
                        continue
                    data_str = decoded_line[len("data: "):]
                    if data_str == "[DONE]":
                        break
                    chunk = json.loads(data_str)
                    if chunk.get("choices") and chunk["choices"][0].get("delta", {}).get("content"):
                        content = chunk["choices"][0]["delta"]["content"]
                        print(content, end="", flush=True)
                        full_response += content

        return Message(role=Role.ASSISTANT, content=full_response)
