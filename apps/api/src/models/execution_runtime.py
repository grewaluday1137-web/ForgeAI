import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON, Enum, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.models.base import Base
from src.models.enums import ExecutionStatus

class ExecutionJob(Base):
    __tablename__ = "execution_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    repository_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    patch_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("code_patches.id", ondelete="SET NULL"), nullable=True)
    
    status: Mapped[ExecutionStatus] = mapped_column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False)
    
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    container_session = relationship("ContainerSession", back_populates="job", uselist=False, cascade="all, delete-orphan")
    logs = relationship("RuntimeLog", back_populates="job", cascade="all, delete-orphan", order_by="RuntimeLog.created_at")
    artifacts = relationship("BuildArtifact", back_populates="job", cascade="all, delete-orphan")

class ContainerSession(Base):
    __tablename__ = "container_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("execution_jobs.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    container_id: Mapped[str] = mapped_column(String(255), nullable=True)
    image: Mapped[str] = mapped_column(String(255), nullable=False)
    
    cpu_limit: Mapped[str] = mapped_column(String(50), nullable=True)
    memory_limit: Mapped[str] = mapped_column(String(50), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    job = relationship("ExecutionJob", back_populates="container_session")

class RuntimeLog(Base):
    __tablename__ = "runtime_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("execution_jobs.id", ondelete="CASCADE"), nullable=False)
    
    phase: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. PROVISIONING, INSTALLING, BUILDING, VALIDATING
    stream: Mapped[str] = mapped_column(String(10), nullable=False, default="stdout") # stdout or stderr
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    job = relationship("ExecutionJob", back_populates="logs")

class BuildArtifact(Base):
    __tablename__ = "build_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("execution_jobs.id", ondelete="CASCADE"), nullable=False)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. BINARY, REPORT, LOG
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    job = relationship("ExecutionJob", back_populates="artifacts")
