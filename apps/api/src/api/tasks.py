from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from src.db.session import get_db
from src.models.user import User
from src.models.workflow import Task
from src.api.deps import get_current_active_user
from src.schemas.workflow import TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/{task_id}", response_model=TaskResponse)
async def api_get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns details for a specific task."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task
