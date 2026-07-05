from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.models.user import User
from src.api.deps import get_current_active_user
from src.schemas.workspace import WorkspaceCreate, WorkspaceResponse
from src.services.workspaces import create_workspace, get_workspaces_by_project
from uuid import UUID

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.post("", response_model=WorkspaceResponse)
async def api_create_workspace(
    workspace_in: WorkspaceCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_workspace(db, workspace_in, current_user.id)

@router.get("/project/{project_id}", response_model=list[WorkspaceResponse])
async def api_get_workspaces(
    project_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_workspaces_by_project(db, project_id, current_user.id)
