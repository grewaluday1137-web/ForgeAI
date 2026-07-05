from abc import ABC, abstractmethod
from typing import Any
import json


class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content


class AIProvider(ABC):
    """
    Abstract AI provider interface.
    The Planner and all agents must only interact through this interface —
    never directly with Gemini, OpenAI, or any vendor SDK.
    """

    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        response_schema: dict | None = None,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        """
        Send messages to the AI model and return structured output.
        If response_schema is provided, the provider must enforce JSON output.
        """
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable name of the provider."""
        ...
