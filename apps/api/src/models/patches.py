import uuid
from datetime import datetime, UTC
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.models.base import Base
from src.models.enums import PatchStatus


class CodePatch(Base):
    """
    A single AI-generated patch (unified diff) for one or more files.
    Follows the lifecycle: GENERATED -> VALIDATED -> APPROVED/REJECTED -> APPLIED
    """
    __tablename__ = "code_patches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    workflow_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True)
    task_description: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)  # AI's explanation of changes
    unified_diff: Mapped[str | None] = mapped_column(Text, nullable=True)  # Full unified diff output
    status: Mapped[PatchStatus] = mapped_column(String(50), nullable=False, default=PatchStatus.GENERATED)
    validation_errors: Mapped[list] = mapped_column(JSONB, default=[], nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    commit_hash: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # Relationships
    file_changes = relationship("FileChange", back_populates="patch", cascade="all, delete-orphan")
    review = relationship("PatchReview", back_populates="patch", uselist=False, cascade="all, delete-orphan")
    prompt_execution = relationship("PromptExecution", back_populates="patch", uselist=False, cascade="all, delete-orphan")


class FileChange(Base):
    """
    Individual file-level changes within a CodePatch.
    """
    __tablename__ = "file_changes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("code_patches.id", ondelete="CASCADE"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    change_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'modified', 'created', 'deleted'
    original_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    diff_hunk: Mapped[str | None] = mapped_column(Text, nullable=True)  # Targeted diff for this file
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    patch = relationship("CodePatch", back_populates="file_changes")


class PatchReview(Base):
    """
    Records the human reviewer's decision on a patch.
    """
    __tablename__ = "patch_reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("code_patches.id", ondelete="CASCADE"), nullable=False)
    reviewer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)  # 'approved', 'rejected'
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    patch = relationship("CodePatch", back_populates="review")


class PromptExecution(Base):
    """
    Logs the exact prompt sent to the LLM for full auditability.
    """
    __tablename__ = "prompt_executions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("code_patches.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    user_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    raw_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    patch = relationship("CodePatch", back_populates="prompt_execution")
