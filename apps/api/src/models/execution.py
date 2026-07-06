import uuid
from datetime import datetime, UTC
from sqlalchemy import String, Integer, Float, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.models.base import Base
from src.models.enums import AgentType, AgentExecutionStatus, LogLevel


class ExecutionPlan(Base):
    """Stores the Planner Agent's structured output for a workflow."""
    __tablename__ = "execution_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Core plan fields
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    scope: Mapped[str] = mapped_column(Text, nullable=False)
    assumptions: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    risks: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    estimated_complexity: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH

    # Phases and tasks as structured JSON
    phases: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    ordered_tasks: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    recommended_agents: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    # Raw AI response for debugging
    raw_ai_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Audit
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    workflow = relationship("Workflow", back_populates="execution_plan")
    creator = relationship("User", foreign_keys=[created_by])


class WorkflowExecution(Base):
    """Tracks a specific end-to-end execution attempt of a workflow."""
    __tablename__ = "workflow_executions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="RUNNING", nullable=False)
    
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Audit
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    workflow = relationship("Workflow", back_populates="executions")


class AgentExecution(Base):
    """Records every individual agent run — one row per agent per workflow."""
    __tablename__ = "agent_executions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    task_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)

    agent_type: Mapped[AgentType] = mapped_column(Enum(AgentType), nullable=False)
    status: Mapped[AgentExecutionStatus] = mapped_column(Enum(AgentExecutionStatus), default=AgentExecutionStatus.QUEUED, nullable=False)

    # Execution data
    input_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    output_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Audit
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    workflow = relationship("Workflow", back_populates="agent_executions")
    logs: Mapped[list["ExecutionLog"]] = relationship("ExecutionLog", back_populates="agent_execution", cascade="all, delete-orphan")


class AgentMemory(Base):
    """Working memory for an agent execution — key/value store."""
    __tablename__ = "agent_memories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_execution_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agent_executions.id", ondelete="CASCADE"), nullable=False)

    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)


class ExecutionLog(Base):
    """Granular, append-only runtime log for full observability."""
    __tablename__ = "execution_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_execution_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("agent_executions.id", ondelete="CASCADE"), nullable=False)

    level: Mapped[LogLevel] = mapped_column(Enum(LogLevel), default=LogLevel.INFO, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    agent_execution = relationship("AgentExecution", back_populates="logs")
