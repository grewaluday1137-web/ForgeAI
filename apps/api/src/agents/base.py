from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from src.agents.context import ExecutionContext
from src.models.enums import AgentType


@dataclass
class AgentResult:
    """Standardized output from any agent run."""
    agent_type: AgentType
    success: bool
    output: dict[str, Any]
    error: str | None = None
    duration_ms: int | None = None
    retry_count: int = 0


class BaseAgent(ABC):
    """
    Abstract base class for all ForgeAI agents.
    Every agent must implement run(), validate(), and can override retry().
    """

    @property
    @abstractmethod
    def agent_type(self) -> AgentType:
        """Return the AgentType enum value for this agent."""
        ...

    @abstractmethod
    async def run(self, context: ExecutionContext) -> AgentResult:
        """
        Execute the agent's primary responsibility.
        Must be fully async, emit events, and persist all state.
        """
        ...

    @abstractmethod
    def validate(self, result: AgentResult) -> bool:
        """
        Validate the agent's output before persisting.
        Returns True if output is acceptable, False if retry is needed.
        """
        ...

    async def retry(self, context: ExecutionContext, attempt: int) -> AgentResult:
        """
        Default retry — just calls run() again.
        Override in subclasses for exponential backoff or modified prompts.
        """
        return await self.run(context)

    def report(self, result: AgentResult) -> dict:
        """Return a summary suitable for WebSocket events."""
        return {
            "agent": self.agent_type.value,
            "success": result.success,
            "duration_ms": result.duration_ms,
            "error": result.error,
        }
