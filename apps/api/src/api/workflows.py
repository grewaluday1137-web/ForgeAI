from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.session import get_db
from src.models.user import User
from src.models.workflow import Workflow, Task
from src.models.execution import ExecutionPlan, AgentExecution
from src.models.enums import WorkflowStatus, AgentType
from src.api.deps import get_current_active_user
from src.schemas.workflow import WorkflowCreate, WorkflowResponse, TaskCreate, TaskResponse
from src.services.workflows import create_workflow, create_task
from src.orchestrator.engine import OrchestratorEngine
from src.agents.registry import registry
from src.orchestrator.state_machine import InvalidStateTransition
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/workflows", tags=["workflows"])


# ─── Schemas for this module ──────────────────────────────────────────────────

class TriggerPlanRequest(BaseModel):
    project_id: UUID | None = None
    user_request: str | None = None


class ExecutionPlanResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    objective: str
    scope: str
    assumptions: list
    risks: list
    estimated_complexity: str
    phases: list
    ordered_tasks: list
    recommended_agents: list
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowStatusResponse(BaseModel):
    id: UUID
    title: str
    status: str
    user_request: str | None
    task_count: int
    completed_tasks: int
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentInfo(BaseModel):
    agent_type: str
    active: bool
    description: str


# ─── Existing Endpoints ───────────────────────────────────────────────────────

@router.get("", response_model=list[WorkflowResponse])
async def api_get_workflows(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all workflows created by the current user."""
    # For now, just filter by created_by
    result = await db.execute(
        select(Workflow).where(Workflow.created_by == current_user.id).order_by(Workflow.updated_at.desc())
    )
    workflows = result.scalars().all()
    return workflows


@router.post("", response_model=WorkflowResponse)
async def api_create_workflow(
    workflow_in: WorkflowCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_workflow(db, workflow_in, current_user.id)


@router.post("/tasks", response_model=TaskResponse)
async def api_create_task(
    task_in: TaskCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_task(db, task_in, current_user.id)


# ─── Orchestration Endpoints ──────────────────────────────────────────────────

@router.post("/{workflow_id}/plan")
async def api_trigger_plan(
    workflow_id: UUID,
    body: TriggerPlanRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers the Planner Agent for the given workflow.
    Execution runs asynchronously in the background.
    Real-time progress is streamed via WebSocket events.
    """
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    if workflow.status not in (WorkflowStatus.CREATED, WorkflowStatus.FAILED):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot plan a workflow in '{workflow.status.value}' status. Only CREATED or FAILED workflows can be planned."
        )

    # Set the user_request if provided
    if body.user_request:
        workflow.user_request = body.user_request
        await db.commit()

    # Resolve project_id if not provided
    project_id = body.project_id
    if not project_id:
        from src.models.workspace import Workspace
        from src.models.repository import Repository
        stmt = select(Repository.project_id).join(Workspace, Workspace.repository_id == Repository.id).where(Workspace.id == workflow.workspace_id)
        proj_res = await db.execute(stmt)
        project_id = proj_res.scalar_one_or_none()
        if not project_id:
            raise HTTPException(status_code=500, detail="Could not resolve project_id for workflow")

    async def run_orchestration():
        """Background task — gets its own DB session."""
        from src.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as bg_db:
            engine = OrchestratorEngine(db=bg_db)
            await engine.start_planning(workflow_id, project_id)

    background_tasks.add_task(run_orchestration)

    return {
        "message": "Planning started",
        "workflow_id": str(workflow_id),
        "status": "PLANNING"
    }


@router.get("/{workflow_id}/plan", response_model=ExecutionPlanResponse)
async def api_get_plan(
    workflow_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns the stored ExecutionPlan for a workflow."""
    result = await db.execute(select(ExecutionPlan).where(ExecutionPlan.workflow_id == workflow_id))
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No execution plan found for this workflow yet.")

    return plan


@router.post("/{workflow_id}/execute")
async def api_execute_workflow(
    workflow_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers the execution of a READY workflow.
    In this milestone, this just updates the status and logs it,
    since only Planner is active.
    """
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    if workflow.status != WorkflowStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot execute workflow in '{workflow.status.value}' status. Must be READY."
        )

    # In a full implementation, this would trigger OrchestratorEngine.start_execution()
    # For Milestone 5, we'll mark it as RUNNING then COMPLETED (since no other agents run).
    workflow.status = WorkflowStatus.RUNNING
    await db.commit()

    return {
        "message": "Execution started",
        "workflow_id": str(workflow_id),
        "status": "RUNNING"
    }


@router.get("/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def api_get_workflow_status(
    workflow_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns a compact status summary of the workflow and its tasks."""
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    task_result = await db.execute(select(Task).where(Task.workflow_id == workflow_id))
    tasks = task_result.scalars().all()

    from src.models.enums import TaskStatus
    completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)

    return WorkflowStatusResponse(
        id=workflow.id,
        title=workflow.title,
        status=workflow.status.value,
        user_request=workflow.user_request,
        task_count=len(tasks),
        completed_tasks=completed,
        updated_at=workflow.updated_at,
    )


@router.get("/{workflow_id}/events")
async def api_get_workflow_events(
    workflow_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns the execution log for this workflow from all agent executions."""
    exec_result = await db.execute(
        select(AgentExecution).where(AgentExecution.workflow_id == workflow_id)
    )
    agent_execs = exec_result.scalars().all()

    from src.models.execution import ExecutionLog
    logs = []
    for ae in agent_execs:
        log_result = await db.execute(
            select(ExecutionLog).where(ExecutionLog.agent_execution_id == ae.id)
        )
        for log in log_result.scalars().all():
            logs.append({
                "id": str(log.id),
                "agent_type": ae.agent_type.value,
                "level": log.level.value,
                "message": log.message,
                "metadata": log.metadata_json,
                "created_at": log.created_at.isoformat(),
            })

    logs.sort(key=lambda x: x["created_at"])
    return {"workflow_id": str(workflow_id), "events": logs}


# ─── Agent Registry Endpoints ─────────────────────────────────────────────────

@router.get("/agents/registry", response_model=list[AgentInfo])
async def api_list_agents(
    current_user: User = Depends(get_current_active_user),
):
    """Lists all registered agents and their active status."""
    return registry.list_all()


@router.post("/agents/{agent_type}/retry")
async def api_retry_agent(
    agent_type: str,
    workflow_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Re-runs a specific agent for a workflow (e.g., after failure)."""
    try:
        agent_enum = AgentType[agent_type.upper()]
    except KeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown agent type: {agent_type}")

    if not registry.is_active(agent_enum):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Agent {agent_type} is not yet active in this milestone.")

    return {"message": f"Agent {agent_type} retry queued", "workflow_id": str(workflow_id)}


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def api_delete_workflow(
    workflow_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a workflow and all its associated tasks and execution plans."""
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()

    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    if workflow.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this workflow")

    await db.delete(workflow)
    await db.commit()
    return None

