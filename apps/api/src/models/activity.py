import uuid
from datetime import datetime, UTC
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.models.base import Base

class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    event: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., 'project.created'
    resource: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., 'project', 'workspace'
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict) # renamed to avoid conflict with SQLAlchemy metadata
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="activities")
    user = relationship("User")
