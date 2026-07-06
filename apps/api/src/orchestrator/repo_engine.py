import asyncio
import logging
import uuid
from uuid import UUID
from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import AsyncSessionLocal as async_session_maker

from src.models.repository import Repository
from src.models.analysis import RepositorySnapshot, RepositoryAnalysis, KnowledgeNode
from src.services.github import github_client
from src.services.git import git_service
from src.services.indexer import RepositoryIndexer
from src.agents.registry import registry
from src.models.enums import AgentType
from src.agents.context import ExecutionContext
from src.websocket.manager import manager

logger = logging.getLogger(__name__)

class RepositoryEngine:
    """
    Handles the asynchronous background flow:
    Connect -> Clone -> Index -> Architect
    """

    async def _publish(self, event: str, payload: dict) -> None:
        """Publish a namespaced event to Redis for real-time WebSocket delivery."""
        try:
            await manager.broadcast_event(event, payload)
        except Exception as e:
            logger.error(f"[RepoEngine] Failed to publish event {event}: {e}")

    async def process_repository(self, repository_id: UUID) -> None:
        """Main pipeline to process a repository connection."""
        try:
            # We use a dedicated DB session for the background task
            async with async_session_maker() as db:
                repo_res = await db.execute(select(Repository).where(Repository.id == repository_id))
                repo = repo_res.scalar_one_or_none()
                if not repo:
                    logger.error(f"Repository {repository_id} not found.")
                    return

                # Get repo info from GitHub
                # For this milestone, we expect repo.remote_url to contain the owner/repo format like "owner/repo"
                owner, repo_name = repo.remote_url.split("/")[-2:]
                if repo_name.endswith(".git"):
                    repo_name = repo_name[:-4]

                # Step 1: Create Snapshot
                snapshot = RepositorySnapshot(
                    repository_id=repository_id,
                    branch=repo.default_branch,
                    status="CLONING"
                )
                db.add(snapshot)
                await db.commit()
                
                await self._publish("repository.connected", {
                    "repository_id": str(repository_id),
                    "message": f"Connected to {owner}/{repo_name}. Starting clone..."
                })

                # Step 2: Clone
                clone_url = f"https://github.com/{owner}/{repo_name}.git"
                local_path = await git_service.clone_repository(owner, repo_name, clone_url)
                commit_hash = await git_service.get_latest_commit(owner, repo_name, repo.default_branch)
                
                snapshot.commit_hash = commit_hash
                snapshot.status = "INDEXING"
                repo.local_path = local_path
                repo.is_connected = True
                repo.last_sync = datetime.now(UTC)
                await db.commit()
                
                await self._publish("repository.synced", {
                    "repository_id": str(repository_id),
                    "message": f"Repository cloned successfully at commit {commit_hash[:7]}."
                })
                
                await self._publish("repository.index.started", {
                    "repository_id": str(repository_id),
                    "message": "Starting indexer..."
                })

                # Step 3: Index
                indexer = RepositoryIndexer(db)
                indexed_count = await indexer.index_repository(repository_id, owner, repo_name)
                
                snapshot.status = "ANALYZING"
                await db.commit()
                
                await self._publish("repository.index.completed", {
                    "repository_id": str(repository_id),
                    "message": f"Indexed {indexed_count} files."
                })

                # Step 4: Architect Agent
                await self._publish("architect.started", {
                    "repository_id": str(repository_id),
                    "message": "Architect Agent is analyzing the codebase..."
                })
                
                architect = registry.get(AgentType.ARCHITECT)
                context = ExecutionContext(
                    workflow_id=repository_id, # Reusing context for repo analysis
                    project_id=repo.project_id,
                    workspace_id=uuid.uuid4(), # Dummy
                    user_id=repo.created_by,
                    user_request=f"Total indexed files: {indexed_count}",
                    repository_id=repository_id
                )
                
                result = await architect.run(context)
                
                if result.success:
                    data = result.output
                    
                    # Store analysis
                    analysis = RepositoryAnalysis(
                        repository_id=repository_id,
                        snapshot_id=snapshot.id,
                        languages=data.get("languages", []),
                        frameworks=data.get("frameworks", []),
                        package_managers=data.get("package_managers", []),
                        architecture_patterns=data.get("architecture_patterns", []),
                        architecture_summary=data.get("architecture_summary", "")
                    )
                    db.add(analysis)
                    
                    # Store key components as KnowledgeNodes
                    for comp in data.get("key_components", []):
                        node = KnowledgeNode(
                            repository_id=repository_id,
                            node_type=comp.get("type", "Module"),
                            name=comp.get("name", "Unknown"),
                            path=comp.get("path", ""),
                            metadata_json={"description": comp.get("description", "")}
                        )
                        db.add(node)
                        
                    snapshot.status = "COMPLETED"
                    snapshot.completed_at = datetime.now(UTC)
                    await db.commit()
                    
                    await self._publish("architect.completed", {
                        "repository_id": str(repository_id),
                        "message": "Architecture analysis complete!"
                    })
                else:
                    logger.error(f"Architect Agent failed: {result.error}")
                    snapshot.status = "FAILED"
                    snapshot.error_message = result.error
                    snapshot.completed_at = datetime.now(UTC)
                    await db.commit()
                    
                    await self._publish("architect.failed", {
                        "repository_id": str(repository_id),
                        "error": result.error
                    })

        except Exception as e:
            logger.error(f"Error processing repository {repository_id}: {e}")
            # Try to mark snapshot as failed
            try:
                async with async_session_maker() as db:
                    snap_res = await db.execute(select(RepositorySnapshot).where(RepositorySnapshot.repository_id == repository_id).order_by(RepositorySnapshot.created_at.desc()))
                    snap = snap_res.scalar_one_or_none()
                    if snap:
                        snap.status = "FAILED"
                        snap.error_message = str(e)
                        await db.commit()
            except:
                pass

repo_engine = RepositoryEngine()
