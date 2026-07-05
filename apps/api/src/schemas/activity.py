from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class ActivityBase(BaseModel):
    event: str = Field(..., max_length=100)
    resource: str = Field(..., max_length=100)
    metadata_json: dict = Field(default_factory=dict)

class ActivityCreate(ActivityBase):
    project_id: UUID
    user_id: UUID | None = None

class ActivityResponse(ActivityBase):
    id: UUID
    project_id: UUID
    user_id: UUID | None = None
    created_at: datetime

    class Config:
        from_attributes = True
