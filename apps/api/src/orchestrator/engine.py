import logging
import asyncio
from datetime import datetime, UTC
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.workflow import Workflow, Task
from src.models.execution import ExecutionPlan, AgentExecution, ExecutionLog
from src.models.enums import WorkflowStatus, TaskStatus, AgentType, AgentExecutionStatus, LogLevel
from src.agents.context import ExecutionContext
from src.agents.registry import registry
from src.orchestrator.state_machine import WorkflowStateMachine
from src.websocket.manager import manager
from src.services.activity import log_activity
from src.schemas.activity import ActivityCreate

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


class OrchestratorEngine:
    """
    The single authority for all agent coordination in ForgeAI.

    Responsibilities:
    - Workflow lifecycle management (state transitions via StateMachine)
    - Task scheduling and dependency resolution
    - Agent execution with retry logic
    - Real-time event publishing via Redis Pub/Sub WebSocket
    - Complete audit trail via ExecutionLog
    - Activity logging for the activity feed

    The Orchestrator is vendor-agnostic — it delegates AI calls entirely to agents.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ─── Workflow Lifecycle ───────────────────────────────────────────────────

    async def start_planning(self, workflow_id: UUID, project_id: UUID) -> None:
        """
        Entry point for the Planner Agent.
        Called as an asyncio background task from the API endpoint.
        """
        logger.info(f"[Orchestrator] Starting planning for workflow={workflow_id}")

        workflow = await self._get_workflow(workflow_id)
        if not workflow:
            logger.error(f"[Orchestrator] Workflow {workflow_id} not found")
            return

        # Transition: CREATED → PLANNING
        await self._transition_workflow(workflow, WorkflowStatus.PLANNING, project_id)
        await self._publish("workflow.planning", {
            "workflow_id": str(workflow_id),
            "message": "Planner Agent is analyzing your request..."
        })

        # Build execution context
        context = ExecutionContext(
            workflow_id=workflow_id,
            project_id=project_id,
            workspace_id=workflow.workspace_id,
            user_id=workflow.created_by,
            user_request=workflow.user_request or workflow.title,
            repository_id=None,
        )

        # Create an AgentExecution record
        agent_exec = AgentExecution(
            workflow_id=workflow_id,
            agent_type=AgentType.PLANNER,
            status=AgentExecutionStatus.RUNNING,
            input_data=context.to_dict(),
            started_at=datetime.now(UTC),
        )
        self.db.add(agent_exec)
        await self.db.flush()

        await self._publish("agent.planner.started", {
            "workflow_id": str(workflow_id),
            "agent_execution_id": str(agent_exec.id),
            "message": "Planner Agent started"
        })

        await self._log(agent_exec.id, LogLevel.INFO, "Planner Agent started", {"provider": "pending"})

        # Run the Planner Agent
        planner = registry.get(AgentType.PLANNER)
        result = None
        for attempt in range(1, MAX_RETRIES + 1):
            if attempt > 1:
                logger.warning(f"[Orchestrator] Retrying Planner (attempt {attempt})")
                await self._log(agent_exec.id, LogLevel.WARNING, f"Retrying Planner (attempt {attempt})", {})
                result = await planner.retry(context, attempt)
            else:
                result = await planner.run(context)

            if planner.validate(result):
                break
            if attempt == MAX_RETRIES:
                result.success = False
                result.error = f"Planner failed after {MAX_RETRIES} attempts."

        if not result or not result.success:
            await self._handle_failure(workflow, agent_exec, project_id, result.error if result else "Unknown error")
            return

        # Persist the ExecutionPlan
        plan_data = result.output
        execution_plan = ExecutionPlan(
            workflow_id=workflow_id,
            objective=plan_data["objective"],
            scope=plan_data["scope"],
            assumptions=plan_data.get("assumptions", []),
            risks=plan_data.get("risks", []),
            estimated_complexity=plan_data.get("estimated_complexity", "MEDIUM"),
            phases=plan_data.get("phases", []),
            ordered_tasks=plan_data.get("ordered_tasks", []),
            recommended_agents=plan_data.get("recommended_agents", []),
            raw_ai_response=plan_data.get("raw_ai_response"),
            created_by=workflow.created_by,
        )
        self.db.add(execution_plan)
        await self.db.flush()

        # Persist Task rows from the plan
        for task_data in plan_data.get("ordered_tasks", []):
            task = Task(
                workflow_id=workflow_id,
                agent_type=AgentType[task_data["agent_type"]] if task_data.get("agent_type") else None,
                title=task_data["title"],
                description=task_data.get("description", ""),
                status=TaskStatus.PENDING,
                priority=task_data.get("priority", 1),
                dependencies=task_data.get("dependencies", []),
                execution_metadata={},
                created_by=workflow.created_by,
                updated_by=workflow.created_by,
            )
            self.db.add(task)

        # Complete the AgentExecution record
        agent_exec.status = AgentExecutionStatus.COMPLETED
        agent_exec.output_data = {k: v for k, v in plan_data.items() if k != "raw_ai_response"}
        agent_exec.completed_at = datetime.now(UTC)
        agent_exec.duration_ms = result.duration_ms
        agent_exec.retry_count = result.retry_count

        # Transition: PLANNING → READY
        await self._transition_workflow(workflow, WorkflowStatus.READY, project_id)

        await log_activity(self.db, ActivityCreate(
            project_id=project_id,
            user_id=workflow.created_by,
            event="workflow.planning.completed",
            resource="workflow",
            metadata_json={
                "workflow_id": str(workflow_id),
                "tasks_count": len(plan_data.get("ordered_tasks", [])),
                "complexity": plan_data.get("estimated_complexity"),
            }
        ))

        await self.db.commit()

        await self._log(agent_exec.id, LogLevel.INFO, "Planner Agent completed successfully", {
            "tasks_created": len(plan_data.get("ordered_tasks", [])),
            "complexity": plan_data.get("estimated_complexity"),
            "provider": plan_data.get("provider"),
        })
        await self._publish("agent.planner.completed", {
            "workflow_id": str(workflow_id),
            "agent_execution_id": str(agent_exec.id),
            "execution_plan_id": str(execution_plan.id),
            "tasks_count": len(plan_data.get("ordered_tasks", [])),
            "complexity": plan_data.get("estimated_complexity"),
            "message": f"Plan ready — {len(plan_data.get('ordered_tasks', []))} tasks identified."
        })
        await self._publish("workflow.ready", {
            "workflow_id": str(workflow_id),
            "message": "Execution plan generated and workflow is ready."
        })

        logger.info(f"[Orchestrator] Planning complete for workflow={workflow_id}")

    # ─── Internal Helpers ─────────────────────────────────────────────────────

    async def _get_workflow(self, workflow_id: UUID) -> Workflow | None:
        result = await self.db.execute(select(Workflow).where(Workflow.id == workflow_id))
        return result.scalar_one_or_none()

    async def _transition_workflow(
        self, workflow: Workflow, new_status: WorkflowStatus, project_id: UUID
    ) -> None:
        WorkflowStateMachine.validate_transition(workflow.status, new_status)
        old_status = workflow.status
        workflow.status = new_status
        workflow.updated_at = datetime.now(UTC)
        await self.db.flush()
        logger.info(f"[Orchestrator] Workflow {workflow.id}: {old_status.value} → {new_status.value}")

    async def _handle_failure(
        self, workflow: Workflow, agent_exec: AgentExecution, project_id: UUID, error: str
    ) -> None:
        logger.error(f"[Orchestrator] Workflow {workflow.id} failed: {error}")
        agent_exec.status = AgentExecutionStatus.FAILED
        agent_exec.error_message = error
        agent_exec.completed_at = datetime.now(UTC)

        try:
            WorkflowStateMachine.validate_transition(workflow.status, WorkflowStatus.FAILED)
            workflow.status = WorkflowStatus.FAILED
        except Exception:
            pass

        await self.db.commit()

        await self._publish("agent.failed", {
            "workflow_id": str(workflow.id),
            "agent_type": "PLANNER",
            "error": error,
            "message": f"Planner Agent failed: {error}"
        })
        await self._publish("workflow.failed", {
            "workflow_id": str(workflow.id),
            "error": error,
        })

    async def _publish(self, event: str, payload: dict) -> None:
        """Publish a namespaced event to Redis for real-time WebSocket delivery."""
        try:
            await manager.broadcast_event(event, payload)
        except Exception as e:
            logger.error(f"[Orchestrator] Failed to publish event {event}: {e}")

    async def _log(
        self,
        agent_execution_id: UUID,
        level: LogLevel,
        message: str,
        metadata: dict,
    ) -> None:
        """Append a granular log line to ExecutionLog for full observability."""
        log_entry = ExecutionLog(
            agent_execution_id=agent_execution_id,
            level=level,
            message=message,
            metadata_json=metadata,
        )
        self.db.add(log_entry)
        try:
            await self.db.flush()
        except Exception:
            pass
