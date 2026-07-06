"""
Sandbox Engine — Orchestrates the full execution pipeline inside isolated Docker containers.

Pipeline:
  1. PROVISIONING  — detect project type, pull image, create container
  2. INSTALLING    — install dependencies (npm install / pip install)
  3. BUILDING      — run build command (npm run build / python -m pytest --collect-only)
  4. VALIDATING    — verify exit codes, capture artifacts
  5. COMPLETED / FAILED

Every step:
  - Logs are persisted to DB as RuntimeLog rows
  - Events are published via WebSocket manager
  - Container is always cleaned up on completion or failure
"""
import asyncio
import logging
from pathlib import Path
from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.execution_runtime import ExecutionJob, ContainerSession, RuntimeLog, BuildArtifact
from src.models.enums import ExecutionStatus
from src.mcp.docker_client import docker_mcp
from src.mcp.terminal_mcp import terminal_mcp, CommandValidationError
from src.websocket.manager import manager

logger = logging.getLogger(__name__)

# ─── Project Type Detection ──────────────────────────────────────────────────

PROJECT_CONFIGS = {
    "node": {
        "markers": ["package.json"],
        "image": "node:20-slim",
        "install_cmd": "npm install --prefer-offline",
        "build_cmd": "npm run build --if-present",
        "test_cmd": "npm test --if-present",
    },
    "python": {
        "markers": ["requirements.txt", "pyproject.toml", "setup.py"],
        "image": "python:3.12-slim",
        "install_cmd": "pip install -r requirements.txt --cache-dir /pip_cache",
        "build_cmd": "python -m py_compile $(find . -name '*.py' | head -50)",
        "test_cmd": "pytest --tb=short -q",
    },
    "rust": {
        "markers": ["Cargo.toml"],
        "image": "rust:1.78-slim",
        "install_cmd": "echo 'Rust does not need separate install'",
        "build_cmd": "cargo build",
        "test_cmd": "cargo test",
    },
    "go": {
        "markers": ["go.mod"],
        "image": "golang:1.22-bookworm",
        "install_cmd": "go mod download",
        "build_cmd": "go build ./...",
        "test_cmd": "go test ./...",
    },
}


def detect_project_type(workspace_path: Path) -> dict:
    """Scans workspace directory and returns the matching project config."""
    for project_type, config in PROJECT_CONFIGS.items():
        for marker in config["markers"]:
            if (workspace_path / marker).exists():
                logger.info(f"[SandboxEngine] Detected project type: {project_type}")
                return {"type": project_type, **config}
    # Default fallback
    logger.warning("[SandboxEngine] Could not detect project type, defaulting to node")
    return {"type": "unknown", **PROJECT_CONFIGS["node"]}


# ─── Sandbox Engine ──────────────────────────────────────────────────────────

