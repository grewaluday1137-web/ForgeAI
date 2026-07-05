from src.models.enums import WorkflowStatus


class InvalidStateTransition(Exception):
    """Raised when an illegal workflow state transition is attempted."""
    pass


# Define all legal transitions
LEGAL_TRANSITIONS: dict[WorkflowStatus, set[WorkflowStatus]] = {
    WorkflowStatus.CREATED:              {WorkflowStatus.PLANNING, WorkflowStatus.CANCELLED},
    WorkflowStatus.PLANNING:             {WorkflowStatus.READY, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED},
    WorkflowStatus.READY:                {WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED},
    WorkflowStatus.RUNNING:              {WorkflowStatus.WAITING_FOR_APPROVAL, WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED},
    WorkflowStatus.WAITING_FOR_APPROVAL: {WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED},
    WorkflowStatus.COMPLETED:            set(),  # Terminal state
    WorkflowStatus.FAILED:               {WorkflowStatus.PLANNING},  # Allow retry from failed
    WorkflowStatus.CANCELLED:            set(),  # Terminal state
}


class WorkflowStateMachine:
    """
    Validates and enforces legal workflow state transitions.
    The Orchestrator calls this before updating any workflow status.
    """

    @staticmethod
    def can_transition(from_status: WorkflowStatus, to_status: WorkflowStatus) -> bool:
        allowed = LEGAL_TRANSITIONS.get(from_status, set())
        return to_status in allowed

    @staticmethod
    def validate_transition(from_status: WorkflowStatus, to_status: WorkflowStatus) -> None:
        """Raises InvalidStateTransition if the transition is not legal."""
        if not WorkflowStateMachine.can_transition(from_status, to_status):
            raise InvalidStateTransition(
                f"Cannot transition workflow from {from_status.value} to {to_status.value}. "
                f"Allowed transitions: {[s.value for s in LEGAL_TRANSITIONS.get(from_status, set())]}"
            )
