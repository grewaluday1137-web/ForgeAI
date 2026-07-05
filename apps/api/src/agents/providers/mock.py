import json
from typing import Any
from src.agents.providers.base import AIProvider, Message


class MockProvider(AIProvider):
    """
    Deterministic mock AI provider for testing and development.
    Returns a realistic structured execution plan without calling any external API.
    Used when GEMINI_API_KEY is not configured.
    """

    @property
    def provider_name(self) -> str:
        return "mock-provider"

    async def complete(
        self,
        messages: list[Message],
        response_schema: dict | None = None,
        temperature: float = 0.3,
    ) -> dict[str, Any]:
        # Extract user request from messages
        user_request = next(
            (m.content for m in messages if m.role == "user"),
            "Implement requested feature"
        )

        return {
            "objective": f"Implement the following: {user_request}",
            "scope": "Full-stack feature implementation including backend API, database, and frontend UI changes.",
            "assumptions": [
                "The project follows existing Clean Architecture patterns.",
                "All new APIs will be versioned under /api/v1.",
                "TypeScript strict mode is enforced on the frontend.",
            ],
            "risks": [
                "Schema changes may require database migration coordination.",
                "Frontend state management complexity may increase.",
            ],
            "estimated_complexity": "MEDIUM",
            "phases": [
                {
                    "id": "phase-1",
                    "name": "Architecture & Planning",
                    "description": "Analyze the repository and design the solution architecture.",
                    "agents": ["ARCHITECT"]
                },
                {
                    "id": "phase-2",
                    "name": "Implementation",
                    "description": "Implement backend and frontend changes.",
                    "agents": ["DEVELOPER"]
                },
                {
                    "id": "phase-3",
                    "name": "Quality Assurance",
                    "description": "Testing, security review, and documentation.",
                    "agents": ["TESTER", "SECURITY", "DOCUMENTATION"]
                },
                {
                    "id": "phase-4",
                    "name": "Review & Deploy",
                    "description": "Final review and deployment preparation.",
                    "agents": ["REVIEWER", "DEPLOYMENT"]
                }
            ],
            "ordered_tasks": [
                {
                    "order": 1,
                    "title": "Analyze repository architecture",
                    "description": "Scan project structure, detect frameworks, and map affected files.",
                    "agent_type": "ARCHITECT",
                    "priority": 1,
                    "dependencies": []
                },
                {
                    "order": 2,
                    "title": "Implement backend API changes",
                    "description": "Add new models, services, and REST endpoints following Clean Architecture.",
                    "agent_type": "DEVELOPER",
                    "priority": 2,
                    "dependencies": ["Analyze repository architecture"]
                },
                {
                    "order": 3,
                    "title": "Implement frontend UI changes",
                    "description": "Create React components, hooks, and API integrations.",
                    "agent_type": "DEVELOPER",
                    "priority": 3,
                    "dependencies": ["Implement backend API changes"]
                },
                {
                    "order": 4,
                    "title": "Generate unit and integration tests",
                    "description": "Write comprehensive tests for all new functionality.",
                    "agent_type": "TESTER",
                    "priority": 4,
                    "dependencies": ["Implement backend API changes", "Implement frontend UI changes"]
                },
                {
                    "order": 5,
                    "title": "Security vulnerability scan",
                    "description": "Audit new code for security issues, exposed secrets, and OWASP risks.",
                    "agent_type": "SECURITY",
                    "priority": 5,
                    "dependencies": ["Implement backend API changes"]
                },
                {
                    "order": 6,
                    "title": "Update documentation",
                    "description": "Update README, API docs, and inline comments.",
                    "agent_type": "DOCUMENTATION",
                    "priority": 6,
                    "dependencies": ["Implement backend API changes", "Implement frontend UI changes"]
                },
                {
                    "order": 7,
                    "title": "Code review and quality check",
                    "description": "Final review of all generated code against quality standards.",
                    "agent_type": "REVIEWER",
                    "priority": 7,
                    "dependencies": ["Generate unit and integration tests", "Security vulnerability scan"]
                },
                {
                    "order": 8,
                    "title": "Prepare deployment artifacts",
                    "description": "Generate Docker configuration, environment variables, and deployment checklist.",
                    "agent_type": "DEPLOYMENT",
                    "priority": 8,
                    "dependencies": ["Code review and quality check"]
                }
            ],
            "recommended_agents": ["ARCHITECT", "DEVELOPER", "TESTER", "SECURITY", "DOCUMENTATION", "REVIEWER", "DEPLOYMENT"]
        }
