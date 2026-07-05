from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.models.user import User
from src.api.deps import get_current_active_user
from src.schemas.repository import RepositoryCreate, RepositoryResponse
from src.services.repositories import create_repository
from uuid import UUID

router = APIRouter(prefix="/repositories", tags=["repositories"])

@router.post("/project/{project_id}", response_model=RepositoryResponse)
async def api_create_repository(
    project_id: UUID,
    repo_in: RepositoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_repository(db, project_id, repo_in, current_user.id)
