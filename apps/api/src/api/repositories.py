from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db
from src.models.user import User
from src.api.deps import get_current_active_user
from src.schemas.repository import RepositoryCreate, RepositoryResponse
from src.services.repositories import create_repository
from src.orchestrator.repo_engine import repo_engine
from src.services.search import SearchEngine
from src.services.context_engine import ContextEngine
from sqlalchemy import select, or_, desc
from src.models.repository import Repository
from src.models.analysis import RepositorySnapshot, RepositoryIndex, RepositoryAnalysis, KnowledgeNode
from src.models.patches import CodePatch, PatchReview, FileChange, PatchStatus
from fastapi import BackgroundTasks, HTTPException, status
from uuid import UUID
import uuid

router = APIRouter(prefix="/repositories", tags=["repositories"])

@router.post("/project/{project_id}", response_model=RepositoryResponse)
async def api_create_repository(
    project_id: UUID,
    repo_in: RepositoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_repository(db, project_id, repo_in, current_user.id)


@router.post("/{repository_id}/connect")
async def api_connect_repository(
    repository_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Triggers the background cloning, indexing, and architecture analysis pipeline."""
    repo_res = await db.execute(select(Repository).where(Repository.id == repository_id))
    repo = repo_res.scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    background_tasks.add_task(repo_engine.process_repository, repository_id)
    return {"message": "Repository connection and analysis queued.", "repository_id": str(repository_id)}


@router.get("/{repository_id}/overview")
async def api_get_overview(
    repository_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns the comprehensive repository overview for the frontend."""
    engine = ContextEngine(db)
    return await engine.get_repository_context(repository_id)


@router.get("/{repository_id}/tree")
async def api_get_tree(
    repository_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns a flat list of files from the RepositoryIndex (can be structured in frontend)."""
    res = await db.execute(select(RepositoryIndex.file_path, RepositoryIndex.file_type).where(RepositoryIndex.repository_id == repository_id).limit(1000))
    files = res.all()
    return {"files": [{"path": f.file_path, "type": f.file_type} for f in files]}


@router.get("/{repository_id}/search")
async def api_search_repository(
    repository_id: UUID,
    q: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Searches the indexed repository."""
    engine = SearchEngine(db)
    return await engine.search_files(repository_id, q)


@router.get("/{repository_id}/architecture")
async def api_get_architecture(
    repository_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Returns the full architecture report."""
    res = await db.execute(select(RepositoryAnalysis).where(RepositoryAnalysis.repository_id == repository_id).order_by(RepositoryAnalysis.created_at.desc()))
    analysis = res.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="No architecture analysis found")
        
    nodes_res = await db.execute(select(KnowledgeNode).where(KnowledgeNode.repository_id == repository_id))
    nodes = nodes_res.scalars().all()
    
    return {
        "analysis": {
            "languages": analysis.languages,
            "frameworks": analysis.frameworks,
            "package_managers": analysis.package_managers,
            "architecture_patterns": analysis.architecture_patterns,
            "architecture_summary": analysis.architecture_summary
        },
        "knowledge_nodes": [
            {"name": n.name, "type": n.node_type, "path": n.path} for n in nodes
        ]
    }

from pydantic import BaseModel
from src.agents.developer.agent import DeveloperAgent
from src.agents.context import ExecutionContext
from src.services.patch_applier import patch_applier

class GenerateRequest(BaseModel):
    task: str

@router.post("/{repository_id}/generate")
async def api_generate_code(
    repository_id: UUID,
    req: GenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Triggers the Developer Agent to generate code for a specific task."""
    repo = await db.get(Repository, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
        
    # In a real system, we'd trigger this via orchestrator in background.
    # For Milestone 7 demo, we'll run it synchronously or just await it.
    agent = DeveloperAgent()
    context = ExecutionContext(
        workflow_id=uuid.uuid4(),  # Mock workflow ID for standalone run
        repository_id=repository_id,
        user_request=req.task
    )
    
    result = await agent.run(context)
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
        
    # Save the generated patch to DB
    patch = CodePatch(
        repository_id=repository_id,
        task_description=req.task,
        explanation=result.output.get("explanation"),
        unified_diff=result.output.get("patches", [{}])[0].get("diff") if result.output.get("patches") else None,
        status=PatchStatus.GENERATED,
        created_by=current_user.id
    )
    db.add(patch)
    await db.flush()
    
    # Save file changes
    for p in result.output.get("patches", []):
        db.add(FileChange(patch_id=patch.id, file_path=p.get("file_path"), change_type="modified", diff_hunk=p.get("diff")))
    for p in result.output.get("new_files", []):
        db.add(FileChange(patch_id=patch.id, file_path=p.get("file_path"), change_type="created", new_content=p.get("content")))
    for p in result.output.get("deleted_files", []):
        db.add(FileChange(patch_id=patch.id, file_path=p, change_type="deleted"))
        
    await db.commit()
    
    # Store raw json in memory so it can be applied later (normally we'd parse from DB)
    return {"message": "Patch generated", "patch_id": patch.id, "patch": result.output}


@router.get("/{repository_id}/patches")
async def api_get_patches(
    repository_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all patches for a repository."""
    stmt = select(CodePatch).where(CodePatch.repository_id == repository_id).order_by(desc(CodePatch.created_at))
    res = await db.execute(stmt)
    patches = res.scalars().all()
    return [{"id": p.id, "task": p.task_description, "status": p.status, "created_at": p.created_at} for p in patches]


@router.post("/{repository_id}/patches/{patch_id}/approve")
async def api_approve_patch(
    repository_id: UUID,
    patch_id: UUID,
    generated_json: dict, # Hack: Pass the raw JSON from frontend for now to apply it easily
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Approves and applies a patch."""
    patch = await db.get(CodePatch, patch_id)
    if not patch:
        raise HTTPException(status_code=404, detail="Patch not found")
        
    repo = await db.get(Repository, repository_id)
    owner, repo_name = repo.remote_url.split("/")[-2:]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
        
    try:
        commit_hash = patch_applier.apply(generated_json, owner, repo_name, f"ForgeAI: {patch.task_description}")
        patch.status = PatchStatus.APPLIED
        patch.commit_hash = commit_hash
        await db.commit()
        return {"message": "Patch applied successfully", "commit_hash": commit_hash}
    except Exception as e:
        patch.status = PatchStatus.FAILED
        patch.validation_errors = [str(e)]
        await db.commit()
        raise HTTPException(status_code=500, detail=str(e))


# ─── Execution Runtime Endpoints ─────────────────────────────────────────────

from src.models.execution_runtime import ExecutionJob, ContainerSession, RuntimeLog, BuildArtifact
from src.models.enums import ExecutionStatus
from src.services.sandbox_engine import SandboxEngine
from src.services.git import git_service

class ExecuteRequest(BaseModel):
    workflow_id: UUID | None = None


@router.post("/{repository_id}/patches/{patch_id}/execute", status_code=202)
async def api_execute_patch(
    repository_id: UUID,
    patch_id: UUID,
    req: ExecuteRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Creates an ExecutionJob and runs the sandbox pipeline in the background."""
    repo = await db.get(Repository, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Resolve workspace path
    owner, repo_name_raw = repo.remote_url.rstrip("/").split("/")[-2:]
    repo_name = repo_name_raw.removesuffix(".git")
    workspace_path = git_service.get_repo_path(owner, repo_name)

    if not workspace_path.exists():
        raise HTTPException(status_code=400, detail="Repository has not been cloned yet. Please index it first.")

    job = ExecutionJob(
        workflow_id=req.workflow_id,
        repository_id=repository_id,
        patch_id=patch_id,
        status=ExecutionStatus.PENDING,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Run sandbox in background
    background_tasks.add_task(_run_sandbox, job.id, str(workspace_path))

    return {"message": "Execution job created", "job_id": job.id, "status": "PENDING"}


async def _run_sandbox(job_id: uuid.UUID, workspace_path: str):
    """Background task: creates a fresh DB session and runs the sandbox engine."""
    from src.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        engine = SandboxEngine(db=session)
        await engine.run(job_id=job_id, workspace_path=workspace_path)


@router.get("/{repository_id}/executions")
async def api_list_executions(
    repository_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all execution jobs for a repository."""
    stmt = select(ExecutionJob).where(ExecutionJob.repository_id == repository_id).order_by(desc(ExecutionJob.created_at))
    res = await db.execute(stmt)
    jobs = res.scalars().all()
    return [
        {
            "id": j.id,
            "patch_id": j.patch_id,
            "status": j.status,
            "started_at": j.started_at,
            "completed_at": j.completed_at,
            "error_message": j.error_message,
            "created_at": j.created_at,
        }
        for j in jobs
    ]


@router.get("/{repository_id}/executions/{job_id}")
async def api_get_execution(
    repository_id: UUID,
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single execution job with full log history."""
    job = await db.get(ExecutionJob, job_id)
    if not job or job.repository_id != repository_id:
        raise HTTPException(status_code=404, detail="Execution job not found")

    logs_res = await db.execute(select(RuntimeLog).where(RuntimeLog.job_id == job_id).order_by(RuntimeLog.created_at))
    logs = logs_res.scalars().all()

    return {
        "id": job.id,
        "status": job.status,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "error_message": job.error_message,
        "logs": [{"phase": l.phase, "stream": l.stream, "content": l.content, "created_at": l.created_at} for l in logs],
    }


@router.delete("/{repository_id}/executions/{job_id}", status_code=204)
async def api_cancel_execution(
    repository_id: UUID,
    job_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Marks a pending/provisioning job as cancelled."""
    job = await db.get(ExecutionJob, job_id)
    if not job or job.repository_id != repository_id:
        raise HTTPException(status_code=404, detail="Execution job not found")

    if job.status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED):
        raise HTTPException(status_code=400, detail="Cannot cancel a finished job")

    job.status = ExecutionStatus.FAILED
    job.error_message = "Cancelled by user"
    await db.commit()
    return None

