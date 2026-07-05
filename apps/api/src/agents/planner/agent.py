import time
import logging
import json
from src.agents.base import BaseAgent, AgentResult
from src.agents.context import ExecutionContext
from src.agents.providers.factory import get_provider
from src.agents.prompts.planner import build_planner_prompt
from src.agents.planner.schemas import ExecutionPlanOutput
from src.models.enums import AgentType

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """
    The Planner Agent — ForgeAI's first and highest-level agent.

    Responsibilities:
    - Understand the user's engineering request
    - Analyze project context from the ExecutionContext
    - Generate a structured, ordered execution plan
    - Break work into actionable tasks with agent assignments
    - Estimate complexity and identify risks
    - Persist the plan (done by the Orchestrator after this returns)
    """

    @property
    def agent_type(self) -> AgentType:
        return AgentType.PLANNER

    async def run(self, context: ExecutionContext) -> AgentResult:
        start_ms = time.monotonic()
        logger.info(f"[PlannerAgent] Starting for workflow={context.workflow_id}")

        try:
            provider = get_provider()
            messages = build_planner_prompt(context)

            logger.info(f"[PlannerAgent] Calling provider={provider.provider_name}")

            raw_output = await provider.complete(
                messages=messages,
                temperature=0.3,
            )

            # Validate via Pydantic
            plan = ExecutionPlanOutput.model_validate(raw_output)

            duration_ms = int((time.monotonic() - start_ms) * 1000)
            logger.info(
                f"[PlannerAgent] Completed in {duration_ms}ms — "
                f"{len(plan.ordered_tasks)} tasks, complexity={plan.estimated_complexity}"
            )

            return AgentResult(
                agent_type=self.agent_type,
                success=True,
                output={
                    **plan.model_dump(),
                    "raw_ai_response": json.dumps(raw_output),
                    "provider": provider.provider_name,
                },
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time.monotonic() - start_ms) * 1000)
            logger.error(f"[PlannerAgent] Failed after {duration_ms}ms: {e}", exc_info=True)
            return AgentResult(
                agent_type=self.agent_type,
                success=False,
                output={},
                error=str(e),
                duration_ms=duration_ms,
            )

    def validate(self, result: AgentResult) -> bool:
        if not result.success:
            return False
        output = result.output
        # Must have at least one task and a non-empty objective
        return (
            bool(output.get("objective"))
            and isinstance(output.get("ordered_tasks"), list)
            and len(output.get("ordered_tasks", [])) > 0
        )
