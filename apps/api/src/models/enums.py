import enum

class ProjectVisibility(str, enum.Enum):
    PRIVATE = "PRIVATE"
    TEAM = "TEAM"
    PUBLIC = "PUBLIC"

class ProjectStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"

class WorkspaceStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"

class WorkflowStatus(str, enum.Enum):
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class ProjectPermission(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    WRITE = "WRITE"
    READ = "READ"

class AgentType(str, enum.Enum):
    PLANNER = "PLANNER"
    ARCHITECT = "ARCHITECT"
    DEVELOPER = "DEVELOPER"
    TESTER = "TESTER"
    REVIEWER = "REVIEWER"
    SECURITY = "SECURITY"
    DOCUMENTATION = "DOCUMENTATION"
    DEPLOYMENT = "DEPLOYMENT"

class AgentExecutionStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    SKIPPED = "SKIPPED"

class LogLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
