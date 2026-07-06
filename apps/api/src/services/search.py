import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from src.models.analysis import RepositoryIndex

logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_files(self, repository_id: UUID, query: str, limit: int = 50) -> list[dict]:
        """
        Searches the repository index for file paths or metadata matching the query.
        For Milestone 6, this is a simple ILIKE search on file_path.
        """
        stmt = (
            select(RepositoryIndex)
            .where(
                RepositoryIndex.repository_id == repository_id,
                RepositoryIndex.file_path.ilike(f"%{query}%")
            )
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        files = result.scalars().all()
        
        return [
            {
                "id": str(f.id),
                "file_path": f.file_path,
                "file_type": f.file_type,
                "size_bytes": f.size_bytes,
            }
            for f in files
        ]
