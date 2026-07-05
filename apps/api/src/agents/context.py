from dataclasses import dataclass, field
from uuid import UUID
from typing import Any


@dataclass
class ExecutionContext:
    """
    Shared execution context passed to every agent.
    All future agents receive this automatically from the Orchestrator.
    """
    workflow_id: UUID
    project_id: UUID
    workspace_id: UUID
    user_id: UUID
    user_request: str

    # Optional — set as the workflow progresses
    repository_id: UUID | None = None
    active_branch: str = "main"
    current_task_id: UUID | None = None
    memory_reference: str | None = None  # Redis key for shared memory

    # Free-form variables for agent-to-agent communication
    execution_variables: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "workflow_id": str(self.workflow_id),
            "project_id": str(self.project_id),
            "workspace_id": str(self.workspace_id),
            "user_id": str(self.user_id),
            "user_request": self.user_request,
            "repository_id": str(self.repository_id) if self.repository_id else None,
            "active_branch": self.active_branch,
            "current_task_id": str(self.current_task_id) if self.current_task_id else None,
            "execution_variables": self.execution_variables,
        }
