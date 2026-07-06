import time
import logging
from typing import Any
from pydantic import ValidationError

from src.agents.base import BaseAgent, AgentResult
from src.agents.context import ExecutionContext
from src.models.enums import AgentType
from src.agents.providers.factory import get_provider
from src.agents.providers.base import Message
from src.agents.prompts.architect import ARCHITECT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class ArchitectAgent(BaseAgent):
    """
    Analyzes a codebase and generates an architecture report and Knowledge Graph schema.
    """

    @property
    def agent_type(self) -> AgentType:
        return AgentType.ARCHITECT

    async def run(self, context: ExecutionContext) -> AgentResult:
        start_time = time.time()
        logger.info(f"[{self.agent_type.value}] Starting architecture analysis for repo.")

        # In a real scenario, we'd fetch the file list from context. 
        # For Milestone 6, we pass a summary of the index in context.user_request temporarily
        # until the context engine is fully wired into the execution context.
        file_list_summary = context.user_request 

        messages = [
            Message(role="system", content=ARCHITECT_SYSTEM_PROMPT),
            Message(role="user", content=f"Analyze the following repository file index:\n\n{file_list_summary}")
        ]

        provider = get_provider()
        
        try:
            logger.info(f"[{self.agent_type.value}] Calling AI provider {provider.provider_name}...")
            # Enforce JSON parsing
            response = await provider.complete(messages=messages, response_schema={}, temperature=0.2)
            duration = int((time.time() - start_time) * 1000)

            return AgentResult(
                agent_type=self.agent_type,
                success=True,
                output=response,
                duration_ms=duration
            )

        except Exception as e:
            logger.error(f"[{self.agent_type.value}] Failed: {e}")
            duration = int((time.time() - start_time) * 1000)
            return AgentResult(
                agent_type=self.agent_type,
                success=False,
                output={},
                error=str(e),
                duration_ms=duration
            )

    def validate(self, result: AgentResult) -> bool:
        if not result.success:
            return False
            
        data = result.output
        required_keys = ["languages", "frameworks", "package_managers", "architecture_patterns", "architecture_summary", "key_components"]
        
        for key in required_keys:
            if key not in data:
                result.error = f"Missing required key: {key}"
                return False
                
        return True
