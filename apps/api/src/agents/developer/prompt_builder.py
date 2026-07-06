import json
import logging
from typing import Any
from src.agents.prompts.developer import DEVELOPER_SYSTEM_PROMPT
from src.agents.providers.base import Message

logger = logging.getLogger(__name__)

class PromptBuilder:
    """
    Constructs dynamic prompts for the Developer Agent by injecting repository context and file contents.
    """

    def build_messages(self, task_description: str, repo_context: dict, relevant_files: list[dict]) -> list[Message]:
        
        # Format the repository context
        context_str = f"Architecture Summary:\n{repo_context.get('architecture_summary', 'N/A')}\n\n"
        context_str += f"Languages: {', '.join(repo_context.get('languages', []))}\n"
        context_str += f"Frameworks: {', '.join(repo_context.get('frameworks', []))}\n"
        
        # Format the relevant files
        files_str = ""
        for f in relevant_files:
            files_str += f"\n--- File: {f['path']} ---\n"
            files_str += f"{f['content']}\n"
            files_str += "-" * 40 + "\n"
            
        user_prompt = f"""
## Repository Context
{context_str}

## Relevant Files
{files_str}

## Task
{task_description}

Remember to output ONLY valid JSON using the required schema. No markdown wrappers.
"""
        return [
            Message(role="system", content=DEVELOPER_SYSTEM_PROMPT),
            Message(role="user", content=user_prompt)
        ]
