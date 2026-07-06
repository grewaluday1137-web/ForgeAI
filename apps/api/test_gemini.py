import asyncio
import sys
sys.path.insert(0, "/app")

from src.agents.providers.gemini import GeminiProvider
from src.agents.providers.base import Message
from src.agents.planner.schemas import ExecutionPlanOutput
from src.agents.prompts.planner import build_planner_prompt
from src.agents.context import ExecutionContext
from uuid import uuid4

async def test_gemini():
    provider = GeminiProvider()
    context = ExecutionContext(
        workflow_id=uuid4(),
        project_id=uuid4(),
        workspace_id=uuid4(),
        user_id=uuid4(),
        user_request="Build a simple login page in Next.js",
        repository_id=None
    )
    messages = build_planner_prompt(context)
    try:
        raw_output = await provider.complete(
            messages=messages,
            response_schema=ExecutionPlanOutput.model_json_schema(),
            temperature=0.3
        )
        print("SUCCESS")
        print(raw_output)
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
