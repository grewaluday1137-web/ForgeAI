import uuid
from datetime import datetime, UTC
from sqlalchemy import String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import Base
from src.models.enums import WorkspaceStatus

class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    type: Mapped[str] = mapped_column(String(50), default="development", nullable=False) # e.g., 'development', 'production', 'experiment'
    
    status: Mapped[WorkspaceStatus] = mapped_column(Enum(WorkspaceStatus), default=WorkspaceStatus.ACTIVE, nullable=False)
    
    # Audit fields
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    repository = relationship("Repository", back_populates="workspaces")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    workflows: Mapped[list["Workflow"]] = relationship("Workflow", back_populates="workspace", cascade="all, delete-orphan")
