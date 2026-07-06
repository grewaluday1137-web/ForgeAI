from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from src.db.session import get_db
from src.models.user import User
from src.api.deps import get_current_active_user
from src.models.execution_runtime import ExecutionJob
from src.models.testing import TestSuite, TestCase, CoverageReport, FailureAnalysis, QualityReport
from src.agents.registry import registry
from src.models.enums import AgentType
from src.agents.context import ExecutionContext

router = APIRouter(prefix="/executions", tags=["testing"])

@router.post("/{job_id}/test", status_code=202)
async def trigger_tests(
    job_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Triggers the Tester Agent for a completed ExecutionJob."""
    job = await db.get(ExecutionJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Execution job not found")
        
    background_tasks.add_task(_run_tester_agent, job.id, job.workflow_id, job.repository_id)
    return {"message": "QA Pipeline triggered", "job_id": job.id}


async def _run_tester_agent(job_id: UUID, workflow_id: UUID, repository_id: UUID):
    from src.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        # Reconstruct some context for the agent
        from src.models.repository import Repository
        repo = await session.get(Repository, repository_id)
        
        ctx = ExecutionContext(
            workflow_id=workflow_id,
            repository_id=repository_id,
            repository_url=repo.remote_url,
            user_request="Verify implementation correctness", # Default
            project_id=repo.project_id
        )
        
        tester = registry.get(AgentType.TESTER)
        await tester.run(ctx)


@router.get("/{job_id}/test-suites")
async def list_test_suites(
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(TestSuite).where(TestSuite.execution_job_id == job_id)
    res = await db.execute(stmt)
    suites = res.scalars().all()
    
    return [
        {
            "id": s.id,
            "file_path": s.file_path,
            "framework": s.framework,
            "is_generated": s.is_generated,
            "total_tests": s.total_tests,
        }
        for s in suites
    ]


@router.get("/{job_id}/coverage")
async def get_coverage(
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(CoverageReport).where(CoverageReport.execution_job_id == job_id)
    res = await db.execute(stmt)
    cov = res.scalars().first()
    if not cov:
        raise HTTPException(status_code=404, detail="No coverage report found")
        
    return {
        "line_coverage": cov.line_coverage,
        "branch_coverage": cov.branch_coverage,
        "function_coverage": cov.function_coverage,
        "raw_data": cov.raw_data
    }


@router.get("/{job_id}/quality")
async def get_quality(
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(QualityReport).where(QualityReport.execution_job_id == job_id)
    res = await db.execute(stmt)
    qr = res.scalars().first()
    if not qr:
        raise HTTPException(status_code=404, detail="No quality report found")
        
    return {
        "quality_score": qr.quality_score,
        "pass_rate": qr.pass_rate,
        "coverage_score": qr.coverage_score,
        "recommendation": qr.recommendation,
        "summary": qr.summary,
        "total_tests": qr.total_tests,
        "passed_tests": qr.passed_tests,
        "failed_tests": qr.failed_tests
    }


@router.get("/{job_id}/failures")
async def get_failures(
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Join TestSuite -> TestCase -> FailureAnalysis
    stmt = (
        select(TestCase, FailureAnalysis, TestSuite)
        .join(TestSuite, TestCase.suite_id == TestSuite.id)
        .join(FailureAnalysis, FailureAnalysis.test_case_id == TestCase.id)
        .where(TestSuite.execution_job_id == job_id)
    )
    res = await db.execute(stmt)
    
    results = []
    for tc, fa, ts in res.all():
        results.append({
            "test_name": tc.name,
            "suite_file": ts.file_path,
            "error_message": tc.error_message,
            "category": fa.category,
            "root_cause": fa.root_cause,
            "suggested_fix": fa.suggested_fix,
            "severity": fa.severity,
            "is_flaky": fa.is_flaky,
        })
        
    return results
