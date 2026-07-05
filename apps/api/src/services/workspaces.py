from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.workspace import Workspace
from src.models.repository import Repository
from src.models.project import ProjectMember
from src.schemas.workspace import WorkspaceCreate
from src.services.activity import log_activity
from src.schemas.activity import ActivityCreate
from src.websocket.manager import manager
from fastapi import HTTPException, status
from uuid import UUID

async def create_workspace(db: AsyncSession, workspace_in: WorkspaceCreate, current_user_id: UUID) -> Workspace:
    # Verify repository exists and user has access to its project
    stmt = select(Repository).where(Repository.id == workspace_in.repository_id)
    repo = (await db.execute(stmt)).scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")

    member_stmt = select(ProjectMember).where(ProjectMember.project_id == repo.project_id, ProjectMember.user_id == current_user_id)
    if not (await db.execute(member_stmt)).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    workspace = Workspace(
        repository_id=repo.id,
        name=workspace_in.name,
        description=workspace_in.description,
        type=workspace_in.type,
        status=workspace_in.status,
        created_by=current_user_id,
        updated_by=current_user_id
    )
    db.add(workspace)
    await db.flush()

    await log_activity(db, ActivityCreate(
        project_id=repo.project_id,
        user_id=current_user_id,
        event="workspace.created",
        resource="workspace",
        metadata_json={"name": workspace.name}
    ))

    await db.commit()
    await db.refresh(workspace)

    await manager.broadcast_event("workspace.created", {
        "id": str(workspace.id),
        "repository_id": str(workspace.repository_id),
        "name": workspace.name
    })

    return workspace

async def get_workspaces_by_project(db: AsyncSession, project_id: UUID, current_user_id: UUID) -> list[Workspace]:
    # Check access
    member_stmt = select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == current_user_id)
    if not (await db.execute(member_stmt)).scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    stmt = select(Workspace).join(Repository).where(Repository.project_id == project_id)
    result = await db.execute(stmt)
    return result.scalars().all()
