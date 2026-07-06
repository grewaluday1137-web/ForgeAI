import os
import logging
import asyncio
from pathlib import Path
from git import Repo, GitCommandError
from src.core.config import settings

logger = logging.getLogger(__name__)

class GitService:
    def __init__(self):
        self.storage_path = Path(settings.REPO_STORAGE_PATH)
        # Ensure base storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_repo_path(self, owner: str, repo: str) -> Path:
        return self.storage_path / owner / repo

    async def clone_repository(self, owner: str, repo_name: str, clone_url: str) -> str:
        """
        Clones a repository to the local storage path.
        If it already exists, pulls the latest changes.
        Runs git operations in a threadpool since GitPython is synchronous.
        """
        repo_path = self._get_repo_path(owner, repo_name)
        
        # Inject PAT into URL if available for private repo support
        if settings.GITHUB_PAT and clone_url.startswith("https://"):
            auth_url = clone_url.replace("https://", f"https://oauth2:{settings.GITHUB_PAT}@")
        else:
            auth_url = clone_url

        def _do_clone():
            if repo_path.exists() and (repo_path / ".git").exists():
                logger.info(f"Repository {owner}/{repo_name} already exists. Pulling latest...")
                repo = Repo(repo_path)
                origin = repo.remotes.origin
                origin.pull()
                return str(repo_path)
            
            logger.info(f"Cloning {owner}/{repo_name} to {repo_path}...")
            repo_path.parent.mkdir(parents=True, exist_ok=True)
            Repo.clone_from(auth_url, repo_path)
            return str(repo_path)

        try:
            # Run the synchronous git operations in a background thread
            loop = asyncio.get_running_loop()
            result_path = await loop.run_in_executor(None, _do_clone)
            return result_path
        except GitCommandError as e:
            logger.error(f"Git command failed: {e}")
            raise ValueError(f"Failed to clone repository: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during clone: {e}")
            raise ValueError(f"Failed to setup repository: {e}")

    async def get_latest_commit(self, owner: str, repo_name: str, branch: str = "main") -> str:
        """Get the latest commit hash for a branch."""
        repo_path = self._get_repo_path(owner, repo_name)
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository not found locally at {repo_path}")
        
        def _get_commit():
            repo = Repo(repo_path)
            return repo.head.commit.hexsha
            
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _get_commit)

git_service = GitService()