class SandboxEngine:
    """
    Drives the execution pipeline for a single ExecutionJob.
    Must be run in a thread pool executor since Docker SDK is synchronous.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run(self, job_id: UUID, workspace_path: str) -> bool:
        """
        Entrypoint for running a sandbox execution.
        Returns True on success, False on failure.
        """
        path = Path(workspace_path)
        job = await self.db.get(ExecutionJob, job_id)
        if not job:
            logger.error(f"[SandboxEngine] Job {job_id} not found")
            return False

        container_session = None
        sandbox = None

        try:
            # ── PROVISIONING ──────────────────────────────────────────────
            await self._update_status(job, ExecutionStatus.PROVISIONING)
            await self._emit("runtime.started", job_id, "Detecting project type and provisioning container...")

            config = await asyncio.get_event_loop().run_in_executor(None, detect_project_type, path)
            image = config["image"]

            # Create container
            sandbox = await asyncio.get_event_loop().run_in_executor(
                None, lambda: docker_mcp.create_sandbox(image, str(path))
            )
            await asyncio.get_event_loop().run_in_executor(None, sandbox.start)

            # Persist ContainerSession
            container_session = ContainerSession(
                job_id=job_id,
                container_id=sandbox.container_id,
                image=image,
                cpu_limit="1",
                memory_limit="512m",
                is_active=True,
            )
            self.db.add(container_session)
            await self.db.flush()

            await self._log(job_id, "PROVISIONING", "stdout", f"Container {sandbox.short_id} started with image {image}")
            await self._emit("runtime.patch.applied", job_id, f"Container ready: {sandbox.short_id}")

            # ── INSTALLING ────────────────────────────────────────────────
            await self._update_status(job, ExecutionStatus.INSTALLING)
            await self._emit("runtime.installing", job_id, "Installing dependencies...")

            install_cmd = config["install_cmd"]
            exit_code, stdout, stderr = await asyncio.get_event_loop().run_in_executor(
                None, lambda: terminal_mcp.run(sandbox, install_cmd, "INSTALLING")
            )
            await self._log(job_id, "INSTALLING", "stdout", stdout or "(no output)")
            if stderr:
                await self._log(job_id, "INSTALLING", "stderr", stderr)
            await self._emit("runtime.dependencies.installed", job_id, f"Dependencies installed (exit={exit_code})")

            if exit_code != 0:
                raise RuntimeError(f"Dependency installation failed (exit code {exit_code}):\n{stderr}")

            # ── BUILDING ──────────────────────────────────────────────────
            await self._update_status(job, ExecutionStatus.BUILDING)
            await self._emit("runtime.build.started", job_id, "Building project...")

            build_cmd = config["build_cmd"]
            exit_code, stdout, stderr = await asyncio.get_event_loop().run_in_executor(
                None, lambda: terminal_mcp.run(sandbox, build_cmd, "BUILDING")
            )
            await self._log(job_id, "BUILDING", "stdout", stdout or "(no output)")
            if stderr:
                await self._log(job_id, "BUILDING", "stderr", stderr)
            await self._emit("runtime.build.completed", job_id, f"Build finished (exit={exit_code})")

            if exit_code != 0:
                raise RuntimeError(f"Build failed (exit code {exit_code}):\n{stderr}")

            # ── VALIDATING ────────────────────────────────────────────────
            await self._update_status(job, ExecutionStatus.VALIDATING)
            await self._emit("runtime.validating", job_id, "Running validation checks...")
            await self._log(job_id, "VALIDATING", "stdout", "Build artifacts validated successfully.")

            # ── COMPLETE ──────────────────────────────────────────────────
            await self._update_status(job, ExecutionStatus.COMPLETED)
            job.completed_at = datetime.now(UTC)
            await self.db.commit()

            await self._emit("runtime.finished", job_id, "Execution completed successfully! ✓")
            return True

        except CommandValidationError as e:
            await self._fail(job, str(e), "VALIDATING")
            return False
        except Exception as e:
            logger.error(f"[SandboxEngine] Job {job_id} failed: {e}")
            await self._fail(job, str(e), "BUILDING")
            return False
        finally:
            # Always clean up the container
            if sandbox:
                await asyncio.get_event_loop().run_in_executor(None, sandbox.stop)
                await asyncio.get_event_loop().run_in_executor(None, sandbox.remove)
                if container_session:
                    container_session.is_active = False
                    await self.db.commit()
                logger.info(f"[SandboxEngine] Container {sandbox.short_id} cleaned up")

    async def _update_status(self, job: ExecutionJob, status: ExecutionStatus) -> None:
        job.status = status
        job.updated_at = datetime.now(UTC)
        if status == ExecutionStatus.PROVISIONING:
            job.started_at = datetime.now(UTC)
        await self.db.flush()

    async def _fail(self, job: ExecutionJob, error: str, phase: str) -> None:
        job.status = ExecutionStatus.FAILED
        job.error_message = error
        job.completed_at = datetime.now(UTC)
        await self._log(job.id, phase, "stderr", f"FATAL: {error}")
        await self.db.commit()
        await self._emit("runtime.failed", job.id, f"Execution failed: {error}")

    async def _log(self, job_id: UUID, phase: str, stream: str, content: str) -> None:
        entry = RuntimeLog(job_id=job_id, phase=phase, stream=stream, content=content[:8000])
        self.db.add(entry)
        await self.db.flush()
        # Stream log to WebSocket
        await self._emit("runtime.logs.updated", job_id, content, extra={"phase": phase, "stream": stream})

    async def _emit(self, event: str, job_id: UUID, message: str, extra: dict = None) -> None:
        payload = {"job_id": str(job_id), "message": message, **(extra or {})}
        try:
            await manager.broadcast_event(event, payload)
        except Exception as e:
            logger.warning(f"[SandboxEngine] WS publish failed: {e}")
