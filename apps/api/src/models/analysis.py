import uuid
from datetime import datetime, UTC
from sqlalchemy import String, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.models.base import Base


class RepositorySnapshot(Base):
    __tablename__ = "repository_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    
    commit_hash: Mapped[str | None] = mapped_column(String(40), nullable=True)
    branch: Mapped[str] = mapped_column(String(100), nullable=False)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. PENDING, CLONING, INDEXING, COMPLETED, FAILED
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    repository = relationship("Repository")
    analysis = relationship("RepositoryAnalysis", back_populates="snapshot", uselist=False, cascade="all, delete-orphan")


class RepositoryIndex(Base):
    """
    Stores indexed files and basic metadata for search and context retrieval.
    """
    __tablename__ = "repository_indexes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., 'python', 'typescript', 'config'
    size_bytes: Mapped[int] = mapped_column(nullable=False)
    
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    # The actual content is kept on the filesystem, but we store summary/metadata here.
    metadata_json: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False) # For symbols, imports etc
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    repository = relationship("Repository")


class RepositoryAnalysis(Base):
    """
    The final architecture report and detected metadata produced by the Architect Agent.
    """
    __tablename__ = "repository_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    snapshot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repository_snapshots.id", ondelete="CASCADE"), nullable=False)
    
    # Detected aspects
    languages: Mapped[list[str]] = mapped_column(JSON, default=[], nullable=False)
    frameworks: Mapped[list[str]] = mapped_column(JSON, default=[], nullable=False)
    package_managers: Mapped[list[str]] = mapped_column(JSON, default=[], nullable=False)
    architecture_patterns: Mapped[list[str]] = mapped_column(JSON, default=[], nullable=False)
    
    # Text report
    architecture_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    repository = relationship("Repository")
    snapshot = relationship("RepositorySnapshot", back_populates="analysis")


class KnowledgeNode(Base):
    """
    Nodes in the Project Knowledge Graph (e.g. Repository, Directory, File, Class, Function).
    """
    __tablename__ = "knowledge_nodes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    
    node_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # e.g., 'File', 'Class', 'Function'
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    
    metadata_json: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)


class KnowledgeEdge(Base):
    """
    Relationships between KnowledgeNodes (e.g. imports, depends_on, calls).
    """
    __tablename__ = "knowledge_edges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False)
    
    relationship_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # e.g., 'imports', 'calls', 'belongs_to'
    
    metadata_json: Mapped[dict] = mapped_column(JSONB, default={}, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    source = relationship("KnowledgeNode", foreign_keys=[source_id])
    target = relationship("KnowledgeNode", foreign_keys=[target_id])


class DependencyGraph(Base):
    """
    Tracks external dependencies and their versions.
    """
    __tablename__ = "dependency_graphs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    
    dependency_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    version_constraint: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ecosystem: Mapped[str] = mapped_column(String(50), nullable=False) # e.g., 'npm', 'pip', 'cargo'
    is_dev: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
