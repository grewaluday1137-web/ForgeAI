from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, constr
from src.models.enums import ProjectVisibility, ProjectStatus, ProjectPermission

# ─── Project Schemas ──────────────────────────────────────────────────────────

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=60)
    description: str | None = Field(None, max_length=500)
    icon: str | None = None
    color: str = Field(default="blue", max_length=50)
    visibility: ProjectVisibility = ProjectVisibility.PRIVATE

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=60)
    description: str | None = Field(None, max_length=500)
    icon: str | None = None
    color: str | None = Field(None, max_length=50)
    visibility: ProjectVisibility | None = None
    status: ProjectStatus | None = None

class ProjectResponse(ProjectBase):
    id: UUID
    owner_id: UUID
    slug: str
    status: ProjectStatus
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None

    class Config:
        from_attributes = True

# ─── Project Member Schemas ───────────────────────────────────────────────────

class ProjectMemberBase(BaseModel):
    permissions: ProjectPermission = ProjectPermission.READ

class ProjectMemberCreate(ProjectMemberBase):
    user_id: UUID

class ProjectMemberUpdate(ProjectMemberBase):
    pass

class ProjectMemberResponse(ProjectMemberBase):
    id: UUID
    project_id: UUID
    user_id: UUID
    joined_at: datetime

    class Config:
        from_attributes = True
