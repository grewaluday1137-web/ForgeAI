import json
import asyncio
import logging
from typing import Any
import google.generativeai as genai
from src.agents.providers.base import AIProvider, Message
from src.core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """
    Google Gemini AI provider.
    Uses Gemini 2.0 Flash for fast, cost-efficient agent responses.
    Forces JSON output via response_mime_type when a schema is provided.
    """

    MODEL = "gemini-2.0-flash"

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._model = genai.GenerativeModel(self.MODEL)

    @property
    def provider_name(self) -> str:
        return "gemini-2.0-flash"

    async def complete(
        self,
        messages: list[Message],
        response_schema: dict | None = None,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        """
        Calls the Gemini API asynchronously.
        Combines system + user messages into a single prompt for Gemini's format.
        Forces JSON output when response_schema is provided.
        """
        # Build the prompt from messages
        prompt_parts = []
        for msg in messages:
            if msg.role == "system":
                prompt_parts.append(f"SYSTEM INSTRUCTIONS:\n{msg.content}\n")
            elif msg.role == "user":
                prompt_parts.append(f"USER REQUEST:\n{msg.content}\n")
            elif msg.role == "assistant":
                prompt_parts.append(f"CONTEXT:\n{msg.content}\n")

        full_prompt = "\n---\n".join(prompt_parts)

        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            response_mime_type="application/json" if response_schema else "text/plain",
        )

        try:
            # Run in executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._model.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                )
            )

            text = response.text.strip()

            if response_schema:
                # Attempt to parse JSON — strip markdown code fences if present
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                return json.loads(text)
            else:
                return {"text": text}

        except json.JSONDecodeError as e:
            logger.error(f"GeminiProvider: failed to parse JSON response: {e}")
            raise ValueError(f"Gemini returned invalid JSON: {e}")
        except Exception as e:
            logger.error(f"GeminiProvider: API call failed: {e}")
            raise
