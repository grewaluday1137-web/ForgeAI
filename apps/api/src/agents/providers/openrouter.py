import json
import logging
from typing import Any
from openai import AsyncOpenAI
from src.agents.providers.base import AIProvider, Message
from src.core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterProvider(AIProvider):
    """
    OpenRouter AI provider using the official OpenAI Python SDK.
    Requires OPENROUTER_API_KEY.
    Defaults to anthropic/claude-3.5-sonnet if no specific model is set, or auto-routes.
    """

    MODEL = "meta-llama/llama-3.3-70b-instruct:free"

    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )

    @property
    def provider_name(self) -> str:
        return "openrouter"

    async def complete(
        self,
        messages: list[Message],
        response_schema: dict | None = None,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        
        # Convert internal messages to OpenAI format
        oai_messages = [{"role": m.role, "content": m.content} for m in messages]
        
        extra_body = {}
        # We don't pass the actual schema object because OpenRouter models vary widely in structured output support.
        # Instead, we just prompt the model to return JSON in the system prompt (already done by Planner).

        try:
            response = await self.client.chat.completions.create(
                model=self.MODEL,
                messages=oai_messages,
                temperature=temperature,
                max_tokens=4096,
            )

            text = response.choices[0].message.content.strip()

            if response_schema:
                # Use regex to robustly extract a JSON block if the model is chatty
                import re
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
                if json_match:
                    text = json_match.group(1).strip()
                else:
                    # Try to find the first { and last }
                    start_idx = text.find('{')
                    end_idx = text.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        text = text[start_idx:end_idx+1]
                
                return json.loads(text)
            else:
                return {"text": text}

        except json.JSONDecodeError as e:
            logger.error(f"OpenRouterProvider: failed to parse JSON response: {e}")
            raise ValueError(f"OpenRouter returned invalid JSON: {e}")
        except Exception as e:
            logger.error(f"OpenRouterProvider: API call failed: {e}")
            raise
