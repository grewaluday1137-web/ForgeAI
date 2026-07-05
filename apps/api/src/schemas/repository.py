from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class RepositoryBase(BaseModel):
    provider: str = Field(..., max_length=50)
    remote_url: str | None = Field(None, max_length=500)
    default_branch: str = Field(default="main", max_length=100)
    local_path: str | None = Field(None, max_length=500)

class RepositoryCreate(RepositoryBase):
    pass

class RepositoryUpdate(BaseModel):
    remote_url: str | None = Field(None, max_length=500)
    default_branch: str | None = Field(None, max_length=100)
    is_connected: bool | None = None
    last_sync: datetime | None = None

class RepositoryResponse(RepositoryBase):
    id: UUID
    project_id: UUID
    is_connected: bool
    last_sync: datetime | None = None
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
