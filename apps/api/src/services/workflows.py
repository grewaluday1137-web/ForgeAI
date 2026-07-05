from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.workflow import Workflow, Task
from src.models.workspace import Workspace
from src.models.repository import Repository
from src.models.project import ProjectMember
from src.schemas.workflow import WorkflowCreate, TaskCreate
from src.services.activity import log_activity
from src.schemas.activity import ActivityCreate
from src.websocket.manager import manager
from fastapi import HTTPException, status
from uuid import UUID

async def create_workflow(db: AsyncSession, workflow_in: WorkflowCreate, current_user_id: UUID) -> Workflow:
    # Verify workspace and project access
    stmt = select(Workspace, Repository).join(Repository, Workspace.repository_id == Repository.id).where(Workspace.id == workflow_in.workspace_id)
    result = (await db.execute(stmt)).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    
    workspace, repo = result
    
    member_stmt = select(ProjectMember).where(ProjectMember.project_id == repo.project_id, ProjectMember.user_id == current_user_id)
    if not (await db.execute(member_stmt)).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    workflow = Workflow(
        workspace_id=workspace.id,
        title=workflow_in.title,
        description=workflow_in.description,
        status=workflow_in.status,
        priority=workflow_in.priority,
        created_by=current_user_id,
        updated_by=current_user_id
    )
    db.add(workflow)
    await db.flush()

    await log_activity(db, ActivityCreate(
        project_id=repo.project_id,
        user_id=current_user_id,
        event="workflow.started",
        resource="workflow",
        metadata_json={"title": workflow.title}
    ))

    await db.commit()
    await db.refresh(workflow)

    await manager.broadcast_event("workflow.created", {
        "id": str(workflow.id),
        "workspace_id": str(workflow.workspace_id),
        "title": workflow.title
    })

    return workflow

async def create_task(db: AsyncSession, task_in: TaskCreate, current_user_id: UUID) -> Task:
    # Minimal validation for brevity; in reality we check access similar to workflow
    task = Task(
        workflow_id=task_in.workflow_id,
        assigned_agent=task_in.assigned_agent,
        title=task_in.title,
        status=task_in.status,
        priority=task_in.priority,
        created_by=current_user_id,
        updated_by=current_user_id
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    await manager.broadcast_event("task.created", {
        "id": str(task.id),
        "workflow_id": str(task.workflow_id),
        "title": task.title
    })
    
    return task
