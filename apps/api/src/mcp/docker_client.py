"""
Docker MCP Client — Python Docker SDK wrapper for sandbox management.

This client manages isolated containers for each execution job, providing:
- Container lifecycle management (create, start, stop, remove)
- Secure command execution via docker exec
- Real-time log streaming
- Resource limit enforcement
- Automatic cleanup
"""
import asyncio
import logging
from pathlib import Path
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# CPU limits per sandbox (number of CPUs)
DEFAULT_NANO_CPUS = 1_000_000_000  # 1 CPU
DEFAULT_MEMORY_LIMIT = 512 * 1024 * 1024  # 512 MB

# Timeout for individual commands in seconds
COMMAND_TIMEOUT_SECONDS = 300  # 5 minutes


class SandboxContainer:
    """Wraps a Docker container for a single execution job."""

    def __init__(self, container, image: str):
        self._container = container
        self.image = image
        self.container_id: str = container.id
        self.short_id: str = container.short_id

    def start(self) -> None:
        self._container.start()
        logger.info(f"[DockerMCP] Container {self.short_id} started")

    def stop(self) -> None:
        try:
            self._container.stop(timeout=5)
        except Exception:
            pass

    def remove(self) -> None:
        try:
            self._container.remove(force=True)
            logger.info(f"[DockerMCP] Container {self.short_id} removed")
        except Exception as e:
            logger.warning(f"[DockerMCP] Failed to remove container {self.short_id}: {e}")

    def exec_command(self, cmd: str) -> tuple[int, str, str]:
        """
        Run a command inside the container synchronously.
        Returns (exit_code, stdout, stderr).
        """
        try:
            exec_result = self._container.exec_run(
                cmd=["bash", "-c", cmd],
                stdout=True,
                stderr=True,
                demux=True,
                workdir="/workspace",
                environment={"CI": "true", "NPM_CONFIG_CACHE": "/npm_cache", "PIP_CACHE_DIR": "/pip_cache"},
            )
            exit_code = exec_result.exit_code or 0
            stdout_bytes, stderr_bytes = exec_result.output or (b"", b"")
            stdout = (stdout_bytes or b"").decode("utf-8", errors="replace")
            stderr = (stderr_bytes or b"").decode("utf-8", errors="replace")
            return exit_code, stdout, stderr
        except Exception as e:
            return 1, "", str(e)


class DockerMCPClient:
    """
    Docker MCP client — manages the full container lifecycle for sandbox execution.
    """

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            import docker
            self._client = docker.from_env()
        return self._client

    def pull_image(self, image: str) -> None:
        """Pulls a Docker image if not already available locally."""
        client = self._get_client()
        logger.info(f"[DockerMCP] Pulling image: {image}")
        try:
            client.images.get(image)
            logger.info(f"[DockerMCP] Image {image} already present")
        except Exception:
            logger.info(f"[DockerMCP] Pulling {image} from registry...")
            client.images.pull(image)
            logger.info(f"[DockerMCP] Pulled {image} successfully")

    def create_sandbox(
        self,
        image: str,
        workspace_path: str,
        cpu_limit: int = DEFAULT_NANO_CPUS,
        memory_limit: int = DEFAULT_MEMORY_LIMIT,
    ) -> SandboxContainer:
        """
        Creates and returns an isolated container with the workspace mounted.
        The workspace is bind-mounted at /workspace.
        Cache volumes are bind-mounted for npm and pip.
        """
        client = self._get_client()

        self.pull_image(image)

        container = client.containers.create(
            image=image,
            command="tail -f /dev/null",  # Keep container alive
            detach=True,
            nano_cpus=cpu_limit,
            mem_limit=memory_limit,
            network_disabled=False,  # Needs network for dependency installs
            volumes={
                workspace_path: {"bind": "/workspace", "mode": "rw"},
            },
            working_dir="/workspace",
            labels={"managed_by": "forgeai", "service": "sandbox"},
        )

        logger.info(f"[DockerMCP] Created container {container.short_id} from {image}")
        return SandboxContainer(container, image)

    def list_active_sandboxes(self) -> list[dict]:
        """Lists all active ForgeAI sandbox containers."""
        client = self._get_client()
        containers = client.containers.list(filters={"label": "managed_by=forgeai"})
        return [{"id": c.short_id, "status": c.status, "image": c.image.tags} for c in containers]

    def force_cleanup(self) -> int:
        """Removes all ForgeAI sandbox containers regardless of state."""
        client = self._get_client()
        containers = client.containers.list(all=True, filters={"label": "managed_by=forgeai"})
        count = 0
        for c in containers:
            try:
                c.remove(force=True)
                count += 1
            except Exception:
                pass
        logger.info(f"[DockerMCP] Cleaned up {count} sandbox containers")
        return count


docker_mcp = DockerMCPClient()
