import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.analysis import RepositoryIndex, RepositoryAnalysis, KnowledgeNode, KnowledgeEdge

logger = logging.getLogger(__name__)

class ContextEngine:
    """
    Provides context to other agents by querying the Project Knowledge Graph
    and Repository Index.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_repository_context(self, repository_id: UUID) -> dict:
        """
        Retrieves a summary of the repository for agent context.
        """
        # Get Architecture Summary
        analysis_stmt = select(RepositoryAnalysis).where(RepositoryAnalysis.repository_id == repository_id).order_by(RepositoryAnalysis.created_at.desc())
        analysis_res = await self.db.execute(analysis_stmt)
        analysis = analysis_res.scalars().first()
        
        # Get Key Nodes (e.g., core files, main modules)
        nodes_stmt = select(KnowledgeNode).where(RepositoryAnalysis.repository_id == repository_id).limit(20)
        nodes_res = await self.db.execute(nodes_stmt)
        nodes = nodes_res.scalars().all()
        
        # Get file count
        count_stmt = select(RepositoryIndex).where(RepositoryIndex.repository_id == repository_id)
        count_res = await self.db.execute(count_stmt)
        files = count_res.scalars().all()
        
        return {
            "file_count": len(files),
            "languages": analysis.languages if analysis else [],
            "frameworks": analysis.frameworks if analysis else [],
            "architecture_patterns": analysis.architecture_patterns if analysis else [],
            "architecture_summary": analysis.architecture_summary if analysis else "No analysis available.",
            "key_components": [n.name for n in nodes]
        }
