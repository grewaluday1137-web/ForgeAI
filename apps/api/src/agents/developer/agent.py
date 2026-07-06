import time
# Force Docker Sync
import logging
import json
from src.agents.base import BaseAgent, AgentResult
from src.agents.context import ExecutionContext
from src.models.enums import AgentType
from src.agents.providers.factory import get_provider
from src.agents.developer.prompt_builder import PromptBuilder
from src.db.session import AsyncSessionLocal
from src.services.file_selector import FileSelectionEngine
from src.services.context_engine import ContextEngine

logger = logging.getLogger(__name__)

class DeveloperAgent(BaseAgent):
    """
    The Developer Agent.
    Analyzes project context, selects relevant files, and generates code patches.
    """

    @property
    def agent_type(self) -> AgentType:
        return AgentType.DEVELOPER

    async def run(self, context: ExecutionContext) -> AgentResult:
        start_time = time.time()
        logger.info(f"[{self.agent_type.value}] Starting for workflow {context.workflow_id}")

        try:
            # We need a DB session to retrieve context and select files
            async with AsyncSessionLocal() as db:
                context_engine = ContextEngine(db)
                file_selector = FileSelectionEngine(db)
                
                # Retrieve repository context (architecture, etc.)
                repo_context = await context_engine.get_repository_context(context.repository_id)
                
                # The user_request might contain the actual task for the developer.
                # In the orchestrator we'll pass the specific task description.
                task_description = context.user_request
                
                # For Milestone 7, we expect the remote_url to contain the owner/repo format for git service mapping
                # However we need the owner and repo_name here. We'll extract it from the repository in DB.
                from sqlalchemy import select
                from src.models.repository import Repository
                repo_res = await db.execute(select(Repository).where(Repository.id == context.repository_id))
                repo = repo_res.scalar_one_or_none()
                if not repo:
                    raise ValueError(f"Repository {context.repository_id} not found")
                    
                owner, repo_name = repo.remote_url.split("/")[-2:]
                if repo_name.endswith(".git"):
                    repo_name = repo_name[:-4]
                
                # Select files
                relevant_files = await file_selector.select_relevant_files(
                    repository_id=context.repository_id,
                    owner=owner,
                    repo_name=repo_name,
                    task_description=task_description,
                    max_files=15
                )
                
            # Build prompts
            builder = PromptBuilder()
            messages = builder.build_messages(task_description, repo_context, relevant_files)
            
            # Call LLM
            provider = get_provider()
            logger.info(f"[{self.agent_type.value}] Calling AI provider {provider.provider_name}...")
            
            response = await provider.complete(
                messages=messages,
                response_schema={}, # Expecting generic JSON per prompt
                temperature=0.2
            )
            
            duration = int((time.time() - start_time) * 1000)
            
            # Add metadata for the orchestrator to track PromptExecution
            response["_meta"] = {
                "system_prompt": messages[0].content,
                "user_prompt": messages[1].content,
                "raw_response": json.dumps(response),
                "duration_ms": duration,
                "provider": provider.provider_name
            }

            return AgentResult(
                agent_type=self.agent_type,
                success=True,
                output=response,
                duration_ms=duration
            )

        except Exception as e:
            logger.error(f"[{self.agent_type.value}] Failed: {e}")
            duration = int((time.time() - start_time) * 1000)
            return AgentResult(
                agent_type=self.agent_type,
                success=False,
                output={},
                error=str(e),
                duration_ms=duration
            )

    def validate(self, result: AgentResult) -> bool:
        if not result.success:
            return False
            
        data = result.output
        if "explanation" not in data:
            result.error = "Missing explanation"
            return False
        if "patches" not in data and "new_files" not in data and "deleted_files" not in data:
            result.error = "No changes requested (missing patches, new_files, and deleted_files)"
            return False
            
        return True
