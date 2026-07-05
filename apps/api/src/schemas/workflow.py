from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from src.models.enums import WorkflowStatus, TaskStatus

# ─── Workflow Schemas ─────────────────────────────────────────────────────────

class WorkflowBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    user_request: str | None = Field(None, description="The original user request / prompt for this workflow")
    status: WorkflowStatus = WorkflowStatus.CREATED
    priority: int = 1

class WorkflowCreate(WorkflowBase):
    workspace_id: UUID

class WorkflowUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    status: WorkflowStatus | None = None
    priority: int | None = None

class WorkflowResponse(WorkflowBase):
    id: UUID
    workspace_id: UUID
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ─── Task Schemas ─────────────────────────────────────────────────────────────

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    assigned_agent: str | None = Field(None, max_length=100)
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 1

class TaskCreate(TaskBase):
    workflow_id: UUID

class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    assigned_agent: str | None = Field(None, max_length=100)
    status: TaskStatus | None = None
    priority: int | None = None

class TaskResponse(TaskBase):
    id: UUID
    workflow_id: UUID
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
