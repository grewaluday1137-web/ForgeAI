import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.analysis import RepositoryIndex, KnowledgeNode
from src.services.git import git_service
from pathlib import Path

logger = logging.getLogger(__name__)

class FileSelectionEngine:
    """
    Selects the most relevant files for a coding task.
    In Milestone 7, we use a basic keyword overlap heuristic against file paths and names.
    For a production system, this would use embeddings (RAG) or BM25 search.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def select_relevant_files(self, repository_id: UUID, owner: str, repo_name: str, task_description: str, max_files: int = 20) -> list[dict]:
        """
        Returns a list of dictionaries with 'path', 'content', and 'relevance_score'.
        """
        logger.info(f"Selecting files for task: {task_description[:50]}...")
        
        # 1. Extract naive keywords from task description (lowercase, > 3 chars)
        words = [w.strip(".,!?\"'") for w in task_description.lower().split()]
        keywords = set(w for w in words if len(w) > 3 and w not in {"this", "that", "with", "from", "into", "update", "create", "delete", "make", "change"})
        
        # 2. Fetch all index entries
        stmt = select(RepositoryIndex.file_path).where(RepositoryIndex.repository_id == repository_id)
        res = await self.db.execute(stmt)
        all_files = res.scalars().all()
        
        # 3. Score files based on keyword matches in path
        scored_files = []
        for file_path in all_files:
            score = 0
            path_lower = file_path.lower()
            
            # Boost exact keyword matches in the filename
            filename = path_lower.split("/")[-1]
            for kw in keywords:
                if kw in filename:
                    score += 10
                elif kw in path_lower:
                    score += 3
                    
            if score > 0:
                scored_files.append((file_path, score))
                
        # Sort by score descending, take top N
        scored_files.sort(key=lambda x: x[1], reverse=True)
        top_files = scored_files[:max_files]
        
        # If no keywords matched, just pick the first few files to give *some* context (fallback for simple prompts)
        if not top_files and all_files:
            top_files = [(f, 1) for f in all_files[:max_files]]
            
        # 4. Read the actual contents from the local clone
        repo_path = git_service._get_repo_path(owner, repo_name)
        selected_content = []
        
        for file_path, score in top_files:
            full_path = repo_path / file_path
            try:
                if full_path.exists() and full_path.is_file():
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    selected_content.append({
                        "path": file_path,
                        "content": content,
                        "score": score
                    })
            except Exception as e:
                logger.warning(f"Could not read selected file {file_path}: {e}")
                
        return selected_content

