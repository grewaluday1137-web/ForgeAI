from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from src.models.enums import WorkspaceStatus

class WorkspaceBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: str | None = Field(None, max_length=500)
    type: str = Field(default="development", max_length=50)
    status: WorkspaceStatus = WorkspaceStatus.ACTIVE

class WorkspaceCreate(WorkspaceBase):
    repository_id: UUID

class WorkspaceUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=50)
    description: str | None = Field(None, max_length=500)
    type: str | None = Field(None, max_length=50)
    status: WorkspaceStatus | None = None

class WorkspaceResponse(WorkspaceBase):
    id: UUID
    repository_id: UUID
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
