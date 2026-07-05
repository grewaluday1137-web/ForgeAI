from pydantic import BaseModel, Field
from typing import Literal


class PlanPhase(BaseModel):
    id: str
    name: str
    description: str
    agents: list[str]


class PlanTask(BaseModel):
    order: int
    title: str
    description: str
    agent_type: Literal["ARCHITECT", "DEVELOPER", "TESTER", "SECURITY", "DOCUMENTATION", "REVIEWER", "DEPLOYMENT"]
    priority: int = 1
    dependencies: list[str] = Field(default_factory=list)


class ExecutionPlanOutput(BaseModel):
    """Pydantic schema for the Planner Agent's structured output."""
    objective: str
    scope: str
    assumptions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    estimated_complexity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"
    phases: list[PlanPhase] = Field(default_factory=list)
    ordered_tasks: list[PlanTask] = Field(default_factory=list)
    recommended_agents: list[str] = Field(default_factory=list)
