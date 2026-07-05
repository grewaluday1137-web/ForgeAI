from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.repository import Repository
from src.models.project import ProjectMember
from src.schemas.repository import RepositoryCreate
from src.services.activity import log_activity
from src.schemas.activity import ActivityCreate
from src.websocket.manager import manager
from fastapi import HTTPException, status
from uuid import UUID

async def create_repository(db: AsyncSession, project_id: UUID, repo_in: RepositoryCreate, current_user_id: UUID) -> Repository:
    # 1. Verify project membership/permissions
    stmt = select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == current_user_id)
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add repository to this project")

    # 2. Create Repository
    repo = Repository(
        project_id=project_id,
        provider=repo_in.provider,
        remote_url=repo_in.remote_url,
        default_branch=repo_in.default_branch,
        local_path=repo_in.local_path,
        created_by=current_user_id,
        updated_by=current_user_id
    )
    db.add(repo)
    await db.flush()

    # 3. Log Activity
    await log_activity(db, ActivityCreate(
        project_id=project_id,
        user_id=current_user_id,
        event="repository.connected",
        resource="repository",
        metadata_json={"provider": repo.provider, "remote_url": repo.remote_url}
    ))

    await db.commit()
    await db.refresh(repo)

    # 4. Broadcast
    await manager.broadcast_event("repository.connected", {
        "id": str(repo.id),
        "project_id": str(repo.project_id),
        "provider": repo.provider
    })

    return repo
