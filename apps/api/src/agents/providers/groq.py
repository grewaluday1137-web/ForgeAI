import json
import logging
import re
from typing import Any
from openai import AsyncOpenAI
from src.agents.providers.base import AIProvider, Message
from src.core.config import settings

logger = logging.getLogger(__name__)


class GroqProvider(AIProvider):
    """
    Groq AI provider using the OpenAI-compatible API.
    Groq offers extremely fast free inference for Llama, Mixtral and other OSS models.
    Requires GROQ_API_KEY (starts with gsk_).
    """

    MODEL = "llama-3.3-70b-versatile"

    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY,
        )

    @property
    def provider_name(self) -> str:
        return "groq"

    async def complete(
        self,
        messages: list[Message],
        response_schema: dict | None = None,
        temperature: float = 0.3,
    ) -> dict[str, Any]:

        # Convert internal messages to OpenAI format
        oai_messages = [{"role": m.role, "content": m.content} for m in messages]

        try:
            response = await self.client.chat.completions.create(
                model=self.MODEL,
                messages=oai_messages,
                temperature=temperature,
                max_tokens=4096,
            )

            text = response.choices[0].message.content.strip()

            if response_schema:
                # Robustly extract JSON from the response
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
                if json_match:
                    text = json_match.group(1).strip()
                else:
                    # Find the outermost JSON object
                    start_idx = text.find('{')
                    end_idx = text.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        text = text[start_idx:end_idx + 1]

                return json.loads(text)
            else:
                return {"text": text}

        except json.JSONDecodeError as e:
            logger.error(f"GroqProvider: failed to parse JSON response: {e}")
            raise ValueError(f"Groq returned invalid JSON: {e}")
        except Exception as e:
            logger.error(f"GroqProvider: API call failed: {e}")
            raise
