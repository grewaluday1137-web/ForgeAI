import os
import hashlib
import logging
from pathlib import Path
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.analysis import RepositoryIndex
from src.services.git import git_service

logger = logging.getLogger(__name__)

# Basic file type detection based on extension
EXTENSION_MAP = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript-react",
    ".js": "javascript",
    ".jsx": "javascript-react",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".json": "json",
    ".md": "markdown",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".sh": "shell",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c-header",
    ".hpp": "cpp-header",
}

IGNORED_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", "coverage", ".next"}

class RepositoryIndexer:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def index_repository(self, repository_id: UUID, owner: str, repo_name: str) -> int:
        """
        Traverses the cloned repository and inserts/updates RepositoryIndex records.
        Returns the number of indexed files.
        """
        repo_path = git_service._get_repo_path(owner, repo_name)
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository not found locally at {repo_path}")

        logger.info(f"Indexing repository {owner}/{repo_name}...")
        indexed_count = 0

        # Run file traversal (synchronous operations like os.walk and hashing)
        # Should normally be offloaded to threadpool for large repos, but doing it simply for now.
        for root, dirs, files in os.walk(repo_path):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

            for file in files:
                file_path = Path(root) / file
                
                # Skip symlinks and hidden files except certain config files (like .env or .gitignore)
                if file_path.is_symlink():
                    continue
                if file.startswith(".") and file not in [".env", ".gitignore", ".eslintrc.json", ".prettierrc"]:
                    continue

                rel_path = file_path.relative_to(repo_path).as_posix()
                ext = file_path.suffix.lower()
                
                # Try to determine file type
                file_type = EXTENSION_MAP.get(ext, "unknown")
                if file_type == "unknown" and file in ["Dockerfile", "docker-compose.yml", "Makefile"]:
                    file_type = "config"

                # If we don't know it and it has no extension, assume unknown (could be a binary, we'll skip binaries if large)
                try:
                    size = file_path.stat().st_size
                    # Skip files larger than 1MB
                    if size > 1_000_000:
                        continue
                    
                    with open(file_path, "rb") as f:
                        content = f.read()
                        
                    # basic binary check
                    if b"\0" in content:
                        continue
                        
                    content_hash = hashlib.sha256(content).hexdigest()
                    
                    # Create DB record
                    # In a real system, we'd check if it exists and update, or bulk insert.
                    # For simplicity, we just insert. We should delete old indexes first.
                    idx = RepositoryIndex(
                        repository_id=repository_id,
                        file_path=rel_path,
                        file_type=file_type,
                        size_bytes=size,
                        content_hash=content_hash,
                        metadata_json={}
                    )
                    self.db.add(idx)
                    indexed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to index {file_path}: {e}")
                    
        await self.db.commit()
        logger.info(f"Indexed {indexed_count} files for {owner}/{repo_name}.")
        return indexed_count
