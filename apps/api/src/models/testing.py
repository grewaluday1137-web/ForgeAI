"""
Testing Models — Milestone 9: Tester Agent & QA System

Models:
  - TestSuite: A test file discovered or generated for an execution job
  - TestCase: An individual test function within a suite
  - TestExecution: A single test run (maps test framework output to DB records)
  - CoverageReport: Aggregated coverage metrics from a test run
  - FailureAnalysis: AI-structured diagnosis of a single failed test
  - QualityReport: Final holistic quality score and recommendation
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.models.base import Base
from src.models.enums import TestStatus, FailureCategory


class TestSuite(Base):
    __tablename__ = "test_suites"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("execution_jobs.id", ondelete="CASCADE"), nullable=False)
    repository_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)

    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    framework: Mapped[str] = mapped_column(String(50), nullable=False)  # pytest, jest, vitest, cargo, go
    is_generated: Mapped[bool] = mapped_column(Boolean, default=False)  # AI-generated vs discovered
    source_code: Mapped[str] = mapped_column(Text, nullable=True)

    total_tests: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    test_cases = relationship("TestCase", back_populates="suite", cascade="all, delete-orphan")
    executions = relationship("TestExecution", back_populates="suite", cascade="all, delete-orphan")


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suite_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("test_suites.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[TestStatus] = mapped_column(Enum(TestStatus), default=TestStatus.PENDING)
    duration_ms: Mapped[float] = mapped_column(Float, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    stack_trace: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    suite = relationship("TestSuite", back_populates="test_cases")
    failure_analysis = relationship("FailureAnalysis", back_populates="test_case", uselist=False, cascade="all, delete-orphan")


class TestExecution(Base):
    __tablename__ = "test_executions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suite_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("test_suites.id", ondelete="CASCADE"), nullable=False)
    execution_job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("execution_jobs.id", ondelete="CASCADE"), nullable=False)

    status: Mapped[TestStatus] = mapped_column(Enum(TestStatus), default=TestStatus.PENDING)
    stdout: Mapped[str] = mapped_column(Text, nullable=True)
    stderr: Mapped[str] = mapped_column(Text, nullable=True)
    exit_code: Mapped[int] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[float] = mapped_column(Float, nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    suite = relationship("TestSuite", back_populates="executions")


class CoverageReport(Base):
    __tablename__ = "coverage_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("execution_jobs.id", ondelete="CASCADE"), nullable=False, unique=True)

    line_coverage: Mapped[float] = mapped_column(Float, nullable=True)        # 0.0 - 100.0
    branch_coverage: Mapped[float] = mapped_column(Float, nullable=True)
    function_coverage: Mapped[float] = mapped_column(Float, nullable=True)
    statement_coverage: Mapped[float] = mapped_column(Float, nullable=True)

    covered_lines: Mapped[int] = mapped_column(Integer, nullable=True)
    total_lines: Mapped[int] = mapped_column(Integer, nullable=True)

    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=True)  # Raw coverage JSON
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class FailureAnalysis(Base):
    __tablename__ = "failure_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False, unique=True)

    category: Mapped[FailureCategory] = mapped_column(Enum(FailureCategory), default=FailureCategory.UNKNOWN)
    root_cause: Mapped[str] = mapped_column(Text, nullable=True)
    suggested_fix: Mapped[str] = mapped_column(Text, nullable=True)
    is_flaky: Mapped[bool] = mapped_column(Boolean, default=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    test_case = relationship("TestCase", back_populates="failure_analysis")


class QualityReport(Base):
    __tablename__ = "quality_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    execution_job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("execution_jobs.id", ondelete="CASCADE"), nullable=False, unique=True)

    quality_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0–100
    pass_rate: Mapped[float] = mapped_column(Float, nullable=True)
    coverage_score: Mapped[float] = mapped_column(Float, nullable=True)

    total_tests: Mapped[int] = mapped_column(Integer, default=0)
    passed_tests: Mapped[int] = mapped_column(Integer, default=0)
    failed_tests: Mapped[int] = mapped_column(Integer, default=0)
    skipped_tests: Mapped[int] = mapped_column(Integer, default=0)

    recommendation: Mapped[str] = mapped_column(String(20), nullable=False)  # APPROVE, RETRY, ESCALATE
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
