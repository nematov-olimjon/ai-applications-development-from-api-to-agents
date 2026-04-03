import json
import aiohttp
import requests

from commons.models.message import Message
from commons.models.role import Role
from t1_llm_api.base_client import AIClient


class CustomGeminiAIClient(AIClient):
    """
    Custom HTTP client for Google Gemini API.

    This implementation uses raw HTTP requests (requests/aiohttp) instead of
    the official SDK, demonstrating how to interact with Gemini's API directly
    and handle its Server-Sent Events (SSE) streaming format.
    """

    @staticmethod
    def _to_gemini_role(role: Role) -> str:
        if role == Role.ASSISTANT:
            return "model"
        return "user"

    def _build_gemini_contents(self, messages: list[Message]) -> list[dict]:
        return [
            {
                "role": self._to_gemini_role(m.role),
                "parts": [{"text": m.content}],
            }
            for m in messages
        ]

    def response(self, messages: list[Message], **kwargs) -> Message:
        """
        Get a synchronous response using raw HTTP POST request.

        Args:
            messages (list[Message]): The conversation history.
            **kwargs: Additional parameters like max_tokens (default: 1024).

        Returns:
            Message: The AI's response message.

        Raises:
            ValueError: If the API response contains no candidates.
            Exception: If the HTTP request fails (non-200 status code).

        Note:
            The URL is constructed by appending ':generateContent' to the model endpoint.
            Uses 'x-goog-api-key' header for authentication.
            Response candidates contain content parts that are concatenated.
        """
        #TODO:
        # https://ai.google.dev/gemini-api/docs/text-generation
        # - Prepare headers with api key and content type
        # - Add System prompt
        # - Execute post request to AI API (use `requests`)
        # - Parse response
        # - Print response to console
        # - Return ASSISTANT message
        headers = {
            "Content-Type": "application/json",
        }

        url = f"{self._endpoint}/{self._model_name}:generateContent?key={self._api_key}"

        contents = self._build_gemini_contents(messages)

        payload = {
            "system_instruction": {
                "parts": [{"text": self._system_prompt}]
            },
            "contents": contents,
        }

        resp = requests.post(url, headers=headers, json=payload)

        if resp.status_code != 200:
            raise Exception(f"API request failed with status {resp.status_code}: {resp.text}")

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("API response contains no candidates")

        response_content = ""
        for part in candidates[0].get("content", {}).get("parts", []):
            response_content += part.get("text", "")

        print(response_content)
        return Message(role=Role.ASSISTANT, content=response_content)

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        """
        Get a streaming response using raw HTTP with Server-Sent Events (SSE).

        The response is streamed using Gemini's SSE format, with text chunks
        printed immediately as they arrive.

        Args:
            messages (list[Message]): The conversation history.
            **kwargs: Additional parameters like max_tokens (default: 1024).

        Returns:
            Message: The complete AI response message after all chunks are received.

        Note:
            The URL is constructed with ':streamGenerateContent?alt=sse' endpoint.
            Uses Server-Sent Events (SSE) format where each line starts with "data: ".
            Each SSE chunk contains candidates with content parts.
            Each text chunk is printed to stdout as it arrives.
        """
        #TODO:
        # https://ai.google.dev/gemini-api/docs/text-generation
        # - Prepare headers with api key and content type
        # - Add System prompt
        # - Execute post request to AI API (use `aiohttp`)
        # - Handle stream with chunks
        # - Parse response
        # - Print chunks to console
        # - Return ASSISTANT message
        headers = {
            "Content-Type": "application/json",
        }

        url = f"{self._endpoint}/{self._model_name}:streamGenerateContent?alt=sse&key={self._api_key}"

        contents = self._build_gemini_contents(messages)

        payload = {
            "system_instruction": {
                "parts": [{"text": self._system_prompt}]
            },
            "contents": contents,
        }

        full_response = ""
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                async for line in resp.content:
                    decoded_line = line.decode("utf-8").strip()
                    if not decoded_line.startswith("data: "):
                        continue
                    data_str = decoded_line[len("data: "):]
                    chunk = json.loads(data_str)
                    candidates = chunk.get("candidates", [])
                    if candidates:
                        for part in candidates[0].get("content", {}).get("parts", []):
                            text = part.get("text", "")
                            if text:
                                print(text, end="", flush=True)
                                full_response += text

        return Message(role=Role.ASSISTANT, content=full_response)
