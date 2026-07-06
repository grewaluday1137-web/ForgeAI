import httpx
import logging
from src.core.config import settings

logger = logging.getLogger(__name__)

class GitHubClient:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ForgeAI-Agent"
        }
        if settings.GITHUB_PAT:
            self.headers["Authorization"] = f"Bearer {settings.GITHUB_PAT}"

    async def get_repository(self, owner: str, repo: str) -> dict:
        """Fetch repository metadata from GitHub."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code != 200:
                logger.error(f"GitHub API error {response.status_code}: {response.text}")
                raise ValueError(f"Failed to fetch repository {owner}/{repo}: {response.text}")
            return response.json()

    async def list_branches(self, owner: str, repo: str) -> list[dict]:
        """Fetch all branches for a repository."""
        url = f"{self.base_url}/repos/{owner}/{repo}/branches"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            if response.status_code != 200:
                logger.error(f"GitHub API error {response.status_code}: {response.text}")
                raise ValueError(f"Failed to list branches for {owner}/{repo}: {response.text}")
            return response.json()

github_client = GitHubClient()
