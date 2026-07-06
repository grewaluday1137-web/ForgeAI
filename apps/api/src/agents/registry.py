import logging
from src.agents.base import BaseAgent
from src.models.enums import AgentType
from src.agents.planner.agent import PlannerAgent
from src.agents.architect.agent import ArchitectAgent
from src.agents.developer.agent import DeveloperAgent
from src.agents.tester.agent import TesterAgent

logger = logging.getLogger(__name__)


class _InactiveAgent(BaseAgent):
    """Placeholder for agents not yet implemented in this milestone."""

    def __init__(self, agent_type: AgentType):
        self._agent_type = agent_type

    @property
    def agent_type(self) -> AgentType:
        return self._agent_type

    async def run(self, context):
        raise NotImplementedError(
            f"Agent {self._agent_type.value} is registered but not yet active. "
            "It will be implemented in a future milestone."
        )

    def validate(self, result) -> bool:
        return False


class AgentRegistry:
    """
    Central registry for all ForgeAI agents.
    All 8 agent types are registered; only PlannerAgent, ArchitectAgent, and DeveloperAgent execute.
    Future milestones activate remaining agents without any architectural changes.
    """

    def __init__(self):
        self._registry: dict[AgentType, BaseAgent] = {}
        self._active: set[AgentType] = set()
        self._setup()

    def _setup(self):
        # Import and register the active agents
        self.register(AgentType.PLANNER, PlannerAgent(), active=True)
        self.register(AgentType.ARCHITECT, ArchitectAgent(), active=True)
        self.register(AgentType.DEVELOPER, DeveloperAgent(), active=True)
        self.register(AgentType.TESTER, TesterAgent(), active=True)

        # Register all other agents as inactive placeholders
        for agent_type in [
            AgentType.REVIEWER,
            AgentType.SECURITY,
            AgentType.DOCUMENTATION,
            AgentType.DEPLOYMENT,
        ]:
            self.register(agent_type, _InactiveAgent(agent_type), active=False)

    def register(self, agent_type: AgentType, agent: BaseAgent, active: bool = True):
        self._registry[agent_type] = agent
        if active:
            self._active.add(agent_type)
        logger.info(f"[AgentRegistry] Registered {agent_type.value} (active={active})")

    def get(self, agent_type: AgentType) -> BaseAgent:
        agent = self._registry.get(agent_type)
        if not agent:
            raise KeyError(f"Agent {agent_type.value} is not registered.")
        return agent

    def is_active(self, agent_type: AgentType) -> bool:
        return agent_type in self._active

    def list_all(self) -> list[dict]:
        return [
            {
                "agent_type": agent_type.value,
                "active": self.is_active(agent_type),
                "description": self._get_description(agent_type),
            }
            for agent_type in AgentType
        ]

    def _get_description(self, agent_type: AgentType) -> str:
        descriptions = {
            AgentType.PLANNER: "Analyzes requests and generates structured execution plans.",
            AgentType.ARCHITECT: "Analyzes repository structure and recommends implementation strategy.",
            AgentType.DEVELOPER: "Implements code changes, new files, and refactors.",
            AgentType.TESTER: "Generates and executes unit and integration tests.",
            AgentType.REVIEWER: "Reviews generated code for quality and correctness.",
            AgentType.SECURITY: "Audits code for vulnerabilities and security risks.",
            AgentType.DOCUMENTATION: "Updates README, API docs, and inline comments.",
            AgentType.DEPLOYMENT: "Prepares Docker config, env validation, and deployment checklist.",
        }
        return descriptions.get(agent_type, "No description available.")


# Singleton registry instance
registry = AgentRegistry()
