import uuid
from datetime import datetime, UTC
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from src.models.base import Base

class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    provider: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., 'github', 'gitlab', 'local'
    remote_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    default_branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    local_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    is_connected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_sync: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Audit fields
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="repositories")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    workspaces: Mapped[list["Workspace"]] = relationship("Workspace", back_populates="repository", cascade="all, delete-orphan")
