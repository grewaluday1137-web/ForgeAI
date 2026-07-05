from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.models.user import User
from src.api.deps import get_current_active_user
from src.schemas.project import ProjectCreate, ProjectResponse
from src.services.projects import create_project, get_projects
from uuid import UUID

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectResponse)
async def api_create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_project(db, project_in, current_user.id)

@router.get("", response_model=list[ProjectResponse])
async def api_get_projects(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_projects(db, current_user.id)

@router.get("/slug/{slug}", response_model=ProjectResponse)
async def api_get_project_by_slug(
    slug: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    from src.services.projects import get_project_by_slug
    return await get_project_by_slug(db, slug, current_user.id)
